# Apply the shared team brain (add-missing only, safe to rerun; install.ps1 runs it every session start):
#   ~/.claude/CLAUDE.md gets @imports of team/CLAUDE.md + team/lessons.md (live files: the pull keeps them fresh);
#   ~/.claude/settings.json gets team/settings.json merged in: allow rules, hooks, auto-mode trust lines unioned, other keys only if missing.
# Placeholders in team/settings.json: {HOME}, {GS} (Ghostskills clone), {GHUSER} (your GitHub login; lines with it are dropped if gh is not signed in).
param([string]$ClaudeDir = (Join-Path $HOME '.claude'), [string]$GS = '', [string]$GhUser = '')
if (-not $GS) { $GS = Split-Path $MyInvocation.MyCommand.Path | Split-Path }   # PS 5.1: $PSScriptRoot is empty in param defaults
$ErrorActionPreference = 'Stop'
$utf8 = New-Object Text.UTF8Encoding $false
function Read-Text($p) { [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8) }
function Write-Text($p, $t) { New-Item -ItemType Directory -Force (Split-Path $p) | Out-Null; [IO.File]::WriteAllText($p, $t, $utf8) }
function Has($o, $k) { $o.PSObject.Properties.Name -contains $k }
$homeF = $HOME -replace '\\', '/'; $gsF = $GS -replace '\\', '/'
$gsRef = if ($gsF.StartsWith("$homeF/")) { '~' + $gsF.Substring($homeF.Length) } else { $gsF }

# 1. CLAUDE.md imports (your own lines stay above; nothing is copied, so updates arrive with every pull).
$md = Join-Path $ClaudeDir 'CLAUDE.md'
$text = if (Test-Path $md) { Read-Text $md } else { '' }
$add = foreach ($f in 'CLAUDE.md', 'lessons.md') { $line = "@$gsRef/team/$f"; if (-not $text.Contains($line)) { $line } }
if ($add) {
    if ($text -and -not $text.EndsWith("`n")) { $text += "`n" }
    if (-not $text.Contains('# Team brain')) { $text += "`n# Team brain (Ghostskills, shared; your lines above win)`n" }
    Write-Text $md ($text + (($add -join "`n") + "`n")); Write-Output "CLAUDE.md: team rules + lessons imported"
}

# 2. settings.json merge.
if (-not $GhUser -and (Get-Command gh -ErrorAction SilentlyContinue)) {
    $ErrorActionPreference = 'Continue'; $GhUser = "$(gh api user -q .login 2>$null)".Trim(); $ErrorActionPreference = 'Stop'
}
$raw = (Read-Text (Join-Path $GS 'team/settings.json')).Replace('{GS}', $gsF).Replace('{HOME}', $homeF)
if ($GhUser) { $raw = $raw.Replace('{GHUSER}', $GhUser) }
$want = $raw | ConvertFrom-Json
$want.autoMode.environment = @($want.autoMode.environment | Where-Object { $_ -notmatch '\{GHUSER\}' })
$file = Join-Path $ClaudeDir 'settings.json'
$s = if (Test-Path $file) { Read-Text $file | ConvertFrom-Json } else { [pscustomobject]@{} }
$before = $s | ConvertTo-Json -Depth 30

function Merge($cur, $new, $path) {
    foreach ($k in $new.PSObject.Properties.Name) {
        $v = $new.$k
        if (-not (Has $cur $k)) { $cur | Add-Member $k $v; continue }
        if ($path -eq 'hooks') {   # hook events: add each hook whose command is not there yet
            $list = @($cur.$k); $have = $list | ConvertTo-Json -Depth 10
            foreach ($h in @($v)) { if (-not $have -or -not $have.Contains(($h.hooks[0].command | ConvertTo-Json).Trim('"'))) { $list += $h } }
            $cur.$k = @($list)
        } elseif ($v -is [array]) { $c = @($cur.$k); $cur.$k = @($c + @($v | Where-Object { $c -notcontains $_ })) }
        elseif ($v -is [pscustomobject] -and $cur.$k -is [pscustomobject]) { Merge $cur.$k $v $k }
    }
}
Merge $s $want ''
$after = $s | ConvertTo-Json -Depth 30
if ($after -ne $before) {
    if (Test-Path $file) { Copy-Item $file "$file.bak" -Force }
    Write-Text $file $after; Write-Output 'settings.json: team allow rules, hooks and trust added'
}
