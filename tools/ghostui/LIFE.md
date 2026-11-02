# Life (read for every design; correct ≠ alive)
Learned · ghost 2026-11-02 (Chalet Hanté): v1 passed every rule and still read "AI-made, lifeless". v2 fixed it with the moves below.

## Why rules alone feel dead
- Same card on every block, everything static until clicked, copy that only labels, data with no story.

## Add (pick 3+)
- Cast: give the subject characters or objects with a name, a trait and a quirk (residents, plants, devices, regulars). Show them as small drawn avatars, reused in feed, chart notes, toasts.
- Lives on its own: 2-3 things move at rest, slow and varied (wander, bob, blink, flicker, needle jitter, particles). Different delays, never in sync.
- Reacts to you: something follows the pointer/finger (eyes, light, tilt); press = small physical response (peek, pop, swing).
- The signature is a scene, not a chart: draw the world (rooms + furniture, plants in a bed, cars on a road) with the data living inside it.
- Hand-made touch: a light SVG wobble (feTurbulence + feDisplacementMap scale 3-4) on drawn lines, or a font with quirks (Fraunces SOFT/WONK, italic accent word in headings).
- Main action tells a story: CTA triggers a visible event in the scene + a one-line narrated caption + a new feed entry.
- Voice: copy written by someone (local slang, a joke in the empty spots, "3 âmes, 0 loyer"); headings with one italic accent word.
- One real live detail: today's moon phase, sunrise, season, local weather; computed, not faked.

## Limits
- Max 1 hero animation; ambient loops 2-30 s, transform/opacity, canvas for particles (≤50, pause when hidden).
- Everything visible at rest; prefers-reduced-motion → still, readable.
- Never: emoji as characters, bouncing everything, motion with no meaning.

## Test
Screenshot it: would someone smile, or want to poke something? No → add from the list above.
