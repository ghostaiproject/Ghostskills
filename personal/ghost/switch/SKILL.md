---
name: switch
description: Use when the user sends /switch [notes]: hand the current work to a fresh Claude Code session as one paste-ready brief (fresh context = fewer tokens).
---
# /switch: paste-ready brief for a fresh session
Never start, message or look up sessions (start_session fails under Remote Control); no tool calls. Text after `/switch` = extra notes for the brief.
1. Brief, from your own summary (never paste transcripts, tool dumps or secrets), ≤1.5 KB, plain text in ONE code block so it copies in one tap:
   `Goal` · `Done` · `State` (repo, branch, key files, servers/URLs) · `Next` (numbered) · `Open` (questions/approvals pending), last line `Resume from Next 1; ask before anything in Open.`
2. This chat: stop work here (no edits after the brief); `/save` first if a ctx is loaded.
3. Reply: narrow banner `/SWITCH` → the code block → one line: open a new session (desktop app or claude.ai/code) and paste it; offer to archive this one (only on yes).
