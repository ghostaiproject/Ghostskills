# Install Ghostskills on this PC: clone/pull the repo, link its skills into ~/.claude/skills, auto-update every Claude session.
# First run: -Projects grocrun,window (cards to add) -Personal <you> (your personal folder) -NoAutoUpdate (skip the hook)
#   -Config owner/repo (your private setup repo: CLAUDE.md, settings, hooks, memory; applied by its apply.ps1).
#   -Config auto: use <your-github>/claude-config, creating it (private) and capturing this PC into it if it does not exist.
#   -NoTeam: skip the shared team brain (team/: rules + lessons imported into CLAUDE.md, settings template merged in).
# Later runs (and the SessionStart hook) use -Update: pull + link any new skill, choices read from ~/.claude/ghostskills.json.
param([string[]]$Projects = @(), [string]$Personal = '', [string]$Dir = (Join-Path $HOME 'Ghostskills'),
      [string]$ClaudeDir = (Join-Path $HOME '.claude'), [string]$Config = '', [switch]$Update, [switch]$NoAutoUpdate, [switch]$NoTeam)
$ErrorActionPreference = 'Stop'
$url = 'https://github.com/ghostaiproject/Ghostskills.git'
$cfgFile = Join-Path $ClaudeDir 'ghostskills.json'
function Say($m) { if (-not $Update) { Write-Output $m } }

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'git not found. Install it: winget install Git.Git  (then reopen the terminal)' }
if ($Update -and (Test-Path $cfgFile)) {
    $c = [IO.File]::ReadAllText($cfgFile) | ConvertFrom-Json
    $Dir = $c.dir; $Projects = @($c.projects); $Personal = $c.personal; $Config = "$($c.config)"; $NoTeam = -not $c.team   # installs from before team/ existed: no team
}

# 1. Repo: clone once, then fast-forward only (never touches local work).
if (Test-Path (Join-Path $Dir '.git')) {
    $branch = git -C $Dir rev-parse --abbrev-ref HEAD
    if ($branch -eq 'main' -and -not (git -C $Dir status --porcelain)) { git -C $Dir pull -q --ff-only 2>$null }
    else { Say "Repo on '$branch' or has local changes: not pulled (switch to main and /sync first)." }
} else { git clone -q $url $Dir; Say "Cloned to $Dir" }

# 2. Pick skill folders: core, cer-01, tools for everyone + chosen projects/personal.
# -File passes -Projects a,b as ONE string: split it.
$Projects = @($Projects | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$roots = @('core', 'cer-01', 'tools') + ($Projects | Where-Object { $_ } | ForEach-Object { "projects/$_" })
if ($Personal) { $roots += "personal/$Personal" }
$skills = foreach ($r in $roots) {
    $p = Join-Path $Dir $r
    # Write-Host, not Say: output here lands in $skills as a nameless "skill" (that moved the whole skills folder, 2026-11-04).
    if (-not (Test-Path $p)) { if (-not $Update) { Write-Host "skip $r (not in repo)" }; continue }
    Get-ChildItem $p -Recurse -Filter SKILL.md | Where-Object { $_.FullName -notmatch '[\\/]_template[\\/]' } | ForEach-Object { $_.Directory }
}

# 3. Link each one (junction: no admin needed, edits land in the repo). A real folder there is moved to a backup first.
$target = Join-Path $ClaudeDir 'skills'
New-Item -ItemType Directory -Force $target | Out-Null
$backup = Join-Path $ClaudeDir ("skills-backup-" + (Get-Date -Format yyyyMMdd-HHmmss))
foreach ($s in $skills) {
    if (-not ($s -is [IO.DirectoryInfo]) -or -not $s.Name) { continue }
    $link = Join-Path $target $s.Name
    $item = Get-Item $link -Force -ErrorAction SilentlyContinue
    if ($item -and $item.LinkType) { if ($item.Target -contains $s.FullName) { continue }; $item.Delete() }
    elseif ($item) { New-Item -ItemType Directory -Force $backup | Out-Null; Move-Item $link $backup; Say "backed up old $($s.Name) to $backup" }
    New-Item -ItemType Junction -Path $link -Target $s.FullName | Out-Null
    Write-Output "linked $($s.Name)"
}
# Drop links to skills removed from the repo.
Get-ChildItem $target -Directory | Where-Object { $_.LinkType -and "$($_.Target)".StartsWith($Dir) -and -not (Test-Path "$($_.Target)") } |
    ForEach-Object { $_.Delete(); Write-Output "removed $($_.Name) (gone from repo)" }

# 4. Save choices + add a SessionStart hook that runs -Update (once).
# 3b. Team brain (add-missing, every run; the installer applies trust and allow rules, Claude never writes them).
if (-not $NoTeam) { & (Join-Path $Dir 'scripts/team.ps1') -ClaudeDir $ClaudeDir -GS $Dir | ForEach-Object { Say $_ } }

# 3c. -Config auto → <login>/claude-config: create it from templates/claude-config if missing (needs gh signed in).
if ($Config -eq 'auto') {
    $ErrorActionPreference = 'Continue'
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'gh not found. Install it: winget install GitHub.cli, then gh auth login' }
    $login = "$(gh api user -q .login 2>$null)".Trim()
    if (-not $login) { throw 'Not signed in to GitHub: run gh auth login, then rerun this line.' }
    gh auth setup-git 2>&1 | Out-Null
    $Config = "$login/claude-config"; $cdir = Join-Path (Split-Path $Dir) 'claude-config'
    gh repo view $Config --json name 2>&1 | Out-Null
    if ($LASTEXITCODE) {
        gh repo create $Config --private --description 'My Claude Code setup (Ghostskills installer)' 2>&1 | Out-Null
        if ($LASTEXITCODE) { throw "could not create $Config" }
        if (-not (Test-Path (Join-Path $cdir '.git'))) { git init -q $cdir; git -C $cdir remote add origin "https://github.com/$Config.git" }
        Copy-Item (Join-Path $Dir 'templates/claude-config/*') $cdir -Force
        if (-not "$(git -C $cdir config user.email)") { git -C $cdir config user.name $login; git -C $cdir config user.email "$login@users.noreply.github.com" }
        if (-not (Test-Path (Join-Path $ClaudeDir 'CLAUDE.md'))) { [IO.File]::WriteAllText((Join-Path $ClaudeDir 'CLAUDE.md'), "# My Claude Code rules`n") }
        try { & (Join-Path $cdir 'apply.ps1') -Capture -ClaudeDir $ClaudeDir -GS $Dir | Out-Null } catch { Write-Host "capture: $_" }
        git -C $cdir branch -M main 2>&1 | Out-Null; git -C $cdir push -q -u origin main 2>&1 | Out-Null
        if ($LASTEXITCODE) { Write-Host "created $Config, NOT pushed: run apply.ps1 -Capture in $cdir later" } else { Say "Created private $Config with this PC's setup." }
    }
    $ErrorActionPreference = 'Stop'
}
@{ dir = $Dir; projects = @($Projects); personal = $Personal; config = $Config; team = -not $NoTeam } | ConvertTo-Json | Set-Content $cfgFile -Encoding utf8
if (-not $Update -and -not $NoAutoUpdate) {
    $settingsFile = Join-Path $ClaudeDir 'settings.json'
    $s = if (Test-Path $settingsFile) { [IO.File]::ReadAllText($settingsFile) | ConvertFrom-Json } else { [pscustomobject]@{} }
    $cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$(($Dir -replace '\\','/'))/scripts/install.ps1`" -Update"
    if (-not $s.hooks) { $s | Add-Member hooks ([pscustomobject]@{}) }
    if (-not $s.hooks.SessionStart) { $s.hooks | Add-Member SessionStart @() }
    if (-not ($s.hooks.SessionStart | ConvertTo-Json -Depth 10 | Select-String -SimpleMatch 'install.ps1')) {
        $s.hooks.SessionStart = @($s.hooks.SessionStart) + [pscustomobject]@{ hooks = @([pscustomobject]@{ type = 'command'; command = $cmd; timeout = 30 }) }
        if (Test-Path $settingsFile) { Copy-Item $settingsFile "$settingsFile.bak" }
        [IO.File]::WriteAllText($settingsFile, ($s | ConvertTo-Json -Depth 20))
        Say "Auto-update on: every Claude Code session pulls main + links new skills."
    }
}
# 5. Personal setup repo (private): clone/pull next to Ghostskills, then apply it. -Update only adds what the PC lacks.
if ($Config) {
    $cdir = Join-Path (Split-Path $Dir) ($Config -split '/')[-1]
    $ErrorActionPreference = 'Continue'   # PS 5.1: git stderr must not stop the install
    if (Test-Path (Join-Path $cdir '.git')) { if (-not (git -C $cdir status --porcelain)) { git -C $cdir pull -q --ff-only 2>&1 | Out-Null } }
    else { git clone -q "https://github.com/$Config.git" $cdir 2>&1 | Out-Null }
    if (Test-Path (Join-Path $cdir 'apply.ps1')) {
        $a = @{ ClaudeDir = $ClaudeDir; GS = $Dir }; if ($Update) { $a.Update = $true }
        & (Join-Path $cdir 'apply.ps1') @a | ForEach-Object { Say $_ }
    } else { Write-Host "config $Config not reachable (private repo: sign in with gh auth login first)" }
}
Say "Done. Restart Claude Code, then type /load."
