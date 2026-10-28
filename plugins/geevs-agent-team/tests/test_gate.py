import contextlib
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "hooks"))
import gate  # noqa: E402

FAKE_AWS_KEY = "AKIA" + "ABCDEFGHIJKLMNOP"


def run(event):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), unittest.mock.patch("sys.stdin", io.StringIO(json.dumps(event))):
        code = gate.main()
    text = out.getvalue().strip()
    return code, json.loads(text) if text else None


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class Project(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        git(self.root, "init", "-q", "-b", "main")
        (self.root / ".claude").mkdir()
        (self.root / ".claude/agent-team.local.json").write_text("{}")

    def tearDown(self):
        self.tmp.cleanup()

    def bash(self, command, cwd=None):
        return run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "cwd": str(cwd or self.root),
                "tool_input": {"command": command},
            }
        )[1]


class CommitOnDefault(Project):
    def test_commit_on_main_asks(self):
        result = self.bash("git commit -m x")
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "ask")

    def test_compound_commit_asks(self):
        self.assertIsNotNone(self.bash("cd . && git add . && git commit -m x"))

    def test_commit_from_subdirectory_asks(self):
        sub = self.root / "src"
        sub.mkdir()
        self.assertIsNotNone(self.bash("git commit -m x", cwd=sub))

    def test_commit_on_feature_branch_passes(self):
        git(self.root, "checkout", "-q", "-b", "feat/x")
        self.assertIsNone(self.bash("git commit -m x"))

    def test_other_commands_pass(self):
        self.assertIsNone(self.bash("git status"))


class Secrets(Project):
    def write(self, tool, tool_input):
        return run(
            {"hook_event_name": "PreToolUse", "tool_name": tool, "cwd": str(self.root), "tool_input": tool_input}
        )[1]

    def test_credential_content_denied(self):
        for tool, field in (("Write", "content"), ("Edit", "new_string")):
            with self.subTest(tool=tool):
                result = self.write(tool, {"file_path": "a.py", field: FAKE_AWS_KEY})
                self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_multiedit_scanned(self):
        result = self.write("MultiEdit", {"file_path": "a.py", "edits": [{"new_string": FAKE_AWS_KEY}]})
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_normal_content_passes(self):
        self.assertIsNone(self.write("Write", {"file_path": "a.py", "content": "x = 1"}))


class StopGate(Project):
    def start_run(self, phase, passes):
        run_dir = self.root / ".agents/runs/r1"
        run_dir.mkdir(parents=True)
        (self.root / ".agents/active-run").write_text("r1\n")
        criteria = [{"id": "AC1", "passes": passes}]
        (run_dir / "progress.json").write_text(json.dumps({"phase": phase, "criteria": criteria}))

    def stop(self):
        return run({"hook_event_name": "Stop", "cwd": str(self.root)})[1]

    def test_blocks_open_build_with_failing_criteria(self):
        self.start_run("build", False)
        result = self.stop()
        self.assertEqual(result["decision"], "block")
        self.assertIn("AC1", result["reason"])

    def test_allows_when_all_pass(self):
        self.start_run("review", True)
        self.assertIsNone(self.stop())

    def test_allows_waiting_phases(self):
        for phase in ("spec", "approved", "release", "blocked"):
            with self.subTest(phase=phase):
                self.tearDown()
                self.setUp()
                self.start_run(phase, False)
                self.assertIsNone(self.stop())

    def test_no_active_run_allows(self):
        self.assertIsNone(self.stop())

    def test_second_stop_attempt_allowed(self):
        self.start_run("build", False)
        result = run({"hook_event_name": "Stop", "cwd": str(self.root), "stop_hook_active": True})[1]
        self.assertIsNone(result)


class Budget(Project):
    def setUp(self):
        super().setUp()
        self.run_dir = self.root / ".agents/runs/r1"
        self.run_dir.mkdir(parents=True)
        (self.root / ".agents/active-run").write_text("r1\n")
        self.transcript = self.root / "t.jsonl"
        self.transcript.write_text("")

    def state(self, budget):
        state = {"phase": "build", "criteria": [], "created_at": "2026-10-29T00:00:00.000Z", "budget_usd": budget}
        (self.run_dir / "progress.json").write_text(json.dumps(state))

    def spawn(self):
        return run(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Agent",
                "cwd": str(self.root),
                "transcript_path": str(self.transcript),
                "tool_input": {"subagent_type": "builder"},
            }
        )[1]

    def finish(self, agent_id, usage):
        transcript = self.root / f"{agent_id}.jsonl"
        message = {"id": "m1", "model": "claude-sonnet-5-5", "usage": usage}
        transcript.write_text(json.dumps({"type": "assistant", "message": message}) + "\n")
        return run(
            {
                "hook_event_name": "SubagentStop",
                "cwd": str(self.root),
                "agent_id": agent_id,
                "agent_type": "geevs-agent-team:builder",
                "agent_transcript_path": str(transcript),
            }
        )[1]

    def log(self):
        return [json.loads(line) for line in (self.run_dir / "spend.jsonl").read_text().splitlines()]

    def test_subagent_spend_logged_from_its_transcript(self):
        self.state(5.0)
        usage = {
            "input_tokens": 1000,
            "cache_creation_input_tokens": 2000,
            "cache_read_input_tokens": 10000,
            "output_tokens": 500,
        }
        self.assertIsNone(self.finish("a1", usage))
        self.assertEqual(
            self.log()[-1],
            {"agent_id": "a1", "agent": "geevs-agent-team:builder", "models": ["claude-sonnet-5-5"], "usd": 0.013},
        )

    def test_missing_agent_transcript_logs_zero(self):
        self.state(5.0)
        run(
            {
                "hook_event_name": "SubagentStop",
                "cwd": str(self.root),
                "agent_id": "a2",
                "agent_transcript_path": "/no/such/file",
            }
        )
        self.assertEqual(self.log()[-1]["usd"], 0)

    def test_spawn_under_budget_passes(self):
        self.state(5.0)
        self.assertIsNone(self.spawn())
        self.assertEqual(self.log()[-1], {"main_usd": 0.0})

    def test_spawn_over_budget_asks(self):
        self.state(1.0)
        (self.run_dir / "spend.jsonl").write_text(json.dumps({"agent": "x", "usd": 1.5}) + "\n")
        result = self.spawn()
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "ask")
        self.assertIn("$1.50", result["hookSpecificOutput"]["permissionDecisionReason"])

    def test_no_active_run_ignores_agents(self):
        (self.root / ".agents/active-run").unlink()
        self.assertIsNone(self.spawn())
        self.assertFalse((self.run_dir / "spend.jsonl").exists())


class NotOptedIn(unittest.TestCase):
    def test_everything_passes_without_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            git(tmp, "init", "-q", "-b", "main")
            events = [
                {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git commit -m x"}},
                {"hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"content": FAKE_AWS_KEY}},
                {"hook_event_name": "Stop"},
            ]
            for event in events:
                with self.subTest(event=event["hook_event_name"]):
                    self.assertIsNone(run({**event, "cwd": tmp})[1])

    def test_bad_json_passes(self):
        with unittest.mock.patch("sys.stdin", io.StringIO("not json")):
            self.assertEqual(gate.main(), 0)


if __name__ == "__main__":
    unittest.main()
