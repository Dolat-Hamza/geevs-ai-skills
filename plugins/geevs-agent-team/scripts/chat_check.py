"""The same proofs on plain folders, for chat where there is no git repository or hook."""

import argparse
import filecmp
import json
import pathlib
import shutil
import sys
import tempfile

import proofs

SKIP = shutil.ignore_patterns("__pycache__", "*.pyc")


def claims(folder, claims_file):
    listed = json.loads(pathlib.Path(claims_file).read_text())
    if not isinstance(listed, list) or not listed:
        return {"ok": False, "reason": "no claims listed"}
    problems = proofs.claim_problems(folder, listed)
    problems += [f"number {n} has no sourced claim" for n in proofs.uncovered_numbers(folder, listed)]
    return {"ok": not problems, "claims": len(listed), "problems": problems}


def new_tests(before, after):
    """Test files that are new or changed in the fixed folder."""
    found = []
    for path in sorted(after.rglob("*")):
        name = path.relative_to(after).as_posix()
        if path.is_file() and "__pycache__" not in name and proofs.TEST_PATH.search(name):
            old = before / name
            if not old.is_file() or not filecmp.cmp(old, path, shallow=False):
                found.append(name)
    return found


def tests(before, after, command):
    """New tests must fail on the original folder and pass on the fixed one."""
    before, after = pathlib.Path(before), pathlib.Path(after)
    names = new_tests(before, after)
    if not names:
        return {"ok": False, "reason": "no new or changed test files in the fixed folder"}
    with tempfile.TemporaryDirectory() as tmp:
        scratch = pathlib.Path(tmp) / "before"
        shutil.copytree(before, scratch, ignore=SKIP)
        for name in names:
            (scratch / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(after / name, scratch / name)
        red = proofs.run(command, scratch)
    green = proofs.run(command, after)
    ok = red != 0 and green == 0
    result = {"ok": ok, "tests": names, "red_exit": red, "green_exit": green}
    if not ok:
        result["reason"] = "new tests pass on the original" if red == 0 else "tests fail on the fix"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(prog="chat_check")
    sub = parser.add_subparsers(dest="proof", required=True)
    c = sub.add_parser("claims")
    c.add_argument("folder")
    c.add_argument("claims_file")
    t = sub.add_parser("tests")
    t.add_argument("before")
    t.add_argument("after")
    t.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.proof == "claims":
        result = claims(args.folder, args.claims_file)
    else:
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        if not command:
            parser.error("give the test command after --")
        result = tests(args.before, args.after, command)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
