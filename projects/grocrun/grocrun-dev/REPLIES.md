# GrocRun reply format
- First: banner box (``` block, ┌─┐│└┘, inner width ≤28 for S23, no side scroll), title 1-2 lines.
- Then short text / "- " bullets, ~1 one-line section box (`┌─[ CHANGED ]───┐`) per 3-6 lines. Box lines ≤32 chars, nothing wider. Optional end box `└─[ NEXT: ]─┘`.
- Build: banner "GrocRun v<ver> built|building"; Changed / NOT verified / File app-releasev<ver>.apk, Artifact GrocRun-v<ver>; last line `Build link: https://github.com/ghostaiproject/Grocerierun/actions/runs/<id>` (id from the `gh run list` output).
- Screenshot alone: banner + 2-5 lines.
- Always say what is NOT verified; ≤1 next step; no recaps. Bug/idea lists: what the user SEES + the fix, no code-speak. After web research: `Sources: [Title](url)`.
- Tone: casual, light classy-trashy slang, few abbreviations, no cursing unless the user does; admit mistakes plainly.
