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
import proofs  # noqa: E402
import run_state  # noqa: E402

TEST_COMMAND = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
CALC_TEST = """import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from calc import double

class Double(unittest.TestCase):
    def test_three(self):
        self.assertEqual(double(3), {expected})
"""


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def commit(repo, message):
    git(repo, "add", ".")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message)


class Repo(unittest.TestCase):
    """A main branch with a bug in calc.double, and a branch that works on it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        (self.repo / "calc.py").write_text("def double(x):\n    return x + 2\n")
        (self.repo / "README.md").write_text("Minimum fee 2.00 GBP.\nFees round half-up to 2 decimals.\n")
        commit(self.repo, "init")
        git(self.repo, "checkout", "-q", "-b", "fix/double")

    def tearDown(self):
        self.tmp.cleanup()

    def add_test(self, expected=6):
        (self.repo / "tests").mkdir(exist_ok=True)
        (self.repo / "tests/test_calc.py").write_text(CALC_TEST.format(expected=expected))

    def fix(self):
        (self.repo / "calc.py").write_text("def double(x):\n    return x * 2\n")


class RedGreen(Repo):
    def test_failing_then_passing_test_is_proof(self):
        self.add_test()
        self.fix()
        commit(self.repo, "fix")
        result = proofs.red_green(self.repo, TEST_COMMAND)
        self.assertTrue(result["ok"], result)
        self.assertNotEqual(result["red_exit"], 0)
        self.assertEqual(result["green_exit"], 0)
        self.assertEqual(result["tests"], ["tests/test_calc.py"])

    def test_test_that_passes_on_base_is_not_proof(self):
        self.add_test(expected=5)
        commit(self.repo, "weak test")
        result = proofs.red_green(self.repo, TEST_COMMAND)
        self.assertFalse(result["ok"])
        self.assertIn("pass on the base", result["reason"])

    def test_failing_on_branch_is_not_proof(self):
        self.add_test()
        commit(self.repo, "test only")
        self.assertIn("fail on the branch", proofs.red_green(self.repo, TEST_COMMAND)["reason"])

    def test_no_test_changes_is_not_proof(self):
        self.fix()
        commit(self.repo, "fix without test")
        self.assertIn("no test files", proofs.red_green(self.repo, TEST_COMMAND)["reason"])

    def test_scratch_worktree_removed(self):
        self.add_test()
        self.fix()
        commit(self.repo, "fix")
        proofs.red_green(self.repo, TEST_COMMAND)
        listed = subprocess.run(["git", "-C", str(self.repo), "worktree", "list"], capture_output=True, text=True)
        self.assertEqual(len(listed.stdout.strip().splitlines()), 1)


class Needs(unittest.TestCase):
    def test_classifies_changed_files(self):
        self.assertEqual(proofs.needs(["calc.py", "docs/a.md"]), {"code": True, "docs": True})
        self.assertEqual(proofs.needs(["docs/note.md"]), {"code": False, "docs": True})
        self.assertEqual(proofs.needs(["logo.png"]), {"code": False, "docs": False})

    def test_test_path_patterns(self):
        for path in ("tests/test_a.py", "src/__tests__/a.js", "a.test.ts", "pkg/a_test.go", "test_a.py"):
            with self.subTest(path=path):
                self.assertTrue(proofs.TEST_PATH.search(path))
        self.assertIsNone(proofs.TEST_PATH.search("contest.py"))


class Claims(Repo):
    def write_note(self, text):
        (self.repo / "note.md").write_text(text)
        commit(self.repo, "note")

    def claim(self, **overrides):
        base = {
            "file": "note.md",
            "claim": "minimum fee is 2.00 GBP",
            "source": "README.md:1",
            "quote": "Minimum fee 2.00 GBP.",
        }
        return {**base, **overrides}

    def test_traced_claims_pass(self):
        self.write_note("# Fees\n\n1. The minimum fee is 2.00 GBP.\n")
        result = proofs.traced(self.repo, [self.claim()])
        self.assertTrue(result["ok"], result)

    def test_quote_must_be_on_cited_line(self):
        self.write_note("The minimum fee is 2.00 GBP.\n")
        result = proofs.traced(self.repo, [self.claim(source="README.md:2")])
        self.assertIn("claim 1: quote not found at README.md:2", result["problems"])

    def test_out_of_range_line_is_not_found(self):
        self.write_note("The minimum fee is 2.00 GBP.\n")
        self.assertFalse(proofs.traced(self.repo, [self.claim(source="README.md:99")])["ok"])

    def test_claim_must_appear_in_document(self):
        self.write_note("Fees are low.\n")
        result = proofs.traced(self.repo, [self.claim()])
        self.assertIn("claim 1: text not found in note.md", result["problems"])

    def test_unsourced_number_flagged(self):
        self.write_note("The minimum fee is 2.00 GBP. Transfers settle in 3 days.\n")
        result = proofs.traced(self.repo, [self.claim()])
        self.assertIn("number 3 has no sourced claim", result["problems"])

    def live_note(self):
        """The customer note written in the 1.2.0 live test, with its README lines."""
        (self.repo / "README.md").write_text(
            "| under 1,000 | 1.0% |\nMinimum fee 2.00 GBP. Fees round half-up to 2 decimals.\n"
        )
        self.write_note(
            "Every transfer has a minimum fee of 2.00 GBP (README.md, line 2). For example, on a "
            "transfer of 100 GBP the rate is 1.0% (README.md, line 1), which would be 1.00 GBP, but "
            "that is below the minimum, so the fee is 2.00 GBP.\n"
        )

    def note_claims(self, **example):
        rate = {
            "file": "note.md",
            "claim": "on a transfer of 100 GBP the rate is 1.0% (README.md, line 1)",
            "source": "README.md:1",
            "quote": "| under 1,000 | 1.0% |",
        }
        derived = {
            "file": "note.md",
            "claim": "which would be 1.00 GBP",
            "source": "README.md:1",
            "quote": "| under 1,000 | 1.0% |",
        }
        minimum = {
            "file": "note.md",
            "claim": "minimum fee of 2.00 GBP (README.md, line 2)",
            "source": "README.md:2",
            "quote": "Minimum fee 2.00 GBP.",
        }
        return [{**rate, **example.get("rate", {})}, {**derived, **example.get("derived", {})}, minimum]

    def test_live_claims_without_calc_now_fail(self):
        self.live_note()
        problems = proofs.traced(self.repo, self.note_claims())["problems"]
        self.assertIn("claim 1: 100 not in the quote and no calc given", problems)
        self.assertIn("claim 2: 1.00 not in the quote and no calc given", problems)

    def test_given_input_and_calc_pass(self):
        self.live_note()
        claims = self.note_claims(rate={"given": [100]}, derived={"given": [100], "calc": "100 * 1.0 / 100"})
        self.assertTrue(proofs.traced(self.repo, claims)["ok"])

    def test_wrong_figure_caught_by_calc(self):
        self.live_note()
        (self.repo / "note.md").write_text((self.repo / "note.md").read_text().replace("1.00 GBP", "1.50 GBP"))
        commit(self.repo, "wrong figure")
        claims = self.note_claims(
            rate={"given": [100]},
            derived={"claim": "which would be 1.50 GBP", "given": [100], "calc": "100 * 1.0 / 100"},
        )
        self.assertIn("claim 2: 1.50 does not match calc result 1.0", proofs.traced(self.repo, claims)["problems"])

    def test_calc_cannot_smuggle_unquoted_numbers(self):
        self.live_note()
        claims = self.note_claims(rate={"given": [100]}, derived={"given": [100], "calc": "100 * 1.5 / 150 * 1"})
        problems = proofs.traced(self.repo, claims)["problems"]
        self.assertTrue(any("calc uses 1.5" in p for p in problems))

    def test_calc_rejects_code(self):
        self.live_note()
        claims = self.note_claims(rate={"given": [100]}, derived={"given": [100], "calc": "__import__('os')"})
        self.assertTrue(any("calc not valid" in p for p in proofs.traced(self.repo, claims)["problems"]))

    def test_no_claims_is_not_proof(self):
        self.write_note("Text.\n")
        self.assertFalse(proofs.traced(self.repo, [])["ok"])


def call(*argv):
    err = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        code = run_state.main(list(argv))
    return code, err.getvalue()


class CheckGate(Repo):
    """run_state check demands the proof that matches what the branch changed."""

    def setUp(self):
        super().setUp()
        self.old = os.getcwd()
        self.project = pathlib.Path(self.tmp.name) / "project"
        (self.project / ".agents").mkdir(parents=True)
        os.chdir(self.project)
        call("new", "r1", "x")
        spec = "## Acceptance criteria\n- [ ] AC1: double(3) is 6. Check: `python3 -m unittest`\n"
        pathlib.Path(".agents/runs/r1/spec.md").write_text(spec)
        call("criteria", "r1")

    def tearDown(self):
        os.chdir(self.old)
        super().tearDown()

    def review(self):
        call("tree", "r1", "save", str(self.repo))
        call("pass", "r1", "AC1", "unittest ok")
        return call("check", "r1")

    def test_code_change_needs_redgreen(self):
        self.add_test()
        self.fix()
        commit(self.repo, "fix")
        code, err = self.review()
        self.assertEqual(code, 1)
        self.assertIn("test-first", err)
        self.assertEqual(call("redgreen", "r1", str(self.repo), "--", *TEST_COMMAND)[0], 0)
        self.assertEqual(call("check", "r1")[0], 0)

    def test_new_commit_invalidates_proof(self):
        self.add_test()
        self.fix()
        commit(self.repo, "fix")
        self.review()
        call("redgreen", "r1", str(self.repo), "--", *TEST_COMMAND)
        (self.repo / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        commit(self.repo, "tweak")
        self.assertIn("out of date", call("check", "r1")[1])

    def test_doc_change_needs_claims(self):
        (self.repo / "note.md").write_text("The minimum fee is 2.00 GBP.\n")
        commit(self.repo, "note")
        self.assertIn("source tracing", self.review()[1])
        claims = pathlib.Path(self.tmp.name) / "claims.json"
        claims.write_text(
            json.dumps(
                [
                    {
                        "file": "note.md",
                        "claim": "minimum fee is 2.00 GBP",
                        "source": "README.md:1",
                        "quote": "Minimum fee 2.00 GBP.",
                    }
                ]
            )
        )
        self.assertEqual(call("claims", "r1", str(self.repo), str(claims))[0], 0)
        self.assertEqual(call("check", "r1")[0], 0)

    def test_failed_proof_reported_and_recorded(self):
        self.add_test(expected=5)
        commit(self.repo, "weak test")
        self.review()
        code, err = call("redgreen", "r1", str(self.repo), "--", *TEST_COMMAND)
        self.assertEqual(code, 1)
        self.assertIn("pass on the base", err)
        state = json.loads(pathlib.Path(".agents/runs/r1/progress.json").read_text())
        self.assertFalse(state["proofs"]["code"]["ok"])

    def test_review_round_clears_proofs(self):
        self.add_test()
        self.fix()
        commit(self.repo, "fix")
        self.review()
        call("redgreen", "r1", str(self.repo), "--", *TEST_COMMAND)
        call("review-round", "r1")
        state = json.loads(pathlib.Path(".agents/runs/r1/progress.json").read_text())
        self.assertNotIn("proofs", state)


class CriteriaRule(unittest.TestCase):
    def setUp(self):
        self.old = os.getcwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)
        pathlib.Path(".agents").mkdir()
        call("new", "r1", "x")

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def criteria(self, text):
        pathlib.Path(".agents/runs/r1/spec.md").write_text(text)
        return call("criteria", "r1")

    def test_criterion_without_check_rejected(self):
        code, err = self.criteria("- [ ] AC1: it works\n- [ ] AC2: passes. Check: `make test`\n")
        self.assertEqual(code, 1)
        self.assertIn("AC1", err)
        self.assertNotIn("AC2", err)

    def test_comparison_allowed_placeholder_rejected(self):
        self.assertEqual(self.criteria("- [ ] AC1: fast. Check: `python3 bench.py` shows ms < 50\n")[0], 0)
        self.assertEqual(self.criteria("- [ ] AC1: works. Check: `run_state redgreen r1 <worktree>`\n")[0], 1)

    def test_untouched_template_rejected(self):
        self.assertEqual(call("criteria", "r1")[0], 1)


if __name__ == "__main__":
    unittest.main()
