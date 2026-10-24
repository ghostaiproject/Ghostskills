---
name: load
description: Use when the user sends /load (with a name, a number, or nothing), or the save/cmds skill needs its menu: starts a chat on one context, picked from a numbered menu, kept apart from every other context.
---
# /load [name|#]
Card = ctx · # · repo (owner/name or none) · branch (default main) · state file · also load · load extras · save extras · ship · list · extra cmds.

## Menu (no tool calls)
List = every `<ctx>-card` skill in the skill list by the `(#N)` in its description (none → after them, A→Z), then memory /areas names not covered (A→Z). A card's # never changes, so numbers stay the same when projects are added.
- No arg → banner "Load?" then one line each: `<#> <ctx> · <3-5 words>`. End: "Number?". Stop; the reply is the pick.
- Number or name → that item. Unknown → show the menu.

## Card
1. `<ctx>-card` skill → invoke it; its card is the card.
2. Else no-project ctx: cwd or a parent has HANDOFF.md + .git → that repo, state HANDOFF.md; otherwise no repo, state = memory /areas/<ctx>.md.

## Steps
1. Mode: LOCAL if cwd or a parent has the state file + .git → that is the root; one Bash: `git status -s && git fetch -q origin <branch> && git rebase -q --autostash origin/<branch> && git log -1 --oneline` (dirty/conflict → one line, discard nothing). Else CLOUD: add_repo (push) + `git clone --depth 1 -b <branch> https://github.com/<repo> /home/claude/<name lowercase>` (timeout 600000) unless it exists. No repo → skip.
2. Read the state file only (+ also load + the edged skill's Load, same batch); run load extras. No repo → memory_read the area file. Missing → one line; /save creates it.
3. Reply: banner "<ctx> loaded" + mode; latest version/status; ≤3 open items; "What's next?".

Remember card + mode for /save. Stay in this ctx until another /load. Never mix state, rules or memory between ctxs.
