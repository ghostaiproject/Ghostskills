---
name: ghostui
description: UI rules for designing app screens, sites, dashboards and mockups (identity, layout, type, color, components, motion). Use with ghostfiles for any app/site design work.
---
# GhostUI (app + site design; look → ghostfiles)
Sources (measured, not guessed) · ghost 2026-11-02: ~30 Justinmind templates · Material 3, Carbon, Fluent, Primer, Polaris, Radix tokens · 33 daisyUI themes · live sites Linear, Stripe, Raycast, Apple, Headspace, Things, Duolingo · land-book.com (12k sites, 90 top-liked analysed).
Read when needed: IDENTITY.md (style recipes) · MOTION.md (timings, keyframes) · LAYOUT.md (phone/tablet/desktop) · LANDING.md (websites: sections, hero copy, site trends).

## 1. Identity first (every design)
- Mood from the subject's world: place, season, time, material.
- Pick a recipe in IDENTITY.md (or blend two). Its knobs = radius, border, depth, type, color temperature.
- One signature element only this app has (dial, floor plan, keyboard keys, live gradient). Make it the hero.
- Color carries meaning: data → color (cold→warm), each category its own hue; accent only on primary actions.
- Display face with character + calm body face. Never one font for everything.
- One ambient touch (snow, glow, grain, gradient canvas), visible at rest.
- Test: could this screen belong to another app? Yes → not done.

## 2. Color
- Never pure grey, black or white (0 of 90 top sites use #000/#FFF). Off-white tinted warm, ink colored (teal, plum, forest).
- Never pure grey or pure black. Tint neutrals toward the brand hue (Linear #0F1011, Apple #1D1D1F, Headspace #2D2C2B on #F9F4F2).
- Dark mode bg L 14-24%, slightly chromatic (hue of brand). Text tinted to theme (warm themes = warm text).
- Text hierarchy = 3 levels by alpha on one ink: 100% · 72% · 56% (Apple), or 3 tinted greys (Linear).
- 12-step scale per hue (Radix): 1-2 backgrounds · 3-5 component fills/hover/pressed · 6-8 borders · 9-10 solid · 11-12 text.
- Palette = base + primary + secondary (analogous or triadic) + bright accent (L~90) for highlights only.

## 3. Type
- Sizes (M3 / Radix consensus): 11 · 12 · 14 · 16 · 20 · 24 · 28 · 35 · 45 · 57; hero numbers 72-120.
- Display tracking negative: -0.01em at 28px → -0.025em at 60px+. Small caps labels +0.08em.
- Weights: premium/calm = light display 300 (Stripe) or 510-600 (Linear, Apple); playful = 700 everywhere (Duolingo, Headspace).
- Line height: ~1.1 display, 1.4-1.5 body.

## 4. Shape + depth
- Radius scale (M3): 4 · 8 · 12 · 16 · 20 · 28 · 48 · full. Nested radius = outer − padding.
- Radius = personality: 0-4 serious/finance · 8-12 tools · 16-32 friendly · fields 2rem = playful.
- Depth options (pick one per app): hairline 0.5-1px rgba border + 1px inset white 5% highlight (Linear) · tinted soft shadow rgba(50,50,93,.12) 0 16px 32px (Stripe) · solid offset 0 2-4px darker shade, tactile (Headspace, Duolingo) · layered "physical key" shadows (Raycast).
- Glass (backdrop blur) only on floating nav/sheets over content.

## 5. Every screen ships phone + desktop
- One build, 3 layouts (LAYOUT.md): phone ≤719 one column · tablet 720-1099 two columns · desktop ≥1100 rail + 3-zone grid, max ~1480.
- Desktop shows MORE, not bigger: side nav, extra panels (activity feed, charts, forecast, status chips). Phone keeps the essentials + one CTA.
- No empty canvas: every column ends near the same line; fill gaps with real content, never stretch cards.
- Check: render 390 · 820 · 1440 (shots.py), no sideways scroll, no big empty areas.

## 6. Patterns
- Hero number + tiny label + live state chip.
- Stat row: 3 tiles, label top, bold value below.
- Toggle card: icon tile + switch + name + status; on = its hue fill + glow.
- Phone dashboard: signature hero → stats → cards → primary CTA.
- Onboarding: 3-4 steps · illustration · 30px headline · 1 sentence · 1 CTA · dots · swipe.
- Login: greeting 35px · 2 labeled fields · full-width pill · text links.
- Tactile button: 0 4px 0 darker shade; press → translateY(2px) + shadow 2px, 100ms.

## Never
Single-hue screens · pure #000/#808080 · one font for all · paragraphs on cards · content starting invisible · two depth styles mixed · a phone column stranded in the middle of a desktop · shipping without rendering 390/820/1440 first.
