import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import chat_check  # noqa: E402

TEST_COMMAND = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
CALC = "def double(n):\n    return n * {factor}\n"
CALC_TEST = """import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from calc import double

class Double(unittest.TestCase):
    def test_three(self):
        self.assertEqual(double(3), {expected})
"""


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class Tests(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        self.before, self.after = self.root / "before", self.root / "after"
        write(self.before / "calc.py", CALC.format(factor=3))
        write(self.after / "calc.py", CALC.format(factor=2))

    def test_fix_with_new_test_passes(self):
        write(self.after / "tests/test_calc.py", CALC_TEST.format(expected=6))
        result = chat_check.tests(self.before, self.after, TEST_COMMAND)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["tests"], ["tests/test_calc.py"])

    def test_test_that_passes_on_original_fails(self):
        write(self.after / "calc.py", CALC.format(factor=3))
        write(self.after / "tests/test_calc.py", CALC_TEST.format(expected=9))
        result = chat_check.tests(self.before, self.after, TEST_COMMAND)
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "new tests pass on the original")

    def test_unchanged_tests_do_not_count(self):
        write(self.before / "tests/test_calc.py", CALC_TEST.format(expected=6))
        write(self.after / "tests/test_calc.py", CALC_TEST.format(expected=6))
        result = chat_check.tests(self.before, self.after, TEST_COMMAND)
        self.assertFalse(result["ok"])
        self.assertIn("no new or changed test", result["reason"])

    def test_broken_fix_fails(self):
        write(self.after / "calc.py", CALC.format(factor=4))
        write(self.after / "tests/test_calc.py", CALC_TEST.format(expected=6))
        result = chat_check.tests(self.before, self.after, TEST_COMMAND)
        self.assertEqual(result["reason"], "tests fail on the fix")


class Claims(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        write(self.root / "sources/prices.md", "Fee\nUnder 1,000 GBP the fee is 1.0%.\n")
        write(self.root / "work/faq.md", "On 250.50 GBP the fee is 2.51 GBP.\n")
        self.claim = {
            "file": "work/faq.md",
            "claim": "On 250.50 GBP the fee is 2.51 GBP.",
            "source": "sources/prices.md:2",
            "quote": "Under 1,000 GBP the fee is 1.0%.",
            "given": ["250.50"],
            "calc": "2.51",
        }

    def check(self, claims):
        path = self.root / "claims.json"
        path.write_text(json.dumps(claims))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = chat_check.main(["claims", str(self.root), str(path)])
        return code, json.loads(out.getvalue())

    def test_wrong_calc_is_rejected(self):
        self.claim["calc"] = "250.50 * 1.0 / 100"
        code, result = self.check([self.claim])
        self.assertEqual(code, 1)
        self.assertTrue(any("does not match calc result" in p for p in result["problems"]))

    def test_rounded_figure_needs_its_own_given(self):
        self.claim["given"] = ["250.50", "2.51"]
        del self.claim["calc"]
        code, result = self.check([self.claim])
        self.assertEqual(code, 0, result)

    def test_misquoted_source_fails(self):
        self.claim["quote"] = "Under 1,000 GBP the fee is 2.0%."
        self.claim["given"] = ["250.50", "2.51"]
        code, result = self.check([self.claim])
        self.assertEqual(code, 1)
        self.assertIn("claim 1: quote not found at sources/prices.md:2", result["problems"])

    def test_rounding_is_recomputed(self):
        self.claim["calc"] = "round(250.50 * 1.0 / 100, 2)"
        code, result = self.check([self.claim])
        self.assertEqual(code, 0, result)

    def test_wrong_rounding_is_caught(self):
        write(self.root / "work/faq.md", "On 250.50 GBP the fee is 2.50 GBP.\n")
        self.claim["claim"] = "On 250.50 GBP the fee is 2.50 GBP."
        self.claim["calc"] = "round(250.50 * 1.0 / 100, 2)"
        code, result = self.check([self.claim])
        self.assertIn("claim 1: 2.50 does not match calc result 2.51", result["problems"])

    def test_minimum_fee_by_max(self):
        write(self.root / "sources/prices.md", "Fee\nUnder 1,000 GBP the fee is 1.0%, minimum fee 2.00 GBP.\n")
        write(self.root / "work/faq.md", "On 150.00 GBP the fee is 2.00 GBP.\n")
        self.claim.update(
            claim="On 150.00 GBP the fee is 2.00 GBP.",
            quote="Under 1,000 GBP the fee is 1.0%, minimum fee 2.00 GBP.",
            given=["150.00"],
            calc="max(round(150.00 * 1.0 / 100, 2), 2.00)",
        )
        code, result = self.check([self.claim])
        self.assertEqual(code, 0, result)

    def test_quotes_from_two_lines(self):
        write(self.root / "sources/prices.md", "Under 1,000 GBP the fee is 1.0%.\nOther\nMinimum fee 2.00 GBP.\n")
        write(self.root / "work/faq.md", "On 150.00 GBP the fee is 2.00 GBP.\n")
        self.claim.update(
            claim="On 150.00 GBP the fee is 2.00 GBP.",
            source="sources/prices.md:1,3",
            quote=["Under 1,000 GBP the fee is 1.0%.", "Minimum fee 2.00 GBP."],
            given="150.00",
            calc="max(round(150.00 * 1.0 / 100, 2), 2.00)",
        )
        code, result = self.check([self.claim])
        self.assertEqual(code, 0, result)
        self.claim["quote"] = ["Under 1,000 GBP the fee is 1.0%.", "Other"]
        self.claim["source"] = "sources/prices.md:1"
        code, result = self.check([self.claim])
        self.assertIn("claim 1: quote not found at sources/prices.md:1", result["problems"])

    def test_other_functions_are_rejected(self):
        self.claim["calc"] = "abs(2.51)"
        code, result = self.check([self.claim])
        self.assertTrue(any("calc not valid" in p for p in result["problems"]))

    def test_empty_list_fails(self):
        code, result = self.check([])
        self.assertEqual(code, 1)


class Cli(unittest.TestCase):
    def test_tests_needs_a_command(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            chat_check.main(["tests", "a", "b", "--"])


if __name__ == "__main__":
    unittest.main()
