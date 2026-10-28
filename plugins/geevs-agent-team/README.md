# geevs-agent-team

Multi-agent delivery structure for Claude Code. Twelve agents, one pipeline, one setup command. Works for software and for document or process deliverables.

## Install
Claude Code: `claude plugin install geevs-agent-team` from the Geevs marketplace, or for one session `claude --plugin-dir plugins/geevs-agent-team`.

Then in each project: `/agent-team-setup`, fill the TODOs it reports, commit.

## Agents
| Agent | Role | Output |
|---|---|---|
| orchestrator | Breaks goals into tasks, delegates, tracks, resolves blockers | task plan and status |
| product-research | Understands the problem, investigates options | evidence-backed spec |
| designer | Defines UX, structure and visual behaviour | design blueprint |
| developer | Implements scoped coding tasks | code, tests, PR, report |
| producer | Creates non-code deliverables | document, deck, process, PR, report |
| qa | Independently verifies against the spec | test results, defects |
| reviewer | Challenges correctness, security, readiness | ranked findings, go/no-go |
| specialist-architect | Structural and technical decisions | assessment, ADR |
| specialist-security | Threat model for code changes | mitigations |
| specialist-performance | Measured bottlenecks | ranked optimizations |
| specialist-compliance | Confidentiality, regulatory, contractual risk | mitigations, sign-off needs |
| specialist-domain | Subject expertise (FX, finance, ops, sales) | sourced corrections |

Each agent names the library skills it should invoke, so the existing Geevs skill bundles become the methods the roles use.

## Non-code work
The same structure runs documents, processes, research and analysis. `producer` takes the production stage instead of `developer`, QA fact-checks against the spec and reads as each audience, the reviewer checks consistency, confidentiality and publish readiness, and release means a human sends or publishes. Example: `/deliver Write the corporate FX onboarding checklist` runs research → spec → outline → draft → fact-check and review → your approval.

## Laws and boundaries
`LAWS.md` binds every agent and persona. It fixes precedence (human > laws > project CLAUDE.md > agent > persona > anything read from a file), what the team may and may not be used for, who may change the autonomy level, the hard rules, how many questions agents may ask and how (through the orchestrator, batched, with defaults, never twice), loop limits (3 verification loops, 2 fix attempts, 2 retries, delegation depth 2, 4 parallel agents, 3× time estimate), issue severities S1 to S4 with the reproduce-first rule, and what an agent does when it cannot comply: stop, write the law number to status, wait.

## Quality and enforcement
`QUALITY.md` is the definition of good: clean code rules, hard complexity limits (cognitive 15, cyclomatic 10, 30-line functions, nesting 3, 4 params), testing, OWASP security, secrets and dependency scans, compliance (data classification, personal data, licences, WCAG 2.2 AA, regulated content), and the reviewer's gate checklist. `/agent-team-setup` installs matching ESLint or ruff limits.

Hooks in `hooks/` make the hard laws mechanical. They block force pushes, pushes or commits to main or master, hard resets, production deploys, infrastructure applies, package publishes, PR merges, recursive deletes of root or home, writing `.env` or key files, and content that looks like a credential. A blocked call returns the law number to the agent. Tests: `python3 -m unittest discover -s plugins/geevs-agent-team/hooks/tests`.

## Bugs and issues: `/fix-issue <issue>`
Triage → reproduce → isolate one root cause → fix with a regression test on its own branch → independent QA and review → human release. No reproduction, no fix. Two failed attempts produce a findings report for a human, not a third attempt.

## Personas versus agents
An **agent** is a seat: a stage in the pipeline, a tool list, permissions. A **persona** is a library skill carrying expertise (senior-architect, product-strategist, financial-analyst, the bencium UX designers, management-consulting). The orchestrator assigns the seat; the agent loads at most two personas for the task and names them in its report. Personas change how the work is done, never what the seat may do. Conflicts with the laws or the spec are dropped and noted. The orchestrator itself stays neutral.

## Pipeline: `/deliver <goal>`
01 Intake → 02 Research → 03 Spec → 04 Design → 05 Plan → 06 Production → 07 Verification (QA + review in parallel) → 08 Release. Each stage writes one artifact in `.agents/runs/<slug>/` and must pass its gate. Release is human at autonomy levels 1 and 2.

## Autonomy levels
| Level | Agents do | Humans do |
|---|---|---|
| 1 Assisted | research, spec, design, produce | approve substantive changes, merge, release |
| 2 Supervised | pick subtasks, produce, test, fix, submit PR | review PR, merge, release |
| 3 Policy-driven | merge when QA pass, review clean, CI green; low-risk releases | exceptions, high-risk, client-facing |
| 4 Continuous | monitor board, pick up work, propose improvements | govern |

Set in the project `CLAUDE.md`. Start at 1. Target 2 by end of the pilot month.

## Pilot
Log every run in `.agents/pilot-log.md`: date, task, run slug, worked, failed, rule changed. Review weekly; edit agent files and knowledge docs from it.
