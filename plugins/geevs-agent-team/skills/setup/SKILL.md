---
name: setup
description: Opt the current project into the agent team. Adds permission rules to .claude/settings.json, the hook marker, a CLAUDE.md section and a .gitignore line. Safe to re-run.
disable-model-invocation: true
---

Run from the project root: `python3 <this skill's base directory>/../../scripts/setup_project.py .`

Report the JSON it prints. If the project is a git repository, commit the changes on a new branch, not on main or master.
