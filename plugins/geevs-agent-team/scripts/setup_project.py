"""Opt a project into the agent team: permission rules, hook marker, CLAUDE.md section. Idempotent."""

import json
import pathlib
import sys

VERSION = "1.0.0"
RULES = {
    "deny": [
        "Bash(git push --force *)",
        "Bash(git push -f *)",
        "Bash(git push --force-with-lease *)",
        "Edit(**/.env)",
        "Edit(**/.env.local)",
        "Edit(**/.env.production)",
        "Edit(**/*.pem)",
        "Edit(**/id_rsa)",
        "Edit(**/id_ed25519)",
    ],
    "ask": [
        "Bash(git push *)",
        "Bash(git reset --hard *)",
        "Bash(gh pr merge *)",
        "Bash(vercel deploy *)",
        "Bash(vercel --prod *)",
        "Bash(vercel promote *)",
        "Bash(npm publish *)",
        "Bash(pnpm publish *)",
        "Bash(yarn publish *)",
        "Bash(terraform apply *)",
        "Bash(terraform destroy *)",
        "Bash(kubectl apply *)",
        "Bash(kubectl delete *)",
        "Bash(helm install *)",
        "Bash(helm upgrade *)",
    ],
}
CLAUDE_HEADING = "## Agent team"
CLAUDE_SECTION = f"""
{CLAUDE_HEADING}
- Non-trivial work goes through `/geevs-agent-team:deliver <goal>`.
- Run state lives in `.agents/runs/<slug>/`: `spec.md`, `progress.json`, `review.md`, `research/`.
- A criterion passes only with recorded evidence from the reviewer.
- Pushes, merges, deploys and publishes ask a human; see `.claude/settings.json`.
"""
IGNORE_LINE = ".agents/active-run"


def merge_rules(settings):
    permissions = settings.setdefault("permissions", {})
    added = 0
    for kind, rules in RULES.items():
        current = permissions.setdefault(kind, [])
        for rule in rules:
            if rule not in current:
                current.append(rule)
                added += 1
    return added


def write_settings(root):
    path = root / ".claude/settings.json"
    path.parent.mkdir(exist_ok=True)
    settings = json.loads(path.read_text()) if path.exists() else {}
    added = merge_rules(settings)
    path.write_text(json.dumps(settings, indent=2) + "\n")
    return added


def append_once(path, marker, text):
    current = path.read_text() if path.exists() else ""
    if marker in current:
        return False
    path.write_text(current.rstrip("\n") + ("\n" if current else "") + text.lstrip("\n"))
    return True


def setup(root):
    root = pathlib.Path(root)
    added = write_settings(root)
    (root / ".claude/agent-team.json").write_text(json.dumps({"version": VERSION}) + "\n")
    claude = append_once(root / "CLAUDE.md", CLAUDE_HEADING, CLAUDE_SECTION)
    ignore = append_once(root / ".gitignore", IGNORE_LINE, IGNORE_LINE + "\n")
    return {"rules_added": added, "claude_md_updated": claude, "gitignore_updated": ignore}


if __name__ == "__main__":
    print(json.dumps(setup(sys.argv[1] if len(sys.argv) > 1 else ".")))
