---
name: switch
description: Use when the user sends /switch [notes], or the chat passes ~150K context / a task just shipped: open a fresh Claude Code session pre-loaded with a brief (fresh context = fewer tokens); on Remote Control fall back to a paste-ready brief.
---
# /switch: fresh session with a pre-loaded brief
Text after `/switch` = extra notes for the brief. Auto-trigger (no /switch typed): context past ~150K or a task shipped → ask first with the `next` picker ("Switch to fresh session (Recommended)").
1. Brief, from your own summary (never paste transcripts, tool dumps or secrets), ≤1.5 KB:
   `Goal` · `Done` · `State` (repo, branch, key files, servers/URLs) · `Next` (numbered) · `Open` (questions/approvals pending), last line `Resume from Next 1; ask before anything in Open.`
2. This chat: `/save` first if a ctx is loaded; no edits after the brief.
3. Open it yourself: `start_session` (load with ToolSearch `select:mcp__ccd_session__start_session`), `initiation` "user_asked" (the user typed /switch or picked it), `context` "fresh", `cwd` = the project folder, `title` ≤60 chars, `prompt` = Next + Open + done-when, `background` = Goal + Done + State.
   - Started → reply: banner `/SWITCH` → one line with the session link `[title](#local_<id>)` → offer to archive this chat (only on yes).
4. Refused (Remote Control, no desktop app, error) → never retry: banner `/SWITCH` → the brief as plain text in ONE code block (copies in one tap) → one line: open a new session (desktop app or claude.ai/code) and paste it.
