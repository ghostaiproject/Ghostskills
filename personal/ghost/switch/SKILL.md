---
name: switch
description: Use when the user sends /switch [session]: hand the current work to another Claude Code session on the PC with a short brief (fresh context = fewer tokens), drivable from the phone.
---
# /switch: move work to a fresh PC session
Text after `/switch` = target session name (optional) + extra notes.
1. Brief, from your own summary (never paste transcripts, tool dumps or secrets), ≤1.5 KB:
   `Goal` · `Done` · `State` (repo, branch, key files, servers/URLs) · `Next` (numbered) · `Open` (questions/approvals pending).
2. Target:
   - Named → `list_sessions` (or ListAgents); match the name → SendMessage `[switched via /switch]` + brief. Busy or not found → say so, offer a new one.
   - None named → `start_session`: initiation user_asked, context fresh, same cwd/project (worktree only if this one has one), title = goal in ≤6 words, prompt = brief + "Resume from Next 1; ask before anything in Open."
3. New session → `set_remote_control` on, so the phone can drive it.
4. This chat: stop work here (no edits after the brief); `/save` first if a ctx is loaded.
5. Reply: narrow banner `/SWITCH ✓` + `-> [title](#local_<id>)`, one line: continue there; offer to archive this one (only on yes).
