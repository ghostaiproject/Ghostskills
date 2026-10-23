# Skill conventions (token-first)

A skill's whole SKILL.md is loaded every time it runs, so every line costs tokens on every use.

## Layout
- One folder per skill, folder name = skill name = slash command.
- `core/`: generic skills for everyone. No project names, repos or personal style inside.
- `projects/<ctx>/`: everything for one project. Every skill name starts with `<ctx>-` so projects never clash or mix. Minimum: `<ctx>-load` + `<ctx>-save` (a card handed to core load/save).
- `personal/<user>/`: one person's own skills (their devices, their habits).

## Writing
- Description: one line, says when to use it. It is always loaded, so keep it short.
- Body: rules and steps only. No intros, no "why", no examples unless the format is exact.
- Short imperative lines, arrows (→) instead of sentences, numbered steps.
- Reply style comes from each person's own memory preferences; only project skills that must work without memory (LOCAL sessions) spell it out.
- Rarely used details go in a separate file the skill reads only when needed.
- Target: under ~2 KB; hard cap ~5 KB.
- Change a skill → update it here AND re-upload it on claude.ai so both match.
