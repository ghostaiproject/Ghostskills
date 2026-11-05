---
name: "nap"
description: "Use when the user sends /nap with time inputs (or asks what nap to take): calculates a nap starting from the chat time that keeps their day on a normal schedule, and can show the graph."
---

# /nap

Purpose: the user wants to sleep NOW. From the chat time (the message time in their timezone), calculate the nap that starts now and keeps the rest of the day and tonight on a normal schedule.

## Usage
`/nap <awake since> [bed] [wake]`

- awake since: when they last woke up, e.g. `10am yesterday`, `sat 10:00`
- bed: target bedtime (default 22:00)
- wake: wake time tomorrow (optional)
- now is always the chat time, never asked

Examples: `/nap 10am yesterday` · `/nap sat 10:00 bed 23:00 wake 7:00`

## Input menu (when inputs are missing)
If `/nap` comes with no times, or the awake-since time is missing and not known from the chat, show an inline input menu with the visualize widget tool (load it with ToolSearch `select:mcp__visualize__read_me,mcp__visualize__show_widget`, call read_me with modules ["elicitation"] and platform "mobile" first, silently).

- Header title: "Nap details". Submit button label: "Plan my nap".
- Fields, phrased as questions:
  1. When did you last wake up? Pills Today / Yesterday / 2 days ago (data-name woke_day) + time input (data-name woke_at, type=time, class elicit-date).
  2. What time do you want to be in bed tonight? Pills 21:00 / 22:00 / 23:00 / Other with text input (data-name bedtime). Preselect 22:00.
  3. When do you need to be up tomorrow? Time input (data-name wake_tomorrow).
  4. How wrecked do you feel right now? Cards with icon + subtitle: Fine (can push through) / Tired (need a boost) / Wrecked (eyes closing) (data-name tiredness).
- Skip fields already known from the message or chat; prefill anything known.
- One short line of text with the menu. The submitted answers arrive as the next message; compute from the time of THAT message.
- If skipped, use defaults and ask for the awake-since time in one short line.

## Compute from chat time (do the arithmetic, never estimate)
1. Hours awake = chat time - awake since.
2. Lie down = chat time + 5 min, rounded to the next 5 min.
3. Nap length, starting at lie down:
   - Default 25 min (light sleep only, no grogginess).
   - Backup 90 min (one full cycle) when Wrecked, only if it ends before 15:00.
   - Never 35-60 min (groggy zone). If a 25 min nap would end after 15:00: no nap, stay up until bedtime.
4. Rest of the day: no naps after 15:00.
5. Bedtime: +15 min to fall asleep, cycles of 90 min. If a wake-tomorrow time is given, set lights-out so 5 or 6 full cycles end exactly at it (pick the one closest to their bedtime). Otherwise show the 5 and 6 cycle wake times.
6. After 30h+ awake: one line that even 25 min can run deeper.

## Reply format: compact
1. One narrow banner box: `NAP · <hours>h <min>m awake`.
2. One code block timeline, one line per event, `HH:MM  what` (max about 24 characters per line):
```
07:15  lie down
07:40  alarm, 25 min
15:00  no naps after
21:45  lights out
07:00  up, 6 full cycles
```
3. At most two short lines below: the backup (90 min alarm time, never 35-60) and wake-up steps (light, move, cold water).

No section boxes, no explanations unless the user asks "why?" (then 2-3 lines). Casual, few abbreviations, narrow for a Samsung S23.

## Graph
- Ask in one line at the end only if not already answered this chat: `Graph? phone / PC`.
- Phone: use the nap-graph skill: run its `nap_graph.py` with the timeline lines from the code block above, then pass the SVG as is to the visualize widget (read_me modules ["diagram"] platform "mobile" first, silently). It draws the 24h split dial: night right half, day left half, nap + 15:00 cutoff, cycles C1..Cn, polar hypnogram, exact-time list. One short line of text after. No code tool or skill missing → draw the same split dial by hand (380 wide).
- PC: if nap-graph is there, run it and send the .svg file; otherwise give a copy-paste handoff prompt in a code block for Claude Code to build it with the ghostui design skill (Ghostskills repo, tools/ghostui), mobile + PC layouts. Prompt rules: starts with /load ghostskills, ends with /save, one long line per paragraph, includes the times and plan, and includes the retry-first rule (loop, rethink and retry several ways before any failure message or manual steps; user only steps in for sign-in, 2FA or approvals).

## Don't
- No medication, supplement or caffeine suggestions.
- No long morning sleep when they want to reset the routine.