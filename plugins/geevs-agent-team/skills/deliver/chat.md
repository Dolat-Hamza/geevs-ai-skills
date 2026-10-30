# Deliver in chat

Chat has no agents or hooks, so you run every role yourself and the proofs run as scripts in your code sandbox. `CHECK` stands for `python3 <this skill's base directory>/../../scripts/chat_check.py` written out with the absolute path. If you cannot run code, tell the user to turn on Code execution and file creation under Settings > Capabilities, and stop.

## 1. Interview
Ask at most four questions in one message, only what the request and attachments do not answer. Wait for the answers.

## 2. Spec
Reply with numbered acceptance criteria. Each is a pass/fail statement plus its check: the test, the source line, or the sum. End with "Reply approved, or tell me what to change." Do not start until the user replies approved.

## 3. Build
Work in `/tmp/run/` and save everything as files:
- Sources: save each pasted or attached source verbatim under `sources/`.
- Documents: write the result under `work/`.
- Code: put the code as given in `before/`, copy it to `after/`, then fix it in `after/` and add tests under `after/tests/`.

## 4. Review
Switch roles: you did not write this work. Re-read the spec and the files, not your notes. For each criterion, run its check and give pass or fail with the evidence.

Then the proofs, which must print `"ok": true`:
- Code: `CHECK tests /tmp/run/before /tmp/run/after -- <test command>`. New tests must fail on the original and pass on the fix.
- Documents: write `/tmp/run/claims.json`, a list with one object per factual statement: `file` (`work/<name>`), `claim` (exact text), `source` (`sources/<name>:<line>`, or `:<line>,<line>` for several), `quote` (exact text on that line, or a list with one per line). Every number in the document must appear in some claim. A number not on the quoted lines needs `given` (example inputs as strings, such as `["250.50"]`) or `calc` (exact arithmetic with + - * /, `round(x, 2)` half-up, `max` and `min`, such as `"max(round(150.00 * 1.0 / 100, 2), 2.00)"`). Never put a derived figure in `given`. Run `CHECK claims /tmp/run /tmp/run/claims.json`.

If anything fails, fix it and repeat this step, at most twice. Then stop and report what still fails.

## 5. Release
Give the user the work as a file, the criteria with pass evidence, the proof output, and what was not checked. Sending, publishing and merging are the user's.
