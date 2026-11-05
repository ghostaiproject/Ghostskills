---
name: firetv
description: Control the Fire TV Stick (ADB over Wi-Fi) and Samsung TV (local remote API) from the PC; debloat/restore the stick, read its HDMI logs. Use for any Fire Stick or TV control, fix or customize request.
---
# Fire TV + Samsung control
Scripts sit next to this file (source repo: ghostaiproject/GhostTv). Run with `powershell -File <dir>\firetv.ps1 <action> ...`. IPs live in `~/.claude/firetv.json`, never in the repo.

1. First run: no config → find IPs (`arp -a`; stick = port 5555 open, TV = port 8002 open) → `firetv.ps1 set <stickIP> <tvIP>`. adb missing → the script installs it (winget).
2. Unauthorized → ask the user to tick "Always allow" + OK on the TV prompt. Samsung first key → TV shows "Allow" → user approves; the token is saved locally.
3. Fire Stick `firetv.ps1`: `info` · `key home|back|up|down|left|right|ok|play|volup|power|sleep…` · `text <words>` · `app netflix|prime|youtube|plex|kodi|crave|<pkg>` · `stop <app>` · `apps` · `logs [pattern]` · `shot` (640px jpg path) · `go <keys>` (keys + jpg in one call) · `run <macro>` (key path from `nav/<name>.txt`; no name = list) · `ui` (screen texts, focus `>>`) · `debloat [track shop unused recs]` · `restore [pkg]`.
4. Samsung `python -I samsung.py` (stdlib; .NET websockets hang on this TV): `info` · `key power|volup|voldown|mute|source|hdmi1|home|back|ok|KEY_*…` · `keys` (list).
5. Debloat list = `bloat.txt` (groups). Removes for user 0 only; logged in `~/.claude/firetv-removed.txt`; `restore` undoes it. Never add OTA/updates, launcher, settings, Appstore, Alexa core, webview, DRM or devicecontrol. Confirm groups with the user (picker) before running.
6. Do every step yourself over adb/samsung.py (settings put, keys, am start, pm, `ux` preset, installs of files the user sent or approved); never hand the user a settings list. User only: security grants (accessibility → `access` opens the screen, unknown sources, ADB, updates) and on-TV Allow prompts.
7. HDMI drops when an app opens → `logs`: no hotplug or mode-change lines = the TV cuts the signal → Input Signal Plus + Anynet+/CEC off + extender/port swap.
8. Driving screens (Projectivy etc.): read `nav/README.md` first (screen maps, known key paths, quirks) and reuse a `nav/*.txt` macro; batch the whole path in ONE `go`/`run` call (keys go through one monkey run, `wait` = 1 s pause after home/menu/opening screens). Don't send screenshots to the user mid-work. When a new path works, save it as a macro and add the map line to `nav/README.md`.
