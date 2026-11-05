---
name: nap
description: Use when the user sends /nap (with or without times) or asks what nap to take: opens the Nap Planner artifact, which asks the questions and shows when to lie down, when to set the alarm, tonight's lights-out and a 24h sleep-cycle dial.
---
# /nap

The user wants to sleep NOW. The Nap Planner artifact does the asking and the math from their phone's live clock.

## Reply (default, every /nap)
1. One narrow banner box: `NAP PLANNER`.
2. The link on its own line: https://claude.ai/artifact/PB3jysDYJcdaHFo6MMqhtU
3. One short line: "Fill it in, tap Calculate: lie-down + alarm times are at the top." Nothing else: no form widget, no code-block timeline, no graph question.
- Times in the message (e.g. `/nap 10am yesterday`): still just the link; add one line with what to enter.

## Fallback (link can't open, or user says "in chat")
Compute in chat with the rules below; reply = banner `NAP · <h>h <m>m awake` + a code block `HH:MM  what` (lie down, alarm, 15:00 no naps after, lights out, up + cycles) + at most 2 lines (90 min backup alarm, wake-up steps). Graph: run the nap-graph skill's `nap_graph.py` on those lines and show the SVG in the visualize widget.

## Rules (the artifact uses the same ones; source: Ghostskills tools/nap-graph/app/calc.js)
1. Hours awake = now - last wake-up.
2. Lie down = now + 5 min, rounded up to the next 5 min.
3. Nap: 25 min by default. 90 min (one full cycle) if Wrecked and it ends by 15:00. Never 35-60 min. 25 min would end after 15:00 → no nap, stay up.
4. No naps after 15:00.
5. Night: 15 min to fall asleep + 90 min cycles. With a wake time: lights-out so 5 or 6 full cycles end exactly at it (closest to their bedtime). Without: lights-out = bedtime, show the 5 and 6 cycle wake times.
6. 30h+ awake: one line that even 25 min can run deeper.

## Edit the artifact
Page source: Ghostskills `tools/nap-graph/app/` (page.html, style.css, calc.js, dial.js, ui.js) → `python build.py` → publish `app/dist/index.html` to the same URL.

## Don't
- No medication, supplement or caffeine suggestions.
- No long morning sleep when they want to reset the routine.
