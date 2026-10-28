import io
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import guard  # noqa: E402

REPO = "/work/repo"
FAKE_AWS_KEY = "AKIA" + "ABCDEFGHIJKLMNOP"
FAKE_PEM_HEADER = "-----BEGIN " + "PRIVATE KEY-----"


def branch_for(mapping):
    return lambda cwd: mapping.get(cwd, "feat/x")


def run(kind, tool_input, branches=None, cwd="/session"):
    event = json.dumps({"tool_input": tool_input, "cwd": cwd})
    with (
        mock.patch("sys.stdin", io.StringIO(event)),
        mock.patch.object(guard, "current_branch", side_effect=branch_for(branches or {})),
        mock.patch("sys.stderr", io.StringIO()),
    ):
        return guard.main(["guard.py", kind])


def blocked(cmd, branches=None, cwd="/session"):
    return run("bash", {"command": cmd}, branches, cwd) == guard.BLOCK


class BashGuardBlocks(unittest.TestCase):
    def test_dangerous_commands(self):
        for cmd in [
            "git push --force origin feat/x",
            "git push -f origin feat/x",
            "git push origin +feat/x",
            "git push origin main",
            "git push origin HEAD:master",
            "git reset --hard HEAD~1",
            "vercel deploy --prod",
            "terraform apply",
            "kubectl apply -f k.yaml",
            "helm upgrade app ./chart",
            "npm publish",
            "rm -rf ~",
            "rm -fr /",
            "gh pr merge 3",
            "sudo git push --force origin x",
            "FOO=1 npm publish",
        ]:
            with self.subTest(cmd=cmd):
                self.assertTrue(blocked(cmd))

    def test_commit_on_default_branch(self):
        self.assertTrue(blocked("git commit -m x", {"/session": "main"}))

    def test_commit_after_cd_into_repo_on_main(self):
        self.assertTrue(blocked(f"cd {REPO} && git commit -m x", {REPO: "main"}))

    def test_commit_with_git_c_on_main(self):
        self.assertTrue(blocked(f"git -C {REPO} commit -m x", {REPO: "main"}))

    def test_relative_cd_resolves_from_cwd(self):
        self.assertTrue(blocked("cd repo; git commit -m x", {REPO: "main"}, cwd="/work"))

    def test_push_without_refspec_from_main(self):
        self.assertTrue(blocked("git push", {"/session": "main"}))

    def test_bash_redirect_to_secret_file(self):
        for cmd in ["echo KEY=1 > .env", "cat <<EOF > .env.local\nKEY=1\nEOF", "printf x | tee config/id_rsa"]:
            with self.subTest(cmd=cmd):
                self.assertTrue(blocked(cmd))

    def test_bash_secret_content(self):
        self.assertTrue(blocked(f"echo {FAKE_AWS_KEY} > notes.txt"))

    def test_unbalanced_quotes_fail_closed(self):
        self.assertTrue(blocked('echo "unterminated'))


class BashGuardAllows(unittest.TestCase):
    def test_normal_commands(self):
        for cmd in [
            "git push -u origin feat/x",
            "git status",
            "npm test",
            "rm -rf build",
            "vercel deploy",
            "npm install",
            "terraform plan",
            "gh pr create --fill",
            "echo KEY= > .env.example",
        ]:
            with self.subTest(cmd=cmd):
                self.assertFalse(blocked(cmd))

    def test_commit_on_feature_branch(self):
        self.assertFalse(blocked(f"cd {REPO} && git commit -m x", {REPO: "feat/x"}))

    def test_quoted_text_is_not_a_command(self):
        self.assertFalse(blocked('echo "git push --force origin main" >> report.md'))

    def test_heredoc_body_is_not_a_command(self):
        cmd = "cat >> pilot-log.md <<'EOF'\n| 4 | hook blocked git push --force | rm -rf ~ |\nEOF"
        self.assertFalse(blocked(cmd))

    def test_commit_message_mentioning_main(self):
        self.assertFalse(blocked('git commit -m "Do not push to main"'))


class WriteGuard(unittest.TestCase):
    def test_blocks_secret_files(self):
        for path in ["/p/.env", "/p/.env.local", "/p/id_rsa", "/p/server.pem"]:
            with self.subTest(path=path):
                self.assertEqual(run("write", {"file_path": path, "content": "x"}), guard.BLOCK)

    def test_allows_example_files(self):
        self.assertEqual(run("write", {"file_path": "/p/.env.example", "content": "KEY="}), guard.ALLOW)

    def test_blocks_secret_content(self):
        self.assertEqual(run("write", {"file_path": "/p/a.ts", "content": FAKE_AWS_KEY}), guard.BLOCK)
        self.assertEqual(run("write", {"file_path": "/p/a.ts", "new_string": FAKE_PEM_HEADER}), guard.BLOCK)

    def test_allows_normal_content(self):
        self.assertEqual(run("write", {"file_path": "/p/a.ts", "content": "export const x = 1"}), guard.ALLOW)


class Unknown(unittest.TestCase):
    def test_unknown_mode_allows(self):
        self.assertEqual(guard.main(["guard.py", "other"]), guard.ALLOW)


if __name__ == "__main__":
    unittest.main()
