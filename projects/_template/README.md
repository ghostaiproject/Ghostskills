# New project

1. Copy this folder to `projects/<ctx>/` (`<ctx>` = short lowercase name).
2. Make one skill folder, `<ctx>-card`, with the SKILL.md below. It shows up in the `/load` and `/save` number menus by itself.
3. Project rules (build steps, style, extra commands) → a second skill, `<ctx>-dev`, named in "also load".
4. Add a row to the root README, then upload the new folders as skills on claude.ai.

`<ctx>-card/SKILL.md`:
```
---
name: <ctx>-card
description: Use only when the load or save skill picks <ctx>: holds <what it is>'s card. Never typed by the user.
---
# <ctx> card
ctx <ctx> · <3-5 words> · repo <owner>/<repo> (or none) · state HANDOFF.md · also load: — · load extras: — · save extras: —.
<Project> only: no other project's state, rules or memory.
```
