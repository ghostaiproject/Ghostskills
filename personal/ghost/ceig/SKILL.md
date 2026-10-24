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

## Art-director check (always, before any copy or download)
- Look at the result at full size: it must fit its exact spot (format, subject, palette, background) and pass an art director's bar (no artifacts, no stray text, clean edges, nothing generic).
- Below the bar → say what is off and regenerate in the same chat with a sharper prompt; never save a weak image.
- Copy without download: `canvas.drawImage(img)` → `toBlob` → `navigator.clipboard.write([new ClipboardItem({'image/png':blob})])` in the page (works when Gemini shows only share/download), then PowerShell `Clipboard.GetImage()`.
- After saving, Read the saved file once to confirm it is the right image (Gemini's copy button can belong to an older image).

## In-project review loop (after first gen, when the image is for a project)
1. Put the saved image in its real spot in the project (the asset path the page uses) and open the project in the built-in browser (`preview_start` by name, or reload the open tab).
2. Screenshot the page at `scale` 0.5 with the image in place; compare it with the Gemini result: fit, crop, palette vs the page, contrast with text/UI over it, style match, artifacts.
3. Perfect → stop. Otherwise list the concrete fixes and reprompt Gemini in the same chat ("keep the rest, change: …"), save, swap it in, screenshot again.
4. Max 3 reprompts after the first gen. After the last one, keep the best version and say what is still off.

## Download (ask first)
OK → download arrow (image top right) → `Downloads\Gemini_Generated_Image_*.jpg` (~1376×768 for 16:9).

## Upscale
`wallpaper.ps1 -Name <file> [-Source <path>] [-Width 2560 -Height 1440] [-SetWallpaper]` (next to this file) → newest Gemini download (or -Source) → 3840×2160 PNG (or W×H) in `Pictures\Wallpapers`. Wallpaper only if asked. Say the source resolution (upscale adds no detail).

## End
Close your tab → path + resolution.
