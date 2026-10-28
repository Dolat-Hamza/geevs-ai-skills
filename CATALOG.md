# Catalog

Everything in this repo. **8 plugin bundles** and **12 standalone skills** (≈115 skill units total).

## Plugins (`plugins/`)

### `bencium-controlled-ux-designer` — 1 skills

| Skill | What it does |
|---|---|
| **bencium-controlled-ux-designer** | Expert UI/UX design guidance for unique, accessible interfaces. Use for visual decisions, colors, typography, layouts. Always ask before ma… |

### `bencium-innovative-ux-designer` — 1 skills

| Skill | What it does |
|---|---|
| **bencium-innovative-ux-designer** | Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web component… |

### `business-growth-skills` — 4 skills

| Skill | What it does |
|---|---|
| **contract-and-proposal-writer** | Contract & Proposal Writer |
| **customer-success-manager** | Monitors customer health, predicts churn risk, and identifies expansion opportunities using weighted scoring models for SaaS customer succe… |
| **revenue-operations** | Analyzes sales pipeline health, revenue forecasting accuracy, and go-to-market efficiency metrics for SaaS revenue optimization. Use when a… |
| **sales-engineer** | Analyzes RFP/RFI responses for coverage gaps, builds competitive feature comparison matrices, and plans proof-of-concept (POC) engagements … |

### `engineering-advanced-skills` — 35 skills

| Skill | What it does |
|---|---|
| **agent-designer** | Agent Designer - Multi-Agent System Architecture |
| **agent-workflow-designer** | Agent Workflow Designer |
| **api-design-reviewer** | API Design Reviewer |
| **api-test-suite-builder** | API Test Suite Builder |
| **autoresearch-agent** | Autonomous experiment loop that optimizes any file by a measurable metric. Inspired by Karpathy's autoresearch. The agent edits a target fi… |
| **loop** | Start an autonomous experiment loop with user-selected interval (10min, 1h, daily, weekly, monthly). Uses CronCreate for scheduling. |
| **resume** | Resume a paused experiment. Checkout the experiment branch, read results history, continue iterating. |
| **run** | Run a single experiment iteration. Edit the target file, evaluate, keep or discard. |
| **setup** | Set up a new autoresearch experiment interactively. Collects domain, target file, eval command, metric, direction, and evaluator. |
| **status** | Show experiment dashboard with results, active loops, and progress. |
| **changelog-generator** | Changelog Generator |
| **ci-cd-pipeline-builder** | CI/CD Pipeline Builder |
| **codebase-onboarding** | Codebase Onboarding |
| **database-designer** | Database Designer - POWERFUL Tier Skill |
| **database-schema-designer** | Database Schema Designer |
| **dependency-auditor** | Dependency Auditor |
| **docker-development** | Docker and container development agent skill and plugin for Dockerfile optimization, docker-compose orchestration, multi-stage builds, and … |
| **env-secrets-manager** | Env & Secrets Manager |
| **git-worktree-manager** | Git Worktree Manager |
| **helm-chart-builder** | Helm chart development agent skill and plugin for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw — chart scaffolding, values design, temp… |
| **interview-system-designer** | This skill should be used when the user asks to "design interview processes", "create hiring pipelines", "calibrate interview loops", "gene… |
| **mcp-server-builder** | MCP Server Builder |
| **migration-architect** | Migration Architect |
| **monorepo-navigator** | Monorepo Navigator |
| **observability-designer** | Observability Designer (POWERFUL) |
| **performance-profiler** | Performance Profiler |
| **pr-review-expert** | PR Review Expert |
| **rag-architect** | RAG Architect - POWERFUL |
| **release-manager** | Release Manager |
| **runbook-generator** | Runbook Generator |
| **skill-security-auditor** | Security audit and vulnerability scanner for AI agent skills before installation. Use when: (1) evaluating a skill from an untrusted source… |
| **skill-tester** | Skill Tester |
| **sample-skill** | The Sample Text Processor is a simple skill designed to demonstrate the basic structure and functionality expected in the claude-skills eco… |
| **tech-debt-tracker** | Scan codebases for technical debt, score severity, track trends, and generate prioritized remediation plans. Use when users mention tech de… |
| **terraform-patterns** | Terraform infrastructure-as-code agent skill and plugin for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw. Covers module design patterns… |

### `engineering-skills` — 39 skills

| Skill | What it does |
|---|---|
| **aws-solution-architect** | Design AWS architectures for startups using serverless patterns and IaC templates. Use when asked to design serverless architecture, create… |
| **code-reviewer** | Code review automation for TypeScript, JavaScript, Python, Go, Swift, Kotlin. Analyzes PRs for complexity and risk, checks code quality for… |
| **email-template-builder** | Email Template Builder |
| **epic-design** | Build immersive, cinematic 2.5D interactive websites using scroll storytelling, parallax depth, text animations, and premium scroll effects… |
| **google-workspace-cli** | Google Workspace administration via the gws CLI. Install, authenticate, and automate Gmail, Drive, Sheets, Calendar, Docs, Chat, and Tasks.… |
| **incident-commander** | Incident Commander Skill |
| **ms365-tenant-manager** | Microsoft 365 tenant administration for Global Administrators. Automate M365 tenant setup, Office 365 admin tasks, Azure AD user management… |
| **playwright-pro** | Production-grade Playwright testing toolkit. Use when the user mentions Playwright tests, end-to-end testing, browser automation, fixing fl… |
| **browserstack** | Run tests on BrowserStack. Use when user mentions "browserstack", "cross-browser", "cloud testing", "browser matrix", "test on safari", "te… |
| **coverage** | Analyze test coverage gaps. Use when user says "test coverage", "what's not tested", "coverage gaps", "missing tests", "coverage report", o… |
| **fix** | Fix failing or flaky Playwright tests. Use when user says "fix test", "flaky test", "test failing", "debug test", "test broken", "test pass… |
| **generate** | Generate Playwright tests. Use when user says "write tests", "generate tests", "add tests for", "test this component", "e2e test", "create … |
| **init** | Set up Playwright in a project. Use when user says "set up playwright", "add e2e tests", "configure playwright", "testing setup", "init pla… |
| **migrate** | Migrate from Cypress or Selenium to Playwright. Use when user mentions "cypress", "selenium", "migrate tests", "convert tests", "switch to … |
| **report** | Generate test report. Use when user says "test report", "results summary", "test status", "show results", "test dashboard", or "how did tes… |
| **review** | Review Playwright tests for quality. Use when user says "review tests", "check test quality", "audit tests", "improve tests", "test code re… |
| **testrail** | Sync tests with TestRail. Use when user mentions "testrail", "test management", "test cases", "test run", "sync test cases", "push results … |
| **self-improving-agent** | Curate Claude Code's auto-memory into durable project knowledge. Analyze MEMORY.md for patterns, promote proven learnings to CLAUDE.md and … |
| **extract** | Turn a proven pattern or debugging solution into a standalone reusable skill with SKILL.md, reference docs, and examples. |
| **promote** | Graduate a proven pattern from auto-memory (MEMORY.md) to CLAUDE.md or .claude/rules/ for permanent enforcement. |
| **remember** | Explicitly save important knowledge to auto-memory with timestamp and context. Use when a discovery is too important to rely on auto-captur… |
| **review** | Analyze auto-memory for promotion candidates, stale entries, consolidation opportunities, and health metrics. |
| **status** | Memory health dashboard showing line counts, topic files, capacity, stale entries, and recommendations. |
| **senior-architect** | This skill should be used when the user asks to "design system architecture", "evaluate microservices vs monolith", "create architecture di… |
| **senior-backend** | Designs and implements backend systems including REST APIs, microservices, database architectures, authentication flows, and security harde… |
| **senior-computer-vision** | Computer vision engineering skill for object detection, image segmentation, and visual AI systems. Covers CNN and Vision Transformer archit… |
| **senior-data-engineer** | Data engineering skill for building scalable data pipelines, ETL/ELT systems, and data infrastructure. Expertise in Python, SQL, Spark, Air… |
| **senior-data-scientist** | World-class senior data scientist skill specialising in statistical modeling, experiment design, causal inference, and predictive analytics… |
| **senior-devops** | Comprehensive DevOps skill for CI/CD, infrastructure automation, containerization, and cloud platforms (AWS, GCP, Azure). Includes pipeline… |
| **senior-frontend** | Frontend development skill for React, Next.js, TypeScript, and Tailwind CSS applications. Use when building React components, optimizing Ne… |
| **senior-fullstack** | Fullstack development toolkit with project scaffolding for Next.js, FastAPI, MERN, and Django stacks, code quality analysis with security a… |
| **senior-ml-engineer** | ML engineering skill for productionizing models, building MLOps pipelines, and integrating LLMs. Covers model deployment, feature stores, d… |
| **senior-prompt-engineer** | This skill should be used when the user asks to "optimize prompts", "design prompt templates", "evaluate LLM outputs", "build agentic syste… |
| **senior-qa** | Generates unit tests, integration tests, and E2E tests for React/Next.js applications. Scans components to create Jest + React Testing Libr… |
| **senior-secops** | Senior SecOps engineer skill for application security, vulnerability management, compliance verification, and secure development practices.… |
| **senior-security** | Security engineering toolkit for threat modeling, vulnerability analysis, secure architecture, and penetration testing. Includes STRIDE ana… |
| **stripe-integration-expert** | Stripe Integration Expert |
| **tdd-guide** | Test-driven development skill for writing unit tests, generating test fixtures and mocks, analyzing coverage gaps, and guiding red-green-re… |
| **tech-stack-evaluator** | Technology stack evaluation and comparison with TCO analysis, security assessment, and ecosystem health scoring. Use when comparing framewo… |

### `finance-skills` — 2 skills

| Skill | What it does |
|---|---|
| **financial-analyst** | Performs financial ratio analysis, DCF valuation, budget variance analysis, and rolling forecast construction for strategic decision-making… |
| **saas-metrics-coach** | SaaS financial health advisor. Use when a user shares revenue or customer numbers, or mentions ARR, MRR, churn, LTV, CAC, NRR, or asks how … |

### `geevs-agent-team` — 3 agents, 2 skills

| Component | What it does |
|---|---|
| **deliver** (skill) | `/geevs-agent-team:deliver <goal>`: interview, research, spec, isolated build, independent review, human release |
| **setup** (skill) | Opts a project in: permission rules, hook marker, CLAUDE.md section |
| **researcher** (agent) | One question, cited findings written to a file |
| **builder** (agent) | Implements the approved spec in its own worktree |
| **reviewer** (agent) | Verifies each acceptance criterion and records evidence; cannot edit |

### `product-skills` — 13 skills

| Skill | What it does |
|---|---|
| **agile-product-owner** | Agile product ownership for backlog management and sprint execution. Covers user story writing, acceptance criteria, sprint planning, and v… |
| **competitive-teardown** | Analyzes competitor products and companies by synthesizing data from pricing pages, app store reviews, job postings, SEO signals, and socia… |
| **experiment-designer** | Use when planning product experiments, writing testable hypotheses, estimating sample size, prioritizing tests, or interpreting A/B outcome… |
| **landing-page-generator** | Generates high-converting landing pages as complete Next.js/React (TSX) components with Tailwind CSS. Creates hero sections, feature grids,… |
| **product-analytics** | Use when defining product KPIs, building metric dashboards, running cohort or retention analysis, or interpreting feature adoption trends a… |
| **product-discovery** | Use when validating product opportunities, mapping assumptions, planning discovery sprints, or testing problem-solution fit before committi… |
| **product-manager-toolkit** | Comprehensive toolkit for product managers including RICE prioritization, customer interview analysis, PRD templates, discovery frameworks,… |
| **product-strategist** | Strategic product leadership toolkit for Head of Product covering OKR cascade generation, quarterly planning, competitive landscape analysi… |
| **research-summarizer** | Structured research summarization agent skill for non-dev users. Handles academic papers, web articles, reports, and documentation. Extract… |
| **roadmap-communicator** | Use when preparing roadmap narratives, release notes, changelogs, or stakeholder updates tailored for executives, engineering teams, and cu… |
| **saas-scaffolder** | Generates complete, production-ready SaaS project boilerplate including authentication, database schemas, billing integration, API routes, … |
| **ui-design-system** | UI design system toolkit for Senior UI Designer including design token generation, component documentation, responsive design calculations,… |
| **ux-researcher-designer** | UX research and design toolkit for Senior UX Designer/Researcher including data-driven persona generation, journey mapping, usability testi… |

## Standalone skills (`skills/`)

| Skill | What it does |
|---|---|
| **accesslint/contrast-checker** | Color contrast analyzer for WCAG compliance. Use when analyzing color contrast in code files, when user mentions WCAG compliance, color acc… |
| **accesslint/link-purpose** | Analyzes code for WCAG 2.4.4 Link Purpose (In Context) compliance. Identifies generic link text, ambiguous links, and links without suffici… |
| **accesslint/refactor** | Accessibility refactoring specialist. Automatically fixes accessibility issues across multiple files. Performs complex refactoring like ext… |
| **accesslint/use-of-color** | Analyzes code for WCAG 1.4.1 Use of Color compliance. Identifies where color is used as the only means of conveying information and recomme… |
| **brand-guidelines** | When the user wants to apply, document, or enforce brand guidelines for any product or company. Also use when the user mentions 'brand guid… |
| **composition-patterns** | React composition patterns that scale. Use when refactoring components with |
| **frontend-design** | Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web component… |
| **graphify** | any input (code, docs, papers, images) - knowledge graph - clustered communities - HTML + JSON + audit report |
| **llm-council** | Run any question, idea, or decision through a council of 5 AI advisors who independently analyze it, peer-review each other anonymously, an… |
| **management-consulting** | Structured problem solving and strategic analysis using professional consulting frameworks. Triggers on strategy questions, decision-making… |
| **react-best-practices** | React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, reviewing, or refact… |
| **react-native-skills** | React Native and Expo best practices for building performant mobile apps. Use |
| **skill-router** | ALWAYS INVOKE FIRST before any substantive response. Scans all installed skills (~250) and recommends the best 1-3 to use for the current t… |
| **ui-ux-pro-max** | UI/UX design intelligence for web and mobile. Includes 50+ styles, 161 color palettes, 57 font pairings, 161 product types, 99 UX guideline… |
| **web-design-guidelines** | Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX… |
