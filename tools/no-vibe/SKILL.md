---
name: no-vibe
description: Code that doesn't read as vibe-coded/AI-generated. Use when writing or reviewing code, and for "/no-vibe" or "clean up AI-looking code" in an existing repo (safe, behavior-preserving).
---

# no-vibe: code a senior dev would sign

## Write (every new line)
- Names → domain words (`cartTotal`, `pairedDevices`), never `data/result/response/item/value`; no `x_data/x_info/x_obj` twins.
- Comments → only the why of non-obvious logic. No docstrings on trivial functions, no "# Check if…", no `# Step 1/2` (make functions).
- No stock TODOs ("add error handling", "consider edge cases", "placeholder"). Do it or file it.
- Errors → catch the specific failure where it's expected; never `except: pass` / bare `catch{}` / log-and-continue on auth, signature, money paths (fail closed).
- Size → match the job: no factory/DI/ABC/repository layer for a small script; one pattern per concern across the repo (reuse the existing one).
- Deps → stdlib/existing deps first; every new package: real, maintained, needed (check registry + version docs; no guessed APIs).
- Security → TLS verify on, parameterized SQL, CORS allowlist (not `*`), secrets from env/store, no placeholder creds, logs without PII/raw `{e}` dumps.
- Delete what you replaced: dead code, unused imports, orphaned helpers.
- Explain every line you ship.

## Clean existing code (never break it)
1. Baseline: run the project check/tests → must be green first; note the count.
2. Scan: `python <this folder>/scan.py <repo>` → file:line hits per signal (≤60 lines).
3. Triage each hit: real problem / fixture or false positive (leave a one-line reason) / taste only (skip).
4. Fix in small batches, one signal per commit, behavior-preserving only: rename (all refs), drop dead code/comments, narrow excepts. No logic rewrites.
5. Auth, payments, crypto, data deletion → don't auto-fix: list them for the user.
6. After each batch: same check/tests → same green count, + app/browser smoke where UI is touched. Red → revert that batch.
7. Ship per the project's PR flow. Report: 1 line per signal → fixed n · skipped n (why).
