# geevs-agent-team

A Claude Code plugin that runs a piece of work through a fixed, checked process instead of a single chat. You describe what you want; Claude interviews you, writes a spec you approve, has one agent build it on a separate branch, has a second agent check it independently, and hands it back to you to release.

It works for code (features, bug fixes) and for written work (documents, customer notes, processes).

## When to use it

| Use it for | Skip it for |
|---|---|
| Changes you want reviewed before they ship | Quick questions and one-line edits |
| Work other people will rely on: client-facing text, money, shared code | Exploring or prototyping |
| Anything where you want a written record of what was asked, built and checked | Tasks cheaper to just do in a normal chat |

On small tasks it is slower and uses more of your plan than a normal chat. It pays off when a mistake would be expensive.

## How a run works

```
you: /geevs-agent-team:deliver <what you want>

1. Interview   Claude asks up to 4 questions the repo can't answer.
2. Research    Optional. Up to 3 researcher agents look things up and write cited notes.
3. Spec        Claude writes spec.md: the problem, the scope, and pass/fail acceptance criteria.
4. YOU APPROVE Nothing is built until you say yes.
5. Build       A builder agent works on its own branch in a separate copy of the repo.
6. Review      A reviewer agent that did not write the work checks every criterion and
               records evidence. Failures go back to the builder, at most 3 reviews.
7. Release     Claude summarises what changed and the evidence. YOU push or merge.
```

You make two decisions: approving the spec and releasing the result. Everything in between runs on its own.

## The three agents

| Agent | Job | Model | Can it change files? |
|---|---|---|---|
| researcher | Answers one question with sources, writes a note | Haiku | Told to write only its note |
| builder | Implements the approved spec on its own branch | Sonnet | Yes, in its own copy of the repo |
| reviewer | Checks each acceptance criterion end to end and records evidence | Sonnet | No (Write and Edit are removed) |

The coordinating role is your own Claude Code session, so you can answer its questions directly.

## Install

You need Claude Code and access to the Geevs skills repository.

```bash
claude plugin marketplace add Dolat-Hamza/geevs-ai-skills
```
```bash
claude plugin install geevs-agent-team@geevs
```

Restart Claude Code after installing or updating.

## Set up a project (once per project folder)

1. Open Claude Code **in the project's folder**. The safety rules only load when Claude Code is opened there.
2. Run `/geevs-agent-team:setup`.

Setup writes two files, both kept out of git so nothing needs committing and they apply on every branch:

- `.claude/settings.local.json`: the permission rules below.
- `.claude/agent-team.local.json`: a marker that switches the plugin's checks on for this folder.

Projects that have not run setup are untouched.

## Your first run

```
/geevs-agent-team:deliver Transfers of exactly 1,000 GBP are charged the wrong tier; fix it to match the pricing table.
```

Answer the questions, read the spec, and reply to approve it. When Claude reports the run is at release, review the branch and the evidence, then push or merge it yourself.

## What is enforced, and what isn't

These are enforced by code, so they hold even if an agent ignores its instructions:

| Rule | How |
|---|---|
| `git push`, PR merge, `git reset --hard`, deploys and package publishes ask you first | Permission rules from setup |
| Force pushes and edits to `.env` and key files are refused | Permission rules from setup |
| A commit on `main` or `master` asks you first | Plugin hook |
| Text that looks like a password or API key can't be written to a file | Plugin hook |
| Claude is stopped if it tries to end its turn mid-build with criteria unchecked (the first attempt is blocked) | Plugin hook |
| A criterion only passes with recorded evidence, and at most 3 reviews run | `run_state.py` |
| The reviewer can't change the work | Tools removed, and the repo is checked after each review |
| Past the run's usage budget, Claude asks before starting more agents | Plugin hook |

Not enforced: the agents' working style, how good the research is, and anything outside a project that ran setup. Permission rules match the start of a command, so they don't stop wrapped commands such as `bash -c "..."`. For a hard security boundary, turn on Claude Code's sandboxing as well.

## Usage and cost

- Each run has a budget of estimated usage, set to the equivalent of 5 USD by default. Ask Claude to set a different budget when the run starts, or to raise it later.
- Ask Claude for the run's status to see its phase, unchecked criteria and usage so far.
- Measured on test runs: the coordinating session uses about 90% of a run's usage. Running your session on Sonnet (`/model sonnet`) instead of Opus is the biggest saving.
- To see the effect on your plan, run `/usage` before and after a run.

## Where things are saved

Each run gets a folder, `.agents/runs/<name>/`, kept out of git:

| File | What it holds |
|---|---|
| `spec.md` | What you approved |
| `progress.json` | Phase, criteria, pass/fail, evidence |
| `spend.jsonl` | Usage per agent and for the session |
| `research/` | Researcher notes with sources |

The built work itself is on a branch named in the release summary.

## Troubleshooting

| You see | Why | What to do |
|---|---|---|
| Rules don't apply (for example a force push isn't refused) | Claude Code wasn't opened in the project folder, or setup wasn't run there | Open Claude Code in that folder, run setup |
| "run '...' is still open" | One run at a time per project | Finish it, or ask Claude to mark it done or blocked |
| "review limit of 3 reached" | The build failed review three times | Read the reviewer's findings and decide what to change |
| An approval prompt about the budget | The run passed its usage budget | Approve to continue, or stop |
| Claude won't end its turn mid-build | Criteria are still unchecked | Let the review finish, or ask Claude to mark the run blocked |
| A new version doesn't seem to apply | Sessions keep the version they started with | Restart Claude Code |

To switch a project off, delete `.claude/agent-team.local.json`, and remove the rules from `.claude/settings.local.json` if you want those gone too.

## What's in this folder

| Path | Contents |
|---|---|
| `agents/` | researcher, builder, reviewer |
| `skills/` | `deliver` and `setup` |
| `hooks/` | commit, credential, Stop and budget checks; usage pricing |
| `scripts/` | run state and project setup |
| `tests/` | 58 unit tests |

Run the tests from the repository root with:

```bash
python3 -m unittest discover -s plugins/geevs-agent-team/tests
```

Test reports are in the repository's `reports/` folder.
