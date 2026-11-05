# nap-graph / Nap Planner: handoff (2026-11-05)

Resume: new session → `/load cer` (or skills) → "continue nap planner from tools/nap-graph/HANDOFF.md".

## State
- Artifact **Nap Planner** (private): https://claude.ai/artifact/PB3jysDYJcdaHFo6MMqhtU (v1). Form → Calculate → giant LIE DOWN + SET ALARM times with countdowns, Copy alarm, 90 min backup line, tonight strip, 24h split dial (night right, day left, cycles C1..Cn, polar hypnogram, now + alarm dots), exact-time list. Remembers last answers per browser.
- Source: `app/` page.html, style.css, calc.js, dial.js, ui.js → `python app/build.py` → `app/dist/index.html` (publish, same URL) + `dist/preview.html` (local check, phone width).
- Math checked: Yesterday 10:30, bed 22:00, up 07:00, now 08:14 → 08:20 lie, 08:45 alarm, 09:50 backup, 21:45 lights, 6 cycles, 21h44 awake (same as the old chat answer).
- `/nap` skill (personal/ghost/nap) now replies with the artifact link only; chat timeline + `nap_graph.py` SVG = fallback.
- `nap_graph.py` = Python twin of the dial for chat/PC.

## Not verified
- On the S23 inside the claude.ai app (only checked in the browser pane at 400px, light theme).
- Dark theme render on the live artifact.

## Next (pick)
1. Test `/nap` on the phone end to end; fix what looks off.
2. "Add to calendar"/alarm hand-off is limited (artifact can't set phone alarms; Copy alarm only).
3. Optional: share the artifact link if someone else should use it (Share menu).
