import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import run_state  # noqa: E402

SPEC = "# Goal\n\n## Acceptance criteria\n- [ ] AC1: fee for 1000 is 5.00\n- [ ] AC2: tests pass\n"


def call(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = run_state.main(list(argv))
    return code, out.getvalue().strip(), err.getvalue().strip()


class InTempDir(unittest.TestCase):
    def setUp(self):
        self.old = os.getcwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)
        pathlib.Path(".agents").mkdir()

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def start(self, spec=SPEC):
        self.assertEqual(call("new", "fee-fix", "Fix fee")[0], 0)
        pathlib.Path(".agents/runs/fee-fix/spec.md").write_text(spec)

    def state(self):
        return json.loads(pathlib.Path(".agents/runs/fee-fix/progress.json").read_text())


class Lifecycle(InTempDir):
    def test_new_creates_run_and_marks_active(self):
        self.start()
        self.assertEqual(pathlib.Path(".agents/active-run").read_text().strip(), "fee-fix")
        self.assertEqual(self.state()["phase"], "spec")

    def test_rejects_bad_slug_and_duplicate(self):
        self.assertEqual(call("new", "Bad Slug", "x")[0], 1)
        self.start()
        self.assertEqual(call("new", "fee-fix", "again")[0], 1)

    def test_criteria_parsed_from_spec(self):
        self.start()
        self.assertEqual(call("criteria", "fee-fix")[0], 0)
        self.assertEqual([c["id"] for c in self.state()["criteria"]], ["AC1", "AC2"])

    def test_empty_template_criteria_rejected(self):
        self.assertEqual(call("new", "fee-fix", "Fix fee")[0], 0)
        self.assertEqual(call("criteria", "fee-fix")[0], 1)

    def test_approval_requires_criteria(self):
        self.start()
        self.assertEqual(call("phase", "fee-fix", "approved")[0], 1)
        call("criteria", "fee-fix")
        self.assertEqual(call("phase", "fee-fix", "approved")[0], 0)

    def test_unknown_phase_rejected(self):
        self.start()
        self.assertEqual(call("phase", "fee-fix", "shipped")[0], 1)

    def test_done_clears_active_marker(self):
        self.start()
        call("phase", "fee-fix", "done")
        self.assertFalse(pathlib.Path(".agents/active-run").exists())


class Evidence(InTempDir):
    def setUp(self):
        super().setUp()
        self.start()
        call("criteria", "fee-fix")

    def test_pass_requires_evidence(self):
        self.assertEqual(call("pass", "fee-fix", "AC1", "  ")[0], 1)
        self.assertEqual(call("pass", "fee-fix", "AC1", "transfer_fee(1000) -> 5.00")[0], 0)
        self.assertEqual(self.state()["criteria"][0]["evidence"], "transfer_fee(1000) -> 5.00")

    def test_unknown_criterion_rejected(self):
        self.assertEqual(call("pass", "fee-fix", "AC9", "x")[0], 1)

    def test_check_fails_until_all_pass(self):
        call("pass", "fee-fix", "AC1", "ok")
        code, _, err = call("check", "fee-fix")
        self.assertEqual(code, 1)
        self.assertIn("AC2", err)
        call("pass", "fee-fix", "AC2", "ok")
        self.assertEqual(call("check", "fee-fix")[0], 0)

    def test_status_reports_failing(self):
        _, out, _ = call("status")
        self.assertEqual(json.loads(out)["failing"], ["AC1", "AC2"])


class BudgetState(InTempDir):
    def test_new_records_start_and_default_budget(self):
        self.start()
        state = self.state()
        self.assertEqual(state["budget_usd"], run_state.DEFAULT_BUDGET_USD)
        self.assertRegex(state["created_at"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.000Z$")

    def test_custom_and_raised_budget(self):
        self.assertEqual(call("new", "fee-fix", "x", "--budget-usd", "2")[0], 0)
        self.assertEqual(self.state()["budget_usd"], 2.0)
        self.assertEqual(call("budget", "fee-fix", "0")[0], 1)
        self.assertEqual(call("budget", "fee-fix", "8")[0], 0)
        self.assertEqual(self.state()["budget_usd"], 8.0)

    def test_status_reports_spend(self):
        self.start()
        pathlib.Path(".agents/runs/fee-fix/spend.jsonl").write_text('{"main_usd": 0.4}\n{"agent": "a", "usd": 0.6}\n')
        _, out, _ = call("status", "fee-fix")
        self.assertEqual(json.loads(out)["spend_usd"], 1.0)


class ReviewCap(InTempDir):
    def test_rounds_reset_evidence_and_block_after_cap(self):
        self.start()
        call("criteria", "fee-fix")
        for _ in range(run_state.MAX_REVIEW_ROUNDS):
            call("pass", "fee-fix", "AC1", "ok")
            self.assertEqual(call("review-round", "fee-fix")[0], 0)
            self.assertFalse(self.state()["criteria"][0]["passes"])
        code, _, err = call("review-round", "fee-fix")
        self.assertEqual(code, 1)
        self.assertIn("blocked", err)
        self.assertEqual(self.state()["phase"], "blocked")
        self.assertFalse(pathlib.Path(".agents/active-run").exists())


class TreeGuard(InTempDir):
    def setUp(self):
        super().setUp()
        self.repo = pathlib.Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        git = ["git", "-C", str(self.repo)]
        subprocess.run([*git, "init", "-q"], check=True)
        (self.repo / "a.txt").write_text("a")
        subprocess.run([*git, "add", "."], check=True)
        subprocess.run([*git, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"], check=True)
        self.start()

    def test_unchanged_tree_verifies(self):
        call("tree", "fee-fix", "save", str(self.repo))
        self.assertEqual(call("tree", "fee-fix", "verify", str(self.repo))[0], 0)

    def test_untracked_test_artifacts_ignored(self):
        call("tree", "fee-fix", "save", str(self.repo))
        (self.repo / "__pycache__").mkdir()
        self.assertEqual(call("tree", "fee-fix", "verify", str(self.repo))[0], 0)

    def test_commit_during_review_detected(self):
        call("tree", "fee-fix", "save", str(self.repo))
        (self.repo / "b.txt").write_text("b")
        git = ["git", "-C", str(self.repo)]
        subprocess.run([*git, "add", "."], check=True)
        subprocess.run([*git, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "b"], check=True)
        self.assertEqual(call("tree", "fee-fix", "verify", str(self.repo))[0], 1)

    def test_edit_during_review_detected(self):
        call("tree", "fee-fix", "save", str(self.repo))
        (self.repo / "a.txt").write_text("changed")
        self.assertEqual(call("tree", "fee-fix", "verify", str(self.repo))[0], 1)


if __name__ == "__main__":
    unittest.main()
