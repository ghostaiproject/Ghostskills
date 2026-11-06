# claude-config (private)
Your own Claude Code setup, made by the Ghostskills installer: global CLAUDE.md, settings (allow rules, hooks, auto-mode trust), hook scripts, memory.
- New PC/account: run the Ghostskills install line with `-Config <you>/claude-config` → full apply (old files backed up).
- Every session start: `apply.ps1 -Update` adds only what the PC lacks.
- Changed a setting or memory? `powershell -ExecutionPolicy Bypass -File apply.ps1 -Capture` → copies the PC's setup here, commits, pushes.
Keep this repo private: memory and settings are personal.
