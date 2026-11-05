---
name: autoloop
description: The working loop injected on every prompt by a UserPromptSubmit hook (plan, act, verify, ship, wrap up). Never typed by the user.
---
# autoloop
Runs by itself: `~/.claude/hooks/autoloop.ps1` on `UserPromptSubmit` in `~/.claude/settings.json`. Source of truth = `autoloop.ps1` next to this file.

Loop, every prompt:
1. Plan → `update_plan` with the whole plan on the first tool call.
2. Act → batch independent calls; grep/sed over whole-file reads.
3. Verify → run it in the real app or browser; never call it done from the code alone.
4. Ship → commit, push, PR, merge once CI is green.
5. Wrap up → recap + one next-step question; every open choice in one picker.

Short or chatty prompts only get line 1, so the cost per prompt stays tiny.

- Change it → edit `autoloop.ps1` here, copy to `~/.claude/hooks/autoloop.ps1`, PR per the skill sync rule.
- Turn it off → drop the autoloop entry from `hooks.UserPromptSubmit` in `~/.claude/settings.json`.
