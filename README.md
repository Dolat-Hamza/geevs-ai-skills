# Geevs AI Skills & Plugins

A curated collection of **AI agent skills and plugins** for Claude (Cowork /
Claude Code) and compatible agent runtimes — spanning engineering, product,
design/UX, business growth, and finance.

- **8 plugin bundles** (`plugins/`) — each installs a whole set of skills at once
- **geevs-agent-team** (`plugins/geevs-agent-team/`) — gated delivery: `/deliver` with researcher, builder and reviewer agents; see its README
- **12 standalone skills** (`skills/`) — individual, self-contained skills
- **~115 skill units** total

See **[CATALOG.md](CATALOG.md)** for the full list with descriptions.

**Trying the agent team?** Follow [TRY-IT.md](TRY-IT.md): a 30-minute, step-by-step test on [examples/practice-project](examples/practice-project).

## Repository layout

```
plugins/     # Installable plugin bundles (each has .claude-plugin/plugin.json)
  geevs-agent-team/              # /deliver + setup, 3 agents, enforced gates
  engineering-advanced-skills/   # 29 engineering tooling/workflow skills
  engineering-skills/            # senior specialists (architect, backend, devops, ...)
  product-skills/                # product strategy, discovery, analytics, ...
  business-growth-skills/        # GTM: sales eng, revenue ops, CS, proposals
  finance-skills/                # financial analyst, SaaS metrics
  bencium-innovative-ux-designer/
  bencium-controlled-ux-designer/
skills/      # Standalone skills (each folder has a SKILL.md)
  ui-ux-pro-max/  web-design-guidelines/  frontend-design/  graphify/
  accesslint/  composition-patterns/  react-best-practices/  react-native-skills/
  management-consulting/  llm-council/  skill-router/  brand-guidelines/
```

Each **skill** is a folder containing a `SKILL.md` (YAML frontmatter with
`name` + `description`, followed by instructions) and optional `scripts/`,
`references/`, and `assets/`. Each **plugin** adds a `.claude-plugin/plugin.json`
manifest that groups multiple skills.

## Using these

**As a plugin (bulk):** point your agent's plugin/marketplace mechanism at a
`plugins/<name>` folder, or zip the folder to a `.plugin` file and install it —
all of the bundle's skills load at once.

**As individual skills:** copy a `skills/<name>` folder into your agent's skills
directory, or zip the folder and upload it via your app's skill uploader
(in Claude: **Settings → Capabilities → Skills → Upload skill**). The zipped
folder name must match the skill's `name:` in `SKILL.md`.

## Attribution & licensing

These skills were created by others and are re-hosted here with credit. Sources
and licenses are listed in **[ATTRIBUTION.md](ATTRIBUTION.md)**. The bundles from
`alirezarezvani/claude-skills` and `brand-guidelines` are MIT; `frontend-design`
is Apache-2.0; some components have **no stated license** — review ATTRIBUTION.md
before redistributing.
