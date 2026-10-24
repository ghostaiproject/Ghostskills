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


if __name__ == "__main__":
    unittest.main()
