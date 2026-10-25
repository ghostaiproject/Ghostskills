---
name: webd
description: Use when building or redesigning a web page, site, dashboard or mockup: fixed design decision order + defaults, so each choice is made once.
---
# webd: web design decisions
Decide in this order; take the default unless the brief says otherwise.

## Order
1. Audience → who, device, tech comfort. Unsure → phone, low tech → simple mode.
2. Screens → list them; each gets ONE primary action (one filled button). Rest = secondary/text links. Lists of cards too: urgent/first item filled, others soft.
3. Layout → mobile-first 360px, one column; widen at 720 / 1080. Phone nav = bottom bar ≤5 items, icon + label.
4. Tokens → one accent from the brand color (+ dark shade for text on light, light tint for fills); neutrals; red/amber/green status only. Light + dark sets on `:root` / `[data-theme]`. Brand color pale → it is the fill/hero tint, ink does primary buttons. Dark: tint/selected (`--raised`) must stand out from the card.
5. Type → 1 family + mono for figures. Body 16–18px, line-height 1.5; scale 14/16/20/28/36.
6. Spacing → 8px grid (8/16/24/32/48); cards padding 24; air over borders.
7. Components → reuse: button, card, list row, pill, progress, segmented toggle, toast. No new one if one fits.
8. States → empty, loading, done, error, focus, pressed; toast after every action.
9. A11y → AA contrast (check accent on bg both themes), ≥44px targets, label every icon-only button, roving tabindex + arrows for tabs/radios, focus kept on re-render, `prefers-reduced-motion`.
10. Perf → local icons (vendored SVG, no CDN), no layout shift (hide `.app` until first render, 3s fallback), fonts `display=optional`, images sized.
11. Review → Playwright: no console errors, no overflow 320–1920, targets ≥44 → one `sheet.jpg` (desktop, dark, phone) → `/crew opinion` for copy + critique (≤8 lines) → fix → `next`. Card count fits the grid (4 → 2×2). Hero art: page bg = art bg exact, or mask-fade edges; no boxed picture. Palette-only change → recolor the art (PIL hue/sat mask, smooth blend) before regenerating.

## Simple mode (non-tech user)
- ≤3 choices per screen; one big answer first (a number, a yes/no, a "today" list).
- Plain words, no jargon/acronyms without a hint; sentence-case labels ≥16px.
- No dense charts: one bar or ring max; lists over tables.
- Big buttons (≥52px), lots of air, one accent; confirm with a toast, allow undo.

## Copy
- `/crew opinion` for names, taglines, wording, native-language check. Fake data, neutral names.
