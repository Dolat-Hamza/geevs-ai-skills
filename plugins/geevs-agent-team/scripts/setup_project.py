"""Opt a project clone into the agent team. Writes only untracked files, so it applies on every branch."""

import json
import pathlib
import subprocess
import sys

VERSION = "1.1.0"
SETTINGS = ".claude/settings.local.json"
MARKER = ".claude/agent-team.local.json"
EXCLUDES = (".agents/", SETTINGS, MARKER)
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
    path = root / SETTINGS
    path.parent.mkdir(exist_ok=True)
    settings = json.loads(path.read_text()) if path.exists() else {}
    added = merge_rules(settings)
    path.write_text(json.dumps(settings, indent=2) + "\n")
    return added


def exclude_file(root):
    out = subprocess.run(
        ["git", "rev-parse", "--git-path", "info/exclude"], cwd=root, capture_output=True, text=True, check=False
    )
    return (root / out.stdout.strip()) if out.returncode == 0 else None


def write_excludes(root):
    path = exclude_file(root)
    if path is None:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    current = path.read_text().splitlines() if path.exists() else []
    missing = [line for line in EXCLUDES if line not in current]
    if missing:
        path.write_text("\n".join([*current, *missing]) + "\n")
    return len(missing)


def setup(root):
    root = pathlib.Path(root).resolve()
    added = write_settings(root)
    (root / MARKER).write_text(json.dumps({"version": VERSION}) + "\n")
    return {"rules_added": added, "excludes_added": write_excludes(root), "settings": SETTINGS, "marker": MARKER}


if __name__ == "__main__":
    print(json.dumps(setup(sys.argv[1] if len(sys.argv) > 1 else ".")))
