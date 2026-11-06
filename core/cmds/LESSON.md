# /lesson: share one general lesson or rule with the whole team (PR to Ghostskills)
1. Text: the user's words, else the lesson this session learned. One line, imperative, general (no project names, paths, people, secrets: the repo is public). Project-only → its LESSONS.md instead, stop.
2. Kind: a habit/fact → lesson (`team/lessons.md`); a must-follow rule → `-Rule` (`team/CLAUDE.md`). Already in either file → one line "already shared", stop.
3. Run: `powershell -ExecutionPolicy Bypass -File ~/Ghostskills/scripts/lesson.ps1 -Text "<line>" [-Rule]` (clone elsewhere → `dir` in ~/.claude/ghostskills.json).
4. Report one line with the PR link. Owner of the repo → merge once CI passes; others → the owner merges. Every session start pulls main, so it reaches every PC.
