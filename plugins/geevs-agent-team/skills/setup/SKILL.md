---
name: setup
description: Opt this project clone into the agent team. Writes permission rules to .claude/settings.local.json and the hook marker, both excluded from git, so they apply on every branch. Safe to re-run.
---

Run from the project root: `python3 <this skill's base directory>/../../scripts/setup_project.py .`

Report the JSON it prints. Nothing needs committing. Permission rules load only when Claude Code is opened in this folder.
