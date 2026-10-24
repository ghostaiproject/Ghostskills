---
name: skills-card
description: Use only when a core skill (load, save, cmds) picks skills (#2): holds the card for the Ghostskills repo itself. Never typed by the user.
---
# skills card
ctx skills · #2 · this skills repo · repo ghostaiproject/Ghostskills · branch main · state README.md (on save: keep its tables, no LATEST/History) · also load: CONVENTIONS.md · load extras: — · save extras: `scripts/check.ps1` (pwsh; Windows: powershell -ExecutionPolicy Bypass -File; FAIL → fix first).
Ship (= claude.ai upload): `scripts/check.ps1 -Pack` (FAIL → fix) → skill folders changed since the sha in `.uploaded` (none → all): `git diff --name-only <sha> HEAD` → list their zips in dist/ + any removed skill to delete on claude.ai → user uploads → after their ok, write HEAD sha to `.uploaded`, commit + push. No CI wait.
List: one line per skill folder (core, tools, projects, personal); no lessons file · Extra cmds: /drift (LOCAL) → `scripts/check.ps1 -Drift`, one line per installed skill that differs.
