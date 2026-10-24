# Write
Public repo → handles only; never real names, emails, addresses, towns, phone numbers, health, money, secrets or anyone's private info.
1. Repo: cwd or `../Ghostskills` is it → use it; else `git clone --depth 1` (LOCAL: next to the repo root; CLOUD: /home/claude/ghostskills, add_repo first). Fetch + rebase.
2. New line in the right section: `- <text> · <h> <yyyy-mm-dd>`. Same idea already there → append ` +<h>` (a vote), no new line. New ctx → new lore/lessons file.
3. Caps: CORE ≤1.5 KB, people/* ≤1 KB, others ≤4 KB. Over → drop that section's oldest single-vote lines.
4. `scripts/check.ps1` (Windows: `powershell -ExecutionPolicy Bypass -File`) → commit "cer-01: +<n> from <h>" + trailers → `git push origin HEAD:main`. Never force-push. Denied → `gh repo fork --remote`, push branch, `gh pr create`; no gh → print the lines for the owner.
5. One line: what merged + "live in everyone's next /load".
