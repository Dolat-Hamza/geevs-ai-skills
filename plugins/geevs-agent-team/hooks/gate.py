"""Hooks for project clones that opted in via .claude/agent-team.local.json. Everything else passes through."""

import json
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cost  # noqa: E402

MARKER = ".claude/agent-team.local.json"
DEFAULT_BRANCHES = {"main", "master"}
GIT_COMMIT = re.compile(r"\bgit\b[^;&|\n]*\bcommit\b")
SECRET = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsk-(live|ant|proj)-[A-Za-z0-9_-]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{30,}"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
]
OPEN_PHASES = ("build", "review")


def project_root(cwd):
    for folder in [pathlib.Path(cwd), *pathlib.Path(cwd).parents]:
        if (folder / MARKER).exists():
            return folder
    return None


def branch(cwd):
    try:
        out = subprocess.run(
            ["git", "symbolic-ref", "--quiet", "--short", "HEAD"], cwd=cwd, capture_output=True, text=True, timeout=5
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return out.stdout.strip()


def active_run(root):
    """Return (run folder, state) of the open run, or (None, None)."""
    active = root / ".agents/active-run"
    if not active.exists():
        return None, None
    folder = root / ".agents/runs" / active.read_text().strip()
    if not (folder / "progress.json").exists():
        return None, None
    return folder, json.loads((folder / "progress.json").read_text())


def append_spend(folder, entry):
    with open(folder / "spend.jsonl", "a", encoding="utf-8") as log:
        log.write(json.dumps(entry) + "\n")


def decide(decision, reason):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }


def on_bash(event, _root):
    command = event.get("tool_input", {}).get("command", "")
    if GIT_COMMIT.search(command) and branch(event.get("cwd", ".")) in DEFAULT_BRANCHES:
        return decide("ask", "Commit on the default branch. Approve only if intended; agents work on branches.")
    return None


def written_text(tool_input):
    parts = [tool_input.get("content", ""), tool_input.get("new_string", "")]
    parts += [edit.get("new_string", "") for edit in tool_input.get("edits", [])]
    return "\n".join(p for p in parts if p)


def on_write(event, _root):
    if any(p.search(written_text(event.get("tool_input", {}))) for p in SECRET):
        return decide("deny", "Content looks like a credential. Read it from the environment instead.")
    return None


def on_agent_start(event, root):
    folder, state = active_run(root)
    if state is None:
        return None
    main = round(cost.transcript_usd(event.get("transcript_path", ""), state.get("created_at", "")), 4)
    append_spend(folder, {"main_usd": main})
    total = cost.run_total(folder / "spend.jsonl")
    budget = state.get("budget_usd")
    if budget is not None and total >= budget:
        reason = f"Run has spent about ${total:.2f} of its ${budget:.2f} budget. "
        reason += "Approve to continue, or stop and raise the budget with run_state budget."
        return decide("ask", reason)
    return None


def on_agent_done(event, root):
    folder, state = active_run(root)
    if state is None:
        return None
    response = event.get("tool_response")
    response = response if isinstance(response, dict) else {}
    usage, model = response.get("usage"), response.get("resolvedModel")
    usd = round(cost.usage_usd(usage, model), 4) if usage else None
    append_spend(folder, {"agent": event.get("tool_input", {}).get("subagent_type"), "model": model, "usd": usd})
    return None


def on_stop(_event, root):
    _, state = active_run(root)
    if state is None:
        return None
    open_ids = [c["id"] for c in state.get("criteria", []) if not c.get("passes")]
    if state.get("phase") in OPEN_PHASES and open_ids:
        reason = f"Run is in {state['phase']} with unverified criteria: {', '.join(open_ids)}. "
        reason += "Finish review, or set phase to blocked with the reason."
        return {"decision": "block", "reason": reason}
    return None


PRE = {"Bash": on_bash, "Write": on_write, "Edit": on_write, "MultiEdit": on_write, "Agent": on_agent_start}
POST = {"Agent": on_agent_done}


def handle(event):
    root = project_root(event.get("cwd", "."))
    if root is None:
        return None
    kind = event.get("hook_event_name")
    if kind == "Stop":
        return on_stop(event, root)
    table = POST if kind == "PostToolUse" else PRE
    handler = table.get(event.get("tool_name", ""))
    return handler(event, root) if handler else None


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    result = handle(event)
    if result:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
