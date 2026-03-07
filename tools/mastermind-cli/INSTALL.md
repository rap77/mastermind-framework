# MasterMind Framework - Installation Guide

## Overview

MasterMind Framework is a **cognitive architecture** that provides 7 specialized expert brains for product and technical consultation. Install it in any project to get instant access to world-class expertise.

## Installation Methods

### Method 1: UV (Recommended - Fastest)

```bash
# Navigate to framework directory
cd ~/proy/mastermind

# Install in editable mode (development)
uv pip install -e .

# Or install from PyPI (when published)
uv pip install mastermind-framework
```

### Method 2: PIP (Traditional)

```bash
# Navigate to framework directory
cd ~/proy/mastermind

# Install in editable mode
pip install -e .

# Or install from PyPI (when published)
pip install mastermind-framework
```

### Method 3: UVX (No Installation - Experimental)

```bash
# Run without installation
uvx --from git+https://github.com/rap77/mastermind-framework mastermind install init
```

## Project Setup

Once the framework is installed, activate it in your project:

```bash
# Navigate to your project
cd ~/proy/my-project

# Install MasterMind in this project
mastermind install init

# Verify installation
mastermind install status
```

### What Gets Installed

```
~/proy/my-project/
├── .mastermind/                    # Framework configuration
│   └── config.yaml                 # Active brains & settings
├── .mastermind-active              # Activation marker
├── .claude/
│   ├── hooks/
│   │   └── load-mastermind-context.sh  # Auto-load on session start
│   └── skills/
│       └── mastermind-consultant.md    # Main consultant skill
└── [your existing files]
```

## CLI Commands

### Installation Commands

```bash
# Install in current project
mastermind install init

# Install specific brains only
mastermind install init --brains #1,#4,#7

# Install with custom framework path
mastermind install init --framework-path ~/projects/mastermind

# Force reinstall
mastermind install init --force

# Show installation status
mastermind install status

# Uninstall from project
mastermind install uninstall

# Keep config when uninstalling
mastermind install uninstall --keep-config
```

### Framework Commands

```bash
# Show framework status
mastermind framework status

# Create a release
mastermind framework release --version 1.0.0
```

### Brain Commands

```bash
# Show all brains status
mastermind brain status

# Show specific brain status
mastermind brain status #1
```

### Orchestration Commands

```bash
# Full product flow (all 7 brains)
mastermind orchestrate brief.md --flow full_product

# Quick validation (brains #1 + #7)
mastermind orchestrate brief.md --flow validation_only

# Design sprint (brains #1-3 + #7)
mastermind orchestrate brief.md --flow design_sprint

# Dry run (no actual queries)
mastermind orchestrate brief.md --dry-run
```

## Usage in Claude Code

Once installed, the framework integrates seamlessly with Claude Code:

### 1. Automatic Activation

When you start a session in a project with `.mastermind-active`, the framework automatically activates:

```
SessionStart hook executes
→ Reads .mastermind-active
→ Loads framework context
→ mastermind-consultant skill becomes available
```

### 2. Query the Brains

Use the `mastermind-consultant` skill:

```python
# Example: Ask Product Strategy brain
mcp__notebooklm-mcp__notebook_query(
    notebook_id="f276ccb3-0bce-4069-8b55-eae8693dbe75",
    query="How should I prioritize features for my MVP?"
)
```

### 3. Quick Brain Selection

| Question | Brain |
|----------|-------|
| "Should I build this?" | #1 Product Strategy |
| "How do users interact?" | #2 UX Research |
| "How should this look?" | #3 UI Design |
| "Frontend architecture?" | #4 Frontend |
| "Backend architecture?" | #5 Backend |
| "Testing & deployment?" | #6 QA/DevOps |
| "Is this good? Improve?" | #7 Growth/Data |

## Configuration

### Project Configuration (`.mastermind/config.yaml`)

```yaml
project:
  name: my-project
  path: /home/user/projects/my-project

framework:
  version: 1.0.0
  path: /home/user/proy/mastermind

brains:
  #1:
    name: Product Strategy
    notebook_id: f276ccb3-0bce-4069-8b55-eae8693dbe75
    expertise: What & Why - Product definition, strategy, discovery
    active: true
  # ... (other brains)
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `MASTERMIND_FRAMEWORK_PATH` | Override framework auto-detection |
| `MASTERMIND_ACTIVE_BRAINS` | Override active brains selection |

## Uninstallation

### Remove from Project

```bash
# In your project directory
mastermind install uninstall

# Or manually
rm .mastermind-active
rm -rf .mastermind/
rm .claude/hooks/load-mastermind-context.sh
rm .claude/skills/mastermind-*.md
```

### Remove Framework Globally

```bash
# If installed with uv/pip
uv pip uninstall mastermind-framework
# or
pip uninstall mastermind-framework
```

## Troubleshooting

### "Command not found: mastermind"

**Solution:** The framework isn't installed or PATH isn't updated.

```bash
# Check installation
pip list | grep mastermind

# Reinstall
cd ~/proy/mastermind && uv pip install -e .
```

### "Could not find MasterMind Framework directory"

**Solution:** Set environment variable or use explicit path.

```bash
# Set environment variable
export MASTERMIND_FRAMEWORK_PATH=~/proy/mastermind

# Or use explicit path
mastermind install init --framework-path ~/proy/mastermind
```

### "Skill not activating in Claude Code"

**Solution:** Check that files are in place.

```bash
# Verify files exist
ls -la .mastermind-active
ls -la .claude/skills/mastermind-consultant.md
ls -la .claude/hooks/load-mastermind-context.sh

# Restart Claude Code
```

### "Brain not responding"

**Solution:** Check NotebookLM MCP connection.

```bash
# Verify MCP server is running
# Check .mastermind/config.yaml for correct notebook IDs
mastermind brain status #1
```

## Development

### Editable Installation (Development Mode)

```bash
# Clone repository
git clone https://github.com/rap77/mastermind-framework.git
cd mastermind-framework

# Install in editable mode
uv pip install -e .

# Now changes to the code are immediately available
```

### Running Tests

```bash
cd tools/mastermind-cli
uv run pytest tests/
```

## Versioning

This project uses Semantic Versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

Current version: **1.0.0**

## Support

- **Issues:** https://github.com/rap77/mastermind-framework/issues
- **Documentation:** https://github.com/rap77/mastermind-framework/blob/main/docs/
- **Community:** (Discord/Slack coming soon)

## License

MIT License - See LICENSE file for details.

## Credits

Created by [@rap77](https://github.com/rap77)

With contributions from the MasterMind community.

## Slash Commands for Quick Brain Access

Once installed, you can use these slash commands to quickly consult specific brains:

```bash
/ask product [question]     # Product Strategy - What & Why
/ask ux [question]          # UX Research - User experience
/ask design [question]      # UI Design - Visual design
/ask frontend [question]    # Frontend - Frontend architecture
/ask backend [question]     # Backend - Backend architecture
/ask qa [question]          # QA/DevOps - Testing & operations
/ask growth [question]      # Growth/Data - Metrics & evaluation
```

### Advanced Commands

```bash
/ask-all [question]        # ALL 7 brains as a team - comprehensive analysis
/ask-ui-docs [context]      # Generate UI/UX design system documentation
/audit [new|in-progress|stuck]  # Full project health check with all brains
/project-health-check [type]   # Same as /audit - comprehensive audit
```

### Project Health Check (`/audit`)

Run a comprehensive project audit using all 7 MasterMind brains:

**Project Types:**
- **NEW**: Projects with only documentation (validates architecture before coding)
- **IN-PROGRESS**: Partially built (analyzes what's working, what's missing)
- **STUCK**: Projects needing redirection (identifies issues + recovery plan)

**Example:**
```bash
# Audit an in-progress project
/audit in-progress

# Audit a new project with only documentation
/audit new

# Audit a stuck project
/audit stuck
```

**What it generates:**
- `docs/audit/EXECUTIVE-SUMMARY.md` - Overall health score, priorities, quick wins
- `docs/audit/brain-1-product-strategy.md` - Product alignment, feature prioritization
- `docs/audit/brain-2-ux-research.md` - UX patterns, user journey, research gaps
- `docs/audit/brain-3-ui-design.md` - Design system audit, component review
- `docs/audit/brain-4-frontend.md` - Frontend architecture, state management
- `docs/audit/brain-5-backend.md` - Backend architecture, database design, API quality
- `docs/audit/brain-6-qa-devops.md` - Test coverage, CI/CD, deployment
- `docs/audit/brain-7-growth-data.md` - Metrics, experimentation, improvements
- `docs/audit/missing-docs-*.md` - Generated documentation for identified gaps

### UI/UX Documentation (`/ask-ui-docs`)

Generate comprehensive UI/UX design system documentation:

**Example:**
```bash
/ask-ui-docs Next.js 16, React 19, Tailwind 4, shadcn/ui, product catalog phase
```

**What it generates:**
1. Design Tokens - Colors (hex), typography, spacing (exact values)
2. Component Library - Atomic components with all states
3. Layout System - Grid, breakpoints, containers
4. Mockup Specs - Redlining guidelines with exact measurements
5. Accessibility Guide - WCAG AA compliance checklist
6. Handoff Guide - For AI tools and developers

### Examples

```bash
# Quick product validation
/ask product Should we add social login as MVP feature?

# UX guidance
/ask ux How should we research user needs for this feature?

# Design decisions
/ask design What's the best pattern for this multi-step form?

# Frontend architecture
/ask frontend Zustand or Redux for Next.js 16 state management?

# Backend design
/ask backend How should we structure the API for multi-tenant SaaS?

# Testing strategy
/ask qa What's the best approach for E2E testing this feature?

# Evaluation
/ask growth Is this good MVP scope? What metrics should we track?
```

### Using Multiple Brains (Team Approach)

For comprehensive analysis, use multiple commands:

```bash
# 1. Product validation
/ask product Is this feature worth building?

# 2. UX research
/ask ux How do users currently solve this problem?

# 3. Design
/ask design What UI patterns work best?

# 4. Implementation
/ask frontend How do we build the frontend?
/ask backend How do we build the backend?

# 5. Quality
/ask qa How do we test this?

# 6. Evaluation
/ask growth Is this good? How do we improve?
```
