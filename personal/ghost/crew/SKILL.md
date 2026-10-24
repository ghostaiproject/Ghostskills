---
name: crew
description: Use when the user sends /crew, or a task needs an image/wallpaper/draw/render (Gemini), a calc/convert/sum/clean (local Python) or an opinion/second opinion (ChatGPT): free pre-pass via crew.py, Claude answers last.
---
# /crew: free second brains, Claude answers last
`crew` = `python $HOME/.claude/skills/crew/crew.py`. One Bash call per brain, ≤10 lines back. Never paste screenshots, pages or long replies.

## Route (keywords; nothing matches → no crew, 0 cost)
- image · wallpaper · draw · render → `crew gemini "<scene>" [--fmt 16:9|1:1|9:16] [--style film|anime|gouache|ink]` (ceig rules, art + size check, ≤3 reprompts inside)
- calc · convert · sum · clean → `crew calc "<python expr>"` · `"convert 5 km to mi"` · `"sum 1,2,3"` · `"clean <file>"` · `--code "<python>"`
- opinion · second opinion → `crew gpt "<question>"` (optional brain)
- Several groups → one call each, own sub-prompt. Unsure → `crew route "<request>"`.

## Read the output
- `OK …` → use it. Image → path only; SendUserFile it. Read it once only if a line says `NOT verified: art check`.
- `(cache: nothing called)` → repeat, free.
- `skipped <brain>: <why>` → go on without it, repeat that line to the user.
- `NOT verified: …` → repeat it in the reply.
- Exit 3 / `→ sign in` → one line to the user, run `crew login <brain>` in the background (opens the sign-in page; user signs in, closes the window), wait, then rerun.
- `weak image after 3 reprompts` → say what is off; never present it as final.

## /crew menu (no argument)
Show `1 status · 2 sign in · 3 clear cache`, user replies a number:
1 → `crew status` · 2 → ask `1 gemini · 2 gpt`, then `crew login <brain>` (background) · 3 → `crew clear`.

## Rules
- Retries live in crew.py (selectors, reload, fresh tab, window mode, other browser, rebuilt profile). Still skipped → rerun once with `--fresh`, then do it yourself; hand work to the user only for sign-in, 2FA or approvals.
- Never type passwords or codes. No API keys, no paid APIs.
- Setup once: `pip install playwright` → `python -m playwright install chromium`.
