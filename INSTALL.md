# Install ghostaiproject (for Claude Code reading this)
The user typed "install ghostaiproject" (or similar): set up the team's shared brain on this Windows PC: skills, team rules, lessons, auto-mode trust for ghostaiproject repos, and their own private setup repo.
Do every step yourself; the user only signs in. Never edit `~/.claude/settings.json` or trust text yourself: the installer the user runs does that.

1. Tools: `git --version`, `gh --version`. Missing → `winget install --id Git.Git -e` / `winget install --id GitHub.cli -e`, then tell the user to reopen Claude Code (PATH) and say "install ghostaiproject" again.
2. GitHub: `gh auth status`. Not signed in → ask the user to run `gh auth login` (GitHub.com, HTTPS, login with a web browser) in a terminal and say when done. Then `gh auth setup-git`.
3. Projects: ask in ONE picker which project cards they want (folders in `projects/` of github.com/ghostaiproject/Ghostskills, except `_template` and `skills`: list them with `gh api repos/ghostaiproject/Ghostskills/contents/projects -q ".[].name"`). None is fine.
4. Give the user this ONE line to run themselves (Run button, or `!` + the line in Claude Code), with their picks filled in:
   ```
   irm https://raw.githubusercontent.com/ghostaiproject/Ghostskills/main/scripts/install.ps1 -OutFile $env:TEMP\gs.ps1; powershell -ExecutionPolicy Bypass -File $env:TEMP\gs.ps1 -Config auto -Projects <a,b>
   ```
   It clones `~/Ghostskills`, links the skills, imports `team/CLAUDE.md` + `team/lessons.md` into `~/.claude/CLAUDE.md`, merges `team/settings.json` (allow rules, hooks, trust), creates their private `<login>/claude-config` with this PC's setup, and adds a SessionStart hook that pulls main every session.
5. Check: `~/.claude/ghostskills.json` exists, `~/.claude/CLAUDE.md` has the two `@.../team/...` lines, `gh repo view <login>/claude-config` works. Something failed → read the output, fix, rerun the line (safe to rerun).
6. Tell them: restart Claude Code, then `/load`. Lessons for everyone → `/lesson` (opens a PR; the owner, ghostaiproject, approves). Write access → ask ghostaiproject for a collaborator invite; without it PRs come from a fork.
