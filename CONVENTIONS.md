# Skill conventions (token-first)

A skill's whole SKILL.md is loaded every time it runs, so every line costs tokens on every use.

## Layout
- One folder per skill, folder name = skill name. Commands people type are shared in core: /load, /save, /cmds, /sync, /ship, /list. A project adds its own only when no shared one fits.
- `core/`: generic skills for everyone. No project names, repos or personal style inside.
- `projects/<ctx>/`: everything for one project. Every skill name starts with `<ctx>-` so projects never clash or mix. Minimum: one `<ctx>-card` skill (#, repo, branch, state file, extras, how to ship), which core /load and /save list in their number menu. Its description carries `(#N)`: the menu number, fixed forever, next free one for a new project (`/new`). Users never type project skill names.
- `cer-01/`: CER-01, the crew's shared persona (one skill + its files).
- `tools/`: generic helper skills (no project inside) people add only if they need them.
- `personal/<user>/`: one person's own skills (their devices, their habits); may add their own commands (e.g. /link, /ceig).
- Context isolation ("never mix ctxs") lives once in core/load; cards don't repeat it.

## Writing
- Description: one line, says when to use it. It is always loaded, so keep it short.
- Body: rules and steps only. No intros, no "why", no examples unless the format is exact.
- Short imperative lines, arrows (→) instead of sentences, numbered steps.
- Reply style: the person's own memory and instructions > project dev rules > cer-01/people/<handle> > cer-01/CORE.md. Shared personality goes in cer-01/, never copied into other skills.
- cer-01/ is public: handles only, no private data; new items come in through the harvest or /cer, one line each, tagged `· <handle> <date>`.
- Rarely used details go in a separate file the skill reads only when needed. Content that grows → one file per ctx, read only that ctx's. A step that may be skipped decides first, then reads.
- Target: under ~2 KB; hard cap ~5 KB.
- Change a skill → update it here, run `scripts/check.ps1 -Pack` (no FAIL), re-upload its zip from `dist/` on claude.ai so both match. Removed a skill → delete it on claude.ai too.
