---
name: grocrun-card
description: Use only when a core skill (load, save, cmds) picks grocrun (#1): holds the GrocRun Android app's card. Never typed by the user.
---
# grocrun card
ctx grocrun · #1 · GrocRun Android app · repo ghostaiproject/Grocerierun · branch main · state HANDOFF.md · also load: grocrun-dev skill · save extras: grocrun-dev EXTRAS.md "Save extras".
Load extras: same batch as HANDOFF.md, one Bash: `gh run list --repo ghostaiproject/Grocerierun --workflow build-apk.yml --limit 1 --json number,databaseId,headBranch,displayTitle,conclusion`. Run newer than HANDOFF LATEST or not on main → say version, branch, run + result; ask once whether to merge it into main. Never merge without an ok.
Ship: version in app/build.gradle.kts verMajor/verMinor/verPatch (feature → minor+1, fix → patch+1; re-check after fetch) · workflow build-apk.yml · reply per grocrun-dev "Build" · local build: `./gradlew assembleRelease` (gradlew.bat on Windows), then `adb install -r` if a phone is plugged in.
List: design/ + LESSONS.md. Extra cmds: —.
