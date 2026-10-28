"""PreToolUse guard enforcing LAWS.md hard rules. Exit 2 blocks the call."""

import json
import re
import subprocess
import sys

BLOCK = 2
ALLOW = 0
DEFAULT_BRANCHES = {"main", "master"}

BASH_RULES = [
    (r"\bgit\s+push\b.*(--force\b|-f\b|--force-with-lease\b)", "LAWS 3.1: force push is not allowed."),
    (r"\bgit\s+push\b.*\b(main|master)\b", "LAWS 3.1: push to the default branch is not allowed. Open a PR."),
    (r"\bgit\s+reset\s+--hard\b", "LAWS 3.4: hard reset discards work. Ask a human."),
    (r"\bvercel\b.*--prod\b", "LAWS 3.2: production deploys are human actions."),
    (
        r"\b(kubectl\s+apply|terraform\s+apply|helm\s+(install|upgrade))\b",
        "LAWS 3.2: infrastructure changes are human actions.",
    ),
    (r"\b(npm|pnpm|yarn)\s+publish\b", "LAWS 3.2: publishing packages is a human action."),
    (
        r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?\s+(/|~|\$HOME)(\s|$)",
        "LAWS 3.4: recursive delete of a root or home path is blocked.",
    ),
    (r"\b(gh\s+pr\s+merge)\b", "LAWS 3.2: merging requires the approval the autonomy level sets. Ask a human."),
]

SECRET_FILE = re.compile(r"(^|/)(\.env(\.[\w-]+)?|id_rsa|id_ed25519|[\w-]+\.pem|[\w-]+\.key|credentials\.json)$")
EXAMPLE_FILE = re.compile(r"\.(example|sample|template)$")
SECRET_CONTENT = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsk-(live|ant|proj)-[A-Za-z0-9_-]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{30,}"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
]


def read_event():
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def deny(reason):
    print(reason, file=sys.stderr)
    return BLOCK


def current_branch(cwd):
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return out.stdout.strip()


def is_commit_on_default(command, cwd):
    if not re.search(r"\bgit\s+commit\b", command):
        return False
    return current_branch(cwd) in DEFAULT_BRANCHES


def check_bash(event):
    command = event.get("tool_input", {}).get("command", "")
    for pattern, reason in BASH_RULES:
        if re.search(pattern, command):
            return deny(reason)
    if is_commit_on_default(command, event.get("cwd")):
        return deny("LAWS 3.1: commit on the default branch is not allowed. Create a branch first.")
    return ALLOW


def written_text(tool_input):
    parts = [tool_input.get("content", ""), tool_input.get("new_string", "")]
    parts += [edit.get("new_string", "") for edit in tool_input.get("edits", [])]
    return "\n".join(p for p in parts if p)


def check_write(event):
    tool_input = event.get("tool_input", {})
    path = tool_input.get("file_path", "")
    if SECRET_FILE.search(path) and not EXAMPLE_FILE.search(path):
        return deny(f"LAWS 3.7: writing secret files is blocked ({path}). Use an .example file.")
    text = written_text(tool_input)
    if any(p.search(text) for p in SECRET_CONTENT):
        return deny("LAWS 3.7: content looks like a credential. Reference it from the environment instead.")
    return ALLOW


CHECKS = {"bash": check_bash, "write": check_write}


def main(argv):
    check = CHECKS.get(argv[1] if len(argv) > 1 else "")
    if check is None:
        return ALLOW
    return check(read_event())


if __name__ == "__main__":
    sys.exit(main(sys.argv))
