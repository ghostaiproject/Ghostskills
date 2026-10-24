# Ghostskills

Team Claude skills, written to be token-light. Rules: [CONVENTIONS.md](CONVENTIONS.md).

Install on claude.ai: everyone uploads **core**, then only the **project** folders they work on. Personal folders are one person's own; skip them unless you want them. `tools` = generic helpers, add the ones you need.
Upload files: `scripts/check.ps1 -Pack` (Windows: `powershell -ExecutionPolicy Bypass -File scripts\check.ps1 -Pack`) → one zip per skill in `dist/`.

## Commands to remember
`/load` → numbered menu of your projects (+ memory contexts) → reply with the number.
`/save` → saves whatever this chat loaded; nothing loaded → same menu.
`/cmds` → numbered list of every command for the loaded project → reply with the number.
`/new <ctx>` → adds a project (card + README row + next number).
`/edged` → the crew's shared personality: harvest, add, +1, tidy, show.
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

## edged (everyone, shared personality)
[edged](edged/SKILL.md): one personality for the whole crew, kept in git and merged to main.
- **CORE.md** (every chat): voice, quirks, catchphrases, moments, never-say list. **people/<handle>.md**: your lang, edge level (1 chill · 2 spicy · 3 full send), screen, likes, nevers.
- Read only when needed: glossary.md, takes.md, lore/<ctx>.md, lessons/<ctx>.md (one file per project, so a chat only pays for its own). Rare steps (first time, harvest, /edged, write) are separate files too.
- `/load` pulls the live CORE + your people file from GitHub, so merges reach everyone's next chat with no re-upload. First time → 3 quick questions; first /load of a project → 2 lines of that project's lore + lessons.
- `/save` ends with a harvest: ≤3 things from the chat worth keeping (a line that got a lmao, a new term, a gotcha) → you pick → merged to main. No push rights → a PR.
- `/edged +1 <words>` votes; `/edged tidy` promotes lines with 2+ votes into CORE.
- **The repo is public**: handles only. The checker blocks emails and phone numbers and caps sizes (CORE 1.5 KB, people 1 KB, others 4 KB).

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
