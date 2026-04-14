# Phase 19 (MM-Flow Completion) — FASE 1 Plan Review Context
> Generated: 2026-04-14T12:00:00Z
> Iteration: 1
> Purpose: Full context for Brain #7 (Systems Thinker) plan validation

---

## [IMPLEMENTED REALITY]

### PostgreSQL — Verified running
```
Container: mastermind-postgres-1
DB: mastermind_bd
Existing tables (18):
  activity_log (partitioned), activity_log_2026_04, activity_log_2026_05
  api_keys, backend_capabilities, backend_sessions, brain_consultations
  context_checkpoints, cross_phase_contracts, executions, experience_records
  mm_flow_state, organizations, projects, sessions, tasks, users, workspaces
```

### Seed data — Verified
```sql
-- Organizations
slug = 'RAP-software'  ← used in agent_registry seed
slug = 'Prosell-CA'

-- Projects
slug = 'mastermind'    ← active project
slug = 'prosell-ecommerce'

-- Workspaces
mastermind workspace: current_phase = 19, branch = master, active_backend = claude
prosell workspace:    current_phase = 1,  branch = master, active_backend = z_ai
```

### CRITICAL DISCREPANCY — Plan says modules "exist", they DON'T
The plan's "Diagnóstico → ✅ Implementado y funciona" table references:
- `.mm-flow/multi_backend_manager.py`
- `.mm-flow/brain_router.py`
- `.mm-flow/state_machine.py`
- etc.

**Reality:** `.mm-flow/` directory doesn't exist. No Python modules there.

What DOES exist in Python:
- `apps/api/mastermind_cli/orchestrator/brain_router.py` — YES, exists
- `apps/api/mastermind_cli/api/app.py:212` — audit router wired with try/except fallback
- `apps/api/routers/audit.py` — 51.9K, 13 routes (0 JWT auth — FASE 4 concern)

**Impact on FASE 1:** NONE. FASE 1 is pure SQL + one Python file. No dependency on `.mm-flow/*.py`.
**Impact on FASE 2+:** The CLI module (`mm-flow execute-phase`) needs to be built from scratch.
This is documented in the plan ("placeholder, doesn't run") so it's expected.

### audit.sql — Exists, NOT yet applied
File: `docker/postgres/mm-flow-audit.sql` (446 lines)
Tables it creates (9):
  phase_executions, decisions, dev_sessions, verification_gates,
  artifacts, phase_metrics, audit_log, brain_feedback, niche_metrics_config

**NOTE:** `phase_executions` also referenced in plan as "already exists in database.py:416".
Checked: NOT yet in PostgreSQL. It's in the SQLITE schema (database.py) as a different table.
Applying audit.sql creates the PostgreSQL version — no conflict.

---

## [PLAN SUMMARIES — FASE 1 Tasks]

**Goal:** PostgreSQL audit infrastructure + agent registry + config loader ready.
**DoD (done when):** 5 verifiable outputs below pass.

### Task 1.1 — PostgreSQL levantado ✅ ALREADY DONE
```bash
docker compose up -d postgres  # already running
```
**Verified:** `docker exec mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "\dt"` → 18 tables.

---

### Task 1.2 — Apply mm-flow-audit.sql
```bash
docker exec -i mastermind-postgres-1 psql -U postgres -d mastermind_bd \
  < docker/postgres/mm-flow-audit.sql
```
**Verification:**
```sql
SELECT table_name FROM information_schema.tables
WHERE table_name IN ('phase_executions','decisions','audit_log','brain_feedback');
-- Expected: 4 rows
```

---

### Task 1.3 — Verify workspace seed (read-only check)
```bash
docker exec mastermind-postgres-1 psql -U postgres -d mastermind_bd \
  -c "SELECT w.current_phase, b.active_backend FROM workspaces w
      JOIN projects p ON w.project_id = p.id WHERE p.slug = 'mastermind';"
```
**Expected:** current_phase=19, active_backend=claude
**No writes needed** — workspace already exists.

---

### Task 1.4 — Create agent_registry table + seed 7 brains
New SQL migration: `docker/postgres/mm-flow-agent-registry.sql`

Key constraint: `UNIQUE(organization_id, project_id, brain_id)` — NOT just `(org, brain)`.
Without project_id in the UNIQUE, Brain #1 from two different projects share one row.

```sql
CREATE TABLE agent_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  project_id UUID NOT NULL REFERENCES projects(id),
  brain_id INTEGER NOT NULL,
  name VARCHAR NOT NULL,
  role VARCHAR NOT NULL,
  capabilities TEXT[],
  model_quality VARCHAR DEFAULT 'balanced',
  model_budget VARCHAR DEFAULT 'haiku',
  applies_in TEXT[],
  is_barrier BOOLEAN DEFAULT FALSE,
  token_budget_per_phase INTEGER DEFAULT 10000,
  tokens_consumed_total INTEGER DEFAULT 0,
  status VARCHAR DEFAULT 'available',
  last_heartbeat TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(organization_id, project_id, brain_id)
);
```

Seed: 7 brains for (RAP-software, mastermind), idempotent via `ON CONFLICT DO NOTHING`.

**Guardrail CI:**
```sql
SELECT COUNT(*) FROM agent_registry
WHERE project_id = (SELECT id FROM projects WHERE slug = 'mastermind');
-- Apply twice → result must still be 7, not 14
```

---

### Task 1.5 — config.yml + config_loader.py [BLOQUEANTE para FASE 2]

**Location:** `.planning/.mm-flow/config.yml` (user-editable brain routing config)
**Loader:** `apps/api/mastermind_cli/mm_flow/config_loader.py` (new module)

**Loader contract:**
- missing file → use defaults, log warning (NO crash)
- malformed YAML → raise `ConfigError` with descriptive message
- unknown model key → raise `ConfigError`

**3 required tests (pytest):**
1. `test_missing_file_uses_defaults` → assert "quality" in model_profiles
2. `test_malformed_yaml_raises_config_error` → pytest.raises(ConfigError, match="malformado")
3. `test_unknown_model_key_raises_config_error` → pytest.raises(ConfigError, match="clave desconocida")

---

## [CODE SNIPPETS]

### Existing: brain_router.py (apps/api/mastermind_cli/orchestrator/brain_router.py)
Referenced as dependency — exists, keyword-based routing. FASE 2 replaces with DynamicDispatchEngine.

### Existing: audit router wiring in app.py
```python
# Line ~212 in apps/api/mastermind_cli/api/app.py
try:
    from routers import audit as audit_router_module
    audit_router = audit_router_module.router
except ImportError:
    audit_router = None  # fallback
```
Impact: audit routes load but have no JWT auth (FASE 4 concern, not FASE 1).

### Proposed: config_loader.py structure
```python
# apps/api/mastermind_cli/mm_flow/config_loader.py
from dataclasses import dataclass
import yaml, logging

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    pass

VALID_MODEL_KEYS = {"quality", "balanced", "budget"}

_DEFAULTS = {
    "model_profiles": {
        "quality":  {"model": "claude-opus-4-6",   "use_when": "critical decisions"},
        "balanced": {"model": "claude-sonnet-4-6", "use_when": "standard brains"},
        "budget":   {"model": "claude-haiku-4-5",  "use_when": "context recovery"},
    },
    "brain_routing": {
        "DISCUSSION":     {"brains": [1,2,3], "parallel": True,  "barrier": [7]},
        "PLANNING":       {"brains": [4,5,6], "parallel": True,  "barrier": [7]},
        "EXECUTION_WAVE": {"brains": [7],     "parallel": False, "barrier": []},
        "VERIFICATION":   {"brains": [7],     "parallel": False, "barrier": [], "blocking": True},
    },
    "verification_gates": {"spec_coverage_threshold": 0.95, "max_gate_retries": 1},
}

def load_config(path: str = ".planning/.mm-flow/config.yml") -> "MMFlowConfig":
    try:
        with open(path) as f:
            raw = yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.warning(f"config.yml not found at {path} — using defaults")
        raw = {}
    except yaml.YAMLError as e:
        raise ConfigError(f"config.yml malformado en {path}: {e}") from e

    data = {**_DEFAULTS, **raw}
    for key in data["model_profiles"]:
        if key not in VALID_MODEL_KEYS:
            raise ConfigError(f"clave desconocida: '{key}'. Válidas: {VALID_MODEL_KEYS}")
    return _build_config(data)
```

---

## [CORRECTED ASSUMPTIONS]

Brain #7 might assume:

1. **"The `.mm-flow/` Python modules need to be wired into FASE 1"** — WRONG.
   FASE 1 is pure SQL + one loader file. No `.mm-flow/` CLI modules needed yet.

2. **"phase_executions already exists in PostgreSQL"** — WRONG.
   It exists in SQLite schema (`database.py:416`), NOT in PostgreSQL.
   audit.sql creates the PostgreSQL version.

3. **"This is a migration of existing Python code"** — WRONG.
   It's greenfield. The plan's "existing" column describes a future state, not current reality.

4. **"The 3 SQL operations are independent"** — PARTIALLY WRONG.
   Task 1.4 (agent_registry) depends on organizations + projects tables existing (they do).
   Task 1.5 (config_loader) depends on NO SQL — it's standalone Python.
   Tasks 1.2, 1.4, 1.5 can be sequenced but not fully parallelized (1.2 should run first
   to verify no FK conflicts with 1.4).

---

## [WHAT I NEED FROM BRAIN #7]

You are a Systems Thinker (Balfour, Kohavi, Munger). Evaluate through that lens.

1. **Planning Fallacy** — Where are we underestimating FASE 1?
   - The SQL tasks look simple, but are there FK ordering issues in audit.sql?
   - Is config_loader.py the right abstraction boundary or will FASE 2 immediately break it?

2. **Omission Bias** — What's missing that will BLOCK execution?
   - Does audit.sql assume any tables that don't exist yet?
   - Does agent_registry seed depend on slugs that might not match exactly?
   - Is there a test infrastructure gap (where do the 3 config_loader tests live, which test runner)?

3. **Systems Thinking** — What feedback loops?
   - FASE 1 Task 1.5 (config.yml defaults) hard-codes model names.
     If those model IDs change in the future, defaults become wrong silently.
     Should the defaults live in code or be read from somewhere validated?
   - agent_registry seed hard-codes `slug = 'RAP-software'` and `slug = 'mastermind'`.
     If a new org/project is added, the seed pattern doesn't scale.
     Is that a FASE 1 problem or future?

4. **Over-engineering risk** — What won't be used?
   - agent_registry has `token_budget_per_phase`, `tokens_consumed_total`, `last_heartbeat`.
     These fields require update logic (FASE 2+). FASE 1 just seeds them as zeros/nulls.
     Are they premature complexity or justified by FASE 2 dependency?

5. **Acceptance criteria quality** — Are the done criteria verifiable?
   - Task 1.2: SQL query returning 4 rows ✅ verifiable
   - Task 1.3: Read-only check ✅ verifiable
   - Task 1.4: COUNT(*) = 7 after 2 seeds ✅ verifiable
   - Task 1.5: 3 pytest tests passing ✅ verifiable
   - Is anything missing from DoD?

**Verdict expected:** APPROVED | APPROVED_WITH_CONDITIONS | REJECTED_REVISE
Be specific about which task and which concern.
