---
name: load
description: Use when the user sends /load [ctx], or a <ctx>-load skill hands over its card: loads one context's saved state, kept apart from every other context.
---
# /load [ctx]
Card = ctx · repo (owner/name or none) · state file · also load · load extras · save extras.

## Find the card
1. Handed over by a `<ctx>-load` skill → use it.
2. A `<ctx>-load` skill is in the skill list → invoke it, stop.
3. No ctx → one box: every `*-load` skill + memory /areas names; ask.
4. Else no-project ctx: cwd or a parent has HANDOFF.md + .git → that repo, state HANDOFF.md; otherwise no repo, state = memory /areas/<ctx>.md.

## Steps
1. Mode: LOCAL if cwd or a parent has the state file + .git → that is the root; one Bash: `git status -s && git fetch -q origin main && git rebase -q --autostash origin/main && git log -1 --oneline` (dirty/conflict → one line, discard nothing). Else CLOUD: add_repo (push) + `git clone --depth 1 https://github.com/<repo> /home/claude/<name lowercase>` (timeout 600000) unless it exists. No repo → skip.
2. Read the state file only (+ also load, same batch); run load extras. No repo → memory_read the area file. Missing → one line; /save creates it.
3. Reply: banner "<ctx> loaded" + mode; latest version/status; ≤3 open items; "What's next?".

Remember card + mode for /save. Stay in this ctx until another load. Never mix state, rules or memory between ctxs.
