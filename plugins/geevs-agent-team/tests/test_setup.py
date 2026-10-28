import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import setup_project  # noqa: E402


class Setup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def settings(self):
        return json.loads((self.root / ".claude/settings.json").read_text())

    def test_fresh_project(self):
        result = setup_project.setup(self.root)
        self.assertGreater(result["rules_added"], 0)
        self.assertIn("Bash(git push *)", self.settings()["permissions"]["ask"])
        self.assertTrue((self.root / ".claude/agent-team.json").exists())
        self.assertIn("## Agent team", (self.root / "CLAUDE.md").read_text())
        self.assertIn(".agents/active-run", (self.root / ".gitignore").read_text())

    def test_idempotent(self):
        setup_project.setup(self.root)
        second = setup_project.setup(self.root)
        self.assertEqual(second, {"rules_added": 0, "claude_md_updated": False, "gitignore_updated": False})
        self.assertEqual((self.root / "CLAUDE.md").read_text().count("## Agent team"), 1)

    def test_keeps_existing_settings_and_rules(self):
        (self.root / ".claude").mkdir()
        existing = {"model": "opus", "permissions": {"allow": ["Bash(npm test)"], "ask": ["Bash(git push *)"]}}
        (self.root / ".claude/settings.json").write_text(json.dumps(existing))
        setup_project.setup(self.root)
        settings = self.settings()
        self.assertEqual(settings["model"], "opus")
        self.assertEqual(settings["permissions"]["allow"], ["Bash(npm test)"])
        self.assertEqual(settings["permissions"]["ask"].count("Bash(git push *)"), 1)

    def test_appends_to_existing_claude_md(self):
        (self.root / "CLAUDE.md").write_text("# Project\nrules\n")
        setup_project.setup(self.root)
        text = (self.root / "CLAUDE.md").read_text()
        self.assertTrue(text.startswith("# Project\nrules\n"))
        self.assertIn("## Agent team", text)


if __name__ == "__main__":
    unittest.main()
