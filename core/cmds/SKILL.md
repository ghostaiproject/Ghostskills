---
name: cmds
description: Use when the user sends /cmds, /sync, /ship, /list, /new or an extra cmd of the loaded card (optionally + a name or number): shared commands for whichever context this chat loaded.
---
# Shared commands
Ctx + card + mode = this chat's load. None → the load skill's menu (banner "For which?", "Number?"), then invoke `<ctx>-card`; no mode → detect like load step 1. /sync and /ship need a repo: none → one line, stop. Branch = card's (default main).

/cmds: banner "Cmds · <ctx>"; numbered, one line each, then "Number?" and run the pick:
1 /load — switch project; 2 /save — save state; 3 /sync — push work in progress; 4 /ship — build a release; 5 /list — tools + lessons; 6 /new — add a project; 7+ the card's extra cmds (typed directly → run it as the card says).

/sync: one Bash: `git add -A && git diff --cached --name-only`. Any path like .env*, *.jks, *.keystore, *.pem, *.p12, local.properties → `git reset -q`, list them, ask; stop. Else one Bash: `git commit -q -m "wip: <summary> [skip ci]"` + trailers `&& git fetch -q origin <branch> && git rebase -q origin/<branch> && git push -q origin HEAD:<branch>`. Banner "Synced" + HEAD + file count + "safe to switch device". Never force-push.

/ship: card's ship line (none → one line: "<ctx> has no ship steps yet", stop; it names a skill → invoke that skill, stop). Bump the version where it says, commit + trailers, fetch + rebase, push; workflow given → one `gh run list --repo <repo> --workflow <file> --limit 1 --json databaseId` for the run id. Banner "<ctx> v<ver> building" + last line `Build link: https://github.com/<repo>/actions/runs/<id>`. Don't wait for CI; user says it failed → pull annotations, fix. "local build" (LOCAL only) → card's local build.

/new <ctx>: read NEW.md (next to this file), follow it.

/list: card's list line (default: tool folders in `design/`, lessons in LESSONS.md); missing → skip silently; nothing at all → one line "nothing to list for <ctx>". Banner "Tools + lessons"; one line per tool folder; lessons grouped by area, one line each. No other reads.
