---
name: ghosttv-card
description: Use only when a core skill (load, save, cmds) picks ghosttv (#4): holds the GhostTv project's card (Fire Stick + Samsung TV control). Never typed by the user.
---
# ghosttv card
ctx ghosttv · #4 · Fire Stick + Samsung TV control, debloat, look · repo ghostaiproject/GhostTv · branch main · state HANDOFF.md · also load: firetv skill · save extras: —.
Load extras: same batch, one PowerShell: `powershell -File ~/.claude/skills/firetv/firetv.ps1 info` + `python -I ~/.claude/skills/firetv/samsung.py info`. Unreachable/unauthorized → say it first (stick off, ADB debugging off, or prompt waiting on the TV).
Ship: no version; main is live. 1) edit `skill/` in GhostTv 2) `powershell -File install.ps1` (local copy) 3) mirror to Ghostskills `personal/ghost/firetv/` (skill sync rule) 4) commit + push both; Ghostskills via PR + CI.
List: removed apps = `~/.claude/firetv-removed.txt`; groups = `skill/bloat.txt`; user apps = `firetv.ps1 apps`.
Extra cmds: /tv <keys> → `samsung.py key …` · /stick <keys> → `firetv.ps1 key …` · /debloat [groups] → confirm groups (picker), then `firetv.ps1 debloat` · /restore [pkg].
Never: change security settings (ADB, unknown sources, updates, accessibility) yourself; download/install APKs without the user's OK (name file, source, size).
