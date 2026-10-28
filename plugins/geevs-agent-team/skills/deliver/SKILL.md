---
name: deliver
description: Run the full agent delivery pipeline for one deliverable or change: intake, research, spec, design, plan, production, verification, release. Use for any non-trivial piece of work. Invoke as /deliver <goal>.
---

# deliver

Plugin version: 0.2.2. State it at the top of every report.

Obey `.agents/LAWS.md` before anything below. It sets precedence, question budgets, loop limits, issue handling and persona rules.

Orchestrated pipeline. The main session acts as, or delegates to, the `orchestrator` agent. Each stage writes one artifact into `.agents/runs/<slug>/` and must pass its gate before the next stage starts.

If `.agents/LAWS.md` is missing, run `/agent-team-setup` first.

## Stages, owners, artifacts, gates

| # | Stage | Owner | Artifact | Gate to pass |
|---|---|---|---|---|
| 01 | Intake | orchestrator with human | `01-intake.md` | Goal, value, audience, constraints, definition of done filled; confirmed by the human or by the request text |
| 02 | Research | product-research | `02-research.md` | Existing materials cited by file; options compared; risks split verified/assumed |
| 03 | Specification | product-research | `03-spec.md` | Every acceptance criterion binary and checkable; out-of-scope listed; open questions have defaults |
| 04 | Design | designer | `04-design.md` | Outline, format, tone, reader journey set; reuses existing templates |
| 05 | Plan | orchestrator (+ specialists) | `05-plan.md` | Each task has problem, criteria, scope, do-not-touch, checks, dependencies, size under one day |
| 06 | Production | developer (code) or producer (deliverables), one per task, parallel where independent | `06-dev-<task>.md` or `06-prod-<task>.md` + PR | Self-check evidence per criterion; report lists unchecked areas |
| 07 | Verification | qa and reviewer, independently and in parallel | `07-qa.md`, `07-review.md` | QA verdict pass, or pass with minor defects when every defect is S4 and logged; review has no blockers |
| 08 | Release | human or authorized policy | `08-release.md` | Human approval recorded; owner, channel, correction path noted |

## Procedure
1. Create `.agents/runs/<slug>/` and copy templates from this skill's `templates/` folder.
2. Fill `01-intake.md` from the request. If the request answers every field, record `confirmed: request text` and continue. Otherwise ask the human the missing fields as the one intake batch (LAWS 4); stop until answered.
3. Delegate stages 02 to 04 in order and write 05 yourself. Pass prior artifacts by absolute path.
4. Pull a specialist (architect, security, performance, compliance, domain) into stage 05 when the plan touches their trigger areas listed in their agent descriptions.
5. For stage 06 spawn one developer or producer per task in its own worktree.
6. Stage 07 runs qa and reviewer in parallel on the PR. Failures go back to stage 06 with the specific items. QA and reviewer may use the library skills named in their agent files. Max three loops, then escalate to human. After any loop that changes the deliverable, both QA and reviewer re-check it.
7. Stage 08: present the human a release summary. Never publish, send or merge to the default branch without recorded approval, unless `CLAUDE.md` autonomy level permits it.
8. Update `00-status.md` after every stage change.

## Autonomy level
Read the current level from `CLAUDE.md`. Level 1 and 2: human approves merge and release. Level 3: merge allowed when QA pass and review clean. Release always human for client-facing material. See `README.md`.

## Handoffs
Every handoff names the run folder by absolute path. Agents in a worktree read inputs and write artifacts there, because untracked run files are not copied into worktrees. Create worktrees under `.agents/worktrees/`.

## Handling failure
- Gate fail: return to owner with failing checklist items, do not advance.
- Agent asks a question the docs answer: point it at the doc, do not answer from memory.
- Scope creep discovered mid-pipeline: stop, write it to `00-status.md` under decisions needed, ask human.
