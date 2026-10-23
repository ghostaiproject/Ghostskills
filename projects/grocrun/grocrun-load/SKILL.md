---
name: grocrun-load
description: Use when the user sends /grocrun-load or /load grocrun: starts a chat on the GrocRun Android app with its own saved state.
---
# /grocrun-load
Card: ctx grocrun · repo ghostaiproject/Grocerierun · state HANDOFF.md · also load: grocrun-dev skill · save extras: grocrun-dev "Save extras".
Load extras: same batch as HANDOFF.md, one Bash: `gh run list --repo ghostaiproject/Grocerierun --workflow build-apk.yml --limit 1 --json number,databaseId,headBranch,displayTitle,conclusion`. Run newer than HANDOFF LATEST or not on main → say version, branch, run + result; ask once whether to merge it into main. Never merge without an ok.
Invoke skill `load` with this card; follow its steps. GrocRun only: no other project's state, rules or memory.
