---
name: nap-graph
description: Turn a /nap answer timeline into a precise 24h split-dial SVG (night right half, day left half, cycles C1..Cn, polar hypnogram, exact-time list). Use when a /nap reply asks "Graph? phone" or the user wants the nap graph.
---
# nap-graph: /nap timeline → 24h split dial
Script: `python nap_graph.py` (this folder). Feed it the /nap code block lines, as args or stdin:
```
python nap_graph.py "13:00 nap 25 min" "15:00 no naps after" "21:45 lights out" "07:00 up, 6 full cycles" > nap.svg
```
Understands: `lie down` + `alarm, N min` · `nap N min` · `no naps after`/`cutoff` · `lights out`/`bed` · `up[, N full cycles]` (no N → cycles that fit after 15 min to fall asleep).

## Read the dial
- Top = lights out, right half = night (lights → up), left half = day (up → lights): the night gets half the dial so the hypnogram stays readable; hour ticks are exact in both halves.
- Outer ring: gray awake, teal nap, purple asleep, dashed orange spoke = no-nap cutoff.
- Middle ring: one color per 90 min cycle, C1..Cn. Inside: stepped hypnogram, farther out = lighter (Awake, REM, N1, N2, N3); deep early, REM longer late.
- Under the dial: exact times (nap span, cutoff, lights out + sleep onset, each cycle's end, up).

## Use in a /nap reply
- Phone: run the script, pass the SVG as is to the visualize widget (it brings its own dark background), one short line after.
- PC: SendUserFile the .svg.
- Example: `example.svg` (13:00 nap, 21:45 lights out, 07:00 up, 6 cycles).
