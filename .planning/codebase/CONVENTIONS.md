# CONVENTIONS.md - Code Conventions

**MasterMind Framework** - Coding standards and patterns

## Language Conventions

### Python

**File encoding:** UTF-8

**Line length:** No strict limit (prefer < 120 for readability)

**Imports:** Grouped and sorted:
1. Standard library
2. Third-party
3. Local imports

```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import click
from rich.console import Console

# Local
from mastermind_cli.orchestrator import Coordinator
from mastermind_cli.utils import validation
```

**Type hints:** Used where beneficial (pytghon 3.14+)

```python
from typing import Optional, Dict, List

def orchestrate(
    brief: str,
    flow: Optional[str] = None,
    use_mcp: bool = False
) -> Dict[str, Any]:
    ...
```

**Error handling:**

```python
# Prefer specific exceptions
raise ValueError(f"Invalid brain ID: {brain_id}")

# Click command errors
click.echo("Error: message", err=True)
raise click.Abort()

# Orchestrator errors
return {
    "status": "error",
    "error": "descriptive message"
}
```

**String formatting:** f-strings (Python 3.6+)

```python
name = "MasterMind"
print(f"Framework: {name}")
```

### YAML

**Indentation:** 2 spaces (consistent)

**Key naming:** kebab-case for keys, snake_case for nested values

```yaml
version: "1.0"
brains:
  - id: M1
    short_id: marketing-strategy
    notebook_id: "abc-123"
    system_prompt: "agents/brains/marketing-01-strategy.md"
```

**Multiline strings:** Use `|` for literal, `>` for folded

```yaml
description: |
  This is a literal string.
  Newlines are preserved.

summary: >
  This is a folded string.
  Newlines become spaces.
```

### Markdown

**Headers:** ATX style (`#`, `##`)

**Code blocks:** Fenced with language specifier

````markdown
```python
def hello():
    print("Hello")
```
````

**YAML frontmatter:** Required for source files

```yaml
---
source_id: "FUENTE-XXX"
brain: "brain-marketing-01-strategy"
title: "Source Title"
author: "Author Name"
type: "book"
language: "en"
version: "1.0.0"
---
```

## Naming Conventions

### Python

| Type | Convention | Example |
|------|------------|---------|
| Module | `snake_case` | `brain_executor.py` |
| Class | `PascalCase` | `OrchestratorCoordinator` |
| Function/Method | `snake_case` | `orchestrate_briefs()` |
| Variable | `snake_case` | `brain_id` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Private | `_leading_underscore` | `_internal_method()` |

### Files

| Type | Convention | Example |
|------|------------|---------|
| Python modules | `snake_case.py` | `coordinator.py` |
| YAML configs | `kebab-case.yaml` | `brains-marketing.yaml` |
| Markdown docs | `UPPER-CASE.md` | `README.md`, `CHANGELOG-v1.3.0.md` |
| Source files | `FUENTE-XXX.md` | `FUENTE-M1-001-inspired.md` |
| System prompts | `{niche}-{number}-{name}.md` | `marketing-01-strategy.md` |

### Directories

| Type | Convention | Example |
|------|------------|---------|
| Packages | `snake_case` | `mastermind_cli/` |
| Brains | `BRAIN-XX-NAME` | `BRAIN-01-STRATEGY/` |
| Nichos | `lowercase-with-hyphens` | `marketing-digital/` |

## Git Conventions

### Commit Format

**Conventional commits:** `type(scope): description`

```bash
feat(marketing): add M9-M16 knowledge sources
fix(orchestrator): resolve race condition in brain executor
docs(readme): update installation instructions
refactor(coordinator): extract flow detector to separate module
test(e2e): add marketing test suite
chore(deps): upgrade pydantic to 2.10
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Scopes:** Module or feature name

**No Co-Authored-By:** Never add AI attribution to commits

### Branch Naming

`feature/{prp}-{short-description}`

```bash
feature/prp-marketing-003-knowledge-m9-m16
feature/prp-008-master-interviewer
```

### Tagging

Semantic versioning: `v{major}.{minor}.{patch}`

```bash
v1.0.0    # Initial release
v1.1.0    # New feature (backward compatible)
v1.2.0-marketing-m1-m8  # Pre-release for specific niche
v1.3.0    # Feature complete
```

## Code Patterns

### Click Commands

```python
@click.group()
def command_group():
    """Command group description."""
    pass

@command_group.command()
@click.argument('required_arg')
@click.option('--optional', '-o', help='Optional flag')
def subcommand(required_arg, optional):
    """Subcommand description."""
    pass
```

### Pydantic Models

```python
from pydantic import BaseModel, Field

class BrainConfig(BaseModel):
    """Brain configuration model."""

    id: str = Field(..., description="Brain ID (e.g., M1)")
    name: str = Field(..., description="Brain name")
    notebook_id: str = Field(..., description="NotebookLM notebook ID")
    status: str = Field(default="active", description="Brain status")
```

### MCP Integration

```python
from mastermind_cli.orchestrator.mcp_integration import MCPIntegration

mcp = MCPIntegration()
result = mcp.call_tool(
    server="notebooklm-mcp",
    tool="notebook_query",
    parameters={"notebook_id": notebook_id, "query": query}
)
```

### Error Handling

```python
try:
    result = coordinator.orchestrate(brief, flow)
except ValueError as e:
    click.echo(f"Validation error: {e}", err=True)
    raise click.Abort()
except Exception as e:
    click.echo(f"Unexpected error: {e}", err=True)
    if verbose:
        click.echo(traceback.format_exc(), err=True)
    raise click.Abort()
```

## Documentation Conventions

### Source Files (Fichas)

**Required sections:**
1. `### 1. Principios Fundamentales` - Min 3 principles
2. `### 2. Frameworks y Metodologías`
3. `### 3. Modelos Mentales`
4. `### 4. Criterios de Decisión`
5. `### 5. Anti-patrones`

**Required YAML fields:**
```yaml
---
source_id: "FUENTE-XXX"
brain: "brain-software-01-product-strategy"
niche: "software-development"
title: "Title"
author: "Author Name"
expert_id: "EXP-XXX"
type: "book|video|article"
language: "en|es"
year: YYYY
distillation_date: "YYYY-MM-DD"
distillation_quality: "complete|partial|pending"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "YYYY-MM-DD"
status: "active|draft|deprecated"
---
```

### Python Docstrings

```python
def orchestrate(
    brief: str,
    flow: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Orchestrate brains to process user brief.

    Args:
        brief: User brief text
        flow: Force specific flow (auto-detect if None)
        dry_run: Generate plan without executing

    Returns:
        Dictionary with status and output

    Example:
        >>> result = orchestrate("quiero una app de fitness")
        >>> print(result["status"])
        'completed'
    """
```

### README Sections

1. Project title and description
2. Installation instructions
3. Quick start guide
4. CLI commands reference
5. Architecture overview
6. Contributing guidelines
7. License

## Testing Conventions

### Test Naming

```python
# Unit tests
def test_coordinator_orchestrate():
    """Test orchestration coordination."""
    pass

def test_flow_detector_validation_only():
    """Test validation-only flow detection."""
    pass

# E2E tests
test-marketing-01-brand-awareness.md
test-marketing-02-lead-gen.md
```

### Test Structure

```python
# Arrange, Act, Assert (AAA)
def test_brain_executor_with_mock():
    # Arrange
    brief = "test brief"
    mock_mcp = Mock(return_value={"result": "output"})

    # Act
    result = brain_executor.execute(brief, mcp=mock_mcp)

    # Assert
    assert result["status"] == "completed"
    assert mock_mcp.called
```

## Comment Conventions

### When to Comment

**DO comment:**
- Complex algorithms ("why", not "what")
- Non-obvious business logic
- Workarounds for bugs
- TODO/FIXME markers

**DON'T comment:**
- Obvious code (`x += 1  # increment x`)
- Outdated information
- redundant with code

### Comment Style

```python
# Single-line comments explain WHY
# Multi-line comments for complex logic

# TODO(feature): Add support for XYZ
# FIXME(bug#123): Resolve edge case

# NOTE: This is a workaround for upstream bug
# https://github.com/author/repo/issues/123
```

## Language Specific Notes

### Spanish vs English

| Context | Language |
|---------|----------|
| Code (variables, functions) | English |
| Comments | English (code), Spanish (docs) |
| Documentation (README, guides) | Spanish |
| User-facing messages | Spanish |
| Error messages | Spanish |
| Git commits | English (conventional commits) |

**Example:**
```python
# English function name
def validate_brain_config(brain_id: str) -> bool:
    """Validate brain configuration file.

    Checks that the brain configuration exists and has valid YAML.
    """
    # Spanish comment in code is OK for domain-specific concepts
    # Verificar que el cerebro existe
    if not brain_exists(brain_id):
        return False
```

## Pre-commit Hooks

**Enabled hooks:**
- Gentleman Guardian Angel (GGA) - AI code review
- Trim trailing whitespace
- Fix end of files
- Check YAML syntax
- Check for large files
- Check for merge conflicts

**Skipping hooks:** Never use `--no-verify` (prohibited by user rules)
