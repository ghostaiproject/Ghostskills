---
name: load
description: Use when the user sends /load [context] to start a chat on a project: loads that context's saved state from the context table.
---
# /load [ctx]
## Context table
| ctx | repo (ghostaiproject/) | state | also load |
|---|---|---|---|
| grocrun | Grocerierun | HANDOFF.md | grocrun-dev skill |
| window | Ouvrelesfnetre | HANDOFF.md | — |
| skills | Ghostskills | README.md | CONVENTIONS.md |
| other | none | memory /areas/<ctx>.md | — |
Each ctx is separate: never mix state, rules or memory between rows.
New ctx → add a row here + in loadlist (Ghostskills repo) + re-save both on claude.ai.

## Steps
1. No ctx or unknown → one box listing ctx names; ask.
2. Mode: LOCAL if cwd or a parent has the state file + .git → that is the root; one Bash: `git status -s && git fetch -q origin main && git rebase -q --autostash origin/main && git log -1 --oneline` (dirty/conflict → one line, discard nothing). Else CLOUD: add_repo (push) + `git clone --depth 1 https://github.com/ghostaiproject/<repo> /home/claude/<repo lowercase>` (timeout 600000) unless it exists. No repo → skip.
3. Read the state file only (+ "also load" in the same batch). No repo → memory_read the area file. State missing → say so in one line; /save creates it.
4. Reply: banner "<ctx> loaded" + mode; latest version/status; ≤3 open items; "What's next, bro?".
Remember ctx + mode for /save. Stay in this ctx until another /load.
