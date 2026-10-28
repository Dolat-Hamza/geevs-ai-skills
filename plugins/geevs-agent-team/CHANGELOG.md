# Changelog

## 0.2.1 — 2026-10-28
- Orchestrator names developer in its delegation list.
- Orchestrator escalation matches LAWS 3.3: drafting client-facing material is allowed; only its release needs approval.

## 0.2.0 — 2026-10-28
From the first live test (fix-issue and deliver runs in a sandbox).
- Guard parses commands per segment, follows `cd` and `git -C`, ignores quoted text and heredoc bodies, blocks secret writes through shell redirects and `tee`, blocks push from main without a refspec, fails closed on unparseable commands. 19 tests.
- Every seat has the Skill tool; agent files say which skills to load and that skill-router and graphify do not apply.
- qa, reviewer, developer, producer and orchestrator have `/fix-issue` stage and artifact instructions.
- Specialists write only their own artifact; architect, compliance and domain lose Bash.
- LAWS: release artifact per pipeline, "payments" defined, client-facing material may be drafted but not released without approval, assumed defaults go to the decision log, only the main session spawns an orchestrator, "area" defined, offline-safe scanner rules allowed.
- QUALITY: offline-safe semgrep invocation, specialists join at `/fix-issue` stage 3, every installed type checker runs.
- Pipelines accept "pass with minor defects" when all defects are S4; both QA and reviewer re-check after a fix loop.
- Templates: fix-issue titles and defect table columns fixed.
- Setup creates a branch when on the default branch and marks unfilled sections `TODO:`.
- Producer: no internal metadata in customer copy; PR only when a remote exists.

## 0.1.4
- Reviewer can save its own review artifact.

## 0.1.3
- S1 limited to production or client-facing use; fix-issue status template; orchestrator follows the running skill's numbering.

## 0.1.2
- Intake and triage proceed on the request text; orchestrator uses process skills only; no repo-only file references.

## 0.1.1
- Valid manifest, marketplace install, project-local laws.
