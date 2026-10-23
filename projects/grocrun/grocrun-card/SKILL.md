---
name: grocrun-card
description: Use only when the load or save skill picks grocrun: holds the GrocRun Android app's card. Never typed by the user.
---
# grocrun card
ctx grocrun · GrocRun Android app · repo ghostaiproject/Grocerierun · state HANDOFF.md · also load: grocrun-dev skill · save extras: grocrun-dev "Save extras".
Load extras: same batch as HANDOFF.md, one Bash: `gh run list --repo ghostaiproject/Grocerierun --workflow build-apk.yml --limit 1 --json number,databaseId,headBranch,displayTitle,conclusion`. Run newer than HANDOFF LATEST or not on main → say version, branch, run + result; ask once whether to merge it into main. Never merge without an ok.
GrocRun only: no other project's state, rules or memory.
