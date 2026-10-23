---
name: save
description: Use when the user sends /save, or a project skill calls for auto-save: writes the current context's state back to where the /load context table says it lives.
---
# /save
Ctx + mode = the ones from /load (none → ask which ctx). Table lives in the load skill.
1. Repo ctx: fetch + rebase; merge other chats' commits (read their messages).
2. Ctx extras first (grocrun: follow the save extras in grocrun-dev).
3. Rewrite the state file (not append), ≤~7 KB: LATEST (most detail), Open, Project, How it works, History (one line per minor version, hotfixes bare). Drop stale lines; no style rules; add only what other chats' saves miss.
4. Repo ctx: commit [skip ci] + trailers; `git fetch -q origin main && git rebase -q origin/main && git push origin HEAD:main`. Never force-push.
   No repo: rewrite memory /areas/<ctx>.md instead (str_replace/write, keep [stated] lines).
5. CLOUD + repo: SendUserFile the state file (attach); update the latest-status line in memory /areas/<ctx>.md. LOCAL: skip if tools missing.
6. Reply: banner "<ctx> saved"; what changed, size before/after, NOT verified. Then "new chat + /load <ctx>" if the chat is long.
