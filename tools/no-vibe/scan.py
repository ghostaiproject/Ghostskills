"""Scan a repo for vibe-coded / AI-generated code signals. Read-only.
usage: python scan.py <repo> [--max 60]  -> per signal: count + first file:line hits
"""
import re
import sys
from pathlib import Path

EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".kt", ".java", ".rs", ".go", ".cs", ".ps1", ".sh"}
SKIP = {"node_modules", ".git", "dist", "build", "target", "out", ".venv", "venv", "__pycache__", "gen", ".gradle", "vendor"}

SIGNALS = {
    "stock TODO": r"(TODO|FIXME)[:\s].*(add error handling|edge case|placeholder|implement (this|later)|replace this)",
    "silent catch": r"except\s*(Exception)?\s*:\s*pass\b|catch\s*(\([^)]*\))?\s*\{\s*\}",
    "broad except": r"except\s+Exception\b|except\s*:",
    "step headers": r"(#|//)\s*Step\s*\d+\b",
    "what-comment": r"(#|//)\s*(Check if|Initialize|Loop through|Return the|Get the|Set the|Create a new)\b",
    "generic name": r"\b(const|let|var)?\s*(result|data|response|value|item|temp|obj)\s*=(?!=)",
    "tls off": r"verify\s*=\s*False|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED",
    "sql format": r"(execute|query)\s*\(\s*f[\"']|(SELECT|INSERT|UPDATE|DELETE)\b[^\n]*[\"']\s*(%|\+)\s*\w",
    "cors *": r"Access-Control-Allow-Origin[\"']?\s*[:,]\s*[\"']\*|allow_origins\s*=\s*\[\s*[\"']\*",
    "placeholder cred": r"(admin123|password123|changeme|replace_this|your[_-]?api[_-]?key|test_key)",
    "error dump log": r"(logger|logging|console)\.(error|log)\(\s*f?[\"'`](Error|error)[:\s]*[{$]",
}


def files(root):
    for p in root.rglob("*"):
        if p.suffix in EXTS and p.is_file() and not SKIP.intersection(p.parts) and p.stat().st_size < 400_000:
            yield p


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    cap = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 60
    pats = {k: re.compile(v, re.I) for k, v in SIGNALS.items()}
    hits = {k: [] for k in SIGNALS}
    for f in files(root):
        try:
            lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            if len(line) > 400:  # minified/bundled
                continue
            for k, p in pats.items():
                if p.search(line):
                    hits[k].append(f"{f.relative_to(root).as_posix()}:{n}")
    out = []
    for k, h in hits.items():
        if h:
            out.append(f"{k}: {len(h)}  " + " ".join(h[:4]) + (" ..." if len(h) > 4 else ""))
    print("\n".join(out[:cap]) or "clean: no signals")


if __name__ == "__main__":
    main()
