# Changelog

## 1.0.0 — 2026-10-29
Rewrite. The main session orchestrates; agents reduced from 12 to 3 (researcher, builder, reviewer).
- Gates moved from prose to code: `run_state.py`, project permission rules, opt-in hooks with `ask` instead of hard blocks.
- Removed: LAWS.md, QUALITY.md, 23 templates, severity levels, autonomy levels, persona lists, custom shell parser, version lines, illustrative explainer.
- 0.x history: see git log before this release.
