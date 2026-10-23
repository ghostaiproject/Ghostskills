# Ghostskills

Team Claude skills, written to be token-light. Rules: [CONVENTIONS.md](CONVENTIONS.md).

Install on claude.ai: everyone uploads **core**, then only the **project** folders they work on. Personal folders are one person's own; skip them unless you want them. `tools` = generic helpers, add the ones you need.
Upload files: `scripts/check.ps1 -Pack` → one zip per skill in `dist/`.

## Commands to remember
`/load` → numbered menu of your projects (+ memory contexts) → reply with the number.
`/save` → saves whatever this chat loaded; nothing loaded → same menu.
`/cmds` → numbered list of every command for the loaded project → reply with the number.
`/new <ctx>` → adds a project (card + README row + next number).
Shortcuts: `/load 1`, `/load grocrun`. Every card owns its number for good (#1 grocrun, #2 skills, #3 window); a new project gets the next one, so numbers never shift.

## core (everyone, no project inside)
| Skill | Command | Does |
|---|---|---|
| [load](core/load/SKILL.md) | `/load [#\|name]` | Menu, then loads one context; no project card → uses the repo you're in or memory |
| [save](core/save/SKILL.md) | `/save [#\|name]` | Saves the context loaded in this chat |
| [cmds](core/cmds/SKILL.md) | `/cmds` `/sync` `/ship` `/list` `/new` | Numbered command menu · push work in progress (stops on secrets) · build a release · tools + lessons · add a project |

## projects (one folder each, never mixed)
| # | Project | Skills | Does |
|---|---|---|---|
| 1 | [grocrun](projects/grocrun) | grocrun-card, grocrun-dev | GrocRun Android app (Grocerierun) |
| 2 | [skills](projects/skills) | skills-card | This repo |
| 3 | [window](projects/window) | window-card (+ tools/alexa-console-edit) | Echo open-the-windows alert (Ouvrelesfnetre) |

A `<ctx>-card` holds a project's number, repo, branch, state file, extras and how it ships, so the shared commands work on it. It joins the menu by itself; nobody types it. New project → copy [projects/_template](projects/_template).

## tools (generic, add when needed)
| Skill | Does |
|---|---|
| [alexa-console-edit](tools/alexa-console-edit/SKILL.md) | Edit + build an Alexa skill's model in the developer console via Chrome, script-first |

## personal
| Skill | Command | Does |
|---|---|---|
| [link](personal/ghost/link/SKILL.md) | `/link <msg>` | Phone chat → Claude task on Ghost's laptop |
| [next](personal/ghost/next/SKILL.md) | (auto) | After computer actions: ask next step, y/n or numbered |
| [do](personal/ghost/do/SKILL.md) | `/do <task>` | Asks y/n, then controls the PC. Needs [do-gate.ps1](personal/ghost/do/do-gate.ps1) in `~/.claude/hooks` + UserPromptSubmit/PreToolUse hooks |
| [remote-view](personal/ghost/remote-view/SKILL.md) | (auto) / "remote view" | Low-token PC work: text-first, one screenshot at the end |
| [ceig](personal/ghost/ceig/SKILL.md) | `/ceig <idea>` (or auto) | Chrome Extension Image Generation: non-AI-looking images via Gemini in Chrome → download, upscale, wallpaper |

## Keeping it healthy
`scripts/check.ps1` lints every skill (name = folder, `<ctx>-` prefix, card numbers, size, no project repos in core); CI runs it on every push. `-Drift` compares with your local `~/.claude/skills`; `-Pack` builds upload zips.
