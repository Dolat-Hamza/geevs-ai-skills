---
name: agent-team-setup
description: Scaffold the agent team into the current project: copies the agent-knowledge docs, the CLAUDE.md agent section, and the .agents run folder, then fills the knowledge docs from the repo. Run once per project before using /deliver.
---

# agent-team-setup

Obey `LAWS.md` in this plugin before anything below. It sets precedence, question budgets, loop limits, issue handling and persona rules.

1. Locate this plugin's `templates/` folder (sibling of `skills/` in the plugin directory).
2. Copy `templates/agent-knowledge/` to `docs/agent-knowledge/` in the project root. Do not overwrite files that exist.
3. Copy `templates/.agents/` to `.agents/` in the project root.
4. Append `templates/CLAUDE.md` to the project's `CLAUDE.md` if the heading "Agent team instructions" is not already present.
5. Fill the knowledge docs from the repo: read README, package manifests, CI config, existing docs and the top-level structure. Replace every TODO you can answer with evidence from files; leave the rest as TODO with a one-line note of what is needed.
6. Quality tooling: detect the stack. For JS/TS merge `templates/quality/eslint.quality.mjs` into the ESLint config; for Python merge `templates/quality/ruff.quality.toml`. Never overwrite existing rules; report conflicts. Note missing scanners (semgrep, gitleaks, audit) as TODOs.
7. Fill the Commands section of `CLAUDE.md` from package scripts, Makefile or CI config.
8. Report: files created, TODOs remaining, suggested first `/deliver` task (small, real, low risk).
