---
name: agent-team-setup
description: Scaffold the agent team into the current project: copies the agent-knowledge docs, the CLAUDE.md agent section, and the .agents run folder, then fills the knowledge docs from the repo. Run once per project before using /deliver.
---

# agent-team-setup

Obey `.agents/LAWS.md` before anything below. It sets precedence, question budgets, loop limits, issue handling and persona rules.

0. If the project is a git repo on its default branch (main or master), create and switch to `chore/agent-team-setup` first (LAWS 3.1). Report the branch.
1. The plugin root is two levels above this skill's base directory. Its `templates/` folder, `LAWS.md` and `QUALITY.md` live there.
2. Copy `templates/agent-knowledge/` to `docs/agent-knowledge/` in the project root. Do not overwrite files that exist.
3. Copy `templates/.agents/` to `.agents/` in the project root. Copy `LAWS.md`, `QUALITY.md` and `templates/quality/pre-pr-checklist.md` into `.agents/`. Overwrite these three so the project always has the current laws. Re-run this skill after every plugin update to refresh them.
4. Append `templates/CLAUDE.md` to the project's `CLAUDE.md` if the heading "Agent team instructions" is not already present.
5. Fill the knowledge docs from the repo: read README, package manifests, CI config, existing docs and the top-level structure. Fill every empty section and every TODO you can answer with evidence from files, citing the file. Mark the rest `TODO:` with a one-line note of what is needed.
6. Quality tooling: detect the stack. For JS/TS merge `templates/quality/eslint.quality.mjs` into the ESLint config; for Python merge `templates/quality/ruff.quality.toml`. Never overwrite existing rules; report conflicts. Note missing scanners (semgrep, gitleaks, audit) as TODOs.
7. Fill the Commands section of `CLAUDE.md` from package scripts, Makefile or CI config.
8. Report: files created, TODOs remaining, suggested first `/deliver` task (small, real, low risk).
