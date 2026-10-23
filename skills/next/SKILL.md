---
name: next
description: Use after any action Claude takes on the user's computer (Chrome, built-in browser, desktop apps, its files): end the reply with one short next-step question.
---
# Next-step question (computer work)
After any action on the user's computer → last line of the reply is one question on what to do next there.
- Single path → yes/no: `Next: <action>? (y/n)`
- Several options → numbered, user replies with the number:
  `Next?` then `1) <option>` `2) <option>` … (max 4, short labels)
- Options = concrete actions on what's open now (page, app, file), not generic help.
- Reply `y` → do it. `n` → stop, ask nothing more. Number → do that option.
- Keep it last, one block, no extra text after it.
