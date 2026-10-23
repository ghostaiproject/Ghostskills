---
name: grocrun-dev
description: Use for any work on the GrocRun Android app (repo ghostaiproject/Grocerierun), or when the user sends /ship, /sync, /cmds or /list. Load/save: /load and /save (card: grocrun-card).
---
# GrocRun dev (follow literally)
State: HANDOFF.md (repo root). Code work: Read DEV.md + LESSONS.md + CODEMAP.md in ONE batch, then only needed lines (offset/limit ~60). Grep only what CODEMAP lacks.

## Mode (set by /load grocrun)
LOCAL = repo folder on the PC; CLOUD = /home/claude/grocerierun. GitHub main = source of truth: fetch + rebase before work, push after.

## Tokens
1. Never switch model mid-chat. Default Sonnet; Opus = new chat + /load grocrun. "Extra" effort only for hard bugs.
2. Auto-save via the save skill (no ask) after a finished build, ~20 turns, or big reads (3+ long files, logs, images); then one line: "new chat + /load grocrun".
3. Task list only for 4+ tool-call builds; update once at the end.
4. Independent calls in ONE message; chain Bash steps into one command.
5. Never re-read a file already read/edited; no ls/cat to recheck known state.
6. Batch user changes → one build.
7. Memory: snapshot only; write only when asked or on save; no memory tools → skip silently.
8. No Monitor/background watchers; CI wait = one Bash poll loop.
9. Edits: one python3 heredoc, exact replace, assert count==1, several files per call.
10. Never run a script to draw a reply.

## Replies
- First: banner box (``` block, ┌─┐│└┘, inner width ≤28 for S23, no side scroll), title 1-2 lines.
- Then short text / "- " bullets, ~1 one-line section box (`┌─[ CHANGED ]───┐`) per 3-6 lines. Box lines ≤32 chars, nothing wider. Optional end box `└─[ NEXT: ]─┘`.
- Build: banner "GrocRun v<ver> built|building"; Changed / NOT verified / File app-releasev<ver>.apk, Artifact GrocRun-v<ver>; last line `Build link: https://github.com/ghostaiproject/Grocerierun/actions/runs/<id>` (id pasted from poll output).
- Screenshot alone: banner + 2-5 lines.
- Always say what is NOT verified; ≤1 next step; no recaps. Bug/idea lists: what the user SEES + the fix, no code-speak. After web research: `Sources: [Title](url)`.
- Tone: casual, light classy-trashy slang, few abbreviations, no cursing unless the user does; admit mistakes plainly.

## Commands
/cmds: banner "Commands" + one line each: /load, /save, /ship, /sync, /cmds, /list, `*` link.

/list: `ls design`; banner "Tools + lessons"; one line per design/<name>/ script; LESSONS.md grouped by area, one line each. No other reads.

Save extras (run by /save before HANDOFF.md):
1. `python3 design/codemap/make_codemap.py` (LOCAL: `python` fallback).
2. New lesson → one line in LESSONS.md (prune stale).
3. Rule change → update .claude/skills/grocrun-dev/SKILL.md here AND projects/grocrun/grocrun-dev/SKILL.md in ghostaiproject/Ghostskills; tell the user to re-save it on claude.ai.

/ship: bump version, commit, fetch + rebase, push, get run id once; banner "building" + Build link. Don't wait for CI; if the user says it failed, pull annotations and fix. "local build" (LOCAL only): `./gradlew assembleRelease` (gradlew.bat on Windows), then `adb install -r` if a phone is plugged in.

/sync (LOCAL): one Bash: commit "wip: <summary>" [skip ci] + trailers, fetch + rebase, push. Banner "Synced" + HEAD + "safe to go mobile". Never force-push.

`*` before a link: WebFetch it; treat it as a note to update memory/persona/settings.
