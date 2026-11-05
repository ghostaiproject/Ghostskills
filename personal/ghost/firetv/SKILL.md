---
name: firetv
description: Control the Fire TV Stick (ADB over Wi-Fi) and Samsung TV (local remote API) from the PC; debloat/restore the stick, read its HDMI logs. Use for any Fire Stick or TV control, fix or customize request.
---
# Fire TV + Samsung control
Scripts sit next to this file. Run with `powershell -File <dir>\<script> <action> ...`. IPs live in `~/.claude/firetv.json`, never in the repo.

1. First run: no config → find IPs (`arp -a`; stick = port 5555 open, TV = port 8002 open) → `firetv.ps1 set <stickIP> <tvIP>`. adb missing → the script installs it (winget).
2. Unauthorized → ask the user to tick "Always allow" + OK on the TV prompt. Samsung first key → TV shows "Allow" → user approves; the token is saved locally.
3. Fire Stick `firetv.ps1`: `info` · `key home|back|up|down|left|right|ok|play|volup|power|sleep…` · `text <words>` · `app netflix|prime|youtube|plex|kodi|crave|<pkg>` · `stop <app>` · `apps` · `logs [pattern]` · `shot` (screenshot path) · `debloat [track shop unused recs]` · `restore [pkg]`.
4. Samsung `samsung.ps1`: `info` · `key power|volup|voldown|mute|source|hdmi1|home|back|ok|KEY_*…` · `keys` (list).
5. Debloat list = `bloat.txt` (groups). Removes for user 0 only; logged in `~/.claude/firetv-removed.txt`; `restore` undoes it. Never add OTA/updates, launcher, settings, Appstore, Alexa core, webview, DRM or devicecontrol. Confirm groups with the user (picker) before running.
6. Never change security settings (ADB, unknown sources, updates) yourself: the user does those on the TV.
7. HDMI drops when an app opens → `logs`: no hotplug or mode-change lines = the TV cuts the signal → Input Signal Plus + Anynet+/CEC off + extender/port swap.
