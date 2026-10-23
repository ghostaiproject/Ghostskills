---
name: ceig
description: /ceig (Chrome Extension Image Generation). Use when the user asks to generate/render/make an image, wallpaper or artwork, or says "use Gemini": prompt Gemini in Chrome (Claude in Chrome), download, upscale, optionally set as wallpaper.
---
# CEIG: Chrome Extension Image Generation (Gemini)

## Prompt (anti-AI look)
Order: `Generate an image:` + format (e.g. 16:9 desktop wallpaper) → subject + mood (concrete nouns, scale, emotion) → one specific medium → imperfections → 2–4 named colors → composition → exclusions.
- Medium, realistic: `shot on 35mm film, Kodak Portra 400, 50mm lens, natural light, shallow depth of field`
- Medium, illustrated: `cinematic anime painting, hand-drawn line work` / gouache / ink + watercolor
- Imperfections (biggest lever): `film grain, chromatic aberration, haze, dust, uneven light, wet reflections, asymmetric composition`
- Wallpaper → `negative space on the left for desktop icons`
- Exclusions: `no text, no letters, no titles, no logos, no watermarks, no characters`
- Never: masterpiece, 8k, ultra detailed, hyperrealistic, trending on artstation.
- Franchise → only "inspired by the look of X" + no characters.

## Chrome
1. One ToolSearch: tabs_context_mcp, tabs_create_mcp, navigate, computer, javascript_tool, tabs_close_mcp. tabs_context_mcp {createIfEmpty:true} → own tab.
2. Go to `https://gemini.google.com/app` (UI may be French: "Demander à Gemini").
3. Click box → type prompt → Enter does NOT send → screenshot, click round send arrow.
4. Wait ~20 s → JS: `[...document.querySelectorAll('img')].filter(i=>i.naturalWidth>400)` → scrollIntoView → screenshot (save_to_disk) → SendUserFile.
5. Changes → type them in same chat ("darker, keep the rest").

## Download (ask first)
OK from user → click download arrow (image top right) → `Downloads\Gemini_Generated_Image_*.jpg`, ~1376×768 for 16:9.

## Upscale / wallpaper
Run `wallpaper.ps1` (next to this file): `-Name <file> [-SetWallpaper]` → newest Gemini download → 3840×2160 PNG in `Pictures\Wallpapers`. Set wallpaper only if asked. Tell user the source resolution (upscale adds no detail).

## End
Close your tab → report path + resolution.
