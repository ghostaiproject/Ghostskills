# Layout: phone, tablet, desktop (read for any app/site)
Seen on Linear, Apple, Stripe, Raycast + Chalet fix (ghost: "desktop has a lot of empty space").

## Breakpoints
- Phone ≤719: single column, 16px gutter, bottom CTA / sheet for secondary actions.
- Tablet 720-1099: two columns for the top panels, full-width rows for lists and charts; header gets extras (forecast, filters).
- Desktop ≥1100: `grid-template-columns: 240px minmax(0,1fr)` (rail + main), main uses grid-template-areas, max-width 1400-1480, centered.
- Wide ≥1400: more columns in card grids, never wider text lines (≤70ch).

## What desktop adds (pick what fits the subject)
- Side rail: brand, nav list with live values, secondary actions (scenes, filters, saved views). Sticky.
- Third column: activity feed / timeline / notifications / details of the selected item.
- Data panel: chart with real axis (24h, 7d), totals, peak.
- Status chips: doors, alerts, sync state.
- Phone-only parts hide on desktop (bottom CTA, sheet) because the rail already holds them.

## Grid recipe (desktop dashboard)
```css
.dash{display:grid;grid-template-columns:minmax(300px,4fr) minmax(0,5fr) minmax(240px,3fr);
 grid-template-areas:"hero main side" "list list side" "chart chart chart";gap:16px}
```
- Panels in the same row: align-self:stretch; center content inside the shorter one.
- Side column taller than its content → add summary tiles on top + more history rows.
- Every grid child min-width:0; wide charts get their own overflow-x:auto.

## Check before sending
`python3 shots.py page.html` → 390 / 820 / 1440 screenshots, scrollWidth + elements spilling out of their box. Look for: empty zones, sideways scroll, wrapped stat numbers, orphan cards.
