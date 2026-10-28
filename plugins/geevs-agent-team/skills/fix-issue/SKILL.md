---
name: fix-issue
description: Handle a bug, defect or issue end to end under the team laws: triage severity, reproduce, isolate the root cause, fix in an isolated branch with a regression test, verify independently, release with approval. Invoke as /fix-issue <issue description or ticket>.
---

# fix-issue

Shorter pipeline than `/deliver`, same gates and laws. Read `.agents/LAWS.md` section 6 first.

If `.agents/LAWS.md` is missing, run `/agent-team-setup` first.

## Stages
| # | Stage | Owner | Artifact | Gate |
|---|---|---|---|---|
| 1 | Triage | orchestrator (+ human for S1) | `01-triage.md` | severity set, affected area, who is informed; S2 to S4 proceed on the report text, S1 waits for the human |
| 2 | Reproduce | qa | `02-repro.md` | exact steps, expected vs actual, pasted evidence. No repro → stop and report |
| 3 | Isolate | developer or producer (+ specialist if security, performance, data) | `03-cause.md` | one root cause named, evidence, alternatives ruled out |
| 4 | Fix | same agent, own branch | `04-fix.md` + PR | regression test added first and failing, then passing; pasted output; scope = cause + test |
| 5 | Verify | qa ∥ reviewer | `05-qa.md`, `05-review.md` | repro no longer reproduces; no blockers; adjacent regression suite green |
| 6 | Release | human per autonomy level | `06-release.md` | approval recorded, rollback noted |

## Procedure
1. Create `.agents/runs/fix-<slug>/` and copy this skill's `templates/` into it. Use its `00-status.md`, which lists the six fix stages.
2. S1: stop every run touching the area, write it under "Decisions needed" in `00-status.md` for the human, and wait for approval before stage 3. Stage 2 is read-only and may run meanwhile.
3. Stage 2 before stage 3, always. A fix without a reproduction is refused.
4. Stage 4: systematic debugging. Form one hypothesis, test it, record it. Max 2 fix attempts (LAWS 5 and 6). After the second failure write `findings.md` and hand to the human.
5. Defects found outside scope go to `00-status.md`, not into this fix.
6. On release, append to `.agents/pilot-log.md`: cause, fix, test added, time to resolve.
