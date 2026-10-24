# Install Ghostskills on this PC: clone/pull the repo, link its skills into ~/.claude/skills, auto-update every Claude session.
# First run: -Projects grocrun,window (cards to add) -Personal <you> (your personal folder) -NoAutoUpdate (skip the hook).
# Later runs (and the SessionStart hook) use -Update: pull + link any new skill, choices read from ~/.claude/ghostskills.json.
param([string[]]$Projects = @(), [string]$Personal = '', [string]$Dir = (Join-Path $HOME 'Ghostskills'),
      [string]$ClaudeDir = (Join-Path $HOME '.claude'), [switch]$Update, [switch]$NoAutoUpdate)
$ErrorActionPreference = 'Stop'
$url = 'https://github.com/ghostaiproject/Ghostskills.git'
$cfgFile = Join-Path $ClaudeDir 'ghostskills.json'
function Say($m) { if (-not $Update) { Write-Output $m } }

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'git not found. Install it: winget install Git.Git  (then reopen the terminal)' }
if ($Update -and (Test-Path $cfgFile)) {
    $c = Get-Content $cfgFile -Raw | ConvertFrom-Json
    $Dir = $c.dir; $Projects = @($c.projects); $Personal = $c.personal
}

# 1. Repo: clone once, then fast-forward only (never touches local work).
if (Test-Path (Join-Path $Dir '.git')) {
    $branch = git -C $Dir rev-parse --abbrev-ref HEAD
    if ($branch -eq 'main' -and -not (git -C $Dir status --porcelain)) { git -C $Dir pull -q --ff-only 2>$null }
    else { Say "Repo on '$branch' or has local changes: not pulled (switch to main and /sync first)." }
} else { git clone -q $url $Dir; Say "Cloned to $Dir" }

# 2. Pick skill folders: core, cer-01, tools for everyone + chosen projects/personal.
$roots = @('core', 'cer-01', 'tools') + ($Projects | Where-Object { $_ } | ForEach-Object { "projects/$_" })
if ($Personal) { $roots += "personal/$Personal" }
$skills = foreach ($r in $roots) {
    $p = Join-Path $Dir $r
    if (-not (Test-Path $p)) { Say "skip $r (not in repo)"; continue }
    Get-ChildItem $p -Recurse -Filter SKILL.md | Where-Object { $_.FullName -notmatch '[\\/]_template[\\/]' } | ForEach-Object { $_.Directory }
}

# 3. Link each one (junction: no admin needed, edits land in the repo). A real folder there is moved to a backup first.
$target = Join-Path $ClaudeDir 'skills'
New-Item -ItemType Directory -Force $target | Out-Null
$backup = Join-Path $ClaudeDir ("skills-backup-" + (Get-Date -Format yyyyMMdd-HHmmss))
foreach ($s in $skills) {
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
@{ dir = $Dir; projects = @($Projects); personal = $Personal } | ConvertTo-Json | Set-Content $cfgFile -Encoding utf8
if (-not $Update -and -not $NoAutoUpdate) {
    $settingsFile = Join-Path $ClaudeDir 'settings.json'
    $s = if (Test-Path $settingsFile) { Get-Content $settingsFile -Raw | ConvertFrom-Json } else { [pscustomobject]@{} }
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
Say "Done. Restart Claude Code, then type /load."
