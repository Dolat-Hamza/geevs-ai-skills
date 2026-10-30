---
name: agent-team
description: "Run a request through the agent-team process in chat: a few questions, a checklist the user approves, the work, then a separate strict check of every item and every figure before handing it over. Use when the user says 'agent team', 'deliver this', 'run it through the process', or asks for client-facing text, figures, pricing, a fix or a document where mistakes are costly. Do not use for quick questions or small edits."
---

# Agent team (chat edition)

Same steps as the Claude Code plugin, run inside one chat. Chat has no separate agents, safety hooks or file access, so the user's approval and the written check are the safeguards. Never send, publish or act outside this chat.

## 1. Questions
Ask at most four short questions, only what the request and attached files don't answer: who it is for, where facts must come from, limits, and what "done" means. Ask them together in one message, then wait.

## 2. Plan
Write a numbered checklist of what the finished work must do. Each item is pass/fail and says how it will be checked, for example "Every figure matches the attached price list". Then ask: "Reply approved, or tell me what to change." Do not start the work until the user replies approved.

## 3. Work
Produce the work. Use only the sources agreed in step 1. If something needed is missing, stop and ask.

## 4. Check
Switch roles: check the work as a strict reviewer who did not write it. Read only the plan, the work and the sources.
- For each checklist item: pass or fail, with the evidence (a quote, a line, a figure).
- For writing with facts: a table with each statement, its source, and the exact source text.
- For each figure that is worked out rather than quoted: show the sum, and recalculate it. If code execution is available, run the calculation.
- For a fix: show the result before and after for each case in the plan.
If anything fails, fix it and check again, at most twice. If it still fails, hand back what you have and say exactly what is wrong.

## 5. Hand over
Give the final work, then the checklist with ticks and evidence, then what was not checked. Ask the user to approve it before it is used anywhere.
