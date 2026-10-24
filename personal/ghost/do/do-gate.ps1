# Gate for computer use: only unlocked after "/do <task>" followed by "y" (this task)
# or "auto" (rest of the session, until "lock").
# Usage: do-gate.ps1 prompt   (UserPromptSubmit hook)
#        do-gate.ps1 tool     (PreToolUse hook on computer-use tools)
param([string]$Mode)

$raw = [Console]::In.ReadToEnd()
try { $data = $raw | ConvertFrom-Json } catch { $data = $null }
$sid = if ($data -and $data.session_id) { $data.session_id } else { 'default' }
$sid = $sid -replace '[^A-Za-z0-9_-]', ''
$stateDir = Join-Path $env:USERPROFILE '.claude\hooks\do-gate-state'
New-Item -ItemType Directory -Force $stateDir | Out-Null
$stateFile = Join-Path $stateDir "$sid.txt"
$state = if (Test-Path $stateFile) { (Get-Content $stateFile -Raw).Trim() } else { 'off' }

if ($Mode -eq 'prompt') {
    $p = if ($data) { [string]$data.prompt } else { '' }
    $p = $p.Trim()
    if ($state -eq 'auto') {
        # auto stays on for the whole session until the user types lock
        $new = if ($p -match '^(?i)lock$') { 'off' } else { 'auto' }
    } elseif ($p -match '^/do(\s|$)' -or $p -match '<command-name>/?do</command-name>') {
        $new = 'pending'
    } elseif ($p -match '^(?i)(a|auto)$' -and ($state -eq 'pending' -or $state -eq 'armed')) {
        $new = 'auto'
    } elseif ($p -match '^(?i)(y|yes)$' -and ($state -eq 'pending' -or $state -eq 'armed')) {
        $new = 'armed'
    } else {
        $new = 'off'
    }
    Set-Content -Path $stateFile -Value $new -Encoding ascii
    exit 0
}

if ($Mode -eq 'tool') {
    if ($state -eq 'armed' -or $state -eq 'auto') { exit 0 }
    $reason = if ($state -eq 'pending') {
        'PC control is locked until the user answers y or auto to the (y/n/auto) question.'
    } else {
        'PC control is locked. The user must type /do <task> and then answer y.'
    }
    @{ hookSpecificOutput = @{
        hookEventName = 'PreToolUse'
        permissionDecision = 'deny'
        permissionDecisionReason = $reason
    } } | ConvertTo-Json -Compress -Depth 4
    exit 0
}
