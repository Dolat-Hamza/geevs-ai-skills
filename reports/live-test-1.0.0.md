# geevs-agent-team 1.0.0 — live acceptance test

- Date: 2026-10-29
- Claude Code: 2.1.267 (desktop app, Code tab), session started by another session
- Sandbox: `agent-team-sandbox-v1`, `main` at `64e6d48 Sandbox FX fee calculator`, clean
- Plugin: `geevs-agent-team@geevs` 1.0.0, user scope, local directory marketplace pointing at the `geevs-ai-skills` checkout
  - install record `gitCommitSha: 9eb991054f91044ed897663cd7d14fe1e1858dfe`
  - `diff -r` of `~/.claude/plugins/cache/geevs/geevs-agent-team/1.0.0` vs `plugins/geevs-agent-team` on `feat/agent-team-v1`: identical

## Check 1 — Load

`claude plugin list`:
```
  ❯ geevs-agent-team@geevs
    Version: 1.0.0
    Scope: user
    Status: ✔ enabled
```

Agent types offered to the session from this plugin (from the session's agent list):
```
- geevs-agent-team:builder: Implements an approved /deliver spec in an isolated worktree, for code or documents. ... (Tools: Read, Grep, Glob, Bash, Write, Edit)
- geevs-agent-team:researcher: Answers one research question for a /deliver run with cited evidence ... (Tools: Read, Grep, Glob, WebSearch, WebFetch, Write)
- geevs-agent-team:reviewer: Independently verifies a /deliver build against its spec. ... (Tools: Read, Grep, Glob, Bash)
```
No other `geevs-agent-team:*` agents.

Skills: `deliver` and `setup` are **not** in the model's skill list. Both have `disable-model-invocation: true`, so they are user-only slash commands. The installed files are present:
```
skills/deliver/SKILL.md
skills/setup/SKILL.md
```
Trying to run setup from the agent:
```
Skill("geevs-agent-team:setup")
<tool_use_error>Skill geevs-agent-team:setup cannot be used with Skill tool due to
disable-model-invocation. Ask the user to run /geevs-agent-team:setup themselves — it cannot be
invoked via the Skill tool. Do not replicate this skill's workflow by other means — it is reserved
for explicit user invocation.</tool_use_error>
```

Result: **pass.** 3 agents load, nothing extra. Both skills are installed and are user-only by design, which the starting session confirmed is intended. Only a human typing `/geevs-agent-team:setup` or `/geevs-agent-team:deliver` starts them. The plugin README does not say this (see the report section).

## Check 2 — Setup

Branch `chore/agent-team-setup` was created from `main` (`64e6d48`). The human typed `/geevs-agent-team:setup`. Skill base directory shown: `.../geevs-ai-skills/plugins/geevs-agent-team/skills/setup`, which is the checkout, not the plugin cache.

JSON printed:
```
{"rules_added": 24, "claude_md_updated": true, "gitignore_updated": true}
```

`.claude/settings.json`:
```json
{
  "permissions": {
    "deny": [
      "Bash(git push --force *)",
      "Bash(git push -f *)",
      "Bash(git push --force-with-lease *)",
      "Edit(**/.env)",
      "Edit(**/.env.local)",
      "Edit(**/.env.production)",
      "Edit(**/*.pem)",
      "Edit(**/id_rsa)",
      "Edit(**/id_ed25519)"
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
      "Bash(helm upgrade *)"
    ]
  }
}
```
Also written: `.claude/agent-team.json` = `{"version": "1.0.0"}`, a `## Agent team` section in a new `CLAUDE.md`, and `.agents/active-run` appended to `.gitignore`.

Commit on the branch:
```
94640f5 chore: opt into geevs-agent-team 1.0.0
 .claude/agent-team.json |  1 +
 .claude/settings.json   | 32 ++++++++++++++++++++++++++++++++
 .gitignore              |  1 +
 CLAUDE.md               |  5 +++++
 4 files changed, 39 insertions(+)
```
Result: **pass.**

## Test environment caveat (affects checks 3, 4 and 6)

This session was started with no project folder. Its project is a folder the app made for the session, and the shell is reset there between calls ("Shell cwd was reset to .../scratch-workspaces/..."). So Claude Code never loaded the sandbox's `.claude/settings.json` as project settings. I tried to move the session into the sandbox with `change_directory`, and it was refused:
```
The user declined to trust that folder as a workspace, so it was not granted and the session did not move.
```
The plugin hook does not depend on this. `gate.py` finds the marker by walking up from the event's `cwd`, which is the sandbox whenever a command `cd`s there first. The permission rules do depend on it.

## Check 3 — Deny rules

`git push --force origin x` (run once, from the sandbox):
```
Permission for this action was denied by the Claude Code auto mode classifier. Reason: [Git Destructive].
```
It was refused, but by the auto-mode classifier. The message does not show the project `deny` rule firing.

`Write` to `.env` (run once, content `LIVE_TEST=1`):
```
File created successfully at: .../agent-team-sandbox-v1/.env
```
**Not refused.** The file was created. `.env` is gitignored (`.gitignore:3:.env`), and I removed it immediately.

Result: **fail as observed.** The deny rules did not take effect in this session. The likely cause is the caveat above (project settings not loaded), not the rules themselves. The rule `Edit(**/.env)` is the documented form, and Edit rules cover Write. This needs a rerun in a session opened directly in the sandbox.

## Check 4 — Commit hook on main

`git checkout main`. The marker is absent on `main` because setup was committed only on `chore/agent-team-setup`:
```
main
ls: .claude: No such file or directory
```
`git commit --allow-empty -m test` (run once):
```
[main 33cb002] test
```
**No approval prompt. The commit landed on `main`.** I undid my own empty commit with `git reset --soft HEAD~1`. `main` is back at `64e6d48` and nothing was lost.

Cause: `gate.py` passes through any project without `.claude/agent-team.json`. The setup skill says to commit the opt-in on a new branch, not on `main`. So until that branch is merged, `main` (the branch the hook protects) is not opted in. This is a design gap, not a test artefact.

Replaying the installed hook directly, in a throwaway repo on `main`:
```
with marker, on main:
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "Commit on the default branch. Approve only if intended; agents work on branches."}}

without marker, on main:
(exit 0, no output)
```
Result: **fail as observed.** The hook logic is correct when the marker is present, but the documented setup flow leaves `main` unprotected. The human was never prompted, so there was nothing to decline.

## Which results depended on project settings not being loaded

The starting session accepted both findings. Checks 3 and 4 stay recorded as FAIL, and both will be rerun in a fresh session opened in the sandbox folder. The planned 1.1 fix is for setup to write untracked, branch-independent files (`settings.local.json` and a local marker, excluded via `.git/info/exclude`).

| Result | Depends on project settings being loaded? |
|---|---|
| Check 3: `.env` write allowed | **Yes.** The deny rules live only in project settings. |
| Check 3: force push refused by the classifier, not by a rule | **Yes.** It is unknown whether the deny rule would have fired first. |
| Check 4: commit on `main` with no prompt | **No.** The plugin hook loads globally. It passed through because `main` has no marker. |
| Checks 5–7 | Hooks: no, the marker is on `chore/agent-team-setup`. The `ask` rules for push, merge and deploy are not active in this session. |
