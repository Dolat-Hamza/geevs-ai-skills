# geevs-agent-team

Gated delivery for code and documents. The main session orchestrates; three agents do isolated work.

```
/geevs-agent-team:deliver <goal>
  interview ──> research (0-3 researchers) ──> spec ──> [you approve]
  ──> builder (own worktree) ──> reviewer (records evidence) ──> [you push / merge]
                     ^─────── failed criteria, up to 3 reviews ───────┘
```

## Install

```bash
claude plugin marketplace add Dolat-Hamza/geevs-ai-skills
```
```bash
claude plugin install geevs-agent-team@geevs
```

Then, in each project clone, open Claude Code in that folder and run `/geevs-agent-team:setup`. It writes `.claude/settings.local.json` and `.claude/agent-team.local.json`, excluded from git through `.git/info/exclude`, so they apply on every branch without a commit. Nothing is enforced in clones that have not run it.

Verified on Claude Code 2.1.267: researcher ran on `claude-haiku-5-5`, builder and reviewer on `claude-sonnet-5-5`. The docs list 2.1.271 or later for `omitClaudeMd`; older versions ignore it.

## What is enforced and how

| Rule | Mechanism |
|---|---|
| Push, PR merge, hard reset, deploy, publish ask you first | Local permission `ask` rules |
| Force push and edits to `.env`, key files are refused | Local permission `deny` rules |
| Commit on `main`/`master` asks you first | Plugin hook |
| Credential-looking content in a file write is refused | Plugin hook |
| A session cannot end mid-build or mid-review with unverified criteria | Plugin `Stop` hook reading `progress.json` |
| Criteria come from the spec, pass only with evidence, reset every review, at most 3 reviews | `scripts/run_state.py` |
| Reviewer cannot change the work | Write and Edit removed from the agent; HEAD and tracked files checked after review |
| Spend over the run budget asks you before any further agent spawn | `SubagentStop` logs each agent's spend from its transcript; a hook on the Agent tool checks the total |
| Runaway agents | `maxTurns` per agent |

Everything else (agent roles, interview, research scope) is instruction, not enforcement.

Permission rules match command prefixes. They do not stop `bash -c`, full binary paths or scripts. For a hard boundary, enable Claude Code sandboxing.

## Cost

| Agent | Model | Effort | Max turns | Skips CLAUDE.md |
|---|---|---|---|---|
| researcher | haiku | default | 25 | yes |
| builder | sonnet | default | 50 | no |
| reviewer | sonnet | high | 35 | yes |

The orchestrator is your main session and uses your model. Turn caps are two to three times the most turns each role used in recorded runs (12, 15 and 17). A capped agent returns partial work that can be resumed.

Each run has a budget of estimated API cost, $5 by default (`run_state new ... --budget-usd N`, raise with `run_state budget`). Spend is read from each agent's transcript when it stops and from the main session transcript, priced with the published per-model rates in `hooks/cost.py`. On a subscription this is an estimate of usage, not a bill.

Measured, same sandbox and the same two tasks (a boundary bug fix and a one-paragraph customer note):

| Version | Agents | Orchestrator | Total |
|---|---|---|---|
| 0.1.x, all agents on Opus | $11.05 | $4.74 | $15.79 |
| 1.1.1, builder and reviewer on Sonnet | $0.31 | $3.39 (Opus, includes setup and guard checks) | $3.70 |

Per run in 1.1.1: bug fix $0.82, customer note $0.57. The orchestrating session is about 90% of the cost; running it on Sonnet (`/model sonnet`) is the largest remaining saving.

Habits that cut cost the most, from the same data: start each run in a fresh session, keep briefs to file paths, and keep research to the questions the repo cannot answer.

## Run state

`.agents/runs/<slug>/`: `spec.md`, `progress.json`, `spend.jsonl`, `research/`. `.agents/active-run` names the open run.

## Tests

```bash
python3 -m unittest discover -s plugins/geevs-agent-team/tests
```

## Sources

- Gated chain and evaluator pattern: https://www.anthropic.com/engineering/building-effective-agents
- Spec, fresh-context build, read-only reviewer: https://code.claude.com/docs/en/best-practices
- Subagents for research fan-out, files instead of long hand-offs: https://www.anthropic.com/engineering/multi-agent-research-system
- Feature list with pass flags against premature completion: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Permission rule semantics and limits: https://code.claude.com/docs/en/permissions
- Cost levers and prompt caching: https://code.claude.com/docs/en/costs and https://code.claude.com/docs/en/prompt-caching
- Prices: https://platform.claude.com/docs/en/about-claude/pricing
