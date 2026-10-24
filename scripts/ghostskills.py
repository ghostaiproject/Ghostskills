#!/usr/bin/env python3
"""Ghostskills vault core: init, lint, search, reviewed transactions, hooks. Stdlib only."""
import argparse, base64, fnmatch, hashlib, json, math, os, re, sys, tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TX = "ghostskills.transaction.v1"
CONFLICT = 75
META = {"index", "log", "hot", "overview"}
WIKILINK = re.compile(r"!?\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
sha = lambda b: hashlib.sha256(b).hexdigest()
canon = lambda o: json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


class Fail(Exception):
    def __init__(self, msg, code=2):
        super().__init__(msg)
        self.code = code


def out(o):
    getattr(sys.stdout, "reconfigure", lambda **k: None)(encoding="utf-8")
    print(json.dumps(o, indent=2, ensure_ascii=False))


# ---- vault + paths ----
def resolve_vault(arg):
    v = arg or os.environ.get("GHOSTSKILLS_VAULT")
    if not v:
        for d in [Path.cwd(), *Path.cwd().parents]:
            if (d / ".ghostskills.json").is_file():
                v = d
                break
    if not v:
        raise Fail("no vault: pass --vault, set GHOSTSKILLS_VAULT, or run inside one")
    v = Path(v).resolve()
    if v == ROOT or ROOT in v.parents:
        raise Fail("the plugin root is never a vault")
    if not (v / ".ghostskills.json").is_file():
        raise Fail(f"{v} is not an initialized vault (run init)")
    return v


def safe_target(vault, rel):
    p = Path(rel)
    if p.is_absolute() or ".." in p.parts or "\\" in rel or not p.parts:
        raise Fail(f"unsafe path: {rel}")
    if p.parts[0] not in ("wiki", ".raw"):
        raise Fail(f"writes allowed only under wiki/ and .raw/: {rel}")
    t = (vault / p).resolve()
    if vault not in t.parents:
        raise Fail(f"path escapes vault: {rel}")
    return t


def read_sha(p):
    return sha(p.read_bytes()) if p.is_file() else None


def atomic_write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".tmp-")
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    os.replace(tmp, p)


# ---- init ----
def cmd_init(a):
    vault = Path(a.path).resolve()
    if vault == ROOT or ROOT in vault.parents:
        raise Fail("the plugin root is never a vault")
    day = a.generated_at or date.today().isoformat()
    files = {}
    tpl = ROOT / "templates" / "vault"
    for f in sorted(p for p in tpl.rglob("*") if p.is_file()):
        files[f.relative_to(tpl).as_posix()] = f.read_text("utf-8").replace("{{generated_date}}", day[:10])
    files[".ghostskills.json"] = json.dumps({"version": 1, "created": day[:10]}, indent=2) + "\n"
    conflicts = [r for r in files if (vault / r).exists()]
    plan = {"vault": str(vault), "create": sorted(files), "conflicts": conflicts}
    plan_sha = sha(canon({"create": plan["create"], "files": files}))
    if not a.apply:
        return out({**plan, "approved_plan_sha256": plan_sha, "applied": False})
    if conflicts:
        raise Fail(f"refusing to overwrite: {conflicts}", CONFLICT)
    if a.approved_plan_sha256 != plan_sha:
        raise Fail("approved plan hash does not match the current plan")
    for r, c in files.items():
        atomic_write(vault / r, c.encode("utf-8"))
    out({**plan, "applied": True})


# ---- transactions ----
def load_bundle(path):
    b = json.loads(Path(path).read_text("utf-8"))
    if b.get("version") != TX:
        raise Fail(f"bundle version must be {TX}")
    for k in ("operation_id", "operation_type", "writes"):
        if k not in b:
            raise Fail(f"bundle missing {k}")
    if not re.fullmatch(r"[\w.-]{1,80}", b["operation_id"]):
        raise Fail("bad operation_id")
    return b


def inspect(vault, b):
    changed, problems, final, modes = [], [], {}, {}
    for w in b["writes"]:
        t = safe_target(vault, w["path"])
        cur, mode = read_sha(t), w.get("mode")
        if mode not in ("create", "replace"):
            raise Fail(f"{w['path']}: mode must be create or replace")
        if mode == "create" and cur is not None:
            problems.append(f"{w['path']}: exists, create refused")
        if mode == "replace":
            if w["path"].startswith(".raw/"):
                problems.append(f"{w['path']}: raw payloads are create-only")
            if cur is None or cur != w.get("expected_sha256"):
                problems.append(f"{w['path']}: expected hash does not match current file")
        final[w["path"]] = w["content"]
        modes[w["path"]] = mode
        changed.append({"path": w["path"], "mode": mode, "current_sha256": cur})
    wf = []
    if b["operation_type"] in ("save", "ingest"):
        for need in ("wiki/log.md", "wiki/hot.md"):
            if need not in final:
                wf.append(f"missing required write {need}")
        hot = final.get("wiki/hot.md")
        if hot is not None and len(hot.split()) > 500:
            wf.append("hot.md over 500 words")
        idx = vault / "wiki/index.md"
        index = final.get("wiki/index.md") or (idx.read_text("utf-8") if idx.is_file() else "")
        for p in final:
            if p.startswith("wiki/") and Path(p).stem.lower() not in META and modes[p] == "create":
                if f"[[{Path(p).stem}" not in index:
                    wf.append(f"{p}: new page not linked from wiki/index.md")
    plan = {"operation_id": b["operation_id"], "changed": changed, "storage_valid": not problems,
            "workflow_complete": not wf, "problems": problems + wf}
    plan["approval_sha256"] = sha(canon({"bundle": b, "current": [c["current_sha256"] for c in changed]}))
    return plan


def jdir(vault):
    return vault / ".vault-meta" / "journal"


def cmd_inspect(a):
    vault = resolve_vault(a.vault)
    out(inspect(vault, load_bundle(a.bundle)))


def rollback(vault, j):
    for rel, b64 in j["backups"].items():
        t = safe_target(vault, rel)
        if b64 is None:
            t.unlink(missing_ok=True)
        else:
            atomic_write(t, base64.b64decode(b64))


def cmd_apply(a):
    vault = resolve_vault(a.vault)
    b = load_bundle(a.bundle)
    bsha = sha(canon(b))
    jp = jdir(vault) / f"{b['operation_id']}.json"
    if jp.is_file():
        j = json.loads(jp.read_text("utf-8"))
        if j["state"] == "done" and j["bundle_sha256"] == bsha:
            return out({"operation_id": b["operation_id"], "applied": False, "note": "already applied"})
        raise Fail("operation id already used (run recover if interrupted, or use a new id)", CONFLICT)
    plan = inspect(vault, b)
    if not (plan["storage_valid"] and plan["workflow_complete"]):
        raise Fail("inspect failed: " + "; ".join(plan["problems"]), CONFLICT)
    if a.approved_plan_sha256 != plan["approval_sha256"]:
        raise Fail("approved plan hash does not match; re-inspect and review")
    backups = {}
    for w in b["writes"]:
        t = safe_target(vault, w["path"])
        backups[w["path"]] = base64.b64encode(t.read_bytes()).decode() if t.is_file() else None
    j = {"bundle_sha256": bsha, "state": "applying", "backups": backups}
    atomic_write(jp, canon(j))
    try:
        for w in b["writes"]:
            atomic_write(safe_target(vault, w["path"]), w["content"].encode("utf-8"))
    except Exception:
        rollback(vault, j)
        jp.unlink()
        raise
    j["state"] = "done"
    atomic_write(jp, canon(j))
    out({"operation_id": b["operation_id"], "applied": True, "paths": [w["path"] for w in b["writes"]]})


def cmd_recover(a):
    vault = resolve_vault(a.vault)
    jp = jdir(vault) / f"{a.operation_id}.json"
    if not jp.is_file():
        raise Fail("no such operation")
    j = json.loads(jp.read_text("utf-8"))
    if j["state"] == "done":
        return out({"operation_id": a.operation_id, "recovered": False, "note": "already complete"})
    rollback(vault, j)
    jp.unlink()
    out({"operation_id": a.operation_id, "recovered": True, "rolled_back": sorted(j["backups"])})


# ---- pages, lint, search ----
def pages(vault, excludes=()):
    res = {}
    for p in sorted((vault / "wiki").rglob("*.md")):
        parts = p.relative_to(vault).parts
        rel = "/".join(parts)
        if any(x.startswith(".") for x in parts) or any(fnmatch.fnmatch(rel, e) for e in excludes):
            continue
        res[rel] = p.read_text("utf-8")
    return res


def frontmatter(text):
    m = re.match(r"---\r?\n(.*?)\r?\n---", text, re.S)
    return dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M)) if m else {}


def strip_code(text):
    return re.sub(r"```.*?```|`[^`\n]*`", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)


def links(text):
    for i, line in enumerate(strip_code(text).splitlines(), 1):
        for m in WIKILINK.finditer(line):
            yield i, m.group(1).strip()


def resolve_link(target, stems, paths):
    t = target.lower().removesuffix(".md")
    if "/" in t:
        return [p for p in paths if p.lower().removesuffix(".md").endswith(t)]
    return stems.get(t, [])


def cmd_lint(a):
    vault = resolve_vault(a.vault)
    pg = pages(vault, a.exclude or [])
    stems = {}
    for p in pg:
        stems.setdefault(Path(p).stem.lower(), []).append(p)
    found, inbound = [], {p: 0 for p in pg}
    add = lambda rule, p, ln, d: found.append({"rule": rule, "path": p, "line": ln, "detail": d})
    for p, text in pg.items():
        fm = frontmatter(text)
        for k in ("type", "title"):
            if not fm.get(k):
                add("frontmatter", p, 1, f"missing {k}")
        for ln, tgt in links(text):
            hit = resolve_link(tgt, stems, pg)
            if not hit:
                add("dead-link", p, ln, tgt)
            elif len(hit) > 1:
                add("ambiguous-link", p, ln, f"{tgt} -> {hit}")
            elif hit[0] != p:
                inbound[hit[0]] += 1
        body = strip_code(re.sub(r"^---.*?---\r?\n", "", text, count=1, flags=re.S)).splitlines()
        for i, line in enumerate(body):
            if re.match(r"#{2,6} ", line):
                nxt = next((x for x in body[i + 1:] if x.strip()), "")
                if not nxt or re.match(r"#{1,6} ", nxt):
                    add("empty-section", p, i + 1, line.strip())
    for p, n in inbound.items():
        if n == 0 and Path(p).stem.lower() not in META:
            add("orphan", p, 1, "no inbound links")
    if "wiki/index.md" in pg:
        for ln, tgt in links(pg["wiki/index.md"]):
            if not resolve_link(tgt, stems, pg):
                add("stale-index", "wiki/index.md", ln, tgt)
    rep = {"pages": len(pg), "findings": found,
           "by_rule": {r: sum(f["rule"] == r for f in found) for r in sorted({f["rule"] for f in found})}}
    if a.format == "markdown":
        print(f"# Lint: {len(pg)} pages, {len(found)} findings")
        for f in found:
            print(f"- {f['path']}:{f['line']} [{f['rule']}] {f['detail']}")
    else:
        out(rep)
    return 1 if a.strict and found else 0


def cmd_search(a):
    vault = resolve_vault(a.vault)
    tok = lambda s: re.findall(r"\w+", s.lower())
    docs = {p: tok(t) for p, t in pages(vault).items()}
    q, n = set(tok(a.query)), len(docs)
    avg = sum(map(len, docs.values())) / max(n, 1)
    df = {w: sum(w in d for d in docs.values()) for w in q}
    res = []
    for p, d in docs.items():
        s = 0.0
        for w in q:
            f = d.count(w)
            if f:
                idf = math.log(1 + (n - df[w] + .5) / (df[w] + .5))
                s += idf * f * 2.2 / (f + 1.2 * (.25 + .75 * len(d) / avg))
        if s:
            res.append((s, p))
    out([{"path": p, "score": round(s, 3)} for s, p in sorted(res, reverse=True)[:a.top]])


# ---- hooks (default-off, bounded) ----
def cmd_hook(a):
    if a.event == "session-start" and os.environ.get("GHOSTSKILLS_SESSION_CONTEXT") == "1":
        try:
            hot = (resolve_vault(None) / "wiki/hot.md").read_text("utf-8")[:2000]
        except Fail:
            return 0
        getattr(sys.stdout, "reconfigure", lambda **k: None)(encoding="utf-8")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": hot}}))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ghostskills")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init")
    s.add_argument("path"); s.add_argument("--generated-at"); s.add_argument("--apply", action="store_true")
    s.add_argument("--approved-plan-sha256")
    for name in ("inspect", "apply"):
        s = sub.add_parser(name)
        s.add_argument("bundle"); s.add_argument("--vault")
        if name == "apply":
            s.add_argument("--approved-plan-sha256")
    s = sub.add_parser("recover")
    s.add_argument("operation_id"); s.add_argument("--vault")
    s = sub.add_parser("lint")
    s.add_argument("--vault"); s.add_argument("--format", choices=["json", "markdown"], default="json")
    s.add_argument("--strict", action="store_true"); s.add_argument("--exclude", action="append")
    s = sub.add_parser("search")
    s.add_argument("query"); s.add_argument("--vault"); s.add_argument("--top", type=int, default=5)
    s = sub.add_parser("hook")
    s.add_argument("event", choices=["session-start", "stop"])
    a = ap.parse_args(argv)
    try:
        return globals()["cmd_" + a.cmd](a) or 0
    except Fail as e:
        print(f"error: {e}", file=sys.stderr)
        return e.code


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
