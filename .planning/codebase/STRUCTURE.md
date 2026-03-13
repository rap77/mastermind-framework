# STRUCTURE.md - Directory Structure

**MasterMind Framework** - Root-level organization

## Top-Level Structure

```
mastermind-framework/
├── .claude/                    # Claude Code configuration
│   ├── commands/               # Slash commands (/mm:*, /gsd:*)
│   ├── projects/               # Project-specific memories
│   └── skills/                 # Reusable skill files
│
├── .git/                       # Git repository
├── .gitignore                  # Git ignore patterns
├── .gga                        # Gentleman Guardian Angel config
├── .mcp.json                   # MCP server configuration
├── .pre-commit-config.yaml     # Pre-commit hooks
│
├── .planning/                  # GSD planning documents
│   └── codebase/               # Codebase mapping (this file)
│
├── agents/                     # AI agent configurations
│   └── brains/                 # System prompts for each brain
│       ├── marketing-*.md      # Marketing brain prompts (M1-M16)
│       └── software-*.md       # Software brain prompts (future)
│
├── docs/                       # Documentation
│   ├── design/                 # PRD documents (00-11)
│   ├── examples/               # Discovery interview examples
│   ├── nichos/                 # Nicho-specific content
│   │   ├── marketing-digital/  # 16 brains (M1-M16)
│   │   └── software-development/ # 7 brains (M1-M7)
│   ├── testing/                # Testing documentation
│   └── universal/              # Brain #8 content
│
├── mastermind_cli/             # Python CLI package
│   ├── commands/               # CLI commands
│   ├── config/                 # YAML configurations
│   ├── memory/                 # Memory/interview storage
│   ├── orchestrator/           # Orchestration logic
│   └── utils/                  # Utilities
│
├── scripts/                    # Utility scripts
│   ├── cleanup_interviews.py   # Interview cleanup
│   ├── run_e2e_tests.py        # E2E test runner
│   └── escanear_*.py           # Project scanners
│
├── tests/                      # Test files
│   ├── test-briefs/            # E2E test briefs (4 marketing tests)
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
│
├── PRPs/                       # Project Requirement Plans
│
├── pyproject.toml              # Python project config
├── README.md                   # Project readme
├── CLAUDE.md                   # Claude Code instructions
├── AGENTS.md                   # Agent configuration guide
├── RELEASES.md                 # Release notes
├── CHANGELOG-v1.3.0.md         # v1.3.0 changelog
└── main.py                     # Entry point (legacy)
```

## Key Locations

### Configuration Files

| File | Purpose |
|------|---------|
| `.mcp.json` | MCP server definitions (Serena, Context7, Sequential-Thinking) |
| `pyproject.toml` | Python dependencies, CLI entry points, tooling config |
| `.gga` | Gentleman Guardian Angel (code review rules) |
| `.pre-commit-config.yaml` | Git hooks (GGA, YAML validation) |
| `.gitignore` | Git ignore (dist/, logs/, .venv/, .serena/) |

### CLI Structure (`mastermind_cli/`)

```
mastermind_cli/
├── main.py                    # CLI entry point (click group)
├── __init__.py
├── brain_registry.py          # Brain loading and routing
│
├── commands/                  # CLI command modules
│   ├── orchestrate.py         # Orchestrate commands (run, go, continue-plan)
│   ├── source.py              # Source commands (new, update, validate, status, list)
│   ├── brain.py               # Brain commands (status, validate, package)
│   ├── evaluation.py          # Eval commands (list, show, find, search, stats)
│   ├── framework.py           # Framework commands (status, release)
│   └── install.py             # Installation commands
│
├── orchestrator/              # Core orchestration logic
│   ├── coordinator.py         # Main coordinator (orchestrate, route brains)
│   ├── brain_executor.py      # Execute individual brains
│   ├── evaluator.py           # Brain #7/#16 meta-evaluator
│   ├── flow_detector.py       # Detect flow type from brief
│   ├── plan_generator.py      # Generate execution plans
│   ├── output_formatter.py    # Format outputs (rich, JSON, YAML)
│   ├── notebooklm_client.py   # NotebookLM MCP wrapper
│   ├── mcp_wrapper.py         # Generic MCP wrapper
│   ├── mcp_integration.py     # MCP integration utilities
│   └── __init__.py
│
├── memory/                    # Memory and interview storage
│   ├── interview_logger.py    # Discovery interview logging
│   ├── storage.py             # File-based storage backend
│   ├── models.py              # Pydantic data models
│   ├── logger.py              # Evaluation logging
│   └── __init__.py
│
├── utils/                     # Utility functions
│   ├── validation.py          # YAML validation, schema checks
│   ├── yaml.py                # YAML loading/dumping
│   └── git.py                 # Git operations (via gitpython)
│
└── config/                    # Configuration files
    ├── brains.yaml            # Software development brains (M1-M7)
    └── brains-marketing.yaml  # Marketing digital brains (M1-M16)
```

### Nicho Structure (`docs/nichos/`)

```
docs/nichos/
├── TEMPLATE-UNIVERSAL.md      # Template for new nichos
│
├── software-development/      # Nicho: Software Development
│   └── BRAIN-0{1-7}-{NAME}/
│       ├── sources/
│       │   ├── FUENTE-XXX.md  # YAML frontmatter + markdown content
│       │   └── ...
│       └── notebook-config.json
│
└── marketing-digital/         # Nicho: Marketing Digital
    ├── README.md              # Nicho overview
    ├── PROPUESTA-16-CEREBROS.md
    ├── PRP-MARKETING-DIGITAL-NICHO.md
    └── BRAIN-{01-16}-{NAME}/
        ├── sources/
        │   ├── FUENTE-M{XX}-{XXX}.md
        │   └── ...
        └── notebook-config.json
```

### Brain System Prompts (`agents/brains/`)

```
agents/brains/
├── marketing-01-strategy.md
├── marketing-02-brand.md
├── marketing-03-content.md
├── marketing-04-social-organic.md
├── marketing-05-social-paid.md
├── marketing-06-search-ppc.md
├── marketing-07-seo-technical.md
├── marketing-08-seo-content.md
├── marketing-09-email.md
├── marketing-10-retention.md
├── marketing-11-analytics.md
├── marketing-12-cro.md
├── marketing-13-ops.md
├── marketing-14-influencer.md
├── marketing-15-community.md
└── marketing-16-growth-partner.md
```

### Test Structure (`tests/`)

```
tests/
├── test-briefs/               # E2E test briefs
│   ├── README.md
│   ├── test-marketing-01-brand-awareness.md
│   ├── test-marketing-02-lead-gen.md
│   ├── test-marketing-03-ecommerce-funnel.md
│   └── test-marketing-04-retention-campaign.md
│
├── unit/                      # Unit tests
│   ├── test_orchestrator/
│   │   ├── test_coordinator.py
│   │   ├── test_flow_detector.py
│   │   └── test_brain_executor.py
│   └── test_interview_learning.py
│
└── integration/               # Integration tests
    └── (future)
```

### Logs and Output

```
logs/                         # Runtime logs (gitignored)
├── e2e-results-*.json        # E2E test results
└── interviews/               # Discovery interview logs
    ├── hot/                  # Recent interviews (< 7 days)
    ├── warm/                 # Recent interviews (< 30 days)
    └── cold/                 # Old interviews (> 30 days)
```

## Naming Conventions

### Files
- **Source files:** `FUENTE-{BRAIN}-{NUMBER}-{slug}.md`
- **Config files:** `{niche}.yaml` (e.g., `brains-marketing.yaml`)
- **Test files:** `test-{module}.py` or `test-{niche}-{number}-{name}.md`
- **System prompts:** `{niche}-{number}-{name}.md`

### Directories
- **Brains:** `BRAIN-{XX}-{NAME}` (XX = 01-16, NAME = UPPERCASE)
- **Nichos:** `{niche-name}` (lowercase, hyphens)
- **Commands:** `{command}.py` (lowercase)

### Git Tags
- Format: `v{major}.{minor}.{patch}` (e.g., `v1.3.0`)
- Pre-release: `v{major}.{minor}.{patch}-{niche}` (e.g., `v1.2.0-marketing-m1-m8`)

## File Size Guidelines

| File Type | Typical Size | Max Size |
|-----------|--------------|----------|
| Source file (.md) | 200-400 lines | 500 lines |
| System prompt (.md) | 150-200 lines | 250 lines |
| Config (.yaml) | 100-300 lines | 500 lines |
| Python module (.py) | 200-500 lines | 1000 lines |
| Test file (.py) | 100-300 lines | 500 lines |

## Hidden/System Directories

| Directory | Purpose | Git Tracked? |
|-----------|---------|--------------|
| `.git/` | Git repository | No |
| `.venv/` | Python virtual env | No |
| `.serena/` | Serena MCP state | No |
| `.planning/` | GSD planning | Yes |
| `.claude/` | Claude Code config | Partial |
| `dist/` | NotebookLM exports | No |
| `logs/` | Runtime logs | No |
| `.pytest_cache/` | Pytest cache | No |
| `.ruff_cache/` | Ruff cache | No |
