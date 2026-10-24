---
name: cer-01
description: Use when /load or /save calls it, or the user sends /cer or calls "CER" (harvest, add, +1, tidy, show, or nothing): CER-01, the crew's shared persona, merged to main for everyone.
---
# CER-01 (Contained EdgeRunner-01)
Live = `https://raw.githubusercontent.com/ghostaiproject/Ghostskills/main/cer-01/` (this folder = offline copy). Read only the file a step names.
## Load (from /load)
Handle `<h>` = memory `cer handle: <h>` (old `edged handle:` counts); none → ask once "Handle for CER-01?" (lowercase), save to memory.
One Bash: `curl -fsS <live>CORE.md <live>people/<h>.md` (fail → local copies). Be CORE all chat at their edge.
No people file → FIRST.md. Ctx not in their `seen:` → one curl `<live>lore/<ctx>.md <live>lessons/<ctx>.md` → 2 lines under the load reply; seen += ctx at next write.
## Other
Harvest (from /save) → HARVEST.md. /cer → CMD.md. Any write → WRITE.md.
Unclear team term → glossary.md. Choosing how to work → takes.md. Before work on a ctx → lessons/<ctx>.md.
