# New project

Faster: `/new <ctx>` does all of this.

1. Copy this folder to `projects/<ctx>/` (`<ctx>` = short lowercase name).
2. Make one skill folder, `<ctx>-card`, with the SKILL.md below. `<n>` = highest card # + 1, never reused. It shows up in the `/load` and `/save` number menus by itself.
3. Project rules (style, extra commands only this project needs) → a second skill, `<ctx>-dev`, named in "also load".
4. Add a row to the root README, then upload the new folders as skills on claude.ai.

`<ctx>-card/SKILL.md`:
```
---
name: <ctx>-card
description: Use only when a core skill (load, save, cmds) picks <ctx> (#<n>): holds <what it is>'s card. Never typed by the user.
---
# <ctx> card
ctx <ctx> · #<n> · <3-5 words> · repo <owner>/<repo> (or none) · branch main · state HANDOFF.md · also load: — · load extras: — · save extras: —.
Ship: version spot · CI workflow file · local build command (or —) · List: default (design/ + LESSONS.md) · Extra cmds: —.
```
