import contextlib, io, json, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ghostskills as g


def run(*args):
    o, e = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
        code = g.main([str(a) for a in args])
    return code, o.getvalue(), e.getvalue()


class VaultTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.v = Path(self.tmp.name) / "vault"
        code, out, _ = run("init", self.v, "--generated-at", "2026-10-24")
        self.assertEqual(code, 0)
        h = json.loads(out)["approved_plan_sha256"]
        self.assertEqual(run("init", self.v, "--generated-at", "2026-10-24", "--apply",
                             "--approved-plan-sha256", h)[0], 0)

    def tearDown(self):
        self.tmp.cleanup()

    def bundle(self, name="b.json", op="save-1", page="Note"):
        idx = (self.v / "wiki/index.md").read_text("utf-8")
        w = [{"path": f"wiki/{page}.md", "mode": "create",
              "content": f"---\ntype: concept\ntitle: {page}\n---\n\n# {page}\n\nBody. See [[index]].\n"},
             {"path": "wiki/index.md", "mode": "replace", "expected_sha256": g.sha(idx.encode()),
              "content": idx + f"\n- [[{page}]]\n"},
             {"path": "wiki/log.md", "mode": "replace",
              "expected_sha256": g.read_sha(self.v / "wiki/log.md"),
              "content": (self.v / "wiki/log.md").read_text("utf-8") + "\n- saved\n"},
             {"path": "wiki/hot.md", "mode": "replace",
              "expected_sha256": g.read_sha(self.v / "wiki/hot.md"),
              "content": (self.v / "wiki/hot.md").read_text("utf-8") + "\nNew note.\n"}]
        p = Path(self.tmp.name) / name
        p.write_text(json.dumps({"version": g.TX, "operation_id": op, "operation_type": "save", "writes": w}))
        return p

    def test_init_refuses_overwrite_and_plugin_root(self):
        h = json.loads(run("init", self.v)[1])["approved_plan_sha256"]
        self.assertEqual(run("init", self.v, "--apply", "--approved-plan-sha256", h)[0], g.CONFLICT)
        self.assertEqual(run("init", g.ROOT / "x")[0], 2)

    def test_lint_clean_then_dead_link(self):
        self.assertEqual(json.loads(run("lint", "--vault", self.v)[1])["findings"], [])
        (self.v / "wiki/Bad.md").write_text("---\ntype: concept\n---\n# Bad\n[[Missing]]\n", "utf-8")
        rules = {f["rule"] for f in json.loads(run("lint", "--vault", self.v)[1])["findings"]}
        self.assertTrue({"dead-link", "orphan", "frontmatter"} <= rules)
        self.assertEqual(run("lint", "--vault", self.v, "--strict")[0], 1)

    def test_apply_needs_approved_hash_then_idempotent(self):
        b = self.bundle()
        plan = json.loads(run("inspect", b, "--vault", self.v)[1])
        self.assertTrue(plan["storage_valid"] and plan["workflow_complete"])
        self.assertEqual(run("apply", b, "--vault", self.v, "--approved-plan-sha256", "bad")[0], 2)
        self.assertEqual(run("apply", b, "--vault", self.v, "--approved-plan-sha256", plan["approval_sha256"])[0], 0)
        self.assertTrue((self.v / "wiki/Note.md").is_file())
        again = run("apply", b, "--vault", self.v, "--approved-plan-sha256", plan["approval_sha256"])
        self.assertEqual(again[0], 0)
        self.assertIn("already applied", again[1])
        self.assertEqual(run("search", "Body", "--vault", self.v)[0], 0)

    def test_stale_hash_and_unlinked_page_rejected(self):
        b = self.bundle()
        (self.v / "wiki/hot.md").write_text("changed", "utf-8")
        plan = json.loads(run("inspect", b, "--vault", self.v)[1])
        self.assertFalse(plan["storage_valid"])
        data = json.loads(self.bundle("c.json", "save-2", "Other").read_text())
        data["writes"] = [w for w in data["writes"] if w["path"] != "wiki/index.md"]
        c = Path(self.tmp.name) / "d.json"
        c.write_text(json.dumps(data))
        plan = json.loads(run("inspect", c, "--vault", self.v)[1])
        self.assertFalse(plan["workflow_complete"])

    def test_path_escape_and_raw_replace_blocked(self):
        for bad in ("../x.md", "/abs.md", "inbox/x.md", "wiki/../../x.md"):
            b = Path(self.tmp.name) / "e.json"
            b.write_text(json.dumps({"version": g.TX, "operation_id": "e", "operation_type": "other",
                                     "writes": [{"path": bad, "mode": "create", "content": "x"}]}))
            self.assertEqual(run("inspect", b, "--vault", self.v)[0], 2, bad)

    def test_recover_rolls_back_interrupted(self):
        t = self.v / "wiki/hot.md"
        before = t.read_bytes()
        j = {"bundle_sha256": "x", "state": "applying",
             "backups": {"wiki/hot.md": g.base64.b64encode(before).decode(), "wiki/New.md": None}}
        t.write_text("half", "utf-8")
        (self.v / "wiki/New.md").write_text("half", "utf-8")
        g.atomic_write(g.jdir(self.v) / "op.json", g.canon(j))
        self.assertEqual(run("recover", "op", "--vault", self.v)[0], 0)
        self.assertEqual(t.read_bytes(), before)
        self.assertFalse((self.v / "wiki/New.md").exists())


class HardeningTests(VaultTests):
    def raw_bundle(self, writes, op="h"):
        p = Path(self.tmp.name) / "h.json"
        p.write_text(json.dumps({"version": g.TX, "operation_id": op, "operation_type": "other", "writes": writes}))
        return p

    def test_malformed_bundles_fail_cleanly(self):
        p = Path(self.tmp.name) / "m.json"
        ok = {"version": g.TX, "operation_id": "a", "operation_type": "x"}
        for body in ("{nope", "[]", json.dumps({**ok, "writes": None}), json.dumps({**ok, "writes": []}),
                     json.dumps({**ok, "writes": [{"mode": "create", "content": "x"}]}),
                     json.dumps({**ok, "writes": [{"path": "wiki/a.md", "mode": "create"}]}),
                     json.dumps({**ok, "writes": [{"path": "wiki/a.md", "mode": "create", "content": 5}]})):
            p.write_text(body)
            self.assertEqual(run("inspect", p, "--vault", self.v)[0], 2, body)

    def test_windows_unsafe_paths_rejected(self):
        for bad in ("wiki", "wiki/", "wiki/CON.md", "wiki/a.md.", "wiki/ a.md", "wiki//x.md", "wiki/a.md:s",
                    "wiki/x\x00.md", ".raw", "wiki/./x.md"):
            b = self.raw_bundle([{"path": bad, "mode": "create", "content": "x"}])
            self.assertEqual(run("inspect", b, "--vault", self.v)[0], 2, bad)

    def test_duplicate_and_directory_targets_flagged(self):
        dup = [{"path": "wiki/D.md", "mode": "create", "content": "1"}] * 2
        self.assertFalse(json.loads(run("inspect", self.raw_bundle(dup), "--vault", self.v)[1])["storage_valid"])
        (self.v / "wiki/Dir.md").mkdir()
        one = [{"path": "wiki/Dir.md", "mode": "create", "content": "1"}]
        self.assertFalse(json.loads(run("inspect", self.raw_bundle(one), "--vault", self.v)[1])["storage_valid"])

    def test_lock_blocks_concurrent_apply_and_stale_lock_cleared(self):
        b = self.bundle()
        plan = json.loads(run("inspect", b, "--vault", self.v)[1])
        lock = self.v / ".vault-meta" / "lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text("1")
        self.assertEqual(run("apply", b, "--vault", self.v, "--approved-plan-sha256", plan["approval_sha256"])[0], g.CONFLICT)
        old = g.time.time() - g.LOCK_STALE - 5
        g.os.utime(lock, (old, old))
        self.assertEqual(run("apply", b, "--vault", self.v, "--approved-plan-sha256", plan["approval_sha256"])[0], 0)
        self.assertFalse(lock.exists())

    def test_write_failure_rolls_back_with_clean_error(self):
        hot = self.v / "wiki/hot.md"
        before = hot.read_bytes()
        b = self.bundle()
        plan = json.loads(run("inspect", b, "--vault", self.v)[1])
        real = g.atomic_write
        g.atomic_write = lambda p, d: (_ for _ in ()).throw(OSError("disk full")) if p.name == "hot.md" and b"New note" in d else real(p, d)
        try:
            code = run("apply", b, "--vault", self.v, "--approved-plan-sha256", plan["approval_sha256"])[0]
        finally:
            g.atomic_write = real
        self.assertEqual(code, 1)
        self.assertEqual(hot.read_bytes(), before)
        self.assertFalse((self.v / "wiki/Note.md").exists())

    def test_done_journal_drops_backups(self):
        b = self.bundle()
        plan = json.loads(run("inspect", b, "--vault", self.v)[1])
        run("apply", b, "--vault", self.v, "--approved-plan-sha256", plan["approval_sha256"])
        self.assertEqual(json.loads((g.jdir(self.v) / "save-1.json").read_text())["backups"], {})

    def test_bom_latin1_and_missing_wiki_do_not_crash(self):
        (self.v / "wiki/Bom.md").write_bytes(b"\xef\xbb\xbf---\ntype: x\ntitle: y\n---\n# Bom\n[[index]]\n")
        (self.v / "wiki/Lat.md").write_bytes("---\ntype: x\ntitle: y\n---\n# caf\xe9 [[index]]\n".encode("latin-1"))
        rep = json.loads(run("lint", "--vault", self.v)[1])
        self.assertFalse([f for f in rep["findings"] if f["path"].endswith("Bom.md") and f["rule"] == "frontmatter"])
        self.assertEqual(run("search", "caf", "--vault", self.v)[0], 0)
        import shutil
        shutil.rmtree(self.v / "wiki")
        self.assertEqual(run("lint", "--vault", self.v)[0], 2)

    def test_hook_never_crashes(self):
        import os
        os.environ["GHOSTSKILLS_SESSION_CONTEXT"] = "1"
        cwd = os.getcwd()
        os.chdir(self.v)
        try:
            (self.v / "wiki/hot.md").write_bytes(b"\xff\xfe bad")
            self.assertEqual(run("hook", "session-start")[0], 0)
            (self.v / "wiki/hot.md").unlink()
            self.assertEqual(run("hook", "session-start")[0], 0)
        finally:
            os.chdir(cwd)
            os.environ.pop("GHOSTSKILLS_SESSION_CONTEXT")

    def test_index_link_must_match_exactly_and_top_negative(self):
        b = self.bundle(page="Note")
        data = json.loads(b.read_text())
        for w in data["writes"]:
            if w["path"] == "wiki/index.md":
                w["content"] = w["content"].replace("[[Note]]", "[[Notebook]]")
        b.write_text(json.dumps(data))
        self.assertFalse(json.loads(run("inspect", b, "--vault", self.v)[1])["workflow_complete"])
        self.assertEqual(run("search", "index", "--vault", self.v, "--top", "-1")[0], 0)

    def test_path_links_resolve_by_suffix(self):
        (self.v / "wiki/sub").mkdir()
        (self.v / "wiki/sub/Deep.md").write_text("---\ntype: x\ntitle: d\n---\n# d\n[[index]]\n", "utf-8")
        (self.v / "wiki/Src.md").write_text("---\ntype: x\ntitle: s\n---\n# s\n[[sub/Deep]] [[nope/Deep]]\n", "utf-8")
        rep = json.loads(run("lint", "--vault", self.v)[1])
        dead = [f["detail"] for f in rep["findings"] if f["rule"] == "dead-link"]
        self.assertEqual(dead, ["nope/Deep"])


if __name__ == "__main__":
    unittest.main()
