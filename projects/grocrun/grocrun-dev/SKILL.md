---
name: grocrun-dev
description: Use for any work on the GrocRun Android app (repo ghostaiproject/Grocerierun).
---
# GrocRun dev (follow literally)
State: HANDOFF.md (repo root). Code work: Read DEV.md + LESSONS.md + CODEMAP.md in ONE batch, then only needed lines (offset/limit ~60). Grep only what CODEMAP lacks.

## Mode (set by /load grocrun)
LOCAL = repo folder on the PC; CLOUD = /home/claude/grocerierun. GitHub main = source of truth: fetch + rebase before work. App code ships as a branch + PR into main (shows in the CER-01 Approvals tab; the owner merges, then main CI builds + install); never push code to main. [skip ci] state saves (HANDOFF/LESSONS/CODEMAP) may go straight to main.
First step every chat (before HANDOFF/version reads): `git switch main && git pull --rebase`. The PC copy can sit on an old branch (2026-11-04: demo-mode-5.51.0 showed 5.51 while main was 5.53). Uncommitted work or not on main → say the branch and ask before switching.

## Tokens
1. Never switch model mid-chat. Default Sonnet; Opus = new chat + /load grocrun. "Extra" effort only for hard bugs.
2. Auto-save via the save skill (no ask) after a finished build, ~20 turns, or big reads (3+ long files, logs, images); then one line: "new chat + /load grocrun".
3. Task list only for 4+ tool-call builds; update once at the end.
4. Independent calls in ONE message; chain Bash steps into one command.
5. Never re-read a file already read/edited; no ls/cat to recheck known state.
6. Batch user changes → one build.
7. Memory: snapshot only; write only when asked or on save; no memory tools → skip silently.
8. No Monitor/background watchers; CI wait (only if the user asks) = one Bash poll loop.
9. Edits: one python3 heredoc (LOCAL Windows: `python`), exact replace, assert count==1, several files per call.
10. Never run a script to draw a reply.

## Replies
First reply of a chat, or any build/bug-list/screenshot/research reply → read REPLIES.md (next to this file). Short chat replies: casual tone, say what is NOT verified, ≤1 next step.

## Project extras
Save extras (run by /save) and the `*`-link rule → read EXTRAS.md (next to this file) only then.
