---
name: cmds
description: Use when the user sends /cmds, /sync, /ship, /list, /new or an extra cmd of the loaded card (optionally + a name or number): shared commands for whichever context this chat loaded.
---
# Shared commands
Ctx + card + mode = this chat's load. None → the load skill's menu (banner "For which?", "Number?"), then invoke `<ctx>-card`; no mode → detect like load step 1. /sync and /ship need a repo: none → one line, stop. Branch = card's (default main).

/cmds: banner "Cmds · <ctx>"; numbered, one line each, then "Number?" and run the pick:
1 /load — switch project; 2 /save — save state; 3 /sync — push work in progress; 4 /ship — build a release; 5 /list — tools + lessons; 6 /new — add a project; 7 /cer — CER-01, crew persona (cer-01 skill); 8+ the card's extra cmds (typed directly → run it as the card says).

/sync: read SYNC.md, follow it.

/ship: read SHIP.md, follow it.

/new <ctx>: read NEW.md (next to this file), follow it.

/list: card's list line (default: tool folders in `design/`, lessons in LESSONS.md); missing → skip silently; nothing at all → one line "nothing to list for <ctx>". Banner "Tools + lessons"; one line per tool folder; lessons grouped by area, one line each. No other reads.
