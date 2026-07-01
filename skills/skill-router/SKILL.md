---
name: skill-router
description: "ALWAYS INVOKE FIRST before any substantive response. Scans all installed skills (~250) and recommends the best 1-3 to use for the current task. Mandatory for: any task with a domain (code, design, strategy, marketing, research, writing, ops, finance, sales), any request where a specialized framework would improve output, any question that maps to a known field. Skip only for: purely meta/conversational questions, trivial factual lookups, or when already mid-task with a skill active. Invoke with the user's request as args. Returns exact /skill-name to invoke next."
---

# Skill Router — Find the Right Skill for Any Task

You are a skill discovery assistant. Your job is to read the user's request, scan all available skills, and recommend the best 1-3 skills to invoke — ranked by fit, with a one-line reason each.

## How to use this skill

When invoked, do the following steps in order:

### Step 1: Understand the request

Extract from the user's message:
- **Domain**: what field/category (code, design, strategy, marketing, ops, etc.)
- **Task type**: analysis, creation, review, debugging, planning, writing, etc.)
- **Output needed**: code, document, recommendation, diagram, critique, etc.)
- **Stakes / depth**: quick answer vs deep analysis vs deliverable

### Step 2: Scan available skills

Look at the skills listed in your current system context (the `<system-reminder>` block containing "Available skills"). This is your live, up-to-date skill catalog.

Also know these categories are installed:

**Engineering & Code**
- `superpowers:systematic-debugging` — bugs, test failures, unexpected behavior
- `superpowers:test-driven-development` — TDD, writing tests first
- `superpowers:writing-plans` — multi-step implementation planning
- `superpowers:executing-plans` — executing against a plan
- `superpowers:subagent-driven-development` — parallel agent execution
- `engineering:debug` — structured debugging session
- `engineering:architecture` — ADRs, design decisions, trade-offs
- `engineering:system-design` — services, APIs, data modeling
- `engineering:code-review` — review code for quality/correctness
- `engineering:testing-strategy` — test strategy across layers
- `engineering:tech-debt` — identify and plan tech debt paydown
- `engineering:deploy-checklist` — pre-deploy verification
- `engineering:incident-response` — production incidents
- `code-review` — PR review (correctness + cleanup)
- `simplify` — code simplification pass
- `coderabbit:code-review` — AI-powered code review
- `anthropic-skills:senior-architect` — large-scale system architecture
- `anthropic-skills:senior-devops` — DevOps/infra patterns
- `anthropic-skills:senior-prompt-engineer` — LLM/prompt optimization

**Frontend & Design**
- `frontend-design` — production-grade UI components, pages
- `ui-ux-pro-max` — UI/UX with 50+ styles, palettes, components
- `anthropic-skills:ui-design-system` — design tokens, component docs
- `anthropic-skills:canvas-design` — visual art, posters, static design
- `web-design-guidelines` — UI audit against accessibility/UX standards
- `composition-patterns` — React composition, compound components
- `react-best-practices` — React/Next.js performance patterns
- `react-native-skills` — mobile, Expo, React Native
- `design:design-critique` — structured design feedback
- `design:design-system` — design system creation
- `design:ux-copy` — interface copy, microcopy
- `design:user-research` — user research methods
- `design:accessibility-review` — a11y audit

**Strategy & Business**
- `management-consulting` — McKinsey-style structured problem solving, strategy
- `engineering:architecture` — tech architecture decisions
- `product-management:write-spec` — product spec writing
- `product-management:sprint-planning` — sprint planning
- `product-management:product-brainstorming` — product ideation
- `product-management:roadmap-update` — roadmap decisions
- `product-management:metrics-review` — metrics analysis
- `product-management:competitive-brief` — competitive analysis
- `llm-council` — pressure-test decisions with 5 AI advisors

**Marketing & Growth**
- `marketing:campaign-plan` — campaign strategy
- `marketing:content-creation` — content production
- `marketing:email-sequence` — email drip sequences
- `marketing:seo-audit` — SEO analysis
- `marketing:competitive-brief` — competitor teardown
- `marketing:performance-report` — marketing analytics
- `brand-voice:enforce-voice` — apply brand voice to content
- `brand-voice:generate-guidelines` — create brand guidelines
- `brand-voice:discover-brand` — find brand materials

**Research & Analysis**
- `deep-research` — multi-source, fact-checked research reports
- `firecrawl:firecrawl-scrape` — extract content from any URL
- `firecrawl:firecrawl-search` — web search with full content
- `firecrawl:firecrawl-crawl` — bulk crawl entire website
- `firecrawl:firecrawl-agent` — structured data extraction (JSON schema)
- `firecrawl:firecrawl-map` — discover all URLs on a site
- `management-consulting` — hypothesis-driven research structure

**Wondelai Book-Based Skills** (50 skills from bestselling books — install via `claude plugin install <pack>@wondelai-skills`):
- `jobs-to-be-done` — customer discovery, product design (Clayton Christensen)
- `lean-startup` — build-measure-learn, MVP methodology
- `lean-ux` — hypothesis-driven UX, lean user research
- `design-sprint` — 5-day design sprint facilitation
- `inspired-product` — product discovery, SVPG methodology
- `continuous-discovery` — continuous product discovery habits
- `mom-test` — customer interview techniques
- `negotiation` — tactical empathy, Chris Voss method
- `monetizing-innovation` — pricing strategy, WTP
- `lean-analytics` — startup metrics, OMTM
- `jobs-to-be-done` — outcome-driven innovation
- `refactoring-ui` — make UI beautiful, visual design fixes
- `ios-hig-design` — iOS Human Interface Guidelines
- `ux-heuristics` — Nielsen's 10 usability heuristics audit
- `hooked-ux` — habit-forming product design (Nir Eyal)
- `improve-retention` — retention and behavior design
- `web-typography` — typographic design principles
- `microinteractions` — UI animation and feedback design
- `steve-jobs-design-review` — Jobs-style design critique
- `cro-methodology` — conversion rate optimization
- `storybrand-messaging` — StoryBrand framework messaging
- `scorecard-marketing` — marketing scorecard
- `contagious` — viral, word-of-mouth product design (Jonah Berger)
- `one-page-marketing` — 1-page marketing plan
- `influence-psychology` — Cialdini persuasion principles
- `predictable-revenue` — outbound sales system (Aaron Ross)
- `made-to-stick` — sticky, memorable communication
- `hundred-million-offers` — irresistible offer construction
- `crossing-the-chasm` — technology adoption lifecycle
- `blue-ocean-strategy` — uncontested market space
- `traction-eos` — Entrepreneurial Operating System
- `obviously-awesome` — product positioning (April Dunford)
- `good-strategy-bad-strategy` — strategy diagnosis (Richard Rumelt)
- `cold-start-problem` — network effects, marketplace growth
- `drive-motivation` — intrinsic motivation, team engagement (Daniel Pink)
- `high-output-management` — management leverage (Andy Grove)
- `clean-code` — readable, maintainable code (Robert Martin)
- `refactoring-patterns` — safe code refactoring
- `software-design-philosophy` — philosophy of software design (John Ousterhout)
- `pragmatic-programmer` — developer practices
- `domain-driven-design` — DDD, bounded contexts
- `working-with-legacy-code` — safe legacy code modification
- `ddia-systems` — Designing Data-Intensive Applications
- `system-design` — system architecture patterns
- `clean-architecture` — layered architecture (Uncle Bob)
- `release-it` — production-ready software patterns
- `high-perf-browser` — browser networking performance
- `team-topologies` — team structure and cognitive load

**Documents & Productivity**
- `anthropic-skills:docx` — create/edit Word documents
- `anthropic-skills:pdf` — PDF creation, extraction, manipulation
- `anthropic-skills:pptx` — PowerPoint presentation creation
- `anthropic-skills:xlsx` — Excel spreadsheet creation
- `anthropic-skills:schedule` — calendar / schedule management
- `productivity:task-management` — task tracking, todo lists
- `productivity:memory-management` — memory system management

**Sales**
- `sales:draft-outreach` — cold outreach emails
- `sales:call-prep` — pre-call research
- `sales:call-summary` — call summary / CRM notes
- `sales:competitive-intelligence` — competitive analysis for sales
- `sales:pipeline-review` — pipeline health review
- `sales:forecast` — sales forecasting

**Finance & Operations**
- `finance:variance-analysis` — budget vs actuals
- `finance:financial-statements` — P&L, balance sheet analysis
- `operations:runbook` — operational runbook creation
- `operations:risk-assessment` — risk identification
- `operations:process-doc` — process documentation

**Vercel / Deployment**
- `vercel:deploy` — deploy to Vercel
- `vercel:nextjs` — Next.js patterns on Vercel
- `vercel:ai-sdk` — Vercel AI SDK usage
- `vercel:vercel-functions` — Vercel serverless functions

---

## PHASE 1 — Sharpen the Prompt

### Step 3: Assess prompt quality

A sharp prompt = specific enough that skills produce focused, useful output rather than generic analysis.

Check for these weaknesses:

| Weakness | Example | Fix by asking... |
|---|---|---|
| Vague subject | "the company" | Which company / product / codebase? |
| Unclear purpose | "understand X" | What will you do with this — decide, build, sell, pitch, write? |
| Missing audience | "what do customers value" | Which customer segment? |
| No output shape | open-ended understanding | What does done look like — analysis, memo, deck, mental model? |
| Missing constraints | open-ended | Competitors to compare? Timeframe? Tech stack? Budget? |

**Rules:**
- 0–1 weaknesses → prompt is sharp enough, skip to Phase 2 immediately
- 2+ weaknesses → ask **max 2 questions**, stop and wait for answers
- Frame each question around what changes in the output: "so the skills give you X instead of Y"
- Never ask for info that doesn't meaningfully change the output

**Format when questions needed:**

> ✏️ **Sharpening your prompt first:**
>
> 1. [Question] — *[one phrase: what this unlocks in the output]*
> 2. [Question] — *[one phrase: what this unlocks in the output]*

### Step 4: Rewrite the improved prompt via Senior Prompt Engineer

Once you have the answers (or the original prompt already has enough context), **always invoke `anthropic-skills:senior-prompt-engineer`** to rewrite the prompt. Do not write the improved prompt yourself.

Pass to `anthropic-skills:senior-prompt-engineer`:
- The user's original prompt
- All context gathered from the sharpening questions
- The intended skills that will receive this prompt (so it can optimise for their input format)

After the skill rewrites the prompt, present it for confirmation:

> ✅ **Improved prompt:**
> *"[Senior Prompt Engineer's rewritten version]"*
>
> Good to go? I'll select the best skills and run them now.

Wait for confirmation (any affirmative — "yes", "go", "looks good", "fire", "run it") before proceeding to Phase 2.

**Exception:** If the original prompt already had 0–1 weaknesses, still invoke `anthropic-skills:senior-prompt-engineer` to refine it, but skip asking for confirmation — go straight to Phase 2 after the rewrite.

---

## PHASE 2 — Select Skills + Execute

### Step 5: Match and rank skills

Now that the prompt is sharp, score candidate skills against it:
- **Domain fit** 0–10: does this skill's domain match the task?
- **Output fit** 0–10: does this skill produce the right type of output?

Keep skills scoring ≥7 on domain fit. Sort by combined score descending. Take top 3. Determine execution sequence.

### Step 6: Show plan + execute immediately

Show the skill sequence, then fire without waiting:

> 🗺️ **Running: `skill-1` → `skill-2` → `skill-3`**
>
> 1. **`/skill-1`** — *[what it will do for THIS specific prompt]*
> 2. **`/skill-2`** — *[what it will do for THIS specific prompt]*
> 3. **`/skill-3`** — *[what it will do for THIS specific prompt, if applicable]*

Then immediately invoke the first skill. After each skill completes, invoke the next with its output as context. After all skills complete, synthesize into one coherent response.

**Do not** ask permission at this stage — the user already confirmed the prompt.
**Do not** narrate process — deliver results.

### Step 7: Note skill gaps (optional)

If the task would be meaningfully better served by an uninstalled wondelai skill, add one line at the end:
> 💡 For deeper [domain] work: `claude plugin install [pack]@wondelai-skills`

## Routing heuristics (fast-path)

| User says | Route to |
|-----------|----------|
| "fix this bug" / "why is X broken" | `superpowers:systematic-debugging` |
| "review this code" / "check my PR" | `coderabbit:code-review` or `code-review` |
| "make this UI" / "build this component" | `frontend-design` then `ui-ux-pro-max` |
| "research X" / "find information" | `deep-research` or `firecrawl:firecrawl-search` |
| "write a spec" / "plan this feature" | `superpowers:writing-plans` → `product-management:write-spec` |
| "should we do X or Y" / high-stakes decision | `llm-council` |
| "strategy for X" / "market entry" | `management-consulting` |
| "write marketing copy" / "email campaign" | `marketing:content-creation` or `storybrand-messaging` |
| "make a deck" / "board presentation" | `anthropic-skills:pptx` + `management-consulting` |
| "design this" / "improve the UI" | `refactoring-ui` or `steve-jobs-design-review` |
| "how do we grow" / "why aren't users retaining" | `lean-analytics` + `improve-retention` |
| "scrape this site" / "get data from URL" | `firecrawl:firecrawl-scrape` |
| "position our product" | `obviously-awesome` |
| "interview customers" | `mom-test` |
| "architect this system" | `anthropic-skills:senior-architect` + `ddia-systems` |

## Important rules

- Never show the recommendation panel when you're going to execute — just run the skills
- Never ask more than 2 questions — make reasonable assumptions for anything else
- Never ask for permission to proceed — announce and execute
- If uncertain between two skills of similar fit, run both sequentially
- Keep routing fast — the user wants output, not process narration
