---
name: deliver
description: Run a goal through interview, research, spec, isolated build, independent review and human release. For features, bug fixes, documents and processes.
argument-hint: <goal>
disable-model-invocation: true
---

# Deliver: $ARGUMENTS

Set `RS="python3 <this skill's base directory>/../../scripts/run_state.py"` with the absolute path, and run it from the project root. If `.claude/agent-team.json` is missing, run `/geevs-agent-team:setup` first.

## 1. Interview
Ask at most four questions with AskUserQuestion, only what the request, repo and docs do not answer: the goal, who uses the result, constraints, and what done looks like.

## 2. Start
`$RS new <slug> "<goal>"` prints the run folder's absolute path. Use absolute paths in every brief.

## 3. Research
Spawn `researcher` agents only for open questions: none if the repo answers it, otherwise one per independent question, at most three in parallel. Each writes `<run>/research/<topic>.md`.

## 4. Spec
Fill `<run>/spec.md`. Each acceptance criterion is `- [ ] ACn: <observable pass/fail statement and how to check it>`. For a bug, record the exact reproduction command and output; AC1 is that it no longer reproduces. Run `$RS criteria <slug>`.

**Gate 1:** show the spec to the user and wait for approval. Then `$RS phase <slug> approved`.

## 5. Build
`$RS phase <slug> build`. Spawn one `builder` with the spec path, a branch name, and what not to touch.

## 6. Review
1. `$RS review-round <slug>`. If it fails, the review cap is reached and the run is blocked: report to the user and stop.
2. `$RS phase <slug> review`, then `$RS tree <slug> save <worktree>`.
3. Spawn one `reviewer` with the spec path, the worktree path, and the command `$RS pass <slug> <ACn> "<evidence>"`, run from the project root.
4. `$RS tree <slug> verify <worktree>`. If it fails, the review is void: repeat from step 1.
5. If `$RS check <slug>` fails, send the reviewer's findings to a new `builder` on the same branch, then repeat from step 1.

## 7. Release
`$RS check <slug>` must pass. `$RS phase <slug> release`. Give the user: what changed, the branch, evidence per criterion, and open risks. Pushing, merging and deploying are the user's; project settings ask before each. When the user confirms, `$RS phase <slug> done`.

If the work cannot proceed, `$RS phase <slug> blocked` and tell the user why.
