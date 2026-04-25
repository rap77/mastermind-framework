---
name: mm:ship
description: Generate ship payload with version management, changelog, and preconditions verification
argument-hint: "[--verify] [--tag vX.Y.Z] [--patch|--minor|--major] [--archive] [--cleanup]"
---

# /mm:ship

Ship: verify preconditions, calculate next version, generate changelog, and delegate to ship-executor agent for tagging and archiving.

## Usage

```bash
# Mode 1: Full ship (default - increment patch)
/mm:ship

# Mode 2: Verify only (dry-run, no tag created)
/mm:ship --verify

# Mode 3: Explicit version
/mm:ship --tag v0.2.0

# Mode 4: Increment types
/mm:ship --patch    # v0.1.0 → v0.1.1 (default)
/mm:ship --minor    # v0.1.0 → v0.2.0
/mm:ship --major    # v0.1.0 → v1.0.0

# Mode 5: Archive artifacts only
/mm:ship --archive

# Mode 6: Cleanup temporary files only
/mm:ship --cleanup
```

## What It Does

### Input

**Git state** and **version tags**:
- Last tag: `git describe --tags --abbrev=0`
- Changelog: `git log vX.Y.Z..HEAD --oneline`
- Uncommitted check: `git diff --quiet`
- Tests status: `pytest` + `vitest` results

### Process

1. **Handler Execution:**
   ```bash
   python3 .claude/commands/mm/ship-handler.py [options]
   ```

2. **Precondition Verification:**
   - Tests passing (frontend + backend)
   - No uncommitted changes
   - `SPEC.md` exists in `tasks/`

3. **Version Calculation:**
   - Read last tag from git
   - Calculate next version (patch/minor/major)
   - Generate changelog from commits

4. **Ship-Executor Delegation:**
   ```
   Agent(subagent_type="ship-executor")
   ```

5. **Ship Execution:**
   - Run tests (if not --verify mode)
   - Create git tag
   - Archive `tasks/` to `.planning/archive/<version>/`
   - Cleanup `.agent-*-running` files
   - Update `.mastermind/config.yaml` with version

### Output

**Structured Payload:**
```
MODE: ship|verify|archive|cleanup
CURRENT_TAG: v0.1.0
NEXT_TAG: v0.1.1
CHANGELOG: 12 commits since v0.1.0
PRECONDITIONS: pass|fail
LAUNCH: ship-executor
PAYLOAD: {...json...}
```

**Archive Format:**
```
.planning/archive/<version>/
├── SPEC.md
├── plan.md
├── todo.md
└── REVIEWS/
```

## Flags

### Mode Flags

| Flag | Description |
|------|-------------|
| `--verify` | Dry-run: verify preconditions without creating tag |
| `--archive` | Archive artifacts only |
| `--cleanup` | Cleanup temporary files only |

### Version Flags

| Flag | Example | Increment |
|------|---------|-----------|
| `--tag vX.Y.Z` | `--tag v1.2.3` | Explicit tag (overrides auto-calculation) |
| `--patch` | v0.1.0 → v0.1.1 | Patch version (default) |
| `--minor` | v0.1.0 → v0.2.0 | Minor version |
| `--major` | v0.1.0 → v1.0.0 | Major version |

**Only one version flag allowed.** If none specified, `--patch` is default.

## Preconditions

### Required Before Ship

1. **Tests Passing:**
   ```bash
   # Backend
   cd apps/api && uv run pytest

   # Frontend
   cd apps/web && pnpm test
   ```

2. **No Uncommitted Changes:**
   ```bash
   git diff --quiet  # Should exit with 0
   ```

3. **SPEC.md Exists:**
   ```bash
   ls tasks/SPEC.md  # Should exist
   ```

### Failing Preconditions

If any precondition fails:
- `--verify` mode: Reports failure, exits
- `--ship` mode: Aborts before creating tag

## Architecture

```
/mm:ship
    ↓
ship-handler.py (Python script)
    ↓
Verifies preconditions:
    - Tests pass?
    - No uncommitted?
    - SPEC.md exists?
    ↓
Calculates version:
    - Reads last tag
    - Generates changelog
    - Calculates next version
    ↓
Ship-Executor Agent
    ↓
Creates git tag
Archives tasks/
Cleanup temporary files
Updates config.yaml
```

## Changelog Format

Generated from git commits:
```
v0.1.0...HEAD (12 commits)

feat(mm-commands): add init, review, ship commands
fix(handler): correct tag detection logic
docs(readme): update installation instructions
test(ship): add 15 tests for ship-handler
...
```

## Archive Format

After ship, artifacts are moved:
```
.planning/archive/v0.1.0/
├── SPEC.md           # Original specification
├── plan.md           # Implementation plan
├── todo.md           # Completed checklist
└── REVIEWS/          # All code reviews
    ├── 2026-04-23-review-handler-C1.md
    ├── 2026-04-23-phase-c-code-review.md
    └── ...
```

## Examples

### Example 1: Full Ship (Patch Increment)

```bash
$ /mm:ship

INFO: Verifying preconditions...
INFO: Tests: PASS
INFO: Uncommitted changes: NONE
INFO: SPEC.md: EXISTS

MODE: ship
CURRENT_TAG: v0.1.0
NEXT_TAG: v0.1.1
CHANGELOG: 8 commits since v0.1.0
PRECONDITIONS: pass
LAUNCH: ship-executor

✓ Tag created: v0.1.1
✓ Archived to: .planning/archive/v0.1.0/
✓ Cleaned up: 3 .agent-*-running files
✓ Updated config: v0.1.1
```

### Example 2: Verify Only (Dry-Run)

```bash
$ /mm:ship --verify

INFO: Verifying preconditions...
INFO: Tests: PASS
INFO: Uncommitted changes: DETECTED

MODE: verify
CURRENT_TAG: v0.1.0
NEXT_TAG: v0.1.1
CHANGELOG: 8 commits since v0.1.0
PRECONDITIONS: fail

ERROR: Cannot ship with uncommitted changes
```

### Example 3: Minor Version

```bash
$ /mm:ship --minor

MODE: ship
CURRENT_TAG: v0.1.0
NEXT_TAG: v0.2.0
CHANGELOG: 42 commits since v0.1.0
PRECONDITIONS: pass

✓ Tag created: v0.2.0
```

## Files

- `.claude/commands/mm/ship.md` — This file
- `.claude/commands/mm/ship-handler.py` — Python handler script
- `.claude/agents/mm/ship-executor/ship-executor.md` — Ship agent definition
- `.planning/archive/<version>/` — Archive output directory

## Related Commands

- `/mm:discover` — Generate specs and plans
- `/mm:complete-task` — Execute tasks with automatic review
- `/mm:review` — Code review with 5-axis analysis
- `/mm:safe-commit` — Commit with pre-commit validation
