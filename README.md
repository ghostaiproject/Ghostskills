# Ghostskills

Team Claude skills, written to be token-light. Rules: [CONVENTIONS.md](CONVENTIONS.md).

Install on claude.ai: everyone uploads **core**, then only the **project** folders they work on. Personal folders are one person's own; skip them unless you want them.

## core (everyone, no project inside)
| Skill | Command | Does |
|---|---|---|
| [load](core/load/SKILL.md) | `/load <name>` | Loads any context; with no project skill, uses the repo you're in or memory |
| [save](core/save/SKILL.md) | `/save` | Saves the context loaded in this chat |
| [loadlist](core/loadlist/SKILL.md) | `/loadlist` | Lists installed projects + memory contexts |

## projects (one folder each, never mixed)
| Project | Commands | Does |
|---|---|---|
| [grocrun](projects/grocrun) | `/grocrun-load` `/grocrun-save` `/ship` `/sync` `/cmds` `/list` | GrocRun Android app (Grocerierun) |
| [window](projects/window) | `/window-load` `/window-save` | Echo open-the-windows alert (Ouvrelesfnetre) |
| [skills](projects/skills) | `/skills-load` `/skills-save` | This repo |

`/load grocrun` also works: it hands off to `grocrun-load`.

New project → copy [projects/_template](projects/_template).

## personal
| Skill | Command | Does |
|---|---|---|
| [link](personal/ghost/link/SKILL.md) | `/link <msg>` | Phone chat → Claude task on Ghost's laptop |
| [next](personal/ghost/next/SKILL.md) | (auto) | After computer actions: ask next step, y/n or numbered |
