# Transaction bundle (ghostskills.transaction.v1)
```json
{"version":"ghostskills.transaction.v1","operation_id":"save-2026-10-24-a","operation_type":"save",
 "writes":[{"path":"wiki/<Page>.md","mode":"create","content":"..."},
           {"path":"wiki/index.md","mode":"replace","expected_sha256":"<current>","content":"..."}]}
```
- Paths only under `wiki/` or `.raw/`. `.raw/` is create-only. `replace` needs the file's current SHA-256 (`sha256sum`).
- save/ingest must also write `wiki/log.md` (new entry on top) and `wiki/hot.md` (≤500 words), and every new page must be linked from `wiki/index.md`.
- `CORE inspect bundle.json --vault V` → shows changes + `approval_sha256`; show the user the paths, then `CORE apply bundle.json --vault V --approved-plan-sha256 <hash>`.
- Exit 75 = conflict: re-read, rebuild, new operation_id. Interrupted → `CORE recover <operation_id>`. Same id only with the identical bundle.

# Page frontmatter
`type` (concept|entity|source|question|session|meta), `title`, `created`, `updated`, `status`, `tags`, `sources` (wikilinks). Flat YAML, block lists, dates YYYY-MM-DD. Wikilinks `[[Page]]`; cite sources, never invent quotes, locators or dates.
