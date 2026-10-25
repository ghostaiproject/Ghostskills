---
name: wiki-lint
description: Read-only vault health check. Use for lint, audit the wiki, find orphans, dead links, frontmatter gaps.
---
# Lint
Run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ghostskills.py lint --vault V --format markdown` (`--exclude "wiki/scratch/*"` repeatable, `--strict` for a nonzero exit on findings) (no `python3`, e.g. Windows Store stub → `python`).
Checks only: dead/ambiguous links, orphans, frontmatter (type, title), empty sections, stale index entries. Never claim semantic checks.

Report: keep the tool's paths, lines and counts; group by impact (broken navigation → ambiguous → metadata → upkeep). An orphan may be intentional; ambiguous basename → path-qualified link.
Never auto-fix or write a report into the vault. Fixing = separate wiki-save style transaction on the findings the user picks, then re-lint.
