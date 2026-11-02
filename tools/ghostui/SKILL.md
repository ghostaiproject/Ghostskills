---
name: ghostui
description: UI rules for designing app screens, sites, dashboards and mockups (identity, layout, type, color, components, motion). Use with ghostfiles for any app/site design work.
---
# GhostUI (app + site design; look → ghostfiles)
Template specs measured from ~30 Justinmind templates · ghost 2026-11-02. Motion → MOTION.md.
Templates = clean but generic. Specs alone look bland ("one color, nothing designed" · ghost). Identity first.

## Identity (do first, every design)
- Mood from the subject's world: place, season, time, material (chalet → winter dusk, snow, warm interior).
- One signature element only this app would have: dial, floor plan, map, live scene. Make it the hero.
- Color carries meaning: data maps to color (temp cold→warm), each category gets its own hue (light amber, lock mint, blinds sky). Neutrals stay quiet.
- Display face with character for names + numbers (Bricolage Grotesque, Fraunces, Syne); calm body face (Manrope, DM Sans). Never one font for all.
- One ambient touch (snow, glow, grain), drawn visibly at rest.
- Check: could this screen belong to any other app? Yes → not done.

## System
- No drop shadows: depth = tinted canvas + cards + 1px borders + colored glows.
- Accent fills only primary actions; state colors come from the data/category.
- Scale: 11 · 13 · 16 · 20 · 26-30 · 44; hero numbers 72-120. Body 400, labels 600, titles 600-800. Max 4 sizes per screen.
- Radius by role: inputs/buttons 8-14 · cards 20-24 · pills full · avatars 50%.
- 8pt grid; 16px phone gutter; 44px min tap target.

## Patterns
- Hero number: giant value + tiny label + live state chip.
- Stat row: 3 small tiles, label on top, bold value below.
- Device card: icon tile + switch + name + status; on = its own hue fill + glow.
- Dashboard: icon rail → list → card grid → summary (phone: signature hero → stats → cards).
- Onboarding: 3-4 steps · illustration · 30px headline · one sentence · one CTA · dots · swipe.
- Login: greeting 35-38px · 2 labeled fields · full-width pill · text links.

## Never
Single-hue screens. Drop shadows. Paragraphs on cards. Content starting invisible. Shipping without rendering it on a phone-size screen first.
