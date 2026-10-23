---
name: save
description: Use when the user sends /save, a <ctx>-save skill hands over its card, or a project skill calls for auto-save: writes the current context's state back.
---
# /save
Card + mode = handed over by a `<ctx>-save` skill, else from this chat's last load. None → ask which ctx. No mode → detect it like load step 1. Save only that ctx.
1. Repo: fetch + rebase; merge other chats' commits (read their messages).
2. Card's save extras first.
3. Rewrite the state file (not append), ≤~7 KB: LATEST (most detail), Open, Project, How it works, History (one line per minor version, hotfixes bare). Drop stale lines; no style rules; add only what other chats' saves miss.
4. Repo: commit [skip ci] + trailers; `git fetch -q origin main && git rebase -q origin/main && git push origin HEAD:main`. Never force-push.
   No repo: rewrite memory /areas/<ctx>.md instead (str_replace/write, keep [stated] lines).
5. CLOUD + repo: SendUserFile the state file (attach); update the latest-status line in memory /areas/<ctx>.md if it exists. LOCAL: skip if tools missing.
6. Reply: banner "<ctx> saved"; what changed, size before/after, NOT verified. Long chat → "new chat + /<ctx>-load" (no-project ctx: "/load <ctx>").
