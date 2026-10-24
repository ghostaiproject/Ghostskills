---
name: do
description: Run a task by controlling the user's PC (computer use). Only when the user types /do <task>. Asks y/n/auto before taking control.
disable-model-invocation: true
---

The user typed `/do` with this task: $ARGUMENTS

Steps:

1. If auto mode is already on in this session (the user answered `auto` earlier and has not typed `lock`), skip to step 2 without asking. Otherwise do NOT touch the screen yet. Reply with exactly one short line and wait:

   `Control your PC for: "<task in a few words>"? (y/n/auto)`

2. If the user's next message is `y` (or `yes`): load the `anthropic-skills:computer-use` skill, then do the task with computer use. A hook unlocks the computer-use tools only after that `y`.
   If it is `auto` (or `a`): same as `y`, but the PC stays unlocked for the rest of this session: later `/do` tasks start without the question, and most in-task confirms are skipped. It ends when the user types `lock`.
   If it is `n` or anything else: say "Cancelled." and do not use computer use.

3. While working:
   - Use the fewest steps. Prefer the terminal or file tools if they are faster than clicking.
   - Before anything irreversible (send, delete, buy, submit, post) stop and ask `Confirm <action>? (y/n)`. A `y` keeps the PC unlocked; any other reply locks it again. In auto mode, skip this for send, submit and post; still ask for delete and buy.
   - Never enter passwords, payment details or personal IDs.

4. When done, give a 1–3 line summary of what changed. Stop using computer use.

If no task was given after `/do`, ask: `What should I do on your PC?`
