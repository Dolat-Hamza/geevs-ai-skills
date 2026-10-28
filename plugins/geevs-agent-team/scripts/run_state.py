"""Run state for /deliver: one folder per run, criteria with evidence, capped review rounds."""

import argparse
import json
import pathlib
import re
import subprocess
import sys

RUNS = pathlib.Path(".agents/runs")
ACTIVE = pathlib.Path(".agents/active-run")
PHASES = ("spec", "approved", "build", "review", "release", "blocked", "done")
OPEN_PHASES = ("build", "review")
MAX_REVIEW_ROUNDS = 3
CRITERION = re.compile(r"^- \[[ xX]\] (AC\d+):\s*(.+)$", re.M)
SPEC_TEMPLATE = """# {goal}

## Problem

## Scope

## Out of scope

## Reproduction (bugs only)

## Acceptance criteria
- [ ] AC1:
"""


class StateError(Exception):
    pass


def run_dir(slug):
    return RUNS / slug


def load(slug):
    path = run_dir(slug) / "progress.json"
    if not path.exists():
        raise StateError(f"no run '{slug}'")
    return json.loads(path.read_text())


def save(slug, state):
    (run_dir(slug) / "progress.json").write_text(json.dumps(state, indent=2) + "\n")


def active_slug():
    if not ACTIVE.exists():
        raise StateError("no active run")
    return ACTIVE.read_text().strip()


def cmd_new(args):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", args.slug):
        raise StateError("slug must be lowercase letters, digits and dashes")
    folder = run_dir(args.slug)
    if folder.exists():
        raise StateError(f"run '{args.slug}' exists")
    (folder / "research").mkdir(parents=True)
    (folder / "spec.md").write_text(SPEC_TEMPLATE.format(goal=args.goal))
    save(args.slug, {"goal": args.goal, "phase": "spec", "review_rounds": 0, "criteria": []})
    ACTIVE.write_text(args.slug + "\n")
    return str(folder.resolve())


def cmd_criteria(args):
    state = load(args.slug)
    found = CRITERION.findall((run_dir(args.slug) / "spec.md").read_text())
    criteria = [{"id": cid, "text": text.strip(), "passes": False, "evidence": None} for cid, text in found]
    if not criteria or any(not c["text"] for c in criteria):
        raise StateError("spec.md needs at least one '- [ ] ACn: <checkable statement>'")
    state["criteria"] = criteria
    save(args.slug, state)
    return f"{len(criteria)} criteria"


def cmd_phase(args):
    if args.phase not in PHASES:
        raise StateError(f"phase must be one of {', '.join(PHASES)}")
    state = load(args.slug)
    if args.phase == "approved" and not state["criteria"]:
        raise StateError("run 'criteria' before approval")
    state["phase"] = args.phase
    save(args.slug, state)
    if args.phase in ("done", "blocked"):
        ACTIVE.unlink(missing_ok=True)
    return args.phase


def cmd_pass(args):
    if not args.evidence.strip():
        raise StateError("evidence is required")
    state = load(args.slug)
    match = [c for c in state["criteria"] if c["id"] == args.id]
    if not match:
        raise StateError(f"unknown criterion {args.id}")
    match[0].update(passes=True, evidence=args.evidence.strip())
    save(args.slug, state)
    return f"{args.id} passes"


def cmd_review_round(args):
    state = load(args.slug)
    if state["review_rounds"] >= MAX_REVIEW_ROUNDS:
        state["phase"] = "blocked"
        save(args.slug, state)
        ACTIVE.unlink(missing_ok=True)
        raise StateError(f"review limit of {MAX_REVIEW_ROUNDS} reached; run is blocked for a human")
    state["review_rounds"] += 1
    for criterion in state["criteria"]:
        criterion.update(passes=False, evidence=None)
    save(args.slug, state)
    return f"review round {state['review_rounds']}"


def failing(state):
    return [c["id"] for c in state["criteria"] if not c["passes"]]


def cmd_check(args):
    state = load(args.slug)
    missing = failing(state)
    if missing or not state["criteria"]:
        raise StateError("not passing: " + (", ".join(missing) or "no criteria"))
    return "all criteria pass"


def tree_snapshot(path):
    out = subprocess.run(
        ["git", "-C", path, "status", "--porcelain", "--untracked-files=no"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    head = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    return head.stdout.strip() + "\n" + out.stdout


def cmd_tree(args):
    state = load(args.slug)
    if args.action == "save":
        state["tree"] = tree_snapshot(args.path)
        save(args.slug, state)
        return "tree saved"
    if state.get("tree") != tree_snapshot(args.path):
        raise StateError("working tree changed during review")
    return "tree unchanged"


def cmd_status(args):
    slug = args.slug or active_slug()
    state = load(slug)
    return json.dumps({"slug": slug, "phase": state["phase"], "failing": failing(state)})


def parser():
    p = argparse.ArgumentParser(prog="run_state")
    sub = p.add_subparsers(dest="cmd", required=True)
    new = sub.add_parser("new")
    new.add_argument("slug")
    new.add_argument("goal")
    for name in ("criteria", "check", "review-round"):
        sub.add_parser(name).add_argument("slug")
    phase = sub.add_parser("phase")
    phase.add_argument("slug")
    phase.add_argument("phase")
    passed = sub.add_parser("pass")
    passed.add_argument("slug")
    passed.add_argument("id")
    passed.add_argument("evidence")
    tree = sub.add_parser("tree")
    tree.add_argument("slug")
    tree.add_argument("action", choices=("save", "verify"))
    tree.add_argument("path")
    sub.add_parser("status").add_argument("slug", nargs="?")
    return p


COMMANDS = {
    "new": cmd_new,
    "criteria": cmd_criteria,
    "phase": cmd_phase,
    "pass": cmd_pass,
    "review-round": cmd_review_round,
    "check": cmd_check,
    "tree": cmd_tree,
    "status": cmd_status,
}


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        print(COMMANDS[args.cmd](args))
    except StateError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
