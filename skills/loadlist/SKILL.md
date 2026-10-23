---
name: loadlist
description: Use when the user sends /loadlist: shows every context they can /load, no tool calls.
---
# /loadlist
Repo ctxs (copy of the load skill's table; if they differ, the load table wins → fix this list):
- grocrun: GrocRun Android app (Grocerierun)
- window: Echo open-windows alert (Ouvrelesfnetre)
- skills: this skills repo (Ghostskills)
Memory ctxs: each /areas/<name>.md in the memory snapshot listing not covered above (use its description). No reads.

Reply: banner "Contexts"; one line each: `/load <ctx>` — what it is. Repo ctxs first, then memory ctxs. End: "Pick one, bro."
