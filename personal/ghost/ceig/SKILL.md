---
name: ceig
description: Use when the user sends /ceig or asks to generate/render an image, wallpaper or artwork: Gemini in Chrome → download → upscale → optional wallpaper.
---
# /ceig: Chrome Extension Image Generation (Gemini)

## Prompt (anti-AI look)
`Generate an image:` + format → subject + mood (concrete nouns, scale, emotion) → one medium → imperfections → 2–4 colors → composition → exclusions.
- Realistic: `shot on 35mm film, Kodak Portra 400, 50mm lens, natural light, shallow depth of field`
- Illustrated: `cinematic anime painting, hand-drawn line work` / gouache / ink + watercolor
- Imperfections (biggest lever): `film grain, chromatic aberration, haze, dust, uneven light, wet reflections, asymmetric composition`
- Wallpaper → `negative space on the left for desktop icons`
- End: `no text, no letters, no logos, no watermarks, no characters`
- Never: masterpiece, 8k, ultra detailed, hyperrealistic, trending on artstation.
- Franchise → "inspired by the look of X" + no characters.

## Chrome
1. One ToolSearch: tabs_context_mcp, tabs_create_mcp, navigate, computer, javascript_tool, tabs_close_mcp → tabs_context_mcp {createIfEmpty:true}.
2. `https://gemini.google.com/app` (UI may be French: "Demander à Gemini").
3. Click box → type → Enter does NOT send → screenshot → click round send arrow.
4. Wait ~20 s → JS `[...document.querySelectorAll('img')].filter(i=>i.naturalWidth>400)` → scrollIntoView → screenshot (save_to_disk) → SendUserFile.
5. Changes → same chat ("darker, keep the rest").

## Download (ask first)
OK → download arrow (image top right) → `Downloads\Gemini_Generated_Image_*.jpg` (~1376×768 for 16:9).

## Upscale
`wallpaper.ps1 -Name <file> [-SetWallpaper]` (next to this file) → newest Gemini download → 3840×2160 PNG in `Pictures\Wallpapers`. Wallpaper only if asked. Say the source resolution (upscale adds no detail).

## End
Close your tab → path + resolution.
