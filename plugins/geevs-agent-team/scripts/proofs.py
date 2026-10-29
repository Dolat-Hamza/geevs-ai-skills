"""Deterministic proofs for a review: test-first for code, source-traced claims for documents."""

import pathlib
import re
import subprocess
import tempfile

CODE_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".rb",
    ".php",
    ".cs",
    ".swift",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".sql",
    ".sh",
}
DOC_SUFFIXES = {".md", ".txt", ".rst", ".html", ".csv"}
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__)/|(^|/)test_[^/]+$|_test\.[a-z]+$|\.(test|spec)\.[a-z]+$")
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
LIST_ORDINAL = re.compile(r"^\s*\d+[.)]\s", re.M)


def git(path, *args, check=True):
    out = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True, check=False, timeout=60)
    if check and out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or f"git {' '.join(args)} failed")
    return out.stdout.strip()


def default_branch(path):
    for name in ("main", "master"):
        if git(path, "rev-parse", "--verify", "--quiet", name, check=False):
            return name
    raise RuntimeError("no main or master branch to compare against")


def changed_files(path):
    """Base commit, head commit and files changed on the branch since it left the default branch."""
    head = git(path, "rev-parse", "HEAD")
    base = git(path, "merge-base", head, default_branch(path))
    files = [f for f in git(path, "diff", "--name-only", base, head).splitlines() if f]
    return base, head, files


def needs(files):
    """Which proofs a set of changed files requires."""
    suffixes = {pathlib.PurePosixPath(f).suffix.lower() for f in files}
    return {"code": bool(suffixes & CODE_SUFFIXES), "docs": bool(suffixes & DOC_SUFFIXES)}


def run(command, cwd):
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False, timeout=600).returncode


def red_green(path, command):
    """New tests must fail on the base code and pass on the branch."""
    base, head, files = changed_files(path)
    tests = [f for f in files if TEST_PATH.search(f)]
    if not tests:
        return {"ok": False, "head": head, "reason": "no test files changed on the branch"}
    with tempfile.TemporaryDirectory() as tmp:
        scratch = pathlib.Path(tmp) / "base"
        git(path, "worktree", "add", "--detach", str(scratch), base)
        try:
            git(scratch, "checkout", head, "--", *tests)
            red = run(command, scratch)
        finally:
            git(path, "worktree", "remove", "--force", str(scratch), check=False)
    green = run(command, path)
    ok = red != 0 and green == 0
    result = {"ok": ok, "head": head, "base": base, "tests": tests, "red_exit": red, "green_exit": green}
    if not ok:
        result["reason"] = "new tests pass on the base code" if red == 0 else "tests fail on the branch"
    return result


def normalise(text):
    return " ".join(text.replace(",", "").split())


def claim_problems(path, claims):
    problems = []
    for i, claim in enumerate(claims, 1):
        target = pathlib.Path(path) / claim.get("file", "")
        source = pathlib.Path(path) / claim.get("source", "").split(":")[0]
        if not target.is_file() or normalise(claim.get("claim", "")) not in normalise(target.read_text()):
            problems.append(f"claim {i}: text not found in {claim.get('file')}")
        if not source.is_file() or normalise(claim.get("quote", "")) not in normalise(source_text(source, claim)):
            problems.append(f"claim {i}: quote not found at {claim.get('source')}")
    return problems


def source_text(source, claim):
    """The cited line when the source is file:line, otherwise the whole file."""
    lines = source.read_text().splitlines()
    _, _, line = claim.get("source", "").partition(":")
    if not line:
        return "\n".join(lines)
    return lines[int(line) - 1] if line.isdigit() and 0 < int(line) <= len(lines) else ""


def uncovered_numbers(path, claims):
    covered = {n.replace(",", "") for c in claims for n in NUMBER.findall(c.get("claim", ""))}
    files = {c.get("file") for c in claims if c.get("file")}
    missing = set()
    for name in files:
        target = pathlib.Path(path) / name
        if target.is_file():
            text = LIST_ORDINAL.sub("", target.read_text())
            missing |= {n.replace(",", "") for n in NUMBER.findall(text)} - covered
    return sorted(missing)


def traced(path, claims):
    """Every claim appears in its document, every quote in its source, every number in some claim."""
    head = git(path, "rev-parse", "HEAD")
    if not claims:
        return {"ok": False, "head": head, "reason": "no claims listed"}
    problems = claim_problems(path, claims)
    problems += [f"number {n} has no sourced claim" for n in uncovered_numbers(path, claims)]
    return {"ok": not problems, "head": head, "claims": len(claims), "problems": problems}
