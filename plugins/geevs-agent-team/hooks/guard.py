"""PreToolUse guard enforcing LAWS.md hard rules. Exit 2 blocks the call."""

import json
import os
import re
import shlex
import subprocess
import sys

BLOCK = 2
ALLOW = 0
DEFAULT_BRANCHES = {"main", "master"}
OPERATORS = {"&&", "||", ";", "|", "&", "(", ")", ";;", "|&"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>"}
SKIP_PREFIXES = {"sudo", "env", "command", "exec", "nohup", "time"}
ROOT_TARGETS = {"/", "/*", "~", "~/", "$HOME", "${HOME}"}

SECRET_FILE = re.compile(r"(^|/)(\.env(\.[\w-]+)?|id_rsa|id_ed25519|[\w-]+\.pem|[\w-]+\.key|credentials\.json)$")
EXAMPLE_FILE = re.compile(r"\.(example|sample|template)$")
SECRET_CONTENT = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsk-(live|ant|proj)-[A-Za-z0-9_-]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{30,}"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
]
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1([^\n]*)\n.*?\n[ \t]*\2[ \t]*(?=\n|$)", re.S)


class Blocked(Exception):
    """Raised by a check with the law that the command breaks."""


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


def resolve(base, path):
    return os.path.normpath(os.path.join(base or ".", os.path.expanduser(path)))


def segments(command):
    """Split a shell command into simple commands, ignoring heredoc bodies and quoted text."""
    text = HEREDOC.sub(lambda m: m.group(3), command).replace("\n", " ; ")
    lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    current = []
    for token in lexer:
        if token in OPERATORS:
            yield current
            current = []
        else:
            current.append(token)
    yield current


def strip_prefixes(tokens):
    while tokens and (tokens[0] in SKIP_PREFIXES or re.match(r"^\w+=", tokens[0])):
        tokens = tokens[1:]
    return tokens


def check_redirects(tokens):
    targets = [tokens[i + 1] for i, t in enumerate(tokens[:-1]) if t in REDIRECTS]
    if tokens and tokens[0] == "tee":
        targets += [t for t in tokens[1:] if not t.startswith("-")]
    for target in targets:
        if SECRET_FILE.search(target) and not EXAMPLE_FILE.search(target):
            raise Blocked(f"LAWS 3.7: writing secret files is blocked ({target}). Use an .example file.")


def split_git(tokens, cwd):
    """Return (repo_dir, subcommand, args) for a git command, honouring -C and -c."""
    rest = tokens[1:]
    while rest and rest[0] in ("-C", "-c"):
        if rest[0] == "-C" and len(rest) > 1:
            cwd = resolve(cwd, rest[1])
        rest = rest[2:]
    if not rest:
        return cwd, "", []
    return cwd, rest[0], rest[1:]


def check_push(args, repo):
    if any(a.startswith(("--force", "-f")) or a.startswith("+") for a in args):
        raise Blocked("LAWS 3.1: force push is not allowed.")
    refs = [a for a in args if not a.startswith("-")]
    targets = {r.split(":")[-1] for r in refs[1:]}
    if targets & DEFAULT_BRANCHES:
        raise Blocked("LAWS 3.1: push to the default branch is not allowed. Open a PR.")
    if len(refs) <= 1 and current_branch(repo) in DEFAULT_BRANCHES:
        raise Blocked("LAWS 3.1: push from the default branch is not allowed. Push a feature branch.")


def check_git(tokens, cwd):
    repo, sub, args = split_git(tokens, cwd)
    if sub == "push":
        check_push(args, repo)
    elif sub == "reset" and "--hard" in args:
        raise Blocked("LAWS 3.4: hard reset discards work. Ask a human.")
    elif sub == "commit" and current_branch(repo) in DEFAULT_BRANCHES:
        raise Blocked("LAWS 3.1: commit on the default branch is not allowed. Create a branch first.")


def check_vercel(tokens, _cwd):
    if "--prod" in tokens or "--production" in tokens:
        raise Blocked("LAWS 3.2: production deploys are human actions.")


def check_infra(tokens, _cwd):
    if len(tokens) > 1 and tokens[1] in ("apply", "destroy", "install", "upgrade"):
        raise Blocked("LAWS 3.2: infrastructure changes are human actions.")


def check_publish(tokens, _cwd):
    if "publish" in tokens[1:2]:
        raise Blocked("LAWS 3.2: publishing packages is a human action.")


def check_gh(tokens, _cwd):
    if tokens[1:3] == ["pr", "merge"]:
        raise Blocked("LAWS 3.2: merging requires the approval the autonomy level sets. Ask a human.")


def check_rm(tokens, _cwd):
    flags = "".join(t.lstrip("-") for t in tokens[1:] if t.startswith("-") and not t.startswith("--"))
    recursive = "r" in flags.lower() or "--recursive" in tokens
    if recursive and any(t in ROOT_TARGETS for t in tokens[1:]):
        raise Blocked("LAWS 3.4: recursive delete of a root or home path is blocked.")


COMMANDS = {
    "git": check_git,
    "vercel": check_vercel,
    "kubectl": check_infra,
    "terraform": check_infra,
    "helm": check_infra,
    "npm": check_publish,
    "pnpm": check_publish,
    "yarn": check_publish,
    "gh": check_gh,
    "rm": check_rm,
}


def check_segment(tokens, cwd):
    """Check one simple command; return the working directory after it runs."""
    tokens = strip_prefixes(tokens)
    if not tokens:
        return cwd
    check_redirects(tokens)
    if tokens[0] == "cd":
        return resolve(cwd, tokens[1] if len(tokens) > 1 else "~")
    check = COMMANDS.get(tokens[0])
    if check:
        check(tokens, cwd)
    return cwd


def check_bash(event):
    command = event.get("tool_input", {}).get("command", "")
    cwd = event.get("cwd") or "."
    if any(p.search(command) for p in SECRET_CONTENT):
        return deny("LAWS 3.7: command contains what looks like a credential. Use an environment variable.")
    try:
        for tokens in segments(command):
            cwd = check_segment(tokens, cwd)
    except Blocked as blocked:
        return deny(str(blocked))
    except ValueError:
        return deny("Guard could not parse this command (unbalanced quotes). Simplify the quoting and retry.")
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
