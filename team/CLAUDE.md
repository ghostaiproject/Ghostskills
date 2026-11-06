# Ghostaiproject team rules (shared; imported from ~/.claude/CLAUDE.md, kept fresh by the SessionStart pull)
Your own CLAUDE.md lines and memory win over these. Change a rule for everyone → `/lesson` (opens a PR).

# Token rules
- Every call re-reads the whole context. One task per session: once a task ships, or the context passes ~150K, `/switch` to a fresh session with a short brief.
- Batch independent tool calls in one message; each extra round trip re-reads everything.
- Big files (>300 lines): `grep -n` / `sed -n a,bp` the part you need; never Read a whole big file to edit a few spots.
- Subagents only when the user asks, with a tight scope and a ≤30-line report.
- Never dump base64 or minified blobs: cut long lines before printing (`awk 'length>400{print NR": [long "length"]";next}1'`).
- Artifacts with images: keep page source and images in a folder that persists, so the next session edits locally instead of running Artifact read.
- Reads: ≤120 lines per `sed -n` / Bash output. "Output too large / saved to tool-results" → grep that file, never Read it back.
- New code: no single Write over ~250 lines; split into module files, wire each in, rerun the project's check/test before calling it done.
- Big pages: build from small parts (css/js/html + a build script) and edit the parts.
- Browser checks: `read_page`/`get_page_text`/JS first; screenshots at `scale` 0.5, one at the end. Bundle predictable steps into ONE `browser_batch`.
- Several screenshots → tile them into ONE labeled JPEG contact sheet; read and send only that.
- Reports: compact, 1 line per point, no recap of what was done. Choices: AskUserQuestion picker, not a prose question.

# Skill sync rule
- Skills live in `~/.claude/skills/<name>/` (linked by the installer) and the Ghostskills clone (`~/Ghostskills`: core/, projects/, tools/, personal/<you>/).
- Edit the repo copy on a branch (CONVENTIONS.md, `scripts/check.ps1 -Pack`) → commit → push → PR into main (no push rights → from a fork) → one-line report with the PR link.
- Merge gate: only the owner, ghostaiproject, approves and merges PRs into ghostaiproject repos. You are the owner (`gh api user -q .login` = ghostaiproject) → merge once CI passes, then `git switch main` + `git pull`. Anyone else → never merge, never push to main; the owner gets it in the CER-01 app's Approvals tab.
- Stop and ask only if checks/CI fail, there are conflicts, or the repo has unrelated uncommitted work.

# Standing rules
- Retry-first: if something fails, rethink and retry several different ways before showing an error or handing over manual steps. The user only does sign-in, 2FA and approvals.
- After any action on the user's computer, end with a next-step question.
- Finish work with a quick, short recap.
- Example names stay neutral and impersonal: Chalet, Condo, Bureau.
- Never mix one project's state, rules or memory with another's.
- Questions: bundle every open decision into ONE AskUserQuestion picker (up to 4 questions, short labels, a Recommended option).
- Never write your own settings, permissions or auto-mode trust: those ship in `team/settings.json` and the user's installer applies them.
- Install scripts that touch settings or trust: the user runs them; Claude only checks the result · ghostaiproject 2026-11-06
