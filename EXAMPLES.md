# MasterMind Framework — Command Examples

**Real-world examples for every command**

---

## 🎯 How to Read These Examples

Each command example shows **TWO formats**:

**Format 1: Slash Command (Inside Claude Code)** ✅ *Recommended*
```
/mm:discover "Add feature"
```

**Format 2: Python Handler (Terminal/Scripts)**
```bash
python3 .claude/commands/mm/discover-handler.py "Add feature"
```

**Both do the same thing** — choose what works for you:
- Use **slash commands** when working in Claude Code
- Use **Python handlers** for scripts, CI/CD, or testing

---

## Table of Contents

- [Discover Command](#discover-command)
- [Complete-Task Command](#complete-task-command)
- [Review Command](#review-command)
- [Ship Command](#review-command)
- [Init Command](#init-command)
- [Common Workflows](#common-workflows)

---

## Discover Command

### Example 1: Simple Feature Discovery

```bash
python3 .claude/commands/mm/discover-handler.py "Add user login with email and password"
```

**Output:**
```
MODE: new
TASK: discover-planner
PAYLOAD: {
  "mode": "new",
  "idea": "Add user login with email and password",
  "discovery_mode": "fast",
  "working_dir": "/home/user/project",
  "timestamp": "2026-04-25T22:00:00.000Z",
  "session_id": "discover-new-20260425-220000"
}
LAUNCH: discover-planner
INFO: Discovering new project idea...
INFO: Consulted Brain #1 (Product Strategy)
INFO: Consulted Brain #7 (Growth)
INFO: Generated tasks/SPEC.md
INFO: Generated tasks/plan.md
INFO: Generated tasks/todo.md
```

**Generated Files:**
- `tasks/SPEC.md` — Feature requirements
- `tasks/plan.md` — Implementation phases A1-A4
- `tasks/todo.md` — Checklist of tasks

---

### Example 2: Deep Discovery Mode

```bash
python3 .claude/commands/mm/discover-handler.py \
  "Build real-time collaborative whiteboard with WebSockets" \
  --mode deep
```

**Difference:** Deep mode spends more time analyzing:
- Architecture implications
- Technology trade-offs
- Security considerations
- Performance requirements

---

### Example 3: Existing Project Audit

```bash
python3 .claude/commands/mm/discover-handler.py \
  --existing \
  --health
```

**Output:**
```
MODE: existing
TASK: rediscovery-auditor
INFO: Auditing existing project...
INFO: Project Health: GOOD
INFO: Coverage: 85% (7/8 phases complete)
INFO: Gaps Found: 2
  - Missing: Integration tests
  - Missing: Deployment documentation
```

---

## Complete-Task Command

### Example 1: Execute Single Task

```bash
python3 .claude/commands/mm/complete-task-handler.py A1
```

**Output:**
```
INFO: Starting task A1
TASK: A1
TITLE: Eliminar GSD Wrapper Commands
SUBTASK: A1.1 [x] (Borrar `.claude/commands/mm/new-milestone.md`)
SUBTASK: A1.2 [x] (Borrar `.claude/commands/mm/plan-phase.md`)
SUBTASK: A1.3 [x] (Borrar `.claude/commands/mm/execute-phase.md`)
...
GIT: 5/8 subtasks have commits
STATUS: TASK IN PROGRESS - 3 subtasks remaining
```

---

### Example 2: Execute Multiple Tasks

```bash
# Execute tasks in sequence
python3 .claude/commands/mm/complete-task-handler.py A1
python3 .claude/commands/mm/complete-task-handler.py A2
python3 .claude/commands/mm/complete-task-handler.py A3
```

---

## Review Command

### Example 1: Review Uncommitted Changes

```bash
python3 .claude/commands/mm/review-handler.py
```

**Use case:** Review code before committing

---

### Example 2: Review Staged Changes

```bash
# Stage changes first
git add src/auth.js

# Review staged
python3 .claude/commands/mm/review-handler.py --staged
```

**Use case:** Review what's about to be committed

---

### Example 3: Review Last Commit

```bash
python3 .claude/commands/mm/review-handler.py --last-commit
```

**Use case:** Review commit you just made

**Sample Output:**
```
MODE: review
SCOPE: last-commit
FILES: ["src/auth.js"]
LINES: 45
LANGUAGES: ["javascript"]
LAUNCH: code-reviewer

INFO: Reviewing 1 file(s)
INFO: Languages detected: javascript
INFO: Consulted Brain #6 (QA)
INFO: Consulted Brain #7 (Growth)
INFO: Report saved to .planning/REVIEWS/2026-04-25-221500-review.md
```

---

### Example 4: Review Specific Files

```bash
python3 .claude/commands/mm/review-handler.py \
  --files src/auth.js src/user.ts src/login.test.js
```

**Use case:** Review specific files without staging

---

### Example 5: Review Branch Comparison

```bash
python3 .claude/commands/mm/review-handler.py \
  --branch feature/auth
```

**Use case:** Review all changes in a feature branch

---

### Example 6: Review with Custom Line Limit

```bash
python3 .claude/commands/mm/review-handler.py \
  --max-lines 1000
```

**Use case:** Review large diffs (default limit is 500 lines)

---

## Ship Command

### Example 1: Verify Before Shipping

```bash
python3 .claude/commands/mm/ship-handler.py --verify
```

**Sample Output:**
```
MODE: verify
CURRENT_TAG: v0.1.0
NEXT_TAG: v0.1.1
CHANGELOG: 3 commits since v0.1.0
PRECONDITIONS: pass
LAUNCH: ship-executor

INFO: Changelog (3 commits):
  - feat: add user authentication
  - fix: password validation bug
  - docs: update README
```

**Use case:** Check if ready to ship without creating tag

---

### Example 2: Ship Patch Version

```bash
python3 .claude/commands/mm/ship-handler.py --patch
```

**Version bump:** v0.1.0 → v0.1.1

**Use case:** Bug fixes, small improvements

---

### Example 3: Ship Minor Version

```bash
python3 .claude/commands/mm/ship-handler.py --minor
```

**Version bump:** v0.1.0 → v0.2.0

**Use case:** New features, backward compatible

---

### Example 4: Ship Major Version

```bash
python3 .claude/commands/mm/ship-handler.py --major
```

**Version bump:** v0.1.0 → v1.0.0

**Use case:** Breaking changes, major milestones

---

### Example 5: Ship Specific Version

```bash
python3 .claude/commands/mm/ship-handler.py --tag v2.0.0
```

**Use case:** Explicit version control

---

### Example 6: Archive Only (No Tag)

```bash
python3 .claude/commands/mm/ship-handler.py --archive
```

**Use case:** Archive completed tasks without creating version

---

### Example 7: Cleanup Only

```bash
python3 .claude/commands/mm/ship-handler.py --cleanup
```

**What it does:**
- Removes `.agent-*-running` markers
- Cleans up stale task progress files

**Use case:** Maintenance between features

---

## Init Command

### Example 1: Install in Current Directory

```bash
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py --target .
```

---

### Example 2: Install in Specific Directory

```bash
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py \
  --target /home/user/my-project
```

---

### Example 3: Check Installation

```bash
python3 .claude/commands/mm/init-handler.py --check
```

**Sample Output:**
```
Checking MasterMind installation...
INFO: PostgreSQL container is running
INFO: PostgreSQL is listening on localhost:5433
INFO: Project registered in database
INFO: Commands: 5 installed
INFO: Skills: 6 installed
INFO: Agents: 10 installed
STATUS: installed
```

---

### Example 4: Force Re-installation

```bash
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py \
  --target . \
  --force
```

**Use case:** Overwrite existing installation

---

## Common Workflows

### Workflow 1: Feature from Idea to Ship

```bash
# 1. Discover feature
python3 .claude/commands/mm/discover-handler.py \
  "Add password reset functionality"

# 2. Review generated spec
cat tasks/SPEC.md

# 3. Execute first task
python3 .claude/commands/mm/complete-task-handler.py A1

# 4. Make code changes
vim src/password-reset.js

# 5. Review before commit
git add src/password-reset.js
python3 .claude/commands/mm/review-handler.py --staged

# 6. Commit if review passes
git commit -m "feat: add password reset"

# 7. Complete remaining tasks
python3 .claude/commands/mm/complete-task-handler.py A2
python3 .claude/commands/mm/complete-task-handler.py A3

# 8. Final review
python3 .claude/commands/mm/review-handler.py --last-commit

# 9. Ship feature
python3 .claude/commands/mm/ship-handler.py --minor
```

---

### Workflow 2: Code Review Before Push

```bash
# 1. Make changes
vim src/component.tsx

# 2. Run tests
npm test

# 3. Stage changes
git add src/component.tsx

# 4. Review
python3 .claude/commands/mm/review-handler.py --staged

# 5. Read review report
cat .planning/REVIEWS/$(ls -t .planning/REVIEWS/ | head -1)

# 6. Commit if approved
git commit -m "fix: component rendering bug"

# 7. Push
git push origin feature/bugfix
```

---

### Workflow 3: Release Process

```bash
# 1. Ensure all tasks complete
cat tasks/todo.md

# 2. Run full test suite
pytest
npm test

# 3. Verify ship readiness
python3 .claude/commands/mm/ship-handler.py --verify

# 4. If preconditions pass, ship
python3 .claude/commands/mm/ship-handler.py --minor

# 5. Push tag
git push origin v0.2.0
```

---

### Workflow 4: Project Health Check

```bash
# 1. Audit existing project
python3 .claude/commands/mm/discover-handler.py \
  --existing \
  --health

# 2. Check for gaps
python3 .claude/commands/mm/discover-handler.py \
  --existing \
  --gaps

# 3. Re-plan if needed
python3 .claude/commands/mm/discover-handler.py \
  --existing \
  --replan
```

---

## Advanced Examples

### Example 1: Multi-File Review with Context

```bash
# Review multiple related files
python3 .claude/commands/mm/review-handler.py \
  --files \
    src/auth/login.ts \
    src/auth/session.ts \
    src/auth/middleware.ts \
    tests/auth.test.ts
```

**Brain #6 (QA) analyzes:** Test coverage across all auth files
**Brain #7 (Growth) analyzes:** System impact of auth changes

---

### Example 2: Review Large Diff

```bash
# Review with higher line limit
python3 .claude/commands/mm/review-handler.py \
  --staged \
  --max-lines 2000
```

**Use case:** Feature branch with many changes

---

### Example 3: Ship with Archive

```bash
# Ship and archive in one command
python3 .claude/commands/mm/ship-handler.py \
  --tag v1.0.0 \
  --archive
```

**Result:**
- Git tag v1.0.0 created
- Tasks moved to `.planning/archive/v1.0.0/`
- Cleanup executed

---

### Example 4: Batch Task Execution

```bash
# Execute all A-series tasks
for task in A1 A2 A3 A4; do
  python3 .claude/commands/mm/complete-task-handler.py $task
done
```

---

## Tips & Best Practices

### Tip 1: Always Review Before Commit

```bash
# Make it a habit
git add .
python3 .claude/commands/mm/review-handler.py --staged
git commit -m "message"
```

### Tip 2: Verify Before Ship

```bash
# Never ship without verification
python3 .claude/commands/mm/ship-handler.py --verify
# Only if pass:
python3 .claude/commands/mm/ship-handler.py --patch
```

### Tip 3: Use Shell Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias mmd='python3 .claude/commands/mm/discover-handler.py'
alias mmr='python3 .claude/commands/mm/review-handler.py'
alias mms='python3 .claude/commands/mm/ship-handler.py'
alias mmt='python3 .claude/commands/mm/complete-task-handler.py'
```

### Tip 4: Read Review Reports

```bash
# Latest review
cat .planning/REVIEWS/$(ls -t .planning/REVIEWS/ | head -1)

# All reviews
ls -lt .planning/REVIEWS/ | head -10
```

### Tip 5: Check Task Progress

```bash
# Current progress
cat .planning/task-progress.json

# TODO list
cat tasks/todo.md
```

---

## Command Reference Quick Sheet

| Command | Common Flags | Purpose |
|---------|--------------|---------|
| `discover` | `--mode deep`, `--existing` | Generate specs from ideas |
| `complete-task` | `A1`, `B2`, etc. | Execute task from plan |
| `review` | `--staged`, `--last-commit`, `--branch` | Code review with brains |
| `ship` | `--verify`, `--patch`, `--minor`, `--major` | Create releases |
| `init` | `--check`, `--force` | Install in project |

---

**Need more?** See [QUICKSTART.md](QUICKSTART.md) or [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
