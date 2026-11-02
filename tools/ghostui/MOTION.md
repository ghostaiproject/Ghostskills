# Motion (read when a design animates)
Read from the templates' own interaction files (durations ms, easing names).

## Timing
- Micro (press, toggle, color/state change): 100-200, ease-out.
- Enter (element appears/moves in): 300-400, ease-out (easeOutCirc / easeOutQuad).
- Exit (element leaves): 200, ease-in (easeInCirc). Exits faster than enters.
- Panel/drawer/carousel slide: 300, ease-in-out (easeInOutQuad).
- Sheet/dropdown: slide down 500, swing (soft overshoot) → CSS cubic-bezier(.34,1.3,.64,1) at 300-400.
- One hero morph per screen (image grows into detail): 700-900, ease-in-out.
- Fades: 200 quick, 300 standard, 400 for content swaps.

## Choreography
- Swap content: old text slides + fades out (200 in) → image resizes (hero) → new text slides + fades in (400 out). Run hero + text in parallel, offset 50-100.
- Lists/cards on load: stagger 40-60 per item, max 6 items staggered.
- Drawer: panel moves 0 ↔ -width, scrim fades 0 ↔ 40% in the same 300.
- Confirmation popup: scrim fade 300 + card fade/scale .96→1 in 300; dismiss fade 200.

## Gestures (used in weather, onboarding, carousel, flights)
- Swipe left/right → next/prev page/card; swipe up/down → expand/collapse sheet.
- Drag + dragend → sliders and draggable sheets snap to nearest stop.
- Focus in/out on inputs → label + border recolor 150.

## CSS
```css
--ease-out:cubic-bezier(.22,1,.36,1);--ease-in:cubic-bezier(.55,0,1,.45);
--ease-io:cubic-bezier(.65,0,.35,1);--swing:cubic-bezier(.34,1.3,.64,1);
```
Animate transform + opacity only. Honor prefers-reduced-motion → fades only.
