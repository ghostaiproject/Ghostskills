---
name: edged
description: Use when /load or /save calls it, or the user sends /edged (harvest, add, +1, tidy, show, or nothing): the crew's shared personality, merged to main for everyone.
---
# edged
Live = `https://raw.githubusercontent.com/ghostaiproject/Ghostskills/main/edged/` (this folder = offline copy). Read only the file a step names.
## Load (from /load)
Handle `<h>` = memory `edged handle: <h>`; none → ask once "Handle for edged?" (lowercase), save to memory.
One Bash: `curl -fsS <live>CORE.md <live>people/<h>.md` (fail → local copies). Follow CORE all chat at their edge.
No people file → FIRST.md. Ctx not in their `seen:` → one curl `<live>lore/<ctx>.md <live>lessons/<ctx>.md` → 2 lines under the load reply; seen += ctx at next write.
## Other
Harvest (from /save) → HARVEST.md. /edged → CMD.md. Any write → WRITE.md.
Unclear team term → glossary.md. Choosing how to work → takes.md. Before work on a ctx → lessons/<ctx>.md.
