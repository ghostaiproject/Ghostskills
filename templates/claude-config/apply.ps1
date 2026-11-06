# Restore (or capture) this person's Claude Code setup: global CLAUDE.md, settings (allow rules, hooks, auto-mode trust), hook scripts, memory.
#   apply.ps1            full apply (fresh PC/account): repo copy wins, old files backed up to ~/.claude/config-backup-<time>
#   apply.ps1 -Update    add missing only: allow rules, hooks, env keys, hook scripts and memory files the PC lacks; never overwrites
#   apply.ps1 -Capture   PC -> repo: copy the PC's current setup here, then commit + push
# Paths in settings.json use {HOME} (user home, forward slashes) and {GS} (Ghostskills clone).
param([switch]$Update, [switch]$Capture, [string]$ClaudeDir = (Join-Path $HOME '.claude'), [string]$GS = (Join-Path $HOME 'Ghostskills'))
$ErrorActionPreference = 'Stop'
$repo = $PSScriptRoot
$utf8 = New-Object Text.UTF8Encoding $false
function Read-Text($p) { [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8) }
function Write-Text($p, $t) { New-Item -ItemType Directory -Force (Split-Path $p) | Out-Null; [IO.File]::WriteAllText($p, $t, $utf8) }
function Fwd($p) { $p -replace '\\', '/' }
$homeF = Fwd $HOME; $gsF = Fwd $GS
# Memory dirs are named after the project path (C:\Users\Bureau\Ghostskills -> C--Users-Bureau-Ghostskills); the repo stores them relative to home.
$homeSlug = ($HOME -replace '[:\\/ .]', '-')
$keep = 'env', 'bashOutputMaxChars', 'theme', 'permissions', 'autoMode', 'hooks', 'enabledPlugins', 'extraKnownMarketplaces'
$settingsFile = Join-Path $ClaudeDir 'settings.json'
function Load-Settings { if (Test-Path $settingsFile) { Read-Text $settingsFile | ConvertFrom-Json } else { [pscustomobject]@{} } }
function Has($o, $k) { $o.PSObject.Properties.Name -contains $k }
function Set-Key($o, $k, $v) { if (Has $o $k) { $o.$k = $v } else { $o | Add-Member $k $v } }

if ($Capture) {
    Copy-Item (Join-Path $ClaudeDir 'CLAUDE.md') (Join-Path $repo 'CLAUDE.md') -Force
    $s = Load-Settings; $out = [ordered]@{}
    foreach ($k in $keep) { if (Has $s $k) { $out[$k] = $s.$k } }
    $json = ($out | ConvertTo-Json -Depth 30).Replace($gsF, '{GS}').Replace($homeF, '{HOME}')
    Write-Text (Join-Path $repo 'settings.json') $json
    $hk = Join-Path $ClaudeDir 'hooks'
    if (Test-Path $hk) { New-Item -ItemType Directory -Force "$repo/hooks" | Out-Null; Copy-Item "$hk/*.ps1" "$repo/hooks" -Force }
    Get-ChildItem (Join-Path $ClaudeDir 'projects') -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $m = Join-Path $_.FullName 'memory'
        # Skip the desktop app's throwaway scratch workspaces: their paths never exist on another PC.
        if ((Test-Path $m) -and $_.Name.StartsWith($homeSlug) -and $_.Name -notmatch 'scratch') {
            $dst = Join-Path "$repo/memory" ('~' + $_.Name.Substring($homeSlug.Length))
            New-Item -ItemType Directory -Force $dst | Out-Null; Copy-Item "$m/*.md" $dst -Force
        }
    }
    git -C $repo add -A
    if (git -C $repo status --porcelain) { git -C $repo commit -qm "capture: setup from $env:COMPUTERNAME" }
    $ErrorActionPreference = 'Continue'; git -C $repo push -q 2>&1 | Out-Null   # PS 5.1: git's stderr must not stop the script
    if ($LASTEXITCODE) { 'captured, NOT pushed (no remote or no access)' } else { 'captured + pushed' }
    return
}

$backup = Join-Path $ClaudeDir ('config-backup-' + (Get-Date -Format yyyyMMdd-HHmmss))
function Put($src, $dst) {   # copy one file: -Update only fills gaps; full apply backs up a different file first
    if (Test-Path $dst) {
        if ($Update -or ((Read-Text $src) -eq (Read-Text $dst))) { return }
        $b = Join-Path $backup ($dst.Substring($ClaudeDir.Length).TrimStart('\', '/')); New-Item -ItemType Directory -Force (Split-Path $b) | Out-Null; Copy-Item $dst $b
    }
    New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null; Copy-Item $src $dst -Force; Write-Output "set $($dst.Substring($ClaudeDir.Length))"
}
Put (Join-Path $repo 'CLAUDE.md') (Join-Path $ClaudeDir 'CLAUDE.md')
if (Test-Path "$repo/hooks") { Get-ChildItem "$repo/hooks" -File | ForEach-Object { Put $_.FullName (Join-Path $ClaudeDir "hooks/$($_.Name)") } }
if (Test-Path "$repo/memory") {
    Get-ChildItem "$repo/memory" -Directory | ForEach-Object {
        $dir = Join-Path $ClaudeDir ('projects/' + $homeSlug + $_.Name.Substring(1) + '/memory')
        Get-ChildItem $_.FullName -File | ForEach-Object { Put $_.FullName (Join-Path $dir $_.Name) }
    }
}

# Settings merge: allow rules and hooks are unioned (never removed); other keys are set by a full apply, filled only when missing by -Update.
$want = (Read-Text "$repo/settings.json").Replace('{GS}', $gsF).Replace('{HOME}', $homeF) | ConvertFrom-Json
$s = Load-Settings; $before = $s | ConvertTo-Json -Depth 30
foreach ($k in $want.PSObject.Properties.Name) {
    if ($k -eq 'hooks') {
        if (-not (Has $s 'hooks')) { Set-Key $s 'hooks' ([pscustomobject]@{}) }
        foreach ($ev in $want.hooks.PSObject.Properties.Name) {
            $cur = @(if (Has $s.hooks $ev) { $s.hooks.$ev }); $have = $cur | ConvertTo-Json -Depth 10
            foreach ($h in @($want.hooks.$ev)) {
                $cmd = $h.hooks[0].command
                if (-not $have -or -not $have.Contains(($cmd | ConvertTo-Json).Trim('"'))) { $cur += $h }
            }
            Set-Key $s.hooks $ev @($cur)
        }
    } elseif ($k -eq 'permissions') {
        if (-not (Has $s 'permissions')) { Set-Key $s 'permissions' ([pscustomobject]@{}) }
        foreach ($pk in $want.permissions.PSObject.Properties.Name) {
            $cur = @(if (Has $s.permissions $pk) { $s.permissions.$pk })
            Set-Key $s.permissions $pk @($cur + @($want.permissions.$pk | Where-Object { $cur -notcontains $_ }))
        }
    } elseif (-not $Update -or -not (Has $s $k)) { Set-Key $s $k $want.$k }
}
$after = $s | ConvertTo-Json -Depth 30
if ($after -ne $before) {
    if (Test-Path $settingsFile) { Copy-Item $settingsFile "$settingsFile.bak" }
    Write-Text $settingsFile $after; Write-Output 'settings.json updated'
}
if (-not $Update -and (Test-Path $backup)) { Write-Output "old files backed up to $backup" }
