# Ghostskills

My Claude skills, written to be token-light. Rules: [CONVENTIONS.md](CONVENTIONS.md).

| Skill | Commands | Does |
|---|---|---|
| [load](skills/load/SKILL.md) | `/load <ctx>` | Loads a project's state; holds the **context table** |
| [loadlist](skills/loadlist/SKILL.md) | `/loadlist` | Lists every ctx you can load |
| [save](skills/save/SKILL.md) | `/save` | Saves the current ctx's state back |
| [grocrun-dev](skills/grocrun-dev/SKILL.md) | `/ship` `/sync` `/cmds` `/list` | GrocRun Android app dev rules |
| [link](skills/link/SKILL.md) | `/link <msg>` | Phone chat → Claude task on my laptop |
| [next](skills/next/SKILL.md) | (auto) | After computer actions: ask next step, y/n or numbered |

New project = new row in the context table in `skills/load/SKILL.md`.
