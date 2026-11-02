# Motion (read when a design animates)
Measured: Justinmind interaction files · Material 3, Carbon, Fluent, Primer, Polaris tokens · Linear, Raycast, Apple, Stripe CSS.

## Durations (consensus)
- 50-100 press/hover color · 120 tooltip · 150-175 dialog, menu · 200-250 small move · 300 drawer, carousel, sheet · 400 page/content enter · 500-700 big reveal · 700-900 one hero morph.
- Exit ≈ 70% of enter. Nothing over 500 except one hero.

## Curves
```css
--standard:cubic-bezier(.2,0,0,1);      /* M3 standard: most UI moves */
--decel:cubic-bezier(.05,.7,.1,1);      /* M3 emphasized decelerate: things entering */
--accel:cubic-bezier(.3,0,.8,.15);      /* M3 emphasized accelerate: things leaving */
--out-quart:cubic-bezier(.165,.84,.44,1);/* Stripe/Linear reveals, hovers */
--out-expo:cubic-bezier(.23,1,.32,1);   /* Raycast fades */
--swing:cubic-bezier(.34,1.3,.64,1);    /* soft overshoot: sheets, toggles */
```

## Recipes (real values)
- Tooltip: opacity 0→1 + scale .9→1, 120ms, ease-out (Linear).
- Menu/popover: opacity + 2px slide from the trigger side, 150ms (Raycast).
- Dialog: scale .96→1 + translateY 2% + fade, 175ms; scrim fade 150 (Linear, Raycast).
- Dialog click-outside when blocking: scale 1→.98→1 in 150ms "bounce" (Linear).
- Error: shake 0 → -3px → 3px → 0, 300ms (Raycast).
- Drawer: transform 0 ↔ -width, 300; scrim 0 ↔ 40% same time.
- Sheet: translateY 100% → 0, 300-380 swing; drag with finger, snap on release.
- Nav flyout content: 8px slide + fade, old one leaves opposite way (Apple).
- Content swap: old out 200 accel → new in 400 decel, stagger 40-60/item, max 6.
- Section reveal on scroll: 24px rise + fade 500-800 out-quart, once; prefer animation-timeline: view() where supported.
- Press: scale .97 or translateY(2px) 100ms.
- Ambient loop (marquee, gradient, snow): linear, 20-30s, pause off-screen.

## Gestures
Swipe left/right → next/prev · swipe up/down → expand/collapse sheet · drag + release → snap · focus → label + border recolor 150.

## Rules
Animate transform + opacity only. First load = content already visible: never start at opacity 0 (renders blank when animations pause); animate only on later swaps or below the fold. Honor prefers-reduced-motion → fades only.
