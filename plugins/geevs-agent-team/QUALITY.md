# QUALITY — standards every production and review agent enforces

Plugin version: 0.2.2.

Companion to `LAWS.md`. Laws say what may happen; this file says what "good" means. A PR or deliverable that misses a hard limit here fails its gate.

## 1. Clean code
- Names say what a thing is or does. No abbreviations except domain ones in the glossary.
- One function, one job. Max 30 lines, max 4 parameters, max 3 levels of nesting.
- No dead code, commented-out code, or TODOs without an owner and a run slug.
- Comments explain why, in one or two lines. Never what, never paragraphs.
- No duplication: a third copy of the same logic becomes a function.
- Errors handled where they can be acted on, never swallowed. Every catch logs or rethrows with context.
- Explicit types at module boundaries. No `any`, no untyped public functions.
- Dependencies: add only with a one-line reason in the PR, pinned, licence compatible with the project's licence and recorded in its attribution or NOTICE file (create one if missing).
- Match the surrounding conventions. Consistency beats preference.

## 2. Complexity limits (hard)
| Metric | Limit | Tool |
|---|---|---|
| Cognitive complexity per function | 15 | eslint-plugin-sonarjs `cognitive-complexity`, radon / ruff C901 for Python, gocyclo for Go |
| Cyclomatic complexity per function | 10 | same |
| Function length | 30 lines | eslint `max-lines-per-function`, ruff PLR0915 |
| File length | 400 lines | eslint `max-lines` |
| Nesting depth | 3 | eslint `max-depth` |
| Parameters | 4 | eslint `max-params`, ruff PLR0913 |

Over a limit: refactor before review. Early returns, extracted functions, lookup tables instead of branches, guard clauses instead of nested ifs. A limit may be exceeded only with a `// complexity: <reason>` line and reviewer sign-off, logged in the decision log.

## 3. Testing
- Changed or new logic has tests. Tests assert behaviour from the spec's acceptance criteria, not implementation details.
- Test first where practical: failing test, then code.
- Unit for logic, integration for boundaries, end-to-end for the user-visible path of the task.
- Tests are deterministic. Time, randomness and network are injected or faked.
- Never delete, skip or loosen a test to pass. Flaky tests are reported with evidence.
- Coverage is a signal, not a target; untested lines in changed code are listed in the report.

## 4. Security (checked by developer before PR, verified by reviewer)
- OWASP Top 10 pass on the change: injection, broken auth, sensitive data exposure, XXE, broken access control, misconfiguration, XSS, insecure deserialization, vulnerable components, insufficient logging.
- Input validated at the boundary; output encoded for its context.
- Authorization checked server-side on every data access the change touches.
- Secrets only from the environment or a secret manager. Never in code, config, logs, run artifacts or chat.
- Dependencies audited: `npm audit` / `pip-audit` / `cargo audit` clean of high and critical, or each exception justified.
- Static scan: semgrep (or the project's SAST) clean on changed files. Use a pinned ruleset offline-safe: `semgrep scan --config p/<language> --metrics=off <files>`; `--config auto` does not work with metrics off. Secrets scan (gitleaks or equivalent) clean on the diff.
- Logging carries no PII, tokens or card data. Errors shown to users carry no stack traces.
- Anything touching auth, payments, PII, uploads, external calls or infrastructure pulls `specialist-security` at plan time (`/deliver` stage 05) or isolate time (`/fix-issue` stage 3), per LAWS 3.3.

## 5. Compliance
- Data classification named in the spec: public, internal, confidential, client, personal. Handling follows `docs/agent-knowledge/engineering-rules-and-standards.md`.
- Personal data: minimum needed, purpose stated, retention stated, deletable. Never copied into run folders.
- Audit trail: every run keeps its artifacts; every release names the approver.
- Licences: new code or content respects source licences; attributions recorded.
- Accessibility: user-facing UI meets WCAG 2.2 AA (contrast, keyboard, labels, focus). Documents use headings, alt text, plain language.
- Regulated content (FX, payments, financial promotions, contracts, tax): drafted only with `specialist-compliance` involved whenever the output, or its effect, reaches customers. Internal-only code and docs do not need it (`/deliver` stage 05, `/fix-issue` stage 3), marked "needs human approval", never published by an agent.
- Client-facing material carries no commitments on pricing, timelines or guarantees that a human did not approve.

## 6. Documents and deliverables
- Structure from `04-design.md`; one idea per paragraph; headings carry the argument.
- Every number, quote and claim cited to a source the reader can open.
- Terminology from the glossary; no synonyms for the same concept.
- Wording a reader could take the opposite way (cheaper vs dearer, before vs after, included vs extra) is a defect of at least S3, never cosmetic.
- Audience read-through by QA: a named reader can act on it without asking a question.
- Version, owner, date and status (draft / reviewed / approved) on the first page.

## 7. Gate checklist (reviewer fails the PR if any box is empty)
- [ ] Lint, every installed type checker, tests green with pasted output (documents: N/A with reason)
- [ ] Complexity report within limits or justified
- [ ] Security scan and secrets scan clean on the diff
- [ ] Dependency audit clean or exceptions justified
- [ ] Acceptance criteria mapped to tests or checks
- [ ] Scope and do-not-touch list respected
- [ ] Report lists untested areas and uncertainties
- [ ] Data classification and compliance notes present where the spec requires them
