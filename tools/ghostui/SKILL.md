---
name: ghostui
description: UI rules for designing app screens, sites, dashboards and mockups (layout, type, color, components, motion). Use with ghostfiles for any app/site design work.
---
# GhostUI (app + site design; look → ghostfiles)
Measured from ~30 Justinmind templates (styles + interaction files) · ghost 2026-11-02. Motion details → MOTION.md.

## System
- Flat: zero shadows in every template → depth = tinted canvas + white cards + 1px borders.
- Canvas: light #F1F2F7 or #EAEBF6 · dark navy #24365D / #0F1562 with white@10% cards.
- One brand accent per app (seen: #4262FF #5665E3 #6555FF #3A29E8 #004FFB #FD3593) + its 15% tint for chips/selected rows (#DEE3FF, #EAEBF6).
- Chart palette only in charts: #6CC986 #5665E3 #F0C774 #D86A65 #E4A44C.
- Type: one sans (Poppins, Montserrat, Roboto, Lato); serif (Lora, Georgia) only for display headlines.
- Scale: 11 · 13 · 16 · 20 · 26-30 · 38-45; hero numbers 100-120. Body 400, labels 500, titles 600-700. Max 4 sizes per screen.
- Radius: inputs/buttons 5-8 · cards 10-15 · big panels 20 · pills = height/2 (~23) · avatars 50%.
- 8pt grid; 16px phone gutter; 44px min tap target.

## Patterns
- Hero number: giant value + tiny label (temp, total, balance).
- Stat grid 2x2: label on top, bold value below.
- List row: name left · values right · thin divider.
- Card: title · big number · mini chart. Nothing else.
- Device/toggle card: icon + name + status; active = accent fill, inactive = tint.
- Dashboard: icon rail → section list → card grid → summary panel (phone: tabs + stacked cards).
- Onboarding: 3-4 steps · one illustration · 30px headline · one sentence · one CTA · dots · swipe.
- Login: greeting headline 35-38px · 2 labeled fields · full-width pill button · text links.
- Button set: primary fill · secondary tint · ghost outline · icon-only circle.

## Never
Shadows. Two accents. Paragraphs on cards. Over 4 font sizes per screen. Motion over 500ms (except one hero).
