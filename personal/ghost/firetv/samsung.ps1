# Samsung Tizen TV remote over its local API (port 8002). Usage: samsung.ps1 <info|key|keys> [KEY ...]
# TV IP from ~/.claude/firetv.json ("tv"). Pairing token kept locally in ~/.claude/samsung-token.txt (never in repo).
param([Parameter(Position=0)][string]$Action = 'info', [Parameter(Position=1, ValueFromRemainingArguments=$true)][string[]]$Rest)
$ErrorActionPreference = 'Stop'
$cfg = Get-Content (Join-Path $HOME '.claude\firetv.json') -Raw | ConvertFrom-Json
$ip = $cfg.tv; if (-not $ip) { throw 'No TV IP: firetv.ps1 set <stickIP> <tvIP>' }
$tokPath = Join-Path $HOME '.claude\samsung-token.txt'
$alias = @{ power='KEY_POWER'; volup='KEY_VOLUP'; voldown='KEY_VOLDOWN'; mute='KEY_MUTE'; source='KEY_SOURCE'; hdmi='KEY_HDMI'; hdmi1='KEY_HDMI1'; hdmi2='KEY_HDMI2'; hdmi3='KEY_HDMI3'; home='KEY_HOME'; back='KEY_RETURN'; up='KEY_UP'; down='KEY_DOWN'; left='KEY_LEFT'; right='KEY_RIGHT'; ok='KEY_ENTER'; menu='KEY_MENU'; exit='KEY_EXIT'; info='KEY_INFO' }

if ($Action -eq 'info') { (Invoke-RestMethod "http://${ip}:8001/api/v2/" -TimeoutSec 5).device | Select-Object name, modelName, PowerState, networkType, wifiMac | Format-List; return }
if ($Action -eq 'keys') { $alias.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name) = $($_.Value)" }; return }
if ($Action -ne 'key') { 'actions: info key <name|KEY_*>... keys'; return }

[Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
$name = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('ClaudeRemote'))
$tok = if (Test-Path $tokPath) { (Get-Content $tokPath -Raw).Trim() } else { '' }
$uri = "wss://${ip}:8002/api/v2/channels/samsung.remote.control?name=$name" + $(if ($tok) { "&token=$tok" } else { '' })
$ws = New-Object Net.WebSockets.ClientWebSocket
$ct = [Threading.CancellationToken]::None
$ws.ConnectAsync([Uri]$uri, $ct).Wait()

function Recv {
  $buf = New-Object byte[] 8192; $seg = New-Object ArraySegment[byte] -ArgumentList (, $buf)
  $t = $ws.ReceiveAsync($seg, $ct); if (-not $t.Wait(30000)) { throw 'No reply: choose Allow on the TV prompt, then rerun' }
  [Text.Encoding]::UTF8.GetString($buf, 0, $t.Result.Count)
}
$hello = Recv | ConvertFrom-Json
if ($hello.event -ne 'ms.channel.connect') { throw "TV refused: $($hello.event) (choose Allow on the TV; if denied, re-allow in TV Settings > General > External Device Manager > Device Connection Manager > Device List)" }
if ($hello.data.token) { Set-Content $tokPath $hello.data.token -Encoding ascii }

foreach ($k in $Rest) {
  $key = if ($alias.ContainsKey($k)) { $alias[$k] } elseif ($k -like 'KEY_*') { $k } else { 'KEY_' + $k.ToUpper() }
  $msg = @{ method = 'ms.remote.control'; params = @{ Cmd = 'Click'; DataOfCmd = $key; Option = 'false'; TypeOfRemote = 'SendRemoteKey' } } | ConvertTo-Json -Compress
  $bytes = [Text.Encoding]::UTF8.GetBytes($msg)
  $ws.SendAsync((New-Object ArraySegment[byte] -ArgumentList (, $bytes)), 'Text', $true, $ct).Wait()
  Start-Sleep -Milliseconds 400; "sent $key"
}
$ws.CloseAsync('NormalClosure', '', $ct).Wait()
