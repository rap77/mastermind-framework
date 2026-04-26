# MasterMind Framework — Deployment Guide

**Version:** 3.0.0
**Last Updated:** 2026-04-25

---

## Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Overview

**MasterMind Framework** is an enterprise agent orchestration platform with knowledge distillation for LATAM. It provides 7 specialized brains that collaborate to deliver expert-level software development guidance.

### Key Features

- 🧠 **7 Specialized Brains** — Product Strategy, UX Research, UI Design, Frontend, Backend, QA/DevOps, Growth/Data
- 🔄 **Knowledge Distillation** — Brains learn from every interaction and accumulate expertise
- 📊 **Centralized Memory** — PostgreSQL-based single source of truth for all projects
- 🤖 **Autonomous Agents** — discover, review, ship, and task execution agents
- 🚀 **Rust Control Plane** — High-performance state management with event sourcing

### What Makes MasterMind Different?

Traditional AI assistants forget everything between sessions. MasterMind remembers:

- Every brain consultation and its outcome
- Every architectural decision and rationale
- Every artifact generated (specs, reviews, plans)
- Every session and what was accomplished
- Patterns that emerge across multiple projects

This **knowledge distillation** means the system gets smarter with every use.

---

## System Requirements

### Required

| Component | Version | Purpose |
|-----------|---------|---------|
| **PostgreSQL** | 16+ | Centralized memory and single source of truth |
| **Docker** | Latest | Run PostgreSQL container |
| **Python** | 3.14+ | Run handlers and agents |
| **Git** | Latest | Version control |

### Optional but Recommended

| Component | Purpose |
|-----------|---------|
| **Rust Control Plane** | High-performance WebSocket hub (localhost:3001) |
| **Claude Code CLI** | Primary interface for running commands |

### Storage

- **Disk:** 500MB for PostgreSQL + 100MB for framework files
- **RAM:** 1GB minimum (2GB recommended for PostgreSQL)

---

## Architecture

### Centralized Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL (Single Source of Truth)         │
│                  localhost:5433/mastermind_bd                │
├─────────────────────────────────────────────────────────────┤
│  • projects          — All projects using MasterMind       │
│  • brain_consultations — Every brain query/response        │
│  • artifacts         — Specs, reviews, plans, ships        │
│  • decisions         — Architectural decisions             │
│  • experience_records — Brain learning & improvement        │
│  • dev_sessions      — Session history & metrics          │
└─────────────────────────────────────────────────────────────┘
                           ↑
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────┴─────┐   ┌─────┴─────┐   ┌─────┴─────┐
    │ Project A │   │ Project B │   │ Project C │
    │ (Next.js) │   │ (Python)  │   │ (Rust)    │
    └───────────┘   └───────────┘   └───────────┘

    All projects share memory and learn from each other
```

### Multi-Tenancy

- **Organizations** — Separate environments per company/team
- **Projects** — Each project gets its own context
- **Workspaces** — Branch-level isolation (master, develop, feature/*)

---

## How MasterMind Works

### Two Ways to Use MasterMind

**Method 1: Inside Claude Code (Recommended)** ✅
- Use slash commands directly in Claude Code interface
- Commands appear in autocomplete
- Full integration with Claude's context

**Method 2: Python Handlers (Scripts/CI)**
- Direct Python execution
- Useful for scripts, CI/CD, testing
- Same functionality as slash commands

```
Claude Code Interface          Terminal/Scripts
─────────────────────          ─────────────────

  /mm:discover               python3 .claude/commands/mm/discover-handler.py "idea"
       ↓                                 ↓
  /mm:review                python3 .claude/commands/mm/review-handler.py --staged
       ↓                                 ↓
  /mm:ship                  python3 .claude/commands/mm/ship-handler.py --verify
       ↓                                 ↓
  (Full Claude context)     (Standalone execution)
```

---

## Installation

### Step 1: Start PostgreSQL

MasterMind requires PostgreSQL for centralized memory. Start the container:

```bash
cd /path/to/mastermind
docker compose up -d
```

Verify PostgreSQL is running:

```bash
docker compose ps
# Should show: postgres ... Up ... 0.0.0.0:5433->5433/tcp
```

**Test connection:**

```bash
psql -h localhost -p 5433 -U postgres -d mastermind_bd -c "SELECT 1;"
# Should return: ?column?
#              ----------
#                       1
```

### Step 2: Install MasterMind in Your Project

**Option A: Install from Claude Code (Recommended)**

From your project directory in Claude Code:

```
/mm:init --target .
```

**Option B: Install from Terminal**

```bash
cd /path/to/your-project
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py --target .
```

**What gets installed:**

```
your-project/
├── .mastermind/
│   └── config.yaml          # Project configuration
├── .claude/
│   ├── commands/mm/         # Command handlers
│   │   ├── init-handler.py
│   │   ├── discover-handler.py
│   │   ├── complete-task-handler.py
│   │   ├── review-handler.py
│   │   └── ship-handler.py
│   ├── skills/mm/           # Brain interaction skills
│   │   ├── brain-context/
│   │   ├── discover/
│   │   ├── review/
│   │   └── ship/
│   └── agents/mm/           # Autonomous agents
│       ├── brain-01-product/
│       ├── brain-02-ux/
│       ├── ... (7 brains)
│       ├── discover-planner/
│       ├── rediscovery-auditor/
│       └── task-executor/
```

### Step 3: Verify Installation

```bash
python3 .claude/commands/mm/init-handler.py --check --target .
# Should return: STATUS: installed
```

Check your configuration:

```bash
cat .mastermind/config.yaml
```

---

## Available Commands

### Slash Commands (Inside Claude Code)

**Primary way to use MasterMind** — These commands appear in Claude Code's autocomplete:

| Command | Purpose | Example |
|---------|---------|---------|
| `/mm:init` | Install MasterMind in project | `/mm:init --target .` |
| `/mm:discover` | Generate specs from ideas | `/mm:discover "Add auth"` |
| `/mm:complete-task` | Execute task from plan | `/mm:complete-task A1` |
| `/mm:review` | Code review with brains | `/mm:review --staged` |
| `/mm:ship` | Create releases | `/mm:ship --verify` |
| `/mm:safe-commit` | Commit with cognitive barrier | `/mm:safe-commit` |

**Brain Consultation Commands:**
- `/mm:ask-product` — Brain #1 (Product Strategy)
- `/mm:ask-ux` — Brain #2 (UX Research)
- `/mm:ask-ui` — Brain #3 (UI Design)
- `/mm:ask-frontend` — Brain #4 (Frontend)
- `/mm:ask-backend` — Brain #5 (Backend)
- `/mm:ask-qa` — Brain #6 (QA/DevOps)
- `/mm:ask-growth` — Brain #7 (Growth/Data)

**Additional Commands:**
- `/mm:propose` — Generate proposals
- `/mm:audit` — Project health check
- `/mm:discovery` — Deep project analysis

### Python Handlers (Terminal/Scripts)

**Same functionality, for scripts and CI/CD:**

```bash
# Equivalent to /mm:discover
python3 .claude/commands/mm/discover-handler.py "Add auth"

# Equivalent to /mm:review --staged
python3 .claude/commands/mm/review-handler.py --staged

# Equivalent to /mm:ship --verify
python3 .claude/commands/mm/ship-handler.py --verify
```

---

## Quick Start

### Using Claude Code (Recommended)

**1. Discover a feature:**
```
/mm:discover "Add user authentication with OAuth2"
```

**2. Review changes:**
```
/mm:review --staged
```

**3. Ship a version:**
```
/mm:ship --verify
```

### Using Terminal (Alternative)

**1. Discover a New Feature Idea**

```bash
cd /path/to/your-project
python3 .claude/commands/mm/discover-handler.py "Add user authentication with OAuth2"
```

**What happens:**
1. Brain #1 (Product Strategy) analyzes the idea
2. Brain #7 (Growth) validates opportunity
3. Generates `tasks/SPEC.md` with requirements
4. Generates `tasks/plan.md` with implementation phases
5. Generates `tasks/todo.md` with task checklist

### 2. Review Your Changes

```bash
# Review uncommitted changes
python3 .claude/commands/mm/review-handler.py

# Review staged changes
python3 .claude/commands/mm/review-handler.py --staged

# Review last commit
python3 .claude/commands/mm/review-handler.py --last-commit
```

**What happens:**
1. Generates diff of changes
2. Brain #6 (QA) analyzes testing implications
3. Brain #7 (Growth) evaluates system impact
4. Creates 5-axis review report (correctness, readability, architecture, security, performance)
5. Saves to `.planning/REVIEWS/timestamp-review.md`

### 3. Ship a Version

```bash
# Dry-run (verify before shipping)
python3 .claude/commands/mm/ship-handler.py --verify

# Create patch version
python3 .claude/commands/mm/ship-handler.py --patch

# Create specific version
python3 .claude/commands/mm/ship-handler.py --tag v1.2.0
```

**What happens:**
1. Validates preconditions (tests pass, no uncommitted changes, SPEC exists)
2. Runs full test suite (backend + frontend)
3. Creates semantic git tag
4. Archives tasks to `.planning/archive/<version>/`
5. Updates project configuration
6. Generates changelog

---

## Configuration

### Project Configuration (.mastermind/config.yaml)

```yaml
project:
  name: "your-project-name"
  slug: "your-project"        # URL-safe identifier

framework:
  version: 3.0.0

database:
  host: localhost
  port: 5433
  database: mastermind_bd
  user: postgres

stack:
  - typescript                 # Detected technologies
  - nextjs
  - python

brains:
  active: [1, 2, 3, 4, 5, 6, 7]  # All 7 brains enabled
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `MASTERMIND_DB_HOST` | PostgreSQL host | localhost |
| `MASTERMIND_DB_PORT` | PostgreSQL port | 5433 |
| `MASTERMIND_DB_NAME` | Database name | mastermind_bd |
| `MASTERMIND_DB_USER` | Database user | postgres |

---

## Troubleshooting

### PostgreSQL Issues

**Problem:** `psycopg2 not installed — database operations disabled`

**Solution:**
```bash
uv add psycopg2-binary
# OR
pip install psycopg2-binary
```

**Problem:** `connection refused` to PostgreSQL

**Solution:**
```bash
# Check if PostgreSQL is running
docker compose ps

# Start PostgreSQL
docker compose up -d

# Check port 5433 is available
netstat -an | grep 5433
```

### Installation Issues

**Problem:** `STATUS: not-installed` after running init

**Solution:**
```bash
# Check if installation actually happened
ls -la .mastermind/
ls -la .claude/commands/mm/

# Re-run with force flag
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py --target . --force
```

**Problem:** Handlers fail with `ModuleNotFoundError`

**Solution:**
```bash
# Verify all files were copied
ls -la .claude/commands/mm/*.py

# Check Python version (requires 3.14+)
python3 --version
```

### Command Issues

**Problem:** Discover agent doesn't generate files

**Solution:**
```bash
# Check if discover-planner agent exists
ls -la .claude/agents/mm/discover-planner/

# Verify session context
cat .planning/.mm-flow/runtime-state.json
```

**Problem:** Review fails with "no changes detected"

**Solution:**
```bash
# Make sure you have changes to review
git status

# Use --staged if changes are staged
git add .
python3 .claude/commands/mm/review-handler.py --staged
```

**Problem:** Ship fails with "preconditions failed"

**Solution:**
```bash
# Check what's failing
python3 .claude/commands/mm/ship-handler.py --verify

# Common issues:
# - Tests failing: Run test suite and fix failures
# - Uncommitted changes: Commit or stash changes
# - Missing SPEC.md: Run /mm:discover first
```

### Performance Issues

**Problem:** Slow brain consultations

**Solution:**
```bash
# Check PostgreSQL query performance
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Check for long-running queries
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "SELECT pid, now() - query_start as duration, query FROM pg_stat_activity WHERE state = 'active';"
```

### Getting Help

If issues persist:

1. Check logs: `.planning/.mm-flow/runtime-state.json`
2. Review database: Connect to PostgreSQL and check tables
3. Enable debug mode: Set `MASTERMIND_DEBUG=1` environment variable
4. Report issues: GitHub issues with full error messages and context

---

## Advanced Usage

### Multi-Project Setup

If you have multiple projects sharing the same MasterMind instance:

```bash
# Project 1
cd ~/projects/project-a
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py --target .

# Project 2
cd ~/projects/project-b
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py --target .

# Both projects share:
# - Same PostgreSQL database
# - Same brain memory
# - Cross-project learning
```

### Custom Brain Configuration

To disable specific brains or customize behavior:

```yaml
# .mastermind/config.yaml
brains:
  active: [1, 6, 7]  # Only Product, QA, and Growth brains
```

### Database Backup

```bash
# Backup entire database
docker exec mastermind-postgres-1 pg_dump -U postgres mastermind_bd > backup.sql

# Restore from backup
docker exec -i mastermind-postgres-1 psql -U postgres mastermind_bd < backup.sql
```

---

## Next Steps

- See [QUICKSTART.md](QUICKSTART.md) for detailed walkthrough
- See [EXAMPLES.md](EXAMPLES.md) for command examples
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Check `.planning/ROADMAP.md` for future roadmap

---

**Version:** 3.0.0
**Documentation Last Updated:** 2026-04-25
**Support:** GitHub Issues
