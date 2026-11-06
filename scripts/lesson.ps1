# Share one general lesson (or team rule) with everyone: adds a line to team/lessons.md (-Rule: team/CLAUDE.md)
# on a fresh branch from origin/main (a temp worktree: your checkout is never touched), pushes it, opens a PR.
# No push rights → pushes to your fork. The owner merges; every session start pulls main, so it reaches all PCs.
#   lesson.ps1 -Text "PS 5.1: wrap git calls so stderr does not stop the script"   [-Rule] [-Handle you] [-DryRun]
param([Parameter(Mandatory)][string]$Text, [switch]$Rule, [string]$Handle = '', [switch]$DryRun,
      [string]$Dir = (Split-Path $PSScriptRoot), [string]$Upstream = 'ghostaiproject/Ghostskills')
$ErrorActionPreference = 'Continue'   # PS 5.1: git/gh stderr must not stop the script
$Text = ($Text -replace '\s+', ' ').Trim().TrimStart('-', ' ')
if ($Text -match 'ghp_|github_pat_|sk-|@[\w-]+\.[a-z]{2,}') { throw 'Looks like a secret or an email: the repo is public. Rewrite it without.' }
$login = "$(gh api user -q .login 2>$null)".Trim()
if (-not $login) { throw 'Not signed in to GitHub: run gh auth login first.' }
if (-not $Handle) { $Handle = $login }
$date = Get-Date -Format yyyy-MM-dd
$file = if ($Rule) { 'team/CLAUDE.md' } else { 'team/lessons.md' }
$line = "- $Text $([char]0xB7) $Handle $date"   # char, not the literal: PS 5.1 reads BOM-less scripts as ANSI
$branch = "lesson/$(Get-Date -Format yyyyMMdd-HHmmss)"
$canPush = "$(gh api "repos/$Upstream" -q .permissions.push 2>$null)".Trim() -eq 'true'
$remote = "https://github.com/$Upstream.git"; $head = $branch
if (-not $canPush) {
    gh repo fork $Upstream --clone=false 2>&1 | Out-Null
    $remote = "https://github.com/$login/$(($Upstream -split '/')[1]).git"; $head = "${login}:$branch"
}
git -C $Dir fetch -q "https://github.com/$Upstream.git" main 2>&1 | Out-Null
$wt = Join-Path ([IO.Path]::GetTempPath()) ("gs-" + ($branch -replace '/', '-'))
git -C $Dir worktree add -q -b $branch $wt FETCH_HEAD 2>&1 | Out-Null
if (-not (Test-Path (Join-Path $wt $file))) { throw "worktree failed ($wt)" }
try {
    $p = Join-Path $wt $file
    $t = [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8)
    if ($t.Contains($Text)) { 'Already in the team files: nothing to do.'; return }
    if (-not $t.EndsWith("`n")) { $t += "`n" }
    [IO.File]::WriteAllText($p, $t + $line + "`n", (New-Object Text.UTF8Encoding $false))
    if (-not "$(git -C $wt config user.email)") { git -C $wt config user.name $login; git -C $wt config user.email "$login@users.noreply.github.com" }
    git -C $wt commit -qam "lesson: $($Text.Substring(0, [Math]::Min(60, $Text.Length)))" 2>&1 | Out-Null
    if ($DryRun) { "dry run: would push $branch to $remote and open a PR on $Upstream with:"; $line; return }
    git -C $wt push -q $remote "HEAD:$branch" 2>&1 | Out-Null
    if ($LASTEXITCODE) { throw "push to $remote failed" }
    $body = "Adds one line to ``$file``:`n`n$line`n`nOpened by scripts/lesson.ps1 (/lesson)."
    gh pr create --repo $Upstream --base main --head $head --title "lesson: $($Text.Substring(0, [Math]::Min(60, $Text.Length)))" --body $body
} finally {
    git -C $Dir worktree remove --force $wt 2>&1 | Out-Null
    git -C $Dir branch -D $branch 2>&1 | Out-Null   # the branch lives on the remote now
}
