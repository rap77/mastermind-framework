# MasterMind Framework — Quick Start Guide

**Get started in 5 minutes**

---

## 💡 Important: Two Ways to Use MasterMind

**Recommended: Use Slash Commands in Claude Code**
```
/mm:discover "Add feature"
/mm:review --staged
/mm:ship --verify
```

**Alternative: Python Handlers in Terminal**
```bash
python3 .claude/commands/mm/discover-handler.py "Add feature"
```

This guide shows **BOTH** methods. Choose what works for you.

---

## Prerequisites (30 seconds)

```bash
# 1. Start PostgreSQL
cd /path/to/mastermind
docker compose up -d

# 2. Verify it's running
docker compose ps | grep postgres
# Should show: Up ... 0.0.0.0:5433->5433/tcp
```

---

## Installation (1 minute)

### Option A: Install in Current Project (From Claude Code)

```
/mm:init --target .
```

### Option B: Install in Current Project (From Terminal)

```bash
cd /path/to/your-project
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py --target .
```

### Option C: Install in New Project

```bash
mkdir my-new-project && cd my-new-project
git init
/mm:init --target .
# OR from terminal:
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py --target .
```

### Verify Installation

**From Claude Code:**
```
/mm:init --check
```

**From Terminal:**
```bash
python3 .claude/commands/mm/init-handler.py --check
# Output: STATUS: installed
```

---

## Your First Workflow (3 minutes)

### Step 1: Discover a Feature Idea

**From Claude Code (Recommended):**
```
/mm:discover "Add user authentication with email and password"
```

**From Terminal:**
```bash
python3 .claude/commands/mm/discover-handler.py "Add user authentication with email and password"
```

**What you get:**
- `tasks/SPEC.md` — Feature requirements
- `tasks/plan.md` — Implementation phases
- `tasks/todo.md` — Task checklist

**Example output:**
```
MODE: new
TASK: discover-planner
LAUNCH: discover-planner
INFO: Discovering new project idea...
INFO: Consulted Brain #1 (Product Strategy)
INFO: Consulted Brain #7 (Growth)
INFO: Generated tasks/SPEC.md
INFO: Generated tasks/plan.md
INFO: Generated tasks/todo.md
```

### Step 2: Review Generated Specification

```bash
cat tasks/SPEC.md
```

**Example content:**
```markdown
# SPEC: User Authentication System

## Feature Overview
Add user authentication with email/password and session management.

## Requirements
- User registration with email validation
- Secure password hashing (bcrypt)
- Session management with JWT tokens
- Password reset flow
```

### Step 3: Execute a Task

**From Claude Code:**
```
/mm:complete-task A1
```

**From Terminal:**
```bash
python3 .claude/commands/mm/complete-task-handler.py A1
```

**What happens:**
- Task A1 is marked as in-progress
- Agent executes subtasks
- Progress tracked in `task-progress.json`

### Step 4: Review Your Changes

```bash
# Make some changes to your code
echo "// TODO: implement auth" >> src/auth.js

# Stage changes
git add .
```

**From Claude Code:**
```
/mm:review --staged
```

**From Terminal:**
```bash
python3 .claude/commands/mm/review-handler.py --staged
```

**What you get:**
- 5-axis code review (correctness, readability, architecture, security, performance)
- Brain #6 (QA) analysis of testing gaps
- Brain #7 (Growth) system impact evaluation
- Report saved to `.planning/REVIEWS/timestamp-review.md`

**Example output:**
```
MODE: review
SCOPE: staged
FILES: ["src/auth.js"]
LINES: 1
LANGUAGES: ["javascript"]
LAUNCH: code-reviewer
INFO: Reviewing 1 file(s)
INFO: Consulted Brain #6 (QA)
INFO: Consulted Brain #7 (Growth)
INFO: Report saved to .planning/REVIEWS/2026-04-25-214500-review.md
```

### Step 5: Ship Your Feature

**From Claude Code:**
```
/mm:ship --verify
/mm:ship --patch
```

**From Terminal:**
```bash
# First, verify everything is ready
python3 .claude/commands/mm/ship-handler.py --verify

# If all good, create version
python3 .claude/commands/mm/ship-handler.py --patch
```

**What happens:**
- Validates preconditions (tests pass, no uncommitted changes)
- Runs full test suite
- Creates git tag (e.g., v0.1.1)
- Archives tasks to `.planning/archive/v0.1.1/`
- Generates changelog

---

## Common Workflows

### Workflow 1: Start New Feature

**From Claude Code:**
```
# 1. Discover feature
/mm:discover "Add dark mode toggle"

# 2. Review generated spec
cat tasks/SPEC.md

# 3. Start first task
/mm:complete-task A1
```

**From Terminal:**
```bash
# 1. Discover feature
python3 .claude/commands/mm/discover-handler.py "Add dark mode toggle"

# 2. Review generated spec
cat tasks/SPEC.md

# 3. Start first task
python3 .claude/commands/mm/complete-task-handler.py A1
```

### Workflow 2: Code Review Before Commit

```bash
# 1. Make changes
vim src/component.tsx

# 2. Stage changes
git add src/component.tsx
```

**From Claude Code:**
```
# 3. Review before committing
/mm:review --staged

# 4. If review passes, commit
```

**From Terminal:**
```bash
# 3. Review before committing
python3 .claude/commands/mm/review-handler.py --staged

# 4. If review passes, commit
```

```bash
git commit -m "feat: add dark mode toggle"
```

### Workflow 3: Ship a Release

```bash
# 1. Ensure all tasks complete
cat tasks/todo.md

# 2. Run tests
pytest  # or npm test
```

**From Claude Code:**
```
# 3. Verify ship preconditions
/mm:ship --verify

# 4. Create release
/mm:ship --minor
```

**From Terminal:**
```bash
# 3. Verify ship preconditions
python3 .claude/commands/mm/ship-handler.py --verify

# 4. Create release
python3 .claude/commands/mm/ship-handler.py --minor
```

### Workflow 4: Review Previous Commit

```bash
# Review the last commit you made
python3 .claude/commands/mm/review-handler.py --last-commit
```

---

## Real-World Example

Building a TODO app from scratch:

```bash
# 1. Create project
mkdir todo-app && cd todo-app
npm init -y
git init

# 2. Install MasterMind
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py --target .

# 3. Discover feature
python3 .claude/commands/mm/discover-handler.py "Simple TODO app with add, remove, and mark complete"

# 4. Review specification
cat tasks/SPEC.md

# 5. Execute first task
python3 .claude/commands/mm/complete-task-handler.py A1

# 6. Make changes based on task guidance
vim index.html
vim app.js

# 7. Review before commit
git add .
python3 .claude/commands/mm/review-handler.py --staged

# 8. Commit if review passes
git commit -m "feat: add TODO list UI"

# 9. Ship version
python3 .claude/commands/mm/ship-handler.py --tag v0.1.0
```

---

## Tips & Tricks

### Tip 1: Use Shell Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# MasterMind aliases
alias mmd='python3 .claude/commands/mm/discover-handler.py'
alias mmr='python3 .claude/commands/mm/review-handler.py'
alias mms='python3 .claude/commands/mm/ship-handler.py'
alias mmt='python3 .claude/commands/mm/complete-task-handler.py'
```

Usage:
```bash
mmd "Add user profile feature"
mmr --last-commit
mms --verify
```

### Tip 2: Integrate with Git Hooks

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run MasterMind review on staged changes
python3 .claude/commands/mm/review-handler.py --staged
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Tip 3: Review Multiple Files

```bash
# Review specific files
python3 .claude/commands/mm/review-handler.py --files src/auth.js src/user.ts
```

### Tip 4: Compare with Branch

```bash
# Review changes compared to main branch
python3 .claude/commands/mm/review-handler.py --branch main
```

### Tip 5: Check What Brain #7 Thinks

The review report shows Brain #7's system impact analysis:

```bash
cat .planning/REVIEWS/2026-04-25-214500-review.md | grep -A 20 "Brain #7"
```

---

## What's Next?

- Read [DEPLOYMENT.md](DEPLOYMENT.md) for architecture details
- Check [EXAMPLES.md](EXAMPLES.md) for more examples
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you hit issues

---

**Quick Start Time:** 5 minutes
**First Feature:** 15 minutes
**Full Workflow Mastery:** 1 hour
