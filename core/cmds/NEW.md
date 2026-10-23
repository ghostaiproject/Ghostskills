# /new <ctx>
Works in the skills card's repo; this chat's ctx stays as it is.
1. Repo: cwd or a parent is it → use it. Else clone like load CLOUD (LOCAL: next to the current repo root). Fetch + rebase.
2. `<ctx>` = short lowercase; taken (projects/<ctx> exists) → one line, stop. Missing info → ask once: repo (owner/name or none), 3-5 words.
3. # = highest `(#N)` in projects/*/*-card descriptions + 1 (never reuse a number).
4. Write projects/<ctx>/<ctx>-card/SKILL.md from the block in projects/_template/README.md; add a row to README's projects table.
5. `scripts/check.ps1` (pwsh; Windows: powershell -ExecutionPolicy Bypass -File; FAIL → fix) → commit "Add <ctx> project" + trailers → push like /sync.
6. Banner "<ctx> added · #<n>"; one line: upload projects/<ctx>/<ctx>-card on claude.ai (`scripts/check.ps1 -Pack` makes the zip).
