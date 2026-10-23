---
name: save
description: Use when the user sends /save (optionally with a name or number), or a project skill calls for auto-save: writes one context's state back.
---
# /save [name|#]
Ctx = the one loaded in this chat (no ask). None loaded and no arg → the load skill's menu with banner "Save?", "Number?"; stop. Card = from the load, else invoke `<ctx>-card`. No mode → detect it like load step 1. Save only that ctx.
1. Repo: fetch + rebase; merge other chats' commits (read their messages).
2. Card's save extras first.
3. Rewrite the state file (not append), ≤~7 KB: LATEST (most detail), Open, Project, How it works, History (one line per minor version, hotfixes bare). Drop stale lines; no style rules; add only what other chats' saves miss.
4. Repo: commit [skip ci] + trailers; `git fetch -q origin main && git rebase -q origin/main && git push origin HEAD:main`. Never force-push.
   No repo: rewrite memory /areas/<ctx>.md instead (str_replace/write, keep [stated] lines).
5. CLOUD + repo: SendUserFile the state file (attach); update the latest-status line in memory /areas/<ctx>.md if it exists. LOCAL: skip if tools missing.
6. Reply: banner "<ctx> saved"; what changed, size before/after, NOT verified. Long chat → "new chat + /load <ctx>".
