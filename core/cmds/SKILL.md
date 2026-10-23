---
name: cmds
description: Use when the user sends /cmds, /sync, /ship or /list (optionally + a name or number): shared commands for whichever context this chat loaded.
---
# Shared commands
Ctx + card + mode = this chat's load. None → the load skill's menu (banner "For which?", "Number?"), then invoke `<ctx>-card`; no mode → detect like load step 1. /sync and /ship need a repo: none → one line, stop.

/cmds: banner "Cmds · <ctx>"; numbered, one line each, then "Number?" and run the pick:
1 /load · switch project · 2 /save · save state · 3 /sync · push work in progress · 4 /ship · build a release · 5 /list · tools + lessons · 6+ the card's extra cmds.

/sync: one Bash: `git add -A && git commit -q -m "wip: <summary> [skip ci]"` + trailers `&& git fetch -q origin main && git rebase -q origin/main && git push -q origin HEAD:main`. Banner "Synced" + HEAD + "safe to switch device". Never force-push.

/ship: card's ship line (none → one line: "<ctx> has no ship steps yet", stop). Bump the version where it says, commit + trailers, fetch + rebase, push; workflow given → one `gh run list --repo <repo> --workflow <file> --limit 1 --json databaseId` for the run id. Banner "<ctx> v<ver> building" + last line `Build link: https://github.com/<repo>/actions/runs/<id>`. Don't wait for CI; user says it failed → pull annotations, fix. "local build" (LOCAL only) → card's local build.

/list: card's list line (default: tool folders in `design/`, lessons in LESSONS.md); missing → skip silently. Banner "Tools + lessons"; one line per tool folder; lessons grouped by area, one line each. No other reads.
