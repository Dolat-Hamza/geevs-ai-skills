"""Run state for /deliver: one folder per run, criteria with evidence, proofs, capped review rounds."""

import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "hooks"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cost  # noqa: E402
import proofs  # noqa: E402

RUNS = pathlib.Path(".agents/runs")
ACTIVE = pathlib.Path(".agents/active-run")
PHASES = ("spec", "approved", "build", "review", "release", "blocked", "done")
OPEN_PHASES = ("build", "review")
MAX_REVIEW_ROUNDS = 3
DEFAULT_BUDGET_USD = 5.0
CRITERION = re.compile(r"^- \[[ xX]\] (AC\d+):\s*(.+)$", re.M)
CHECK = re.compile(r"`[^`]+`")
SPEC_TEMPLATE = """# {goal}

## Problem

## Scope

## Out of scope

## Reproduction (bugs only)

## Acceptance criteria
- [ ] AC1: <observable statement>. Check: `<command, file:line or source>`
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
    if ACTIVE.exists() and ACTIVE.read_text().strip() != args.slug:
        raise StateError(f"run '{ACTIVE.read_text().strip()}' is still open; set it to done or blocked first")
    folder = run_dir(args.slug)
    if folder.exists():
        raise StateError(f"run '{args.slug}' exists")
    (folder / "research").mkdir(parents=True)
    (folder / "spec.md").write_text(SPEC_TEMPLATE.format(goal=args.goal))
    created = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    state = {"goal": args.goal, "phase": "spec", "review_rounds": 0, "criteria": []}
    state.update(created_at=created, budget_usd=args.budget_usd)
    save(args.slug, state)
    ACTIVE.write_text(args.slug + "\n")
    return str(folder.resolve())


def cmd_criteria(args):
    state = load(args.slug)
    found = CRITERION.findall((run_dir(args.slug) / "spec.md").read_text())
    criteria = [{"id": cid, "text": text.strip(), "passes": False, "evidence": None} for cid, text in found]
    if not criteria:
        raise StateError("spec.md needs at least one '- [ ] ACn: <statement>. Check: `<how>`'")
    unchecked = [c["id"] for c in criteria if not CHECK.search(c["text"]) or "<" in c["text"]]
    if unchecked:
        raise StateError("criteria must name their check in backticks: " + ", ".join(unchecked))
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
    state.pop("proofs", None)
    save(args.slug, state)
    return f"review round {state['review_rounds']}"


def failing(state):
    return [c["id"] for c in state["criteria"] if not c["passes"]]


def missing_proofs(state):
    """Proofs the branch's changed files require that are absent, failed, or for an older commit."""
    path = state.get("worktree")
    if not path:
        return []
    try:
        _, head, files = proofs.changed_files(path)
    except RuntimeError as error:
        raise StateError(str(error)) from error
    recorded = state.get("proofs", {})
    names = {"code": "test-first (redgreen)", "docs": "source tracing (claims)"}
    return [
        names[kind]
        for kind, needed in proofs.needs(files).items()
        if needed and not (recorded.get(kind, {}).get("ok") and recorded[kind].get("head") == head)
    ]


def cmd_check(args):
    state = load(args.slug)
    missing = failing(state)
    if missing or not state["criteria"]:
        raise StateError("not passing: " + (", ".join(missing) or "no criteria"))
    absent = missing_proofs(state)
    if absent:
        raise StateError("proof missing or out of date: " + ", ".join(absent))
    return "all criteria pass with proofs"


def record_proof(slug, kind, result):
    state = load(slug)
    state.setdefault("proofs", {})[kind] = result
    save(slug, state)
    if not result["ok"]:
        raise StateError(f"{kind} proof failed: " + (result.get("reason") or "; ".join(result.get("problems", []))))
    return json.dumps(result)


def cmd_redgreen(args):
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        raise StateError("give the test command after --")
    try:
        result = proofs.red_green(args.path, command)
    except RuntimeError as error:
        raise StateError(str(error)) from error
    return record_proof(args.slug, "code", result)


def cmd_claims(args):
    try:
        claims = json.loads(pathlib.Path(args.claims).read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise StateError(f"cannot read claims file: {error}") from error
    if not isinstance(claims, list):
        raise StateError("claims file must be a JSON list")
    return record_proof(args.slug, "docs", proofs.traced(args.path, claims))


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
        state["worktree"] = str(pathlib.Path(args.path).resolve())
        save(args.slug, state)
        return "tree saved"
    if state.get("tree") != tree_snapshot(args.path):
        raise StateError("working tree changed during review")
    return "tree unchanged"


def cmd_budget(args):
    if args.usd <= 0:
        raise StateError("budget must be positive")
    state = load(args.slug)
    state["budget_usd"] = args.usd
    save(args.slug, state)
    return f"budget ${args.usd:.2f}"


def cmd_status(args):
    slug = args.slug or active_slug()
    state = load(slug)
    spend = cost.run_total(run_dir(slug) / "spend.jsonl")
    summary = {"slug": slug, "phase": state["phase"], "failing": failing(state)}
    summary.update(spend_usd=spend, budget_usd=state.get("budget_usd"))
    return json.dumps(summary)


def parser():
    p = argparse.ArgumentParser(prog="run_state")
    sub = p.add_subparsers(dest="cmd", required=True)
    new = sub.add_parser("new")
    new.add_argument("slug")
    new.add_argument("goal")
    new.add_argument("--budget-usd", type=float, default=DEFAULT_BUDGET_USD)
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
    redgreen = sub.add_parser("redgreen")
    redgreen.add_argument("slug")
    redgreen.add_argument("path")
    redgreen.add_argument("command", nargs=argparse.REMAINDER)
    claims = sub.add_parser("claims")
    claims.add_argument("slug")
    claims.add_argument("path")
    claims.add_argument("claims")
    budget = sub.add_parser("budget")
    budget.add_argument("slug")
    budget.add_argument("usd", type=float)
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
    "redgreen": cmd_redgreen,
    "claims": cmd_claims,
    "budget": cmd_budget,
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
