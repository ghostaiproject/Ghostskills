# Websites + landing pages (read for any site, landing, portfolio, shop page)
Measured on land-book.com (12k curated sites, taxonomy counts) + 90 top-liked sites of the year (tags, palettes) + live: Voy, Kuda, Krea, people4ocean · ghost 2026-11-02.

## What the best sites do (share of 90 top-liked)
- Big footer 52% · parallax 46% · pastel colors 42% · big type in footer 36% · cards 34% · animation 33% · background video 32% · background image 27%.
- Rare (use as a deliberate signature, not default): gradient 8% · 3D 10% · black & white 10% · illustration 3% · visible borders 4% · brutalism.
- Type: sans 78% · serif 22%. Serif rises to ~40% in health, medical, ecommerce, food, furniture. Tech/AI ~20%.

## Color (palettes of the 90)
- 0 of 90 palettes contain pure #000 or #FFF. Lightest color is a tinted off-white (avg L 89%), warm 2:1 over cool (#FEF4EC peach, #F5EFE6 cream, #F2F2F0 stone).
- Ink is colored, not black: deep teal #00414F, plum-black #1B161D, forest #001A0B.
- ~1/3 of a palette is neutral; only ~2 vivid colors per site. Vivid set on dark (Voy: lime #D5E96D, orange #FF623B, lilac #F2DBF1 on #001A0B) or one soft field color for whole sections (Kuda lilac #EED3F8, people4ocean peach #FDE6D4).

## Section anatomy (land-book section types, in usual order)
Hero → Brands/logos → Value proposition → Features → How it works → Stats → Testimonial → Case study → Pricing → FAQ → Resources → Call to action → Big footer.
- Desktop: each section a different layout (split, bento cards, full-bleed media, marquee); alternate field colors to pace the scroll.
- Phone: same order, one column, media first, CTAs full width.

## Hero copy (land-book headline taxonomy)
- Headline 3-8 words. Angles: Vision ("Designing for 100 years of healthy living") · Outcome ("More from your money, more for your life") · Problem ("Stop compressing like it's 1996") · Positioning ("The X for Y": "The help center that never goes stale") · Differentiation ("The last sales tax service you'll ever need") · Invitation · Mechanism.
- Subhead: one sentence = what it is + for whom + how.
- CTAs: 1 primary verb ("Start free", "Download", "Book a demo") + optional ghost secondary ("Watch video").
- Tone: pick one of Bold · Emotional · Friendly · Informational · Minimal · Playful and keep it everywhere.

## Type on sites
- Display huge and tight: h1 line-height 0.92-1.0, tracking -0.02 to -0.03em (Krea). Weight 300 light (Voy) or 800 heavy (Kuda), rarely in between.
- Pair: expressive display (serif like Season, or quirky grotesk like Modena) + neutral grotesk body (Suisse, NB International, TT Commons).
- Footer: oversized brand word or tagline (60px+ desktop) = "big type in footer".

## Motion on sites
- Scroll reveal: 24-40px rise + fade, 0.8-1.4s, cubic-bezier(.22,1,.36,1), once (Voy 1.4s; AOS fades 1s).
- Parallax: media moves 10-20% slower than text; never on body copy.
- Background video / canvas loops in hero or cards, muted, with a poster frame (visible at rest).
- Hover: 150-300ms color/opacity; buttons pill radius 999px.
- Smooth scroll libs common (Lenis, GSAP ScrollTrigger); for us: CSS animation-timeline: view() with a fallback that shows content.

## Checklist for a site
1 identity recipe (IDENTITY.md) · off-white + colored ink · 1-2 vivid colors · display+body pair · hero copy angle chosen · 6-10 sections from the anatomy · one signature motion · big footer · render 390/820/1440.
