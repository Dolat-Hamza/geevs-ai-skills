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

Then, in each project: `/geevs-agent-team:setup`. Nothing is enforced in projects that have not run it.

## What is enforced and how

| Rule | Mechanism |
|---|---|
| Push, PR merge, hard reset, deploy, publish ask you first | Project permission `ask` rules |
| Force push and edits to `.env`, key files are refused | Project permission `deny` rules |
| Commit on `main`/`master` asks you first | Plugin hook |
| Credential-looking content in a file write is refused | Plugin hook |
| A session cannot end mid-build or mid-review with unverified criteria | Plugin `Stop` hook reading `progress.json` |
| Criteria come from the spec, pass only with evidence, reset every review, at most 3 reviews | `scripts/run_state.py` |
| Reviewer cannot change the work | Write and Edit removed from the agent; HEAD and tracked files checked after review |
| Runaway agents | `maxTurns` per agent |

Everything else (agent roles, interview, research scope) is instruction, not enforcement.

Permission rules match command prefixes. They do not stop `bash -c`, full binary paths or scripts. For a hard boundary, enable Claude Code sandboxing.

## Run state

`.agents/runs/<slug>/`: `spec.md`, `progress.json`, `research/`. `.agents/active-run` names the open run.

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
