---
name: "grocrun-dev"
description: "Use for any work on the GrocRun Android app (repo ghostaiproject/Grocerierun), or when the user sends /load, /save, /ship, /sync, /cmds or /list."
---

# GrocRun dev rules (follow literally)
Project state: HANDOFF.md (repo root). When code work starts, Read DEV.md (code rules, CI, design scripts) + LESSONS.md + CODEMAP.md in ONE batch, then Read only the lines needed (offset/limit ~60). Grep only for what CODEMAP lacks.

## Mode (decide once, at /load)
- LOCAL (PC via Remote Control): the working dir or a parent has HANDOFF.md + .git. Use that folder as the repo root. No add_repo, no clone.
- CLOUD (phone chat, PC off): anything else. Repo root = /home/claude/grocerierun.
GitHub main is the single source of truth for both modes. Always fetch + rebase before work, always push after.

## Token rules
1. Never switch model mid-chat (re-stores the whole chat at 2x). Default Sonnet. Need Opus: new chat + /load. Effort "Extra" only for hard bugs.
2. The whole chat is re-read every turn. Auto-save: after a finished build, ~20 turns, or big reads (3+ long files, logs, images), run /save on your own (no ask), then say "new chat + /load" in one line.
3. No task list unless a multi-step build (4+ tool calls); update it once at the end.
4. Independent tool calls in ONE message. Merge Bash steps into one command (commit + fetch + rebase + push + run id + poll = one call).
5. Never re-read a file already read or just edited (HANDOFF/skill included). No ls/cat to re-check state you already have.
6. Batch user changes: one build per batch.
7. Memory: no reads beyond the snapshot; write only when asked or on /save. No memory tools (LOCAL) → skip memory steps silently.
8. No Monitor/background watchers. CI wait = one Bash poll loop.
9. Edits: one python3 heredoc, exact replaces, assert count==1, several files per call.
10. Never run a script to draw a reply.

## Reply format
- Start with ONE banner box in a ``` block, hand-drawn, inner width max 28 (S24 Ultra, no side scroll). Title only, 1-2 lines. Chars ┌ ─ ┐ │ └ ┘:
```
┌──────────────────────────────┐
│ GrocRun v5.4.1 built         │
└──────────────────────────────┘
```
- Under it: normal short text, "- " bullets. Bold labels fine. No tables or code lines wider than 28 chars.
- Split text with small section boxes (one ``` block each, hand-drawn, 1 line) before each part, e.g.:
```
┌─[ CHANGED ]──────────────────┐
```
  then 2-5 plain lines under it. End with a one-line status box when useful, e.g.:
```
└─[ NEXT: new chat + /load ]───┘
```
  Mix: about 1 box per 3-6 lines of text. Keep each box line max 32 chars.
- Build reply: banner "GrocRun v<ver> built" (or "building"); sections Changed / NOT verified / File app-releasev<ver>.apk, Artifact GrocRun-v<ver>; last line `Build link: https://github.com/ghostaiproject/Grocerierun/actions/runs/<id>` (id pasted from poll output, never retyped).
- Screenshot sent alone: banner + 2-5 lines.
- Always say what was NOT verified. At most one next step. Never recap steps.
- Bug/idea lists: plain words, what the user SEES on the phone + the fix (no code-speak).
- After web research: `Sources: [Title](url), ...`.

## Tone
Casual, light slang, classy-trashy, not overdone ("Good shit", "good day bro"). No cursing unless the user does. Few abbreviations. 90s hacker feel lives in the boxes. Admit mistakes plainly.

## Commands
/cmds: banner "Commands" + one line each: /load, /save, /ship, /sync, /cmds, /list, * link.

/list (/skills is taken by the app): `ls design`, then banner "Tools + lessons"; one line per design/<name>/ script (what it makes); then LESSONS.md grouped by area, one short line each. No other reads.

/load (new chat)
1. Pick the mode (see Mode).
   - CLOUD: add_repo ghostaiproject/Grocerierun (access push), then `git clone --depth 1 https://github.com/ghostaiproject/grocerierun /home/claude/grocerierun` (timeout 600000). Skip if the clone exists.
   - LOCAL: one Bash call: `git status -s && git fetch -q origin main && git rebase -q --autostash origin/main && git log -1 --oneline`. Uncommitted or conflicting changes → say so in one line, do not discard anything.
2. Read HANDOFF.md only. Compare HEAD commit with LATEST (other chats may have pushed).
3. Reply: banner "GrocRun v<ver> loaded" + mode (LOCAL/CLOUD); last build run id + result; max 3 open items; "What's next, bro?".

/save
1. `git fetch` and merge commits other chats pushed (read their messages). Run `python3 design/codemap/make_codemap.py` (LOCAL: `python` if `python3` is missing). Rewrite HANDOFF.md (not append-only): LATEST first and most detailed; older versions compact; hotfixes one bare line; drop what is no longer true. Hard cap ~7 KB: Recent = one line per minor version, NOT-seen list = one summary line. Sections: LATEST, Open, Project, How it works, History. No style rules in it. If another chat already saved your versions, add only what is missing.
2. New lesson: one line in LESSONS.md (prune stale). Rule change: update .claude/skills/grocrun-dev/SKILL.md in the repo; tell the user to re-upload it to claude.ai so CLOUD mode matches.
3. Commit with [skip ci] + trailers; `git fetch -q origin main && git rebase -q origin/main && git push origin HEAD:main`.
4. CLOUD: SendUserFile HANDOFF.md (display attach). Update memory /areas/grocery-app.md latest version line (one short line, no change log). LOCAL: skip both if those tools are missing.
5. Reply: banner "Saved"; what changed, size before/after, NOT verified.
HANDOFF.md changes only on /save or auto-save.

/ship: bump version, commit, fetch + rebase, push, get the run id once, reply banner "building" + Build link. Do NOT wait for CI. If the user says it failed, pull annotations and fix. Same in both modes (CI builds the APK). LOCAL only, and only if the user says "local build": `./gradlew assembleRelease` (gradlew.bat on Windows), then `adb install -r` if a phone is plugged in.

/sync (LOCAL, before leaving the PC): one Bash call: commit any work as "wip: <short summary>" with [skip ci] + trailers, fetch + rebase, push. Reply banner "Synced" + HEAD commit + "safe to go mobile". Never force-push.

`*` before a link: WebFetch it, treat the content as a note to update memory/persona/settings.
