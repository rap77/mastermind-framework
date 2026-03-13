# INTEGRATIONS.md - External Integrations

## NotebookLM (Google)

**Purpose:** Knowledge base storage and retrieval for expert brains

**Authentication:** `nlm login` (Chrome profile based)

**Integration method:** MCP server via `notebooklm-mcp` Python package

**Key operations:**
- Create notebooks: `notebook_create`
- Add sources: `source_add` (url, text, drive, file)
- Query notebooks: `notebook_query`
- Generate artifacts: `studio_create` (audio, video, report, slides, infographic)

**Notebooks per niche:**
- **Software Development:** 1 notebook per brain (7 total)
- **Marketing Digital:** 1 notebook per brain (16 total)
- **Universal:** Brain #8 (Master Interviewer)

**Notebook naming convention:**
- Permanent brains: `[CEREBRO] {Nombre} - {Nicho}`
- Project audits: `[AUDIT] {Proyecto} - {Nicho} - {YYYY-MM-DD}`

## MCP (Model Context Protocol)

**Purpose:** Standardized interface for external tools and services

**Client:** Claude Code (`~/.claude/.mcp.json`)

**Active servers:**

### Serena
- **Repository:** `git+https://github.com/oraios/serena`
- **Purpose:** Code navigation, memory management
- **Key tools:** `find_symbol`, `get_symbols_overview`, `list_memories`, `read_memory`, `write_memory`

### Context7
- **Repository:** `@upstash/context7-mcp@latest`
- **Purpose:** Up-to-date library documentation
- **Key tools:** `query-docs`, `resolve-library-id`

### Sequential-Thinking
- **Repository:** `@modelcontextprotocol/server-sequential-thinking`
- **Purpose:** Multi-step reasoning with hypothesis verification
- **Key tools:** `sequentialthinking`

## Git

**Purpose:** Version control, release management

**Operations via gitpython:**
- Branch creation, commits, tags
- Status checking, diff generation
- Remote push/pull

**Integration points:**
- `mastermind_cli/utils/git.py` - Git operations wrapper
- `mm framework release` - Release creation with tags

## GitHub

**Purpose:** Remote repository, issue tracking

**Integration via gh CLI (manual):**
- Release publishing
- PR creation and review
- Issue tracking

## File System

**Purpose:** Source file storage, configuration management

**Key directories:**
- `docs/nichos/{niche}/BRAIN-XX-{NAME}/sources/` - Expert knowledge sources
- `agents/brains/` - System prompts for each brain
- `mastermind_cli/config/` - YAML configuration files
- `.claude/projects/-home-rpadron-proy-mastermind/memory/` - Serena memories

**File formats:**
- `.md` with YAML frontmatter - Source files
- `.yaml` - Configuration files
- `.json` - Notebook configs, MCP settings

## External Data Sources

### YouTube
- **Purpose:** Video content extraction for knowledge sources
- **Integration:** NotebookLM source_add with URL type

### Google Drive
- **Purpose:** Document import for knowledge sources
- **Integration:** NotebookLM source_add with drive type
- **Document types:** doc, slides, sheets, pdf

### Web Scraping
- **Purpose:** Article/blog extraction for knowledge sources
- **Integration:** NotebookLM source_add with url type
- **Supported:** Any web page with public access

## CLI Tooling Integration

### uv (Python Package Manager)
- **Purpose:** Dependency management, virtual environments
- **Integration:** Direct command execution via subprocess
- **Commands:** `uv run`, `uv sync`, `uv add`, `uv remove`

### nvm (Node.js Version Manager)
- **Purpose:** Node.js runtime management for MCP servers
- **Integration:** Environment variable setup
- **MCP servers run via npx**

### pytest
- **Purpose:** Test execution
- **Integration:** `scripts/run_e2e_tests.py` subprocess calls
- **Coverage:** pytest-cov for reporting

## Authentication Methods

| Service | Method | Config Location |
|---------|--------|-----------------|
| **NotebookLM** | Chrome profile | `~/.config/nlm/tokens.json` |
| **GitHub** | SSH token | `~/.gitconfig` |
| **MCP servers** | None (public) | `~/.claude/.mcp.json` |

## Data Flow

```
User Brief (CLI)
    ↓
Orchestrator (coordinator.py)
    ↓
Brain Router → NotebookLM MCP
    ↓
NotebookLM Query → Expert Knowledge
    ↓
Evaluator → Quality Check
    ↓
Output Formatter → Rich Terminal
```

## Error Handling

**Integration failures:**
- NotebookLM timeout → Fallback to mock responses
- MCP server unavailable → Warning message, degraded mode
- Git operation failed → Exit with error message
- File not found → Clear error with path

**Retry logic:**
- NotebookLM queries: 3 retries with exponential backoff
- MCP calls: Single attempt, fail fast
- Git operations: Single attempt, user prompt for fix
