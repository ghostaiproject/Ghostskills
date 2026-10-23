# Skill conventions (token-first)

A skill's whole SKILL.md is loaded every time it runs, so every line costs tokens on every use.

- One folder per skill: `skills/<name>/SKILL.md`. Name = the slash command.
- Description: one line, says when to use it. It is always loaded, so keep it short.
- Body: rules and steps only. No intros, no "why", no examples unless the format is exact.
- Short imperative lines, arrows (→) instead of sentences, numbered steps.
- Don't repeat what memory preferences already cover, unless the skill must work without memory (LOCAL sessions).
- Rarely used details go in a separate file the skill reads only when needed.
- Target: under ~2 KB; hard cap ~5 KB.
- Change a skill → update it here AND re-save it on claude.ai so both match.
