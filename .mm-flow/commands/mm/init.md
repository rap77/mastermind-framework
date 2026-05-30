---
name: mm:init
description: Install MasterMind Framework in any project. Verifies PostgreSQL, copies commands/skills/agents, and registers project in database.
argument-hint: "[--target <path>] [--check] [--force]"
---

# /mm:init

Install MasterMind Framework into any project. Verifies services, detects stack, copies framework files, and registers in PostgreSQL.

## Usage

```bash
# Install in current directory
/mm:init

# Install in specific directory
/mm:init --target /path/to/project

# Check if already installed
/mm:init --check

# Force reinstall (overwrite existing)
/mm:init --target /path/to/project --force
```

## What It Does

### Installation Process

1. **Prerequisites Check:**
   - **PostgreSQL:** Verifies `mastermind_bd` is running (localhost:5433)
   - **Rust Control Plane:** Optional check (warns if not available, doesn't block)
   - **Provider:** Checks for available Claude sessions (backend_sessions)

2. **Stack Detection:**
   - Reads `package.json` → Node.js detected
   - Reads `pyproject.toml` → Python detected
   - Reads `CLAUDE.md` → Custom instructions detected

3. **File Copy:**
   - **Commands:** `.claude/commands/mm/` (init, discover, complete-task, review, ship + handlers)
   - **Skills:** `.claude/skills/mm/` (brain-context, brain-persistence, discover, safe-commit, review, ship)
   - **Agents:** `.claude/agents/mm/` (7 brains + roadmap-planner + objective-packager + task-executor)

4. **Configuration:**
   - Creates `.mastermind/config.yaml` with detected stack + DB connection info

5. **Database Registration:**
   - Registers project in `projects` table (PostgreSQL)

**Output:**
- `STATUS: installed` — Success
- `STATUS: not-installed` -- Project empty (with --check)
- `ERROR: <reason>` — Failure (PostgreSQL down, permissions, etc.)

---

## Protocol (For Assistant)

When user executes `/mm:init [options]`:

### Step 1: Execute Python Handler

```bash
python3 .claude/commands/mm/init-handler.py [options]
```

Run from the project root (where `.claude/` exists).

### Step 2: Parse Handler Output

Capture stdout and look for:
- `STATUS: installed|not-installed` → Installation status
- `ERROR: ...` → Handler error, show to user
- `STACK: {...}` → Detected stack (JSON)
- `DB: connected|unavailable` → PostgreSQL status

### Step 3: Verify Installation

Check that files were created:
- `.mastermind/config.yaml` exists
- `.claude/commands/mm/init.md` exists
- `.claude/agents/mm/brain-01-product-strategy/` exists

### Step 4: Notify User

```
✅ MasterMind Framework installed successfully
📁 Config: .mastermind/config.yaml
🔧 Next: /mm:discover "your idea" to start planning
```

---

## Flags

| Flag | Description |
|------|-------------|
| `--target <path>` | Target directory (default: current directory) |
| `--check` | Check if already installed (doesn't modify files) |
| `--force` | Overwrite if already installed (without this, warns and exits) |

---

## Examples

### Install in Current Directory

```bash
/mm:init
# → Installs MasterMind in current project
# → Creates .mastermind/config.yaml
# → Registers in PostgreSQL
```

### Install in Specific Directory

```bash
/mm:init --target ~/projects/my-new-app
# → Installs in ~/projects/my-new-app
# → Detects stack from package.json/pyproject.toml
```

### Check Installation

```bash
/mm:init --check
# → STATUS: installed (already set up)
# → or STATUS: not-installed (empty project)
```

### Force Reinstall

```bash
/mm:init --target ~/projects/my-app --force
# → Overwrites existing .mastermind/ directory
# → Useful for upgrading framework version
```

---

## Architecture

```
/mm:init
    ↓
Python Handler (init-handler.py)
    ↓
Verifies PostgreSQL (mastermind_bd @ localhost:5433)
    ↓
Detects stack (package.json, pyproject.toml, CLAUDE.md)
    ↓
Copies framework files:
  - .claude/commands/mm/
  - .claude/skills/mm/
  - .claude/agents/mm/
    ↓
Creates .mastermind/config.yaml
    ↓
Registers in PostgreSQL (projects table)
    ↓
Done — ready for /mm:discover
```

---

## Files

- `.claude/commands/mm/init-handler.py` — Python handler (installation logic)
- `.claude/commands/mm/init.md` — This file (slash command interface)
- `.mastermind/config.yaml` — Generated config (stack + DB connection)
- `.claude/db_client.py` — PostgreSQL client module (shared by all handlers)

---

## Integration with MasterMind Workflow

**First-time setup:**

```
1. /mm:init --target /path/to/project
    ↓
2. Framework installed (.claude/, .mastermind/)
    ↓
3. /mm:discover "your idea"
    ↓
4. Roadmap/objective package generation available for the active flow
    ↓
5. /mm:activate-next-objective
    ↓
6. /mm:discover-contract-check --objective <slug>
    ↓
7. /mm:complete-task <TASK_ID> --brief
```

---

## Prerequisites

**Required:**
- **PostgreSQL:** `mastermind_bd` database must be running
  - Check: `docker compose ps` (look for mastermind-postgres-1)
  - Port: localhost:5433

**Optional (recommended):**
- **Rust Control Plane:** For advanced features
  - Check: `curl -s http://localhost:3001/health`
  - Warning if not available, doesn't block installation

---

## Stack Detection

MasterMind auto-detects your project stack:

| File | Stack Detected |
|------|----------------|
| `package.json` | Node.js (Next.js, React, Vue, etc.) |
| `pyproject.toml` | Python (FastAPI, Django, etc.) |
| `requirements.txt` | Python (legacy) |
| `CLAUDE.md` | Claude Code instructions |
| `go.mod` | Go |
| `Cargo.toml` | Rust |

This information is stored in `.mastermind/config.yaml` for brain consultation.

---

## Database Registration

Every `/mm:init` call registers the project in PostgreSQL:

```sql
INSERT INTO projects (
  name,
  path,
  stack,
  framework_version,
  installed_at
) VALUES (
  'project-name',
  '/path/to/project',
  '["nextjs", "python"]',
  'v3.0',
  NOW()
);
```

This enables:
- Cross-project learning (brains see what worked elsewhere)
- Usage analytics
- Multi-project management

---

## Troubleshooting

### "PostgreSQL connection failed"

**Problem:** `mastermind_bd` is not running.

**Solution:**
```bash
cd <mastermind-project-root>
docker compose up -d mastermind-postgres-1
```

### "Target already contains MasterMind"

**Problem:** `.mastermind/` directory exists.

**Solution:** Use `--force` flag to overwrite:
```bash
/mm:init --target /path/to/project --force
```

### "Permission denied"

**Problem:** Cannot write to target directory.

**Solution:** Check directory permissions:
```bash
ls -la /path/to/project
chmod u+w /path/to/project  # if needed
```

---

## See Also

- `/mm:discover` — Generate roadmap/objective packages
- `/mm:complete-task` — Execute tasks from the active objective package
- `/mm:review` — Code review with brains
- `/mm:archive-objective` — Archive a completed objective package
