# Live test: geevs-agent-team 1.1.1

- Date: 2026-10-29
- Folder: `/Users/dolathamza/Documents/Claude/Projects/Geevs AI System/agent-team-sandbox-v2` (session started here, `main`, clean, 1 commit `8dc51af`, no git remote)
- Claude Code: `2.1.267` (output of `claude --version`)
- Installed plugin: `~/.claude/plugins/cache/geevs/geevs-agent-team/1.1.1`, from `installed_plugins.json`: version 1.1.1, scope user, gitCommitSha `f7cbcc0955e8a6d16b0132b7b72338fdd73f7bcb`
- Orchestrator model: this session, Opus 5.5 (`claude-opus-5-5`)

## 1. Load

From this session's skill and agent lists:

- Skills: `geevs-agent-team:deliver`, `geevs-agent-team:setup`. Present.
- Agents: `geevs-agent-team:researcher` (Read, Grep, Glob, WebSearch, WebFetch, Write), `geevs-agent-team:builder` (Read, Grep, Glob, Bash, Write, Edit), `geevs-agent-team:reviewer` (Read, Grep, Glob, Bash). Present, with the tool lists from the agent frontmatter; the reviewer has no Write or Edit.

Note: when `setup` was invoked, the skill reported its base directory as the source checkout, `/Users/dolathamza/Documents/Claude/Projects/Geevs AI System/geevs-ai-skills/plugins/geevs-agent-team/skills/setup`, not the cache path. `diff -rq` of the source folder against the cache (excluding `__pycache__`) printed nothing, so the files are identical. All scripts in this test were run from the cache path.

**Result: PASS**

## 2. Setup

Invoked `/geevs-agent-team:setup` (Skill tool), then ran the installed script from the project root:

```
$ python3 ~/.claude/plugins/cache/geevs/geevs-agent-team/1.1.1/scripts/setup_project.py .
{"rules_added": 24, "excludes_added": 3, "settings": ".claude/settings.local.json", "marker": ".claude/agent-team.local.json"}
```

```
$ cat .claude/settings.local.json
{
  "permissions": {
    "deny": [
      "Bash(git push --force *)",
      "Bash(git push -f *)",
      "Bash(git push --force-with-lease *)",
      "Edit(**/.env)",
      "Edit(**/.env.local)",
      "Edit(**/.env.production)",
      "Edit(**/*.pem)",
      "Edit(**/id_rsa)",
      "Edit(**/id_ed25519)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(git reset --hard *)",
      "Bash(gh pr merge *)",
      "Bash(vercel deploy *)",
      "Bash(vercel --prod *)",
      "Bash(vercel promote *)",
      "Bash(npm publish *)",
      "Bash(pnpm publish *)",
      "Bash(yarn publish *)",
      "Bash(terraform apply *)",
      "Bash(terraform destroy *)",
      "Bash(kubectl apply *)",
      "Bash(kubectl delete *)",
      "Bash(helm install *)",
      "Bash(helm upgrade *)"
    ]
  }
}

$ cat .claude/agent-team.local.json
{"version": "1.1.0"}

$ cat .git/info/exclude
# git ls-files --others --exclude-from=.git/info/exclude
# Lines that start with '#' are comments.
# For a project mostly in C, the following would be a good set of
# exclude patterns (uncomment them if you want to use them):
# *.[oa]
# *~
.agents/
.claude/settings.local.json
.claude/agent-team.local.json

$ git status --porcelain
(no output)
```

Note: the marker says `"version": "1.1.0"` although the plugin is 1.1.1 (`VERSION = "1.1.0"` in `scripts/setup_project.py`).

**Result: PASS**

## 3. Deny rules

Run once each, right after setup, in the same session (the rules were picked up without restarting).

```
$ git push --force origin x
Permission to use Bash with command git push --force origin x has been denied.
```
Refused by the local permission `deny` rule `Bash(git push --force *)` from `.claude/settings.local.json`. The hook does not handle push commands. The repo has no remote, so nothing could have been pushed in any case.

```
Write .env with content "A=1"
File is in a directory that is denied by your permission settings.
```
Refused by the local permission `deny` rule `Edit(**/.env)` (Claude Code applies Edit rules to Write). `ls -la .env` afterwards: `No such file or directory`. The hook would not have refused it: replaying the same Write event into `gate.py` printed nothing (exit 0), because `A=1` matches none of its credential patterns.

The refusal message says "File is in a directory that is denied", although the rule names a file, not a directory. That wording comes from Claude Code.

**Result: PASS**

## 4. Commit hook, by replay

No real commit was run. Branch at the time: `main`.

```
$ echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","cwd":"'"$PWD"'","tool_input":{"command":"git commit -m x"}}' | python3 ~/.claude/plugins/cache/geevs/geevs-agent-team/1.1.1/hooks/gate.py
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "Commit on the default branch. Approve only if intended; agents work on branches."}}
[exit 0]
```

**Result: PASS**

## 5. Bug run: `fix-tier-boundaries`

Invoked `/geevs-agent-team:deliver` with the goal text. The interview answers from the brief were used instead of AskUserQuestion: audience is internal callers; the only constraint is the standard library; done means the boundary fees match the table and all tests pass. No researchers were spawned, because the repo answered every question.

Reproduction on `main` before the build:
```
999.99 10.00
1000 10.00
1000.01 5.00
9999.99 50.00
10000 50.00
10000.01 25.00
```

Gate 1: I sent the spec path and AC1 to AC4 to the parent session. It replied: "approved. Gate 1 for fix-tier-boundaries: verified the 4 criteria in spec.md and progress.json on disk (phase spec, budget 5.0)." Then `phase approved`, then `phase build`.

`git worktree list` during the build (20:41:46 UTC, builder running):
```
/Users/dolathamza/Documents/Claude/Projects/Geevs AI System/agent-team-sandbox-v2                                            8dc51af [main]
/Users/dolathamza/Documents/Claude/Projects/Geevs AI System/agent-team-sandbox-v2/.claude/worktrees/agent-af0c71bc54926220a  8dc51af [worktree-agent-af0c71bc54926220a] locked
```
After the builder committed:
```
.../.claude/worktrees/agent-af0c71bc54926220a  b1b2362 [fix/tier-boundaries] locked
```

Builder: branch `fix/tier-boundaries`, commit `b1b2362` "Include tier thresholds in the higher-volume tier". It changed `>` to `>=` in `tier_rate` and added 2 tests. It reported running the new tests red first and then green. It took 9 tool uses, 22,548 tokens and 48 s.

Review: `review-round` printed `review round 1`, then `phase review`, then `tree save` on the worktree. The reviewer recorded AC1 to AC4 through `run_state pass` and reported no failures and no blocking risks. It took 7 tool uses, 17,398 tokens and 30 s.

```
$ run_state.py tree fix-tier-boundaries verify <worktree>
tree unchanged
[exit 0]
$ run_state.py check fix-tier-boundaries
all criteria pass
[exit 0]
$ run_state.py phase fix-tier-boundaries release
release
$ run_state.py status fix-tier-boundaries
{"slug": "fix-tier-boundaries", "phase": "release", "failing": [], "spend_usd": 0.6615, "budget_usd": 5.0}
```

I checked the result myself: `git diff main --stat` shows `fx/fees.py | 2 +-` and `tests/test_fees.py | 10 ++++++++++`, and the tests print `Ran 6 tests ... OK`. `main` is still at `8dc51af`. Nothing was merged or pushed.

`progress.json` at release:
```json
{
  "goal": "Transfers of exactly 1,000 and exactly 10,000 GBP are charged the lower-volume tier; per the README pricing table they should get the higher-volume tier.",
  "phase": "release",
  "review_rounds": 1,
  "criteria": [
    {
      "id": "AC1",
      "text": "The reproduction command above prints `1000 5.00` and `10000 25.00`, and the other four lines unchanged (`999.99 10.00`, `1000.01 5.00`, `9999.99 50.00`, `10000.01 25.00`).",
      "passes": true,
      "evidence": "repro command on branch b1b2362 prints: 999.99 10.00 / 1000 5.00 / 1000.01 5.00 / 9999.99 50.00 / 10000 25.00 / 10000.01 25.00"
    },
    {
      "id": "AC2",
      "text": "`tests/test_fees.py` has tests asserting `transfer_fee(Decimal(\"1000\")) == Decimal(\"5.00\")` and `transfer_fee(Decimal(\"10000\")) == Decimal(\"25.00\")`; they fail against `fx/fees.py` at `8dc51af` and pass on the branch.",
      "passes": true,
      "evidence": "test_lower_boundary_uses_mid_tier and test_upper_boundary_uses_high_tier assert 1000->5.00, 10000->25.00; against fx/fees.py from 8dc51af (temp dir) both FAIL (10.00!=5.00, 50.00!=25.00); on branch they pass"
    },
    {
      "id": "AC3",
      "text": "`python3 -m unittest discover -s tests` exits 0 with all tests passing.",
      "passes": true,
      "evidence": "python3 -m unittest discover -s tests: Ran 6 tests, OK, exit 0"
    },
    {
      "id": "AC4",
      "text": "`git diff main --stat` on the branch touches only `fx/fees.py` and `tests/test_fees.py`, and `fx/fees.py` imports only standard-library modules.",
      "passes": true,
      "evidence": "git diff main --stat: only fx/fees.py (1 line) and tests/test_fees.py (+10); fees.py imports only decimal; main==8dc51af"
    }
  ],
  "created_at": "2026-10-28T20:40:56.000Z",
  "budget_usd": 5.0,
  "tree": "b1b236204e3eabb9e2bae1422fcdb84bf6c0fe7a\n"
}
```

`spend.jsonl` at release:
```
{"main_usd": 0.2961}
{"agent": "geevs-agent-team:builder", "model": "claude-sonnet-5-5", "usd": null}
{"main_usd": 0.6615}
{"agent": "geevs-agent-team:reviewer", "model": "claude-sonnet-5-5", "usd": null}
```

`model` field of each spend entry: builder `claude-sonnet-5-5`, reviewer `claude-sonnet-5-5`. The two `main_usd` lines have no model field. The orchestrator runs on `claude-opus-5-5`.

**Spend accounting is broken for background agents.** Both agents ran async. PostToolUse fires when the Agent call returns, which for an async agent is the launch acknowledgement, before any work. That acknowledgement has `resolvedModel` but no `usage`, so `usd` is `null`. When the agents finished, no spend was logged. `cost.run_total` counts `null` as 0, so `spend_usd` 0.6615 is only the orchestrator's transcript snapshot, taken at the last Agent spawn; the orchestrator's spend after that point is not counted either. The agents' roughly 40k tokens are missing from the total, and the budget hook can never be triggered by agent spend in this mode.

Other observations:
- The builder worktree lives in `.claude/worktrees/`, which setup does not exclude, so `git status --porcelain` on `main` showed `?? .claude/` while the builder ran.
- The run stays at `release`; `phase done` waits for the human's confirmation, per the skill.

**Result: PASS** for the delivery chain (worktree isolation, Gate 1, evidence, tree verify, check). **FAIL** for spend capture (`usd: null` for every agent).

## 6. Stop gate

During the bug run, right after the builder was spawned in the background, with `progress.json` at phase `build` and AC1 to AC4 unverified, I ended my turn once. The turn was not allowed to end. Claude Code returned:

```
Stop hook feedback:
Run is in build with unverified criteria: AC1, AC2, AC3, AC4. Finish review, or set phase to blocked with the reason.
```
and, in the same event:
```
Stop hook blocking error from command: "python3 "${CLAUDE_PLUGIN_ROOT}/hooks/gate.py"": Run is in build with unverified criteria: AC1, AC2, AC3, AC4. Finish review, or set phase to blocked with the reason.
```

Blocked: yes. Side effect: the orchestrator cannot go idle while a background builder runs, so it has to wait inside the turn instead of ending it and being woken by the agent's completion notice. `gate.py` does not read `stop_hook_active`, so every later stop attempt in that phase is blocked too.

**Result: PASS**

## 7. Budget hook, by replay

```
$ run_state new budget-test "x" --budget-usd 0.01
/Users/dolathamza/Documents/Claude/Projects/Geevs AI System/agent-team-sandbox-v2/.agents/runs/budget-test
$ echo '{"agent":"x","usd":0.5}' > .agents/runs/budget-test/spend.jsonl
$ echo '{"hook_event_name":"PreToolUse","tool_name":"Agent","cwd":"'"$PWD"'","transcript_path":"<this session's transcript: ~/.claude/projects/-Users-dolathamza-Documents-Claude-Projects-Geevs-AI-System-agent-team-sandbox-v2/bf855ad5-0fb6-4d5e-a802-f79f65de195f.jsonl>","tool_input":{"subagent_type":"geevs-agent-team:researcher","prompt":"x"}}' | python3 ~/.claude/plugins/cache/geevs/geevs-agent-team/1.1.1/hooks/gate.py
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "Run has spent about $0.50 of its $0.01 budget. Approve to continue, or stop and raise the budget with run_state budget."}}
[exit 0]
$ cat .agents/runs/budget-test/spend.jsonl
{"agent":"x","usd":0.5}
{"main_usd": 0}
$ run_state status budget-test
{"slug": "budget-test", "phase": "spec", "failing": [], "spend_usd": 0.5, "budget_usd": 0.01}
$ run_state phase budget-test blocked
blocked
```

Observations:
- The PreToolUse hook writes to `spend.jsonl` even when it only decides (it appended `{"main_usd": 0}`). `main_usd` is 0 because no assistant message in the transcript is newer than the run's `created_at` a second earlier.
- `run_state new budget-test` repointed `.agents/active-run` from `fix-tier-boundaries` to `budget-test` without a warning, and `phase blocked` then deleted `active-run`. The bug run was at `release`, so nothing was lost here. If a run had been in `build`, starting a second run would silently turn off its Stop gate and budget hook.

**Result: PASS**


## 8. Document run: `customer-fee-note`

Invoked `/geevs-agent-team:deliver` with the goal text. The brief gave no interview answers for this run, so I assumed: audience is customers, the README is the only source, and done means the reviewer checked every figure. I stated these at Gate 1 and the parent accepted them. No researchers were spawned.

Gate 1: I sent the spec path and AC1 to AC6. The parent replied: "approved, Gate 1 for customer-fee-note, with one condition: worked examples must not use exactly 1,000 or 10,000 GBP ... Where they disagree, the README table is the source of truth." I added that condition to the spec's Out of scope, re-ran `criteria` (`6 criteria`), then `phase approved` and `phase build`. I also passed the condition to the builder and the reviewer in their briefs.

`git worktree list` during the build:
```
/Users/dolathamza/Documents/Claude/Projects/Geevs AI System/agent-team-sandbox-v2                                            8dc51af [main]
/Users/dolathamza/Documents/Claude/Projects/Geevs AI System/agent-team-sandbox-v2/.claude/worktrees/agent-ad9ee130ac6ee829e  8dc51af [worktree-agent-ad9ee130ac6ee829e] locked
/Users/dolathamza/Documents/Claude/Projects/Geevs AI System/agent-team-sandbox-v2/.claude/worktrees/agent-af0c71bc54926220a  b1b2362 [fix/tier-boundaries]
```

Builder: branch `docs/customer-fee-note`, commit `5da92f0` "Add customer fee note on minimum fee and rounding". It took 13 tool uses, 22,293 tokens and 44 s. The note it wrote:

```
# Minimum fee and rounding

As set out in the Pricing table section of `README.md`, every transfer pays at least a minimum fee of 2.00 GBP, and fees are rounded half-up to 2 decimal places, meaning a fee that falls exactly halfway between two pennies is rounded up. For example, a 150 GBP transfer is under 1,000 GBP, so the 1.0% rate gives 1.50 GBP, which is below the minimum, so you pay 2.00 GBP; a 250.50 GBP transfer at 1.0% gives 2.505 GBP, which is above the minimum and rounds half-up to 2.51 GBP.
```

Reviewer: it recorded AC1 to AC6 and found no failures and no blocking risks. It took 7 tool uses, 15,414 tokens and 38 s. **It checked every figure against the README.** From its report:

| Figure in note | README source |
|---|---|
| 2.00 GBP minimum | line 21 |
| rounding to 2 decimals, half-up | line 21 |
| 1,000 GBP threshold ("under 1,000") | table row, line 18 |
| 1.0% rate | table row, line 18 |
| 150 GBP, 250.50 GBP | example inputs in the "under 1,000" row |
| 1.50 GBP | 150 x 1.0%, arithmetic shown in the note |
| 2.505 GBP | 250.50 x 1.0%, arithmetic shown in the note |
| 2.51 GBP | 2.505 rounded half-up, shown in the note |

It also checked the code: `transfer_fee(150)` returns 2.00 and `transfer_fee(250.50)` returns 2.51. It found no figures beyond those listed.

```
$ run_state.py tree customer-fee-note verify <worktree>
tree unchanged
[exit 0]
$ run_state.py check customer-fee-note
all criteria pass
[exit 0]
$ run_state.py phase customer-fee-note release
release
$ run_state.py status customer-fee-note
{"slug": "customer-fee-note", "phase": "release", "failing": [], "spend_usd": 0.3981, "budget_usd": 5.0}
$ git -C <worktree> diff main --stat
 docs/customer-fee-note.md | 3 +++
 1 file changed, 3 insertions(+)
```

`progress.json` at release:
```json
{
  "goal": "Write a one-paragraph customer note explaining the minimum fee and rounding rule, citing the README.",
  "phase": "release",
  "review_rounds": 1,
  "criteria": [
    {
      "id": "AC1",
      "text": "`docs/customer-fee-note.md` exists on the branch and has exactly one body paragraph: after any `#` title line and blank lines, the body has no blank line inside it (check with `awk` or by reading the file).",
      "passes": true,
      "evidence": "docs/customer-fee-note.md on branch docs/customer-fee-note: line 1 '# Minimum fee and rounding', line 2 blank (only blank line, awk NF==0), line 3 single paragraph, no blank inside."
    },
    {
      "id": "AC2",
      "text": "The note states that the minimum fee is 2.00 GBP, which matches `README.md` line 21.",
      "passes": true,
      "evidence": "Note line 3 states 'minimum fee of 2.00 GBP'; README.md line 21: 'Minimum fee 2.00 GBP.'"
    },
    {
      "id": "AC3",
      "text": "The note states that fees are rounded to 2 decimal places, with halves rounded up, which matches `README.md` line 21.",
      "passes": true,
      "evidence": "Note states 'rounded half-up to 2 decimal places, meaning a fee exactly halfway between two pennies is rounded up'; README.md line 21: 'Fees round half-up to 2 decimals.'"
    },
    {
      "id": "AC4",
      "text": "The note cites the README by name (`README.md`, pricing table section).",
      "passes": true,
      "evidence": "Note cites 'the Pricing table section of `README.md`'; README.md has '## Pricing table' at line 15."
    },
    {
      "id": "AC5",
      "text": "Every number in the note either appears in the `README.md` pricing table or follows from it by arithmetic shown in the note, and each worked example matches `fx.fees.transfer_fee` (check with `python3 -c 'from decimal import Decimal as D; from fx.fees import transfer_fee as f; print(f(D(\"<amount>\")))'` for each amount used).",
      "passes": true,
      "evidence": "Figures vs README: 2.00 GBP min -> README l.21; 2 decimals/half-up -> l.21; 1,000 GBP threshold and 1.0% rate (under 1,000) -> table l.18; 150 GBP and 250.50 GBP are inputs under 1,000 (table l.18); 150*1.0%=1.50 (arithmetic shown), 1.50<2.00 so 2.00; 250.50*1.0%=2.505 shown, >2.00, half-up -> 2.51. No other figures. fx.fees.transfer_fee: 150 -> 2.00, 250.50 -> 2.51. Neither example at 1,000 or 10,000."
    },
    {
      "id": "AC6",
      "text": "`git diff main --stat` on the branch lists only `docs/customer-fee-note.md`.",
      "passes": true,
      "evidence": "git diff main --stat in worktree: only docs/customer-fee-note.md | 3 +++ (1 file changed); git status clean."
    }
  ],
  "created_at": "2026-10-28T20:46:11.000Z",
  "budget_usd": 5.0,
  "tree": "5da92f00c1eb4e0badc6e8c6d39ad4a024c6d290\n"
}
```

`spend.jsonl` at release:
```
{"main_usd": 0.2067}
{"agent": "geevs-agent-team:builder", "model": "claude-sonnet-5-5", "usd": null}
{"main_usd": 0.3981}
{"agent": "geevs-agent-team:reviewer", "model": "claude-sonnet-5-5", "usd": null}
```
`model` field: builder `claude-sonnet-5-5`, reviewer `claude-sonnet-5-5`. Both `usd` are `null`, the same spend-capture failure as in check 5.

**Result: PASS** for the delivery chain and the figure check. **FAIL** for spend capture.

## 9. Report

### Pass/fail

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Load: skills `deliver`, `setup`; agents `researcher`, `builder`, `reviewer` | PASS | All five present. The skills report the source checkout as their base directory; its files are identical to the cache. |
| 2 | Setup: JSON, settings, exclude, clean status | PASS | `rules_added 24, excludes_added 3`, porcelain empty at setup time |
| 3 | Deny: force push, write `.env` | PASS | Both refused by local permission `deny` rules, not by the hook |
| 4 | Commit hook replay on `main` | PASS | `"permissionDecision": "ask"` |
| 5 | Bug run to release | PASS (delivery) / FAIL (spend) | `check` and `tree verify` pass, 1 review round; every agent `usd: null` |
| 6 | Stop gate mid-build | PASS | Blocked: "Run is in build with unverified criteria: AC1, AC2, AC3, AC4. ..." |
| 7 | Budget hook replay | PASS | `"permissionDecision": "ask"`, "$0.50 of its $0.01 budget" |
| 8 | Document run to release; reviewer checks figures | PASS (delivery) / FAIL (spend) | Reviewer traced 9 figures to README lines 18 and 21; agent `usd: null` |

### `spend_usd` per run (from `run_state status`)

| Run | spend_usd | budget_usd | What it covers |
|---|---|---|---|
| fix-tier-boundaries | 0.6615 | 5.0 | Orchestrator transcript up to the reviewer spawn only. The agents (22,548 + 17,398 tokens) count as 0. |
| budget-test | 0.5 | 0.01 | The hand-written `{"agent":"x","usd":0.5}`, plus `main_usd` 0 |
| customer-fee-note | 0.3981 | 5.0 | Orchestrator up to the reviewer spawn only. The agents (22,293 + 15,414 tokens) count as 0. |

### Behaved differently from the plugin README

1. **Agent spend is not logged** (README: "Spend is logged per agent from the Agent tool's usage data"). In this app, Agent calls return at once with an async launch acknowledgement. PostToolUse sees `resolvedModel` but no `usage`, so it writes `usd: null`. Nothing is logged when the agent finishes. As a result, `spend_usd` leaves out all subagent cost, and the budget hook can be triggered only by orchestrator spend. The orchestrator's spend after the last Agent spawn is not counted either, because `main_usd` is only sampled on PreToolUse Agent.
2. **The `$5` in `skills/deliver/SKILL.md` line 21 is replaced with an argument.** Claude Code expanded `$5` as the 6th word of the goal. The loaded skill read "The default budget is exactly of estimated API cost" (bug run) and "... is explaining of estimated API cost" (document run). Escape it or write "5 USD".
3. **Version mismatch:** `setup_project.py` writes marker `{"version": "1.1.0"}` under plugin 1.1.1.
4. **`git status` is not clean once an agent runs:** Claude Code puts agent worktrees in `.claude/worktrees/`, which setup does not exclude, so `main` shows `?? .claude/`. It also leaves `worktree-agent-*` branches, which `git branch -a` lists next to the named branches.
5. **Claude Code is older than the README requires:** 2.1.267 here, while the README requires 2.1.271 (`omitClaudeMd`) and 2.1.293 (`model: haiku` on Haiku 5.5). Builder and reviewer still resolved to `claude-sonnet-5-5`, as configured. The researcher was never spawned, so Haiku was not exercised. I did not verify whether `omitClaudeMd` took effect.
6. **`run_state new` silently replaces `.agents/active-run`.** Starting `budget-test` moved the pointer off `fix-tier-boundaries`. Had that run been in `build`, its Stop gate and budget hook would have stopped applying with no warning.
7. **The Stop hook ignores `stop_hook_active`,** so it blocks every stop attempt while the phase is open. The orchestrator therefore cannot end its turn and wait for a background builder's completion notice; I waited with foreground polling loops instead.
8. **`tree verify` ignores untracked files** (`--untracked-files=no`), so a reviewer that creates new files in the worktree would pass the check. Not exercised: both reviewers left their worktrees clean.

### Unclear instructions

1. **Task step 8** says to use "the same Gate 1 handling" but gives no interview answers. I assumed some and stated them at Gate 1, where they were accepted.
2. **Deliver skill:** `RS="python3 <path>"` followed by `$RS ...` fails in zsh, the default macOS shell: "no such file or directory: python3 /Users/.../run_state.py". zsh does not split the variable into words. I called `python3 <path>` directly instead.
3. **Deliver skill:** "Start each run in a fresh session (`/clear`)" conflicts with this test, which ran two deliveries and the budget replay in one session. Because `main_usd` only counts transcript entries newer than the run's `created_at`, the second run was still costed separately.
4. **Deliver skill:** "Ask at most four questions with AskUserQuestion" gives no path for a non-interactive run. I replaced the questions with the brief's answers.
5. **Deliver skill, Release:** "When the user confirms, `phase done`". Both runs are left at `release`, since no human confirmed. `.agents/active-run` still names `customer-fee-note`.
6. **Task step 2:** "expect empty" for `git status --porcelain` holds only until the first builder runs (see item 4 of the previous list).
7. **Task step 7:** "`transcript_path` set" does not say which transcript. I used this session's transcript.

### State left behind

- `main` at `8dc51af`, unchanged. No push, merge or publish.
- Branches: `fix/tier-boundaries` (`b1b2362`), `docs/customer-fee-note` (`5da92f0`), and `worktree-agent-af0c71bc54926220a`, `worktree-agent-ad9ee130ac6ee829e` (both at `8dc51af`).
- Worktrees: `.claude/worktrees/agent-af0c71bc54926220a`, `.claude/worktrees/agent-ad9ee130ac6ee829e`.
- Runs: `fix-tier-boundaries` and `customer-fee-note` at `release`, `budget-test` at `blocked`.
