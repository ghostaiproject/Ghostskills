---
name: maxed
description: Use when the user hits their Claude usage limit (or sends /maxed): reads the exact reset time from claude.ai/settings/usage and schedules a one-time task that resumes the unfinished work right after the reset.
---
# /maxed: resume after the usage reset

1. Load the Claude in Chrome tools (one ToolSearch). Open claude.ai/settings/usage in a new tab. Sign-in/2FA → ask the user; never type passwords.
2. The settings dialog is a modal (URL becomes `/new#settings/usage`) → `find` "dialog containing Resets" → `read_page` with that `ref_id`; not `get_page_text`. Empty result → page still loading, retry once.
3. "Current session" → "Resets at H:MM AM/PM". "This week" → weekly reset; use it only if the weekly limit is the one hit.
4. Next occurrence of that time in America/Toronto + 2 min → ISO 8601 with offset (e.g. `2026-11-05T17:02:00-05:00`; check DST).
5. Standalone prompt (fresh run, no memory of this chat): the task, current state (files, repo, branch), remaining steps, rules (retry several ways before failing; user only does sign-in/2FA/approvals; never type passwords; short replies).
6. `mcp__scheduled-tasks__create_scheduled_task` with `fireAt` (one-time; never cron, never local Cron tools). Runs only while the desktop app is open (else on next launch).
7. Reply in one line: reset time + task scheduled.

## Rules
- Retry/rethink several ways before any failure message.
- Page unreadable → ask the user for the reset time, then schedule.
