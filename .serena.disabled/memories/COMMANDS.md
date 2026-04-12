# MasterMind Framework - Useful Commands

## Python Runtime (uv)

```bash
uv run python main.py           # Run main script
uv sync                          # Sync dependencies
uv add <package>                 # Add dependency
uv remove <package>              # Remove dependency
```

## MasterMind CLI

```bash
# Source management
mastermind source new                    # Create new source
mastermind source update <id>            # Update existing source
mastermind source validate --brain <id>  # Validate sources
mastermind source status --brain <id>    # Check source status
mastermind source list                   # List all sources
mastermind source export --brain <id>    # Export sources

# Brain management
mastermind brain status                   # Check brain status
mastermind brain validate                 # Validate brain configuration
mastermind brain package                  # Package brain for deployment

# Framework
mastermind framework status               # Overall framework status
mastermind framework release              # Create release

# Info
mastermind info                           # Show system info

# Aliases
mm source validate --brain 01-product-strategy
```

## Git

```bash
# Branching (feature branches)
git checkout -b feature/prp-XXX-name

# Merging (fast-forward preferred)
git checkout master
git merge feature/prp-XXX-name --no-edit

# Versioning
git tag v0.1.0 -m "description"
git push origin v0.1.0

# Status
git status
git log --oneline -5
git diff --stat
```

## System Commands (Linux)

```bash
# File operations (use dedicated tools, not basic commands)
fd pattern              # Find files (better than find)
rg pattern              # Search content (better than grep)
bat file                # View file (better than cat)
eza tree                # List files (better than ls)

# Python
python3 -c "import yaml; yaml.safe_load(open('file.yaml'))"  # Validate YAML
```

## Validation

```bash
# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('agents/orchestrator/flow-definitions.yaml'))"

# Validate sources
mastermind source validate --brain 01-product-strategy

# Check for bilingual instruction in prompts
grep -r "same language as the user" agents/
```
