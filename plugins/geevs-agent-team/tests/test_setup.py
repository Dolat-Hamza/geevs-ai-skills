import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import setup_project  # noqa: E402


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


class Setup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        git(self.root, "init", "-q", "-b", "main")

    def tearDown(self):
        self.tmp.cleanup()

    def settings(self):
        return json.loads((self.root / setup_project.SETTINGS).read_text())

    def test_writes_local_settings_and_marker(self):
        result = setup_project.setup(self.root)
        self.assertGreater(result["rules_added"], 0)
        self.assertIn("Bash(git push *)", self.settings()["permissions"]["ask"])
        self.assertTrue((self.root / setup_project.MARKER).exists())

    def test_leaves_no_tracked_changes(self):
        setup_project.setup(self.root)
        self.assertEqual(git(self.root, "status", "--porcelain"), "")

    def test_marker_survives_branch_switch(self):
        (self.root / "a.txt").write_text("a")
        git(self.root, "add", ".")
        git(self.root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
        setup_project.setup(self.root)
        git(self.root, "checkout", "-q", "-b", "feat/x")
        git(self.root, "checkout", "-q", "main")
        self.assertTrue((self.root / setup_project.MARKER).exists())

    def test_idempotent(self):
        setup_project.setup(self.root)
        second = setup_project.setup(self.root)
        self.assertEqual((second["rules_added"], second["excludes_added"]), (0, 0))

    def test_keeps_existing_local_settings(self):
        (self.root / ".claude").mkdir()
        existing = {"model": "sonnet", "permissions": {"allow": ["Bash(npm test)"], "ask": ["Bash(git push *)"]}}
        (self.root / setup_project.SETTINGS).write_text(json.dumps(existing))
        setup_project.setup(self.root)
        settings = self.settings()
        self.assertEqual(settings["model"], "sonnet")
        self.assertEqual(settings["permissions"]["allow"], ["Bash(npm test)"])
        self.assertEqual(settings["permissions"]["ask"].count("Bash(git push *)"), 1)

    def test_works_outside_git(self):
        with tempfile.TemporaryDirectory() as plain:
            result = setup_project.setup(plain)
            self.assertEqual(result["excludes_added"], 0)
            self.assertTrue((pathlib.Path(plain) / setup_project.MARKER).exists())


if __name__ == "__main__":
    unittest.main()
