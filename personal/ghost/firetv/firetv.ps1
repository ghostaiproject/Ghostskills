# Fire TV control over ADB. Usage: firetv.ps1 <action> [args]
# Config (local, never in repo): ~/.claude/firetv.json {"stick":"<ip>","tv":"<ip>"}
param([Parameter(Position=0)][string]$Action = 'info', [Parameter(Position=1, ValueFromRemainingArguments=$true)][string[]]$Rest)
$ErrorActionPreference = 'Stop'
$env:Path = [Environment]::GetEnvironmentVariable('Path','User') + ';' + $env:Path
$cfgPath = Join-Path $HOME '.claude\firetv.json'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$logPath = Join-Path $HOME '.claude\firetv-removed.txt'

function Cfg { if (Test-Path $cfgPath) { Get-Content $cfgPath -Raw | ConvertFrom-Json } else { [pscustomobject]@{ stick = ''; tv = '' } } }
function Need-Adb { if (-not (Get-Command adb -ErrorAction SilentlyContinue)) { winget install --id Google.PlatformTools -e --silent --accept-source-agreements --accept-package-agreements | Out-Null; $env:Path = [Environment]::GetEnvironmentVariable('Path','User') + ';' + $env:Path } }
function Connect {
  Need-Adb; $c = Cfg; if (-not $c.stick) { throw "No stick IP: firetv.ps1 set <stickIP> [tvIP]" }
  $t = "$($c.stick):5555"; adb connect $t | Out-Null
  $s = (adb devices | Select-String ([regex]::Escape($t))).Line
  if ($s -match 'unauthorized') { throw "Approve 'Allow USB debugging' (tick Always allow) on the TV, then rerun" }
  if ($s -notmatch 'device$') { throw "Stick not reachable at ${t}: ADB debugging on? (Settings > My Fire TV > Developer options)" }
  $script:T = $t
}
function Sh([string]$cmd) { adb -s $script:T shell $cmd }

$keys = @{ home=3; back=4; up=19; down=20; left=21; right=22; ok=23; select=23; volup=24; voldown=25; power=26; menu=82; play=85; pause=85; next=87; prev=88; rew=89; ff=90; mute=164; sleep=223; wake=224 }
$apps = @{ netflix='com.netflix.ninja'; prime='com.amazon.firebat'; youtube='com.amazon.firetv.youtube'; plex='com.plexapp.android'; kodi='org.xbmc.kodi'; crave='ca.bellmedia.cravetv'; settings='com.amazon.tv.settings.v2' }

switch ($Action) {
  'set'   { $o = [pscustomobject]@{ stick = $Rest[0]; tv = $(if ($Rest.Count -gt 1) { $Rest[1] } else { (Cfg).tv }) }; $o | ConvertTo-Json | Set-Content $cfgPath -Encoding utf8; "saved $cfgPath" }
  'info'  { Connect; Sh "uptime; getprop ro.product.model; getprop ro.build.version.name; dumpsys display | grep -oE 'mActiveModeId=[0-9]+|mSupportedHdrTypes=\[[^]]*\]' | sort -u; settings get global hdmi_control_enabled; df -h /data | tail -1" }
  'key'   { Connect; foreach ($k in $Rest) { $code = if ($keys.ContainsKey($k)) { $keys[$k] } else { $k }; Sh "input keyevent $code" | Out-Null }; "sent: $($Rest -join ' ')" }
  'text'  { Connect; Sh ("input text '" + (($Rest -join ' ') -replace ' ', '%s' -replace "'", '') + "'") | Out-Null; 'typed' }
  'app'   { Connect; $p = if ($apps.ContainsKey($Rest[0])) { $apps[$Rest[0]] } else { $Rest[0] }; Sh "monkey -p $p -c android.intent.category.LAUNCHER 1" | Out-Null; "opened $p" }
  'stop'  { Connect; $p = if ($apps.ContainsKey($Rest[0])) { $apps[$Rest[0]] } else { $Rest[0] }; Sh "am force-stop $p" | Out-Null; "stopped $p" }
  'apps'  { Connect; Sh 'pm list packages -3' | ForEach-Object { $_ -replace '^package:' } }
  'logs'  { Connect; $pat = if ($Rest) { $Rest -join '|' } else { 'hdmi|hdcp|hotplug|FATAL|ANR' }; Sh "logcat -d -v time | grep -iE '$pat' | grep -v MPB_DRM | tail -40" | ForEach-Object { if ($_.Length -gt 200) { $_.Substring(0,200) } else { $_ } } }
  'shot'  { Connect; $out = Join-Path $env:TEMP 'firetv-shot.png'; Sh 'screencap -p /sdcard/s.png' | Out-Null; adb -s $script:T pull /sdcard/s.png $out | Out-Null; Sh 'rm /sdcard/s.png' | Out-Null; $out }
  'debloat' {
    Connect; $groups = if ($Rest) { $Rest } else { @('track','shop','unused','recs') }
    $have = Sh 'pm list packages' | ForEach-Object { $_ -replace '^package:' }
    Get-Content (Join-Path $here 'bloat.txt') | Where-Object { $_ -and $_ -notmatch '^#' } | ForEach-Object {
      $g, $p = $_ -split '\s+', 2
      if ($groups -notcontains $g) { return }
      if ($have -notcontains $p) { "skip $p (not installed)"; return }
      $r = Sh "pm disable-user --user 0 $p 2>&1"
      if ($r -notmatch 'disabled') { $r = Sh "pm uninstall -k --user 0 $p 2>&1" }
      if ($r -notmatch 'Success') { $r = Sh "pm suspend --user 0 $p 2>&1" }
      if ($r -match 'disabled|Success|suspended state: true') { Add-Content $logPath $p; "removed $p" } else { "FAIL $p : $r" }
    }
  }
  'restore' {
    Connect; if (-not (Test-Path $logPath)) { 'nothing to restore'; return }
    $list = if ($Rest) { $Rest } else { Get-Content $logPath | Sort-Object -Unique }
    foreach ($p in $list) { Sh "cmd package install-existing $p 2>&1; pm enable $p 2>&1; pm unsuspend --user 0 $p 2>&1" | Out-Null; "restored $p" }
    if (-not $Rest) { Remove-Item $logPath }
  }
  'ux'    { Connect; Sh ((Get-Content (Join-Path $here 'ux.sh') | Where-Object { $_ -notmatch '^#' }) -join '; ') }
  'ux-reset' { Connect; Sh 'for k in window_animation_scale transition_animation_scale animator_duration_scale; do settings put global $k 1.0; done; for k in limit_ad_tracking amz_limit_ad_tracking non_amz_limit_ad_tracking; do settings put secure $k 0; done; echo reset' }
  'access' { Connect; Sh 'am start -a android.settings.ACCESSIBILITY_SETTINGS' | Out-Null; 'Accessibility screen open on TV: user toggles the app' }
  default { 'actions: set info key text app stop apps logs shot debloat restore ux ux-reset access' }
}
