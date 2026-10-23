# New project

1. Copy this folder to `projects/<ctx>/` (`<ctx>` = short lowercase name).
2. Make two skill folders, `<ctx>-load` and `<ctx>-save`, each with a SKILL.md like the ones below.
3. Project rules (build steps, style, extra commands) → a third skill, `<ctx>-dev`, and name it in "also load".
4. Add a row to the root README, then upload the new folders as skills on claude.ai.

`<ctx>-load/SKILL.md`:
```
---
name: <ctx>-load
description: Use when the user sends /<ctx>-load or /load <ctx>: starts a chat on <what it is>.
---
# /<ctx>-load
Card: ctx <ctx> · repo <owner>/<repo> (or none) · state HANDOFF.md · also load: — · save extras: —.
Invoke skill `load` with this card; follow its steps. <Project> only: no other project's state, rules or memory.
```

`<ctx>-save/SKILL.md`:
```
---
name: <ctx>-save
description: Use when the user sends /<ctx>-save: saves <what it is> state back.
---
# /<ctx>-save
Card: ctx <ctx> · repo <owner>/<repo> (or none) · state HANDOFF.md · save extras: —.
Invoke skill `save` with this card; follow its steps. <Project> only.
```
