---
name: deliver
description: Run a goal through interview, research, spec, isolated build, independent review and human release. Use when asked to deliver, build, fix or write something non-trivial: features, bug fixes, documents, processes.
argument-hint: <goal>
---

# Deliver: $ARGUMENTS

Below, `RS` stands for `python3 <this skill's base directory>/../../scripts/run_state.py` written out with the absolute path. Run it from the project root. If `.claude/agent-team.local.json` is missing, run `/geevs-agent-team:setup` first.

## Cost rules
- Start each run in a fresh session (`/clear`); the orchestrating conversation is re-read on every call.
- Do not change model or effort during a run; either change invalidates the prompt cache.
- Pass file paths in briefs, never file contents. Agents write to files and return short summaries.
- Check spend with `RS status <slug>`. A hook asks before any agent spawn once the budget is reached.

## 1. Interview
Ask at most four questions with AskUserQuestion, only what the request, repo and docs do not answer: the goal, who uses the result, constraints, and what done looks like.

## 2. Start
`RS new <slug> "<goal>" [--budget-usd N]` prints the run folder's absolute path. The default budget is 5 USD of estimated API cost. Use absolute paths in every brief.

## 3. Research
Spawn `researcher` agents only for open questions: none if the repo or one search answers it, otherwise one per independent question, at most three in parallel. Each writes `<run>/research/<topic>.md`.

## 4. Spec
Fill `<run>/spec.md`. Each acceptance criterion is `- [ ] ACn: <observable pass/fail statement>. Check: <command, file:line or source in backticks>`. `RS criteria` rejects any criterion without a backticked check. For a bug, record the exact reproduction command and output; AC1 is that it no longer reproduces. Run `RS criteria <slug>`.

**Gate 1:** show the spec to the user and wait for approval. Then `RS phase <slug> approved`.

## 5. Build
`RS phase <slug> build`. Spawn one `builder` with the spec path, a branch name, and what not to touch.

## 6. Review
1. `RS review-round <slug>`. If it fails, the review cap is reached and the run is blocked: report to the user and stop.
2. `RS phase <slug> review`, then `RS tree <slug> save <worktree>`.
3. Spawn one `reviewer` with the spec path, the worktree path, and the command `RS pass <slug> <ACn> "<evidence>"`, run from the project root.
4. `RS tree <slug> verify <worktree>`. If it fails, the review is void: repeat from step 1.
5. Proofs, chosen by what the branch changed:
   - Code: `RS redgreen <slug> <worktree> -- <test command>`. New tests must fail on the base code and pass on the branch.
   - Documents: save the reviewer's claims list to `<run>/claims.json`, then `RS claims <slug> <worktree> <run>/claims.json`. Every claim must appear in the document, every quote at its cited source line, and every number in some claim; derived numbers are recomputed from their `calc`.
6. If `RS check <slug>` fails, send the reviewer's findings and any failed proof to a new `builder` on the same branch, then repeat from step 1.

## 7. Release
`RS check <slug>` must pass. `RS phase <slug> release`. Give the user: what changed, the branch, evidence per criterion, and open risks. Pushing, merging and deploying are the user's; project settings ask before each. When the user confirms, `RS phase <slug> done`.

If the work cannot proceed, `RS phase <slug> blocked` and tell the user why.
