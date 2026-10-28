import io
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import guard  # noqa: E402


def run(kind, tool_input, branch="feat/x"):
    event = json.dumps({"tool_input": tool_input, "cwd": "."})
    with (
        mock.patch("sys.stdin", io.StringIO(event)),
        mock.patch.object(guard, "current_branch", return_value=branch),
        mock.patch("sys.stderr", io.StringIO()),
    ):
        return guard.main(["guard.py", kind])


class BashGuard(unittest.TestCase):
    def blocked(self, cmd, branch="feat/x"):
        return run("bash", {"command": cmd}, branch) == guard.BLOCK

    def test_blocks_dangerous(self):
        for cmd in [
            "git push --force origin feat/x",
            "git push origin main",
            "git reset --hard HEAD~1",
            "vercel deploy --prod",
            "terraform apply",
            "npm publish",
            "rm -rf ~",
            "gh pr merge 3",
        ]:
            with self.subTest(cmd=cmd):
                self.assertTrue(self.blocked(cmd))

    def test_allows_normal(self):
        for cmd in ["git push -u origin feat/x", "git status", "npm test", "rm -rf build", "vercel deploy"]:
            with self.subTest(cmd=cmd):
                self.assertFalse(self.blocked(cmd))

    def test_commit_depends_on_branch(self):
        self.assertTrue(self.blocked("git commit -m x", branch="main"))
        self.assertFalse(self.blocked("git commit -m x", branch="feat/x"))


class WriteGuard(unittest.TestCase):
    def test_blocks_secret_files(self):
        for path in ["/p/.env", "/p/.env.local", "/p/id_rsa", "/p/server.pem"]:
            with self.subTest(path=path):
                self.assertEqual(run("write", {"file_path": path, "content": "x"}), guard.BLOCK)

    def test_allows_example_files(self):
        self.assertEqual(run("write", {"file_path": "/p/.env.example", "content": "KEY="}), guard.ALLOW)

    def test_blocks_secret_content(self):
        key = "AKIA" + "ABCDEFGHIJKLMNOP"
        self.assertEqual(run("write", {"file_path": "/p/a.ts", "content": key}), guard.BLOCK)
        self.assertEqual(
            run("write", {"file_path": "/p/a.ts", "new_string": "-----BEGIN PRIVATE KEY-----"}), guard.BLOCK
        )

    def test_allows_normal_content(self):
        self.assertEqual(run("write", {"file_path": "/p/a.ts", "content": "export const x = 1"}), guard.ALLOW)


class Unknown(unittest.TestCase):
    def test_unknown_mode_allows(self):
        self.assertEqual(guard.main(["guard.py", "other"]), guard.ALLOW)


if __name__ == "__main__":
    unittest.main()
