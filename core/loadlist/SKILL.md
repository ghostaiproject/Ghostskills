---
name: loadlist
description: Use when the user sends /loadlist: shows every context they can load, no tool calls.
---
# /loadlist
Project ctxs: each `<ctx>-load` skill in the available-skills list (use its description).
No-project ctxs: each /areas/<name>.md in the memory listing not covered above. No reads.

Reply: banner "Contexts"; one line each: `/<ctx>-load` or `/load <name>` — what it is. Projects first. End: "Pick one."
