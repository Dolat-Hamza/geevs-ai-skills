# Changelog

## 1.1.2 — 2026-10-29
Fixes from the 1.1.1 live test.
- Agent spend is read from the agent transcript at `SubagentStop`. Background agents reported no usage to `PostToolUse`, so 1.1.1 logged their cost as unknown and the budget saw only the orchestrator.
- Stop hook lets the second stop attempt through (`stop_hook_active`).
- Deliver text no longer contains `$5` or `$RS`, which skill argument substitution and zsh broke.
- Setup excludes `.claude/worktrees/` and records the installed plugin version.
- `run_state new` refuses to replace an open run.

## 1.1.1 — 2026-10-29
- `deliver` and `setup` can be started by Claude as well as typed. The human gates (spec approval, push, merge, deploy) are unchanged.

## 1.1.0 — 2026-10-29
- Run budget: spend per agent and for the main session is logged to `spend.jsonl`; at the budget a hook asks before further agent spawns. `run_state status` shows spend; `run_state budget` raises it.
- Per-agent cost settings: researcher on Haiku, builder and reviewer on Sonnet (reviewer at high effort), turn caps from recorded runs, CLAUDE.md skipped where not needed.
- Setup writes only untracked files (`settings.local.json`, local marker, `.git/info/exclude`), so rules and hooks apply on every branch. Found in the 1.0.0 live test: a marker committed on a branch left `main` unguarded.
- Deliver adds cost rules: fresh session per run, no model or effort change mid-run, paths not contents in briefs.

## 1.0.0 — 2026-10-29
Rewrite. The main session orchestrates; agents reduced from 12 to 3 (researcher, builder, reviewer).
- Gates moved from prose to code: `run_state.py`, project permission rules, opt-in hooks with `ask` instead of hard blocks.
- Removed: LAWS.md, QUALITY.md, 23 templates, severity levels, autonomy levels, persona lists, custom shell parser, version lines, illustrative explainer.
- 0.x history: see git log before this release.
