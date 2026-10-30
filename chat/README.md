# Chat edition

`agent-team.zip` brings the same process to a normal Claude chat: a few questions, a checklist you approve, the work, then a separate strict check of every item and figure before it is handed over.

Upload it in Claude: **Settings → Capabilities → Skills → Upload skill**, choose `agent-team.zip`. Then start a chat with "Use the agent team:" followed by your request, and paste or attach the source material.

## How it differs from the Claude Code version

| | Claude Code plugin | Chat skill |
|---|---|---|
| Who checks the work | A separate agent that can't edit | The same Claude, switching to a reviewer role |
| Proof | Scripts must pass before release | Written check: every item, source and sum shown |
| Works on | Project files, on its own branch | What you paste or attach |
| Safety rules | Pushes, merges and deploys ask you first | Chat can't push, merge or publish anything |
| Best for | Code and files in a project | Documents, figures and checked answers |

## Tested
Simulated chats with the skill loaded and no tools: a customer note and a pricing fix. Both asked their questions in one go, waited for approval of the plan, and handed over with a check table. The fix's tests, run afterwards, failed on the original code (2 failures, the two bugs) and passed on the fix. The note's figures recomputed exactly (2.505 rounds to 2.51; total 253.01). Not yet tested inside the claude.ai app itself.
