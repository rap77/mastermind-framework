# STACK.md - Technology Stack

**MasterMind Framework** - Cognitive architecture for expert knowledge consultation

## Core Languages

| Language | Version | Purpose | Runtime |
|----------|---------|---------|---------|
| **Python** | 3.14+ | CLI, orchestrator, business logic | uv (package manager) |
| **JavaScript/Node.js** | Latest (nvm) | MCP servers, tooling | npm/nvm |
| **YAML** | 1.2+ | Configuration, frontmatter | - |
| **Markdown** | - | Documentation, source files | - |

## Python Dependencies

```toml
[project]
name = "mastermind-framework"
version = "1.1.0"
requires-python = ">=3.14"
```

**Core dependencies:**
- `click>=8.1.0` - CLI framework
- `rich>=13.0.0` - Terminal output formatting
- `pyyaml>=6.0` - YAML parsing
- `gitpython>=3.1.0` - Git operations
- `semver>=3.0.0` - Semantic versioning
- `pydantic>=2.0.0` - Data validation

**Dev dependencies:**
- `pytest>=9.0.2` - Testing framework
- `pytest-cov>=7.0.0` - Coverage reporting

**Optional dependencies:**
- `notebooklm-mcp>=0.1.0` - NotebookLM MCP integration

## MCP Servers (Model Context Protocol)

| MCP | Purpose | Command |
|-----|---------|---------|
| **Serena** | Code navigation, memory management | `uvx serena start-mcp-server --context ide-assistant` |
| **Context7** | Documentation lookup | `npx @upstash/context7-mcp@latest` |
| **Sequential-Thinking** | Multi-step reasoning | `npx @modelcontextprotocol/server-sequential-thinking` |
| **NotebookLM** | Knowledge base queries | `nlm` CLI (external) |

## CLI Commands

| Command | Alias | Purpose |
|---------|-------|---------|
| `mastermind` | `mm` | Main CLI entry point |
| `mm source` | - | Source management (new, update, validate, status, list, export) |
| `mm brain` | - | Brain status, validate, package |
| `mm orchestrate` | - | Orchestrate brains to process briefs |
| `mm eval` | - | Evaluation management (list, show, find, search, stats) |
| `mm framework` | - | Framework status, release |

## Configuration Files

| File | Purpose |
|------|---------|
| `.mcp.json` | MCP server configuration |
| `pyproject.toml` | Python project metadata, dependencies, tooling |
| `brains.yaml` | Software development brains config |
| `brains-marketing.yaml` | Marketing digital brains config |
| `.gga` | Gentleman Guardian Angel (code review) config |
| `.pre-commit-config.yaml` | Pre-commit hooks |

## Development Tools

| Tool | Purpose |
|------|---------|
| **uv** | Python package manager (replaces pip/poetry) |
| **ruff** | Linter + formatter |
| **pyright** | Type checker |
| **pytest** | Test runner |
| **pre-commit** | Git hooks |
| **Gentleman Guardian Angel** | AI code review (claude provider) |

## Documentation

| Format | Purpose |
|--------|---------|
| **Markdown** | All documentation (.md files) |
| **YAML frontmatter** | Source file metadata |
| **JSON** | Notebook configs, MCP settings |

## File Locations

```
mastermind_cli/           # CLI Python package
├── commands/             # CLI commands (orchestrate, source, brain, eval)
├── orchestrator/         # Orchestration logic
├── memory/              # Evaluation/interview logging
├── utils/               # Utilities (validation, yaml, git)
└── config/              # YAML configs (brains.yaml, brains-marketing.yaml)

docs/
├── nichos/              # Nicho-specific content
│   ├── software-development/  # 7 brains (BRAIN-01 to BRAIN-07)
│   └── marketing-digital/     # 16 brains (BRAIN-01 to BRAIN-16)
├── design/              # PRD documents
└── examples/            # Example interviews

agents/brains/           # System prompts for each brain
scripts/                 # Utility scripts (cleanup, e2e tests)
tests/                   # Test files (briefs, unit tests)
```
