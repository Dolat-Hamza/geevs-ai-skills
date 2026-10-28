# Changelog

## 0.2.2 — 2026-10-28
From the orchestrator acceptance test (7 scenarios, all passed).
- Every agent, skill, LAWS and QUALITY states the plugin version; agents report it and flag a mismatch with `.agents/LAWS.md`. `scripts/versions.py` keeps them in sync and CI checks it.
- README: install from GitHub, restart after update, install the bundles agents name. Seats report missing skills and continue.
- LAWS 3.1: run artifacts may sit untracked on any branch; worktrees go in gitignored `.agents/worktrees/`. Setup adds the ignore line.
- Pipelines pass the run folder by absolute path so worktrees can read inputs.
- LAWS 6: symptoms proven to share the root cause are in scope.
- LAWS 4: a sub-agent orchestrator uses its final report as the question channel.
- LAWS 3.11: deleting material (anything that existed before the run) needs approval.
- LAWS 3.6: helper scripts go in the run folder's `scripts/`.
- QUALITY 5: compliance joins when output or its effect reaches customers. QUALITY 6: wording that can be read the opposite way is at least S3.
- Orchestrator owns intake and plan explicitly, and re-reads `00-status.md` after each update.

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
