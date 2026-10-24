# /cer
- No arg → banner "CER-01", line count per file, 3 random catchphrases, then `1 harvest · 2 add · 3 tidy · 4 show <file>` + "Number?".
- `add <kind> <text>` → WRITE.md. Kinds: catchphrase, quirk, never (CORE) · glossary · takes · lore/lessons + ctx.
- `+1 <words>` → vote on the matching line (WRITE.md step 2).
- `tidy` → merge duplicates (keep every handle); 2+ handles → promote into CORE; CORE over cap → single-handle lines go back to their file. Show moves, write after an ok.
- `show <file>` → print it, nothing else.
