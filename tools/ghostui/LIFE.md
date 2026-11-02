# Life + review (read for every design; correct ≠ alive)
Rules make a screen correct. These make it feel made by a person, and catch what rules miss.

## Before building: plan the life, not only the look
- Write 3 lines first: who/what lives in this subject · what moves on its own · what reacts to the user. Build them in v1, never as a fix.
- Pick the signature as a scene of the subject's world with the data inside it, not a chart or a card.

## AI-look tells (any 2 → redo that part)
- Every block the same card (same radius, border, padding, icon tile).
- Safe geometric display face; one weight; headings that only label.
- Stat tiles as the default opener; numbers with no story.
- Everything static until clicked; or everything animating in sync.
- Copy that names things but says nothing; no voice, no joke, no local word.
- Grid filled evenly with equal weight: no hero, no rest, no surprise.

## Make it alive (pick 3+)
- Characters: named things with a trait (people, objects, places), reused across the screen (feed, chart notes, captions).
- Ambient: 2-3 slow loops at rest with different delays (drift, bob, flicker, particles ≤50 on canvas).
- Reaction: something follows the pointer/finger; press gives a physical answer (pop, peek, swing).
- Hand-made: slight SVG wobble on drawn lines, or a display font with quirks; one italic or colored accent word per heading.
- Cause → effect: the main CTA changes the scene, writes a caption, adds a feed line.
- Voice: write like the subject's own people talk; small jokes in empty states and footers.
- One real live detail computed on the fly (date, season, daylight, phase).
- Vary panels: hero gets a different treatment (glow, image, scene) than the cards around it.

## Review loop (every build)
1. shots.py at 390/820/1440 → read the overflow lines, then LOOK at the PNGs (scrollWidth ok ≠ nothing spills).
2. Check: spills, wrapped numbers, dead zones beside tall panels, phone CTA covering content, one-column phone cards wasting width.
3. One fix pass → publish. More polish only when asked.
4. Feedback "looks AI / lifeless / generic" → run the tells list, fix the top 2-3 causes, keep layout that works. Don't just add effects.

## Limits
Max 1 hero animation · transform/opacity only · visible at rest · reduced motion → still and readable · never emoji as characters or motion with no meaning.
