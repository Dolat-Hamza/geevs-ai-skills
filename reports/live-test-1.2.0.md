# Live test: geevs-agent-team 1.2.0

Date: 2026-10-29. Folder: `agent-team-sandbox-v2`, `main` at `8dc51af`. Claude Code 2.1.309.
`RS` = `python3 ~/.claude/plugins/cache/geevs/geevs-agent-team/1.2.0/scripts/run_state.py`, run from this folder.

## 1. Load and setup

`claude plugin list`:
```
  ❯ geevs-agent-team@geevs
    Version: 1.2.0
    Scope: user
    Status: ✔ enabled
```
`plugin.json` `"version": "1.2.0"`. Agents in the session: `geevs-agent-team:builder`, `geevs-agent-team:researcher`, `geevs-agent-team:reviewer` (3; files `agents/builder.md`, `researcher.md`, `reviewer.md`). Skills: `geevs-agent-team:deliver`, `geevs-agent-team:setup` (2).

`/geevs-agent-team:setup` (base directory reported as the 1.2.0 cache):
```
{"rules_added": 24, "excludes_added": 1, "settings": ".claude/settings.local.json", "marker": ".claude/agent-team.local.json"}
porcelain:[]
```
Marker: `{"version": "1.2.0"}`. `.git/info/exclude` tail: `.agents/`, `.claude/settings.local.json`, `.claude/agent-team.local.json`, `.claude/worktrees/`.

**Result: PASS**

## 2. Criteria rule

```
$ RS new rule-check x
/Users/dolathamza/Documents/Claude/Projects/Geevs AI System/agent-team-sandbox-v2/.agents/runs/rule-check
$ grep AC1 .agents/runs/rule-check/spec.md
- [ ] AC1: it works
$ RS criteria rule-check
error: criteria must name their check in backticks: AC1
exit=1
$ RS phase rule-check blocked
blocked
exit=0
```
`.agents/active-run` removed by `blocked` (`ls .agents` → `runs`).

**Result: PASS**

## 3. Code run: `fix-tier-boundaries`

Interview answers taken from the brief (no AskUserQuestion; this run is non-interactive): internal callers; standard library only; done = boundary fees match the table and all tests pass. No researcher spawned: the README answers the question.

Reproduction on `main`:
```
$ python3 -c 'from decimal import Decimal as D; from fx.fees import transfer_fee as f; print(f(D("1000")), f(D("10000")))'
10.00 50.00
```

**`RS criteria` refused the first spec** (found defect, confirmed by the starting session at Gate 1):
```
$ RS criteria fix-tier-boundaries
error: criteria must name their check in backticks: AC2
exit=1
```
AC2's check was `` `RS redgreen fix-tier-boundaries <worktree> -- python3 -m unittest discover -s tests` ``. It has a backticked check, but `run_state.py:89` also rejects any criterion containing `<` (meant to catch the template's `<observable statement>`), so a placeholder or a comparison like `amount < 1000` inside the check fails with a misleading message. Reworded to `` `run_state redgreen fix-tier-boundaries` on the build worktree with `python3 -m unittest discover -s tests` `` → `5 criteria`.

Gate 1: spec path and 5 criteria sent to the starting session; reply "approved". `RS phase approved` → `approved`, `RS phase build` → `build`.

Builder (`geevs-agent-team:builder`, background): worktree `.claude/worktrees/agent-a3ae0da451a64062e`, branch `fix/tier-boundaries`, commit `bdf5588 Make FX fee tier thresholds inclusive`. Diff to `fx/fees.py`:
```
-        if amount > threshold:
+        if amount >= threshold:
```
plus 3 tests in `tests/test_fees.py`.

Stop hook while waiting for the background builder: first stop blocked with "Run is in build with unverified criteria: AC1, AC2, AC3, AC4, AC5. Finish review, or set phase to blocked with the reason."; the second stop went through (1.1.2 `stop_hook_active` fix works). Same during review ("Run is in review ...").

Review:
```
$ RS review-round fix-tier-boundaries
review round 1
$ RS phase fix-tier-boundaries review
review
$ RS tree fix-tier-boundaries save <worktree>
tree saved
```
Reviewer (`geevs-agent-team:reviewer`) ran `RS pass` for AC1–AC5 and reported no failures and no blocking risks. For AC2 it ran the new tests against `git show main:fx/fees.py` in a scratch dir: 2 failures `Decimal('10.00') != Decimal('5.00')`, `Decimal('50.00') != Decimal('25.00')`.

Proofs and check:
```
$ RS tree verify
tree unchanged
$ RS check (before proof)
error: proof missing or out of date: test-first (redgreen)
exit=1
$ RS redgreen fix-tier-boundaries <worktree> -- python3 -m unittest discover -s tests
{"ok": true, "head": "bdf55888221d49929288563a550ecd5b01a89920", "base": "8dc51af784653670dbbccbbf7f18a656e6bfc73c", "tests": ["tests/test_fees.py"], "red_exit": 1, "green_exit": 0}
exit=0
$ RS check
all criteria pass with proofs
exit=0
$ RS phase fix-tier-boundaries release
release
```
`RS check` refused once (before the redgreen proof), with "proof missing or out of date: test-first (redgreen)". No other refusal.

`progress.json` at release:
```json
{
  "goal": "Transfers of exactly 1,000 and exactly 10,000 GBP are charged the lower-volume tier; per the README pricing table they should get the higher-volume tier.",
  "phase": "release",
  "review_rounds": 1,
  "criteria": [
    {
      "id": "AC1",
      "text": "The reproduction no longer reproduces; it prints 5.00 25.00. Check: `python3 -c 'from decimal import Decimal as D; from fx.fees import transfer_fee as f; print(f(D(\"1000\")), f(D(\"10000\")))'`",
      "passes": true,
      "evidence": "repro in worktree prints '5.00 25.00'"
    },
    {
      "id": "AC2",
      "text": "New unit tests assert transfer_fee(1000) == 5.00 and transfer_fee(10000) == 25.00, and fail on the unfixed code. Check: `run_state redgreen fix-tier-boundaries` on the build worktree with `python3 -m unittest discover -s tests`",
      "passes": true,
      "evidence": "new tests test_lower_boundary_uses_mid_tier/test_upper_boundary_uses_high_tier assert 5.00 and 25.00; against main's fx/fees.py (scratch copy) 2 failures: 10.00 != 5.00, 50.00 != 25.00; pass on fix"
    },
    {
      "id": "AC3",
      "text": "Amounts just below each threshold keep the lower-volume tier: 999.99 gives 10.00 and 9999.99 gives 50.00. Check: `python3 -c 'from decimal import Decimal as D; from fx.fees import transfer_fee as f; print(f(D(\"999.99\")), f(D(\"9999.99\")))'`",
      "passes": true,
      "evidence": "999.99 and 9999.99 print '10.00 50.00'"
    },
    {
      "id": "AC4",
      "text": "The full test suite passes. Check: `python3 -m unittest discover -s tests`",
      "passes": true,
      "evidence": "python3 -m unittest discover -s tests: Ran 7 tests OK"
    },
    {
      "id": "AC5",
      "text": "Only fx/fees.py and tests/test_fees.py change and no non-stdlib import is added. Check: `git diff --name-only main...HEAD`",
      "passes": true,
      "evidence": "git diff --name-only main...HEAD: fx/fees.py, tests/test_fees.py; diff only changes > to >= and adds tests, no new imports"
    }
  ],
  "created_at": "2026-10-29T14:08:59.000Z",
  "budget_usd": 5.0,
  "tree": "bdf55888221d49929288563a550ecd5b01a89920\n",
  "worktree": "/Users/dolathamza/Documents/Claude/Projects/Geevs AI System/agent-team-sandbox-v2/.claude/worktrees/agent-a3ae0da451a64062e",
  "proofs": {
    "code": {
      "ok": true,
      "head": "bdf55888221d49929288563a550ecd5b01a89920",
      "base": "8dc51af784653670dbbccbbf7f18a656e6bfc73c",
      "tests": [
        "tests/test_fees.py"
      ],
      "red_exit": 1,
      "green_exit": 0
    }
  }
}
```

Starting the document run while this run sat at `release`:
```
$ RS new customer-fee-note "x"
error: run 'fix-tier-boundaries' is still open; set it to done or blocked first
exit=1
```
(1.1.2 fix works.) Release summary sent to the starting session, asking it to confirm `done`.

**Result: PASS**

Starting session replied "done"; `RS phase fix-tier-boundaries done` → `done`.

## 4. Document run: `customer-fee-note`

Interview answers from the brief: retail customers; README is the only source; done = every figure traced to a README line. No researcher spawned. `RS criteria customer-fee-note` → `6 criteria` on the first try. Gate 1: spec and criteria sent to the starting session; reply "approved" (it noted AC4 bans any mention of 1,000/10,000, stricter than intended but acceptable). `approved` → `build`.

Builder: worktree `.claude/worktrees/agent-a0a8fedb19218894c`, branch `docs/customer-fee-note`, commit `c8b340e Add customer fee note`. The note:
```
# Minimum fee and rounding

Every transfer has a minimum fee of 2.00 GBP, and fees round half-up to 2 decimals (README.md, line 21). For example, on a transfer of 100 GBP the rate is 1.0% (README.md, line 18), which would be 1.00 GBP, but because that is below the minimum, the fee is 2.00 GBP (README.md, line 21).
```
Stop hook blocked the first stop in `build` and in `review` again, as in the code run.

`RS review-round` → `review round 1`; `RS phase review`; `RS tree save` → `tree saved`. Reviewer passed AC1–AC6 with no failures or risks and returned this claims list, saved verbatim to `.agents/runs/customer-fee-note/claims.json`:
```json
[
  {"file": "docs/customer-fee-note.md", "claim": "Every transfer has a minimum fee of 2.00 GBP", "source": "README.md:21", "quote": "Minimum fee 2.00 GBP. Fees round half-up to 2 decimals."},
  {"file": "docs/customer-fee-note.md", "claim": "fees round half-up to 2 decimals (README.md, line 21)", "source": "README.md:21", "quote": "Minimum fee 2.00 GBP. Fees round half-up to 2 decimals."},
  {"file": "docs/customer-fee-note.md", "claim": "on a transfer of 100 GBP the rate is 1.0% (README.md, line 18)", "source": "README.md:18", "quote": "| under 1,000 | 1.0% |"},
  {"file": "docs/customer-fee-note.md", "claim": "which would be 1.00 GBP", "source": "README.md:18", "quote": "| under 1,000 | 1.0% |"},
  {"file": "docs/customer-fee-note.md", "claim": "because that is below the minimum, the fee is 2.00 GBP (README.md, line 21)", "source": "README.md:21", "quote": "Minimum fee 2.00 GBP. Fees round half-up to 2 decimals."}
]
```

Proofs and check:
```
$ RS tree customer-fee-note verify <worktree>
tree unchanged
$ RS check customer-fee-note   (before proof)
error: proof missing or out of date: source tracing (claims)
exit=1
$ RS claims customer-fee-note <worktree> <run>/claims.json
{"ok": true, "head": "c8b340e7ef6630eb0fcd0c9f20312e6d1a69685d", "claims": 5, "problems": []}
exit=0
$ RS check customer-fee-note
all criteria pass with proofs
exit=0
```
(Step 5 ran here, before release; see below.) Then `RS phase customer-fee-note release` → `release`.

`progress.json` at release:
```json
{
  "goal": "Write a one-paragraph customer note explaining the minimum fee and rounding rule, with one worked example, citing the README. Avoid exactly 1,000 and 10,000 GBP.",
  "phase": "release",
  "review_rounds": 1,
  "criteria": [
    {
      "id": "AC1",
      "text": "`docs/customer-fee-note.md` exists and its body is exactly one paragraph (one non-heading text block). Check: `cat docs/customer-fee-note.md`",
      "passes": true,
      "evidence": "cat -n docs/customer-fee-note.md: heading line 1, one text paragraph on line 3, no other blocks"
    },
    {
      "id": "AC2",
      "text": "The note states the minimum fee of 2.00 GBP and the half-up rounding to 2 decimals, each attributed to the README. Check: `README.md:21`",
      "passes": true,
      "evidence": "Note line 3 states \"minimum fee of 2.00 GBP\" and \"round half-up to 2 decimals (README.md, line 21)\"; README.md:21 \"Minimum fee 2.00 GBP. Fees round half-up to 2 decimals.\""
    },
    {
      "id": "AC3",
      "text": "The note has exactly one worked example, and its amount, rate and fee match the README table and `transfer_fee` on main. Check: `python3 -c 'from decimal import Decimal as D; from fx.fees import transfer_fee as f; print(f(D(\"AMOUNT\")))'` with the example's amount",
      "passes": true,
      "evidence": "One example (100 GBP, 1.0%, fee 2.00). README.md:18 \"| under 1,000 | 1.0% |\"; transfer_fee(Decimal(\"100\")) prints 2.00; 1.0% of 100 = 1.00 < minimum 2.00"
    },
    {
      "id": "AC4",
      "text": "The note never mentions 1,000 or 10,000 GBP. Check: `grep -nE '(^|[^0-9.,])(1,?000|10,?000)([^0-9,]|$)' docs/customer-fee-note.md` prints nothing",
      "passes": true,
      "evidence": "grep -nE (1,?000|10,?000) pattern on docs/customer-fee-note.md prints nothing (rc=1)"
    },
    {
      "id": "AC5",
      "text": "Every factual statement and every number in the note traces to a README line. Check: `run_state claims customer-fee-note` with the reviewer's claims list",
      "passes": true,
      "evidence": "Every number in note (2.00, 2, 21, 100, 1.0%, 18, 1.00) covered by reviewer claims list, each traced to README.md:18 or README.md:21"
    },
    {
      "id": "AC6",
      "text": "Only `docs/customer-fee-note.md` changes on the branch. Check: `git diff --name-only main...HEAD`",
      "passes": true,
      "evidence": "git diff --name-only main...HEAD prints only docs/customer-fee-note.md; git status clean"
    }
  ],
  "created_at": "2026-10-29T14:13:35.000Z",
  "budget_usd": 5.0,
  "tree": "c8b340e7ef6630eb0fcd0c9f20312e6d1a69685d\n",
  "worktree": "/Users/dolathamza/Documents/Claude/Projects/Geevs AI System/agent-team-sandbox-v2/.claude/worktrees/agent-a0a8fedb19218894c",
  "proofs": {
    "docs": {
      "ok": true,
      "head": "c8b340e7ef6630eb0fcd0c9f20312e6d1a69685d",
      "claims": 5,
      "problems": []
    }
  }
}
```
Starting session confirmed "done" after verifying on disk; `RS phase customer-fee-note done` → `done`, `.agents/active-run` removed.

**Result: PASS**

## 5. Negative proof

Removed the claim for the worked example (`"on a transfer of 100 GBP the rate is 1.0% (README.md, line 18)"`) into `.agents/runs/customer-fee-note/claims-missing-example.json`:
```
$ RS claims customer-fee-note <worktree> <run>/claims-missing-example.json
error: docs proof failed: number 1.0 has no sourced claim; number 100 has no sourced claim; number 18 has no sourced claim
exit=1
$ RS check customer-fee-note
error: proof missing or out of date: source tracing (claims)
exit=1
$ RS claims customer-fee-note <worktree> <run>/claims.json
{"ok": true, "head": "c8b340e7ef6630eb0fcd0c9f20312e6d1a69685d", "claims": 5, "problems": []}
exit=0
$ RS check customer-fee-note
all criteria pass with proofs
exit=0
```
The failure names the uncovered numbers: the amount `100`, the rate `1.0` and the citation's line number `18`. A failed proof replaces the passing one, so `check` refuses until the full list is rerun. The run ends passing.

**Result: PASS**

## 6. Spend

`fix-tier-boundaries/spend.jsonl`:
```
{"main_usd": 0.2608}
{"agent_id": "a3ae0da451a64062e", "agent": "geevs-agent-team:builder", "models": ["claude-sonnet-5-5"], "usd": 0.0585}
{"main_usd": 0.4047}
{"agent_id": "a98a295f5db2d504f", "agent": "geevs-agent-team:reviewer", "models": ["claude-sonnet-5-5"], "usd": 0.053}
```
```
$ RS status fix-tier-boundaries
{"slug": "fix-tier-boundaries", "phase": "done", "failing": [], "spend_usd": 0.5162, "budget_usd": 5.0}
```

`customer-fee-note/spend.jsonl`:
```
{"main_usd": 0.1921}
{"agent_id": "a0a8fedb19218894c", "agent": "geevs-agent-team:builder", "models": ["claude-sonnet-5-5"], "usd": 0.0805}
{"main_usd": 0.353}
{"agent_id": "a9b7e0986aca5affb", "agent": "geevs-agent-team:reviewer", "models": ["claude-sonnet-5-5"], "usd": 0.0479}
```
```
$ RS status customer-fee-note
{"slug": "customer-fee-note", "phase": "release", "failing": [], "spend_usd": 0.4814, "budget_usd": 5.0}
```

Model per agent entry (the field is now `models`, a list):

| Run | Agent | models | usd |
|---|---|---|---|
| fix-tier-boundaries | geevs-agent-team:builder | `["claude-sonnet-5-5"]` | 0.0585 |
| fix-tier-boundaries | geevs-agent-team:reviewer | `["claude-sonnet-5-5"]` | 0.053 |
| customer-fee-note | geevs-agent-team:builder | `["claude-sonnet-5-5"]` | 0.0805 |
| customer-fee-note | geevs-agent-team:reviewer | `["claude-sonnet-5-5"]` | 0.0479 |

Agent cost is now logged at `SubagentStop` with a number, not `null` as in 1.1.1. `spend_usd` = the latest `main_usd` snapshot + the agents' costs (0.4047 + 0.0585 + 0.053 = 0.5162; 0.353 + 0.0805 + 0.0479 = 0.4814). The researcher was never spawned, so Haiku was not exercised.

**Result: PASS** (with the main-session gap noted in "Behaved differently" item 2)

## 7. Report

### Pass/fail

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Load 1.2.0, 3 agents, 2 skills; setup; clean status | PASS | `Version: 1.2.0`; builder/researcher/reviewer; deliver/setup; `rules_added 24`, marker `{"version": "1.2.0"}`, porcelain empty |
| 2 | Criteria rule | PASS | `error: criteria must name their check in backticks: AC1`, exit 1; `phase blocked` → `blocked` |
| 3 | Code run to release | PASS | redgreen `red_exit 1`, `green_exit 0`, `ok true` at `bdf5588`; `check` refused once before the proof, then "all criteria pass with proofs"; 1 review round |
| 4 | Document run to release | PASS | 5 claims from the reviewer; `claims` `ok true`, no problems, at `c8b340e`; `check` refused once before the proof, then passed |
| 5 | Negative claims proof | PASS | "number 1.0 has no sourced claim; number 100 has no sourced claim; number 18 has no sourced claim"; full list passes again |
| 6 | Spend | PASS | Per-agent `usd` recorded for all 4 agents, models `claude-sonnet-5-5` |

### Spend per run

| Run | spend_usd | main_usd (last snapshot) | agents | budget_usd |
|---|---|---|---|---|
| fix-tier-boundaries | 0.5162 | 0.4047 | 0.1115 | 5.0 |
| customer-fee-note | 0.4814 | 0.353 | 0.1284 | 5.0 |

### Behaved differently from the plugin README

1. **`RS criteria` rejects any criterion containing `<`**, even when it has a backticked check (`run_state.py:89`, `or "<" in c["text"]`). A check like `` `RS redgreen slug <worktree> -- ...` `` or a comparison `amount < 1000` fails with "criteria must name their check in backticks", which is misleading. The README promises only "every acceptance criterion names how it is checked". The starting session confirmed this as a defect.
2. **Main-session spend after the last agent spawn is still not counted.** `main_usd` is sampled only on `PreToolUse` for `Agent`, so the proofs, `check`, release and Gate messages after the reviewer spawn are not in `spend_usd`. 1.1.2 fixed agent spend; this gap from 1.1.1 remains.
3. **The claims proof checks that a quote is present, not that it supports the claim.** The claim "which would be 1.00 GBP" passed with the quote `| under 1,000 | 1.0% |` from `README.md:18`. 1.00 is computed, not on that line, and the proof cannot tell. The README says "every fact in a document must trace to a source line"; derived figures pass as long as some claim with any valid quote contains them.
4. **Citation line numbers count as numbers.** "(README.md, line 18)" makes `18` a number that needs a claim (the negative proof listed it). This works, but it means citations are traced like facts.
5. **Spend entries use `models` (a list) and `agent_id`,** not `model` as in 1.1.1. The README does not describe the fields.
6. **Leftover branches:** `worktree-agent-a0a8fedb19218894c` and `worktree-agent-a3ae0da451a64062e` (both at `8dc51af`) sit beside the named branches. `git status --porcelain` on `main` stays empty now that setup excludes `.claude/worktrees/` (1.1.2 fix works).
7. **Fixed since 1.1.1 and seen working:** agent `usd` is logged (no `null`); the Stop hook blocks the first stop and lets the second through; `RS new` refuses while another run is open; the marker records `1.2.0`; skill text no longer breaks on `$5`/`$RS`.

### Unclear instructions

1. **Deliver step 1 (Interview)** says to use AskUserQuestion, with no path for a non-interactive run. I took the answers from the brief.
2. **Deliver step 6.5 vs reviewer.md item 2:** the reviewer marks AC2 (redgreen) and AC5 (claims) as passing before the orchestrator runs the proof. So `pass` evidence and the proof are separate, and the criterion is "passing" before it is proven. `check` still blocks release without the proof, so nothing slips through, but the order is confusing.
3. **Deliver Release:** "When the user confirms, `RS phase done`." `RS new` refuses while a run sits at `release`, so a second run needs the first confirmed `done` (or `blocked`). The skill doesn't say this. I asked the starting session to confirm `done` for the code run.
4. **Deliver Cost rules:** "Start each run in a fresh session (`/clear`)" conflicts with this task, which ran both runs in one session. Each run's `main_usd` counts from its own `created_at`, so the runs were still costed apart.
5. **Task step 5:** "the claim that covers the worked example": two claims are part of the example ("100 GBP ... 1.0%" and "which would be 1.00 GBP"). I removed the first, which holds the amount and rate.
6. **Task step 5 order:** it comes after release in the task list, but a failed `RS claims` replaces the recorded proof. I ran it before `phase release`, so the run reached release with a passing proof.

### State left behind

- `main` at `8dc51af`, unchanged. Nothing pushed, merged or published.
- Branches: `fix/tier-boundaries` (`bdf5588`), `docs/customer-fee-note` (`c8b340e`), plus two `worktree-agent-*` branches at `8dc51af`.
- Worktrees: `.claude/worktrees/agent-a3ae0da451a64062e`, `.claude/worktrees/agent-a0a8fedb19218894c`.
- Runs: `rule-check` blocked, `fix-tier-boundaries` done, `customer-fee-note` done (no active run).
