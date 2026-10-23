# Ghostskills

Team Claude skills, written to be token-light. Rules: [CONVENTIONS.md](CONVENTIONS.md).

Install on claude.ai: everyone uploads **core**, then only the **project** folders they work on. Personal folders are one person's own; skip them unless you want them.

## Three commands to remember
`/load` → numbered menu of your projects (+ memory contexts) → reply with the number.
`/save` → saves whatever this chat loaded; nothing loaded → same menu.
`/cmds` → numbered list of every command for the loaded project → reply with the number.
Shortcuts: `/load 2`, `/load grocrun`. Numbers stay fixed (A→Z), so they're easy to learn.

## core (everyone, no project inside)
| Skill | Command | Does |
|---|---|---|
| [load](core/load/SKILL.md) | `/load [#\|name]` | Menu, then loads one context; no project card → uses the repo you're in or memory |
| [save](core/save/SKILL.md) | `/save [#\|name]` | Saves the context loaded in this chat |
| [cmds](core/cmds/SKILL.md) | `/cmds` `/sync` `/ship` `/list` | Numbered command menu · push work in progress · build a release · tools + lessons |

## projects (one folder each, never mixed)
| Project | Skills | Does |
|---|---|---|
| [grocrun](projects/grocrun) | grocrun-card, grocrun-dev | GrocRun Android app (Grocerierun) |
| [skills](projects/skills) | skills-card | This repo |
| [window](projects/window) | window-card | Echo open-the-windows alert (Ouvrelesfnetre) |

A `<ctx>-card` holds a project's repo, state file, extras and how it ships, so the shared commands work on it. It joins the menu by itself; nobody types it. New project → copy [projects/_template](projects/_template).

## personal
| Skill | Command | Does |
|---|---|---|
| [link](personal/ghost/link/SKILL.md) | `/link <msg>` | Phone chat → Claude task on Ghost's laptop |
| [next](personal/ghost/next/SKILL.md) | (auto) | After computer actions: ask next step, y/n or numbered |
| [ceig](personal/ghost/ceig/SKILL.md) | `/ceig <idea>` (or auto) | Chrome Extension Image Generation: non-AI-looking images via Gemini in Chrome → download, upscale, wallpaper |
