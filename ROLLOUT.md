# Roll out to the team

One plugin, installed on each person's Claude account, works in chat, Cowork and Claude Code.

## Team or Enterprise plan (the Owner does this once)
1. Organization settings → Capabilities: turn on **Code execution and file creation** and **Skills**.
2. Organization settings → Plugins & skills → **Add → Sync from GitHub**: `Dolat-Hamza/geevs-ai-skills`.
3. On the Inventory tab, open **geevs-agent-team** → **Default access** → **Required** (or **Installed by default** for a pilot).

Everyone then has it without installing anything. Pushing to `main` and pressing **Re-sync** (or turning on **Sync automatically**) updates everyone.

## One person, any paid plan
Customize → Plugins → **Add → Add marketplace** → `Dolat-Hamza/geevs-ai-skills`, then add **geevs-agent-team**.

Or, without GitHub access in Claude: **Add → Upload plugin** with [dist/geevs-agent-team.zip](dist/geevs-agent-team.zip). Uploaded copies don't update; upload the new zip after each release.

## What runs where

| | Chat | Cowork | Claude Code |
|---|---|---|---|
| Questions, spec approval, release | yes | yes | yes |
| Proof scripts (tests fail then pass, every figure traced) | yes, in the code sandbox | yes | yes, enforced by hooks |
| Separate researcher, builder, reviewer | no, one Claude switches role | yes | yes |
| Budget limit, ask before push | no | hooks load; not yet tested | yes |

Source: [Plugin feature support across platforms](https://claude.com/docs/plugins/platform-support.md), [Manage plugins for your organization](https://claude.com/docs/plugins/admin.md).
