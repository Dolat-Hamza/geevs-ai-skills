# Agent team instructions

<!-- Added by /agent-team-setup. Edit the autonomy level and commands. -->

## Autonomy level: 1 (assisted execution)
Levels: 1 assisted, 2 supervised, 3 policy-driven, 4 continuous. At level 1 and 2 a human approves every merge and release.

## Laws
The plugin's `LAWS.md` binds every agent: precedence, hard rules, question budget (one batch at intake, max 2 more), loop limits (3 verify loops, 2 fix attempts, 2 retries), issue severities S1 to S4, persona rules. A blocked agent stops and writes the law number to `00-status.md`.

## Quality
The plugin's `QUALITY.md` defines done: functions under 30 lines, cognitive complexity 15, cyclomatic 10, nesting 3, params 4; tests for changed logic; OWASP pass, secrets and dependency scans; data classification and WCAG 2.2 AA where relevant. Hooks block force pushes, pushes and commits to the default branch, deploys, publishes, merges and secret writes.

## Source of truth
Read before acting, do not ask humans for what these answer:
- `docs/agent-knowledge/product-brief.md`
- `docs/agent-knowledge/architecture-and-structure.md`
- `docs/agent-knowledge/engineering-rules-and-standards.md`
- `docs/agent-knowledge/design-system.md`
- `docs/agent-knowledge/testing-and-quality.md`
- `docs/agent-knowledge/decision-log.md`

## How work flows
Non-trivial work goes through `/deliver`. Bugs and defects go through `/fix-issue`. Agents: orchestrator, product-research, designer, developer, producer, qa, reviewer, specialist-architect, specialist-security, specialist-performance, specialist-compliance, specialist-domain. Run artifacts live in `.agents/runs/<slug>/`.

## Every task must have
Problem statement, acceptance criteria, scope, do-not-touch list, tests or checks to run, and a final report of what changed, what was checked, what is uncertain.

## Hard rules
- Never commit to the default branch. One branch or worktree per task.
- Never claim a test or check passed without pasted output.
- Never touch auth, payments, schema migrations, production config, secrets, client-facing, legal or compliance material without recorded human approval.
- Never deploy, publish or send. Release is a human action at this level.
- Facts and numbers come from cited sources, never recall.
- Stay in scope. Report scope problems instead of solving them.

## Commands
- Install: TODO
- Test: TODO
- Lint / typecheck: TODO
- Run locally: TODO
