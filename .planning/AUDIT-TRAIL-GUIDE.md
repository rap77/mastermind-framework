# MM-Flow Audit Trail & Governance System

**Status:** Designed and implemented (ready for Phase A integration)
**Created:** 2026-04-12
**Components:** PostgreSQL schema, FastAPI routes, Engram sync service, state machine integration

---

## Overview

The audit trail system provides **complete development history tracking** for MasterMind Framework and future projects. It captures and persists:

- **Phase Executions** — every run of a phase with metrics
- **Decisions** — all technical/product/process decisions with rationale and confidence
- **Verification Gates** — quality checks (tests, security, performance) with results
- **Development Sessions** — session logs with tasks, commits, discoveries
- **Artifacts** — plans, specs, tests, docs with git links
- **Phase Metrics** — niche-specific KPIs (software, SaaS, hardware)
- **Audit Log** — immutable compliance trail
- **Brain Feedback** — synced insights from Engram memory

**Key Design Principles:**
- Multi-tenant: org_id + project_id isolation at DB level
- Extensible: niche-specific metrics defined in config
- Integrated: Engram ↔ PostgreSQL sync for cross-session wisdom
- Auditable: immutable audit log for compliance
- Queryable: REST API + SQL views for analysis

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Development Execution (Phase X)              │
├─────────────────────────────────────────────────────────┤
│  Brain #1 → Decision           state_machine.py → DB   │
│  Brain #7 → Verification Gate  phase_executions table  │
│  Tests    → Artifact           artifacts table         │
│  Engram   → mem_save()         (sync at end)           │
└──────────────┬──────────────────────────────────────────┘
               │
               ├──→ PostgreSQL Audit Trail
               │    ├─ phase_executions (execution metadata)
               │    ├─ decisions (decision history)
               │    ├─ verification_gates (quality results)
               │    ├─ dev_sessions (session logs)
               │    ├─ artifacts (generated files)
               │    ├─ phase_metrics (KPIs)
               │    ├─ audit_log (compliance)
               │    └─ brain_feedback (synced insights)
               │
               └──→ FastAPI Audit Routes (/api/audit/*)
                    ├─ /timeline (full history)
                    ├─ /phase/{N}/details (phase deep dive)
                    ├─ /decisions (decision queries)
                    ├─ /metrics (KPI analysis)
                    ├─ /audit-log (compliance)
                    └─ /brain-feedback (brain insights)
```

---

## Database Schema

### Phase Executions Table

**Purpose:** Track each phase run with complete execution metadata

```sql
CREATE TABLE phase_executions (
    id                  UUID,               -- Execution ID
    org_id              UUID,               -- Organization (RLS)
    project_id          UUID,               -- Project (RLS)
    workspace_id        UUID,               -- Active workspace
    phase_number        INT,                -- Phase 1-N
    execution_number    INT,                -- 1st run, 2nd retry, etc
    status              VARCHAR(50),        -- pending|in_progress|completed|failed
    started_at          TIMESTAMP,          -- When phase started
    completed_at        TIMESTAMP,          -- When phase finished
    duration_seconds    INT,                -- Total duration
    backend_used        VARCHAR(50),        -- 'claude', 'openrouter', 'z_ai'
    tokens_consumed     INT,                -- Total tokens
    tokens_input        INT,                -- Input tokens
    tokens_output       INT,                -- Output tokens
    output_summary      TEXT,               -- Brief summary
    error_message       TEXT,               -- If failed
    git_commit_hash     VARCHAR(40),        -- Commit at completion
    triggered_by        VARCHAR(255),       -- User, scheduler, brain_7
);
```

**Example Query:**

```sql
-- Timeline of all phases in project
SELECT
    phase_number,
    status,
    duration_seconds,
    tokens_consumed,
    backend_used,
    completed_at
FROM phase_executions
WHERE org_id = $1 AND project_id = $2
ORDER BY phase_number, execution_number DESC;
```

### Decisions Table

**Purpose:** Capture all decisions with rationale, alternatives, confidence

```sql
CREATE TABLE decisions (
    id                  UUID,               -- Decision ID
    org_id              UUID,               -- Organization (RLS)
    project_id          UUID,               -- Project (RLS)
    phase_execution_id  UUID,               -- Link to phase
    decision_type       VARCHAR(100),       -- architectural|technical|product|process
    title               VARCHAR(255),       -- "Zustand > Redux"
    rationale           TEXT,               -- Why this decision?
    alternatives        TEXT,               -- Other options considered
    chosen_option       TEXT,               -- What we selected
    confidence          FLOAT,              -- 0.0 to 1.0
    impact_level        VARCHAR(50),        -- critical|high|medium|low
    made_by             VARCHAR(255),       -- User or Brain #N
    approved_by         VARCHAR(255),       -- Who approved?
    status              VARCHAR(50),        -- pending|approved|rejected|superseded
    tags                TEXT[],             -- For filtering
    engram_link         VARCHAR(255),       -- Reference to Engram observation
);
```

**Example Query:**

```sql
-- All pending approvals in Phase 18
SELECT
    title,
    made_by,
    confidence,
    impact_level
FROM decisions
WHERE org_id = $1
  AND project_id = $2
  AND phase_execution_id = $3
  AND status = 'pending'
ORDER BY confidence DESC;
```

### Verification Gates Table

**Purpose:** Track Brain #7 quality gates and automated checks

```sql
CREATE TABLE verification_gates (
    id                  UUID,               -- Gate ID
    org_id              UUID,               -- Organization (RLS)
    project_id          UUID,               -- Project (RLS)
    phase_execution_id  UUID,               -- Link to phase
    gate_type           VARCHAR(100),       -- test_coverage|security|performance|spec
    gate_name           VARCHAR(255),       -- "Unit test coverage >= 80%"
    status              VARCHAR(50),        -- pending|running|passed|failed|waived
    result              JSONB,              -- Gate-specific results
    score               FLOAT,              -- 0.0 to 1.0
    evaluated_by        VARCHAR(255),       -- Brain #7 or automated
    evaluation_notes    TEXT,               -- Why pass/fail?
    retry_count         INT,                -- How many retries?
    waived_by           VARCHAR(255),       -- Who waived?
    completed_at        TIMESTAMP,          -- When evaluated
);
```

**Example Result JSONB:**

```json
{
  "test_coverage": { "actual": 85, "required": 80, "status": "PASS" },
  "security_scan": { "vulnerabilities": 0, "critical": 0, "high": 0 },
  "performance": { "p95_latency_ms": 150, "max_latency_ms": 500 }
}
```

### Dev Sessions Table

**Purpose:** Log development sessions with task completion and discoveries

```sql
CREATE TABLE dev_sessions (
    id                  UUID,               -- Session ID
    org_id              UUID,               -- Organization (RLS)
    project_id          UUID,               -- Project (RLS)
    phase_number        INT,                -- Which phase
    started_at          TIMESTAMP,          -- Session start
    ended_at            TIMESTAMP,          -- Session end
    duration_minutes    INT,                -- Total time
    status              VARCHAR(50),        -- active|paused|completed|abandoned
    tasks_completed     INT,                -- Tasks done
    tasks_total         INT,                -- Total tasks
    commits_count       INT,                -- How many commits
    commit_hashes       TEXT[],             -- Git commit SHAs
    discoveries         TEXT,               -- Key findings
    blockers            TEXT,               -- Issues hit
    next_steps          TEXT,               -- What's next
);
```

### Artifacts Table

**Purpose:** Track generated plans, specs, tests, docs with git links

```sql
CREATE TABLE artifacts (
    id                  UUID,               -- Artifact ID
    org_id              UUID,               -- Organization (RLS)
    project_id          UUID,               -- Project (RLS)
    phase_execution_id  UUID,               -- Link to phase
    artifact_type       VARCHAR(100),       -- plan|spec|test|doc|report|design
    name                VARCHAR(255),       -- "Phase-18-Backend-Plan.md"
    description         TEXT,               -- What is this?
    file_path           VARCHAR(512),       -- ".planning/phases/18-*/PLAN.md"
    file_hash           VARCHAR(64),        -- SHA-256 for integrity
    git_commit_hash     VARCHAR(40),        -- Commit where created
    created_by          VARCHAR(255),       -- User or Brain #N
    related_decision_id UUID,               -- Link to decision (optional)
);
```

### Phase Metrics Table

**Purpose:** Track niche-specific KPIs per phase

```sql
CREATE TABLE phase_metrics (
    id                  UUID,               -- Metric ID
    org_id              UUID,               -- Organization (RLS)
    project_id          UUID,               -- Project (RLS)
    phase_execution_id  UUID,               -- Link to phase
    niche               VARCHAR(100),       -- 'software'|'saas'|'hardware'
    metric_name         VARCHAR(255),       -- 'test_coverage'
    metric_value        FLOAT,              -- 85.5
    metric_unit         VARCHAR(50),        -- '%', 'ms', 'days'
    target_value        FLOAT,              -- 80
    status              VARCHAR(50),        -- 'pass'|'warn'|'fail'
    measured_at         TIMESTAMP,          -- When measured
);
```

### Audit Log Table (Immutable)

**Purpose:** Compliance and governance audit trail

```sql
CREATE TABLE audit_log (
    id                  UUID,               -- Log entry ID
    org_id              UUID,               -- Organization (RLS)
    project_id          UUID,               -- Project (RLS)
    action_type         VARCHAR(100),       -- phase_started|decision_made|gate_passed
    actor                VARCHAR(255),       -- User name or 'Brain #7'
    actor_type          VARCHAR(50),        -- 'user'|'brain'|'system'
    description         TEXT,               -- What happened?
    phase_number        INT,                -- Which phase
    related_entity_type VARCHAR(100),       -- 'phase_execution'|'decision'|'gate'
    related_entity_id   UUID,               -- FK to entity
    severity            VARCHAR(50),        -- 'info'|'warning'|'error'|'critical'
    created_at          TIMESTAMP,          -- When logged (immutable)
);
```

### Brain Feedback Table

**Purpose:** Sync target for brain insights from Engram

```sql
CREATE TABLE brain_feedback (
    id                  UUID,               -- Feedback ID
    org_id              UUID,               -- Organization (RLS)
    project_id          UUID,               -- Project (RLS)
    phase_execution_id  UUID,               -- Link to phase
    brain_id            INT,                -- 1-7, 8-23, etc
    feedback_type       VARCHAR(100),       -- insight|risk_flag|opportunity|lesson_learned
    title               VARCHAR(255),       -- "Discovered useContext edge case"
    content             TEXT,               -- Full feedback
    confidence          FLOAT,              -- Brain's confidence
    impact_on_phase     VARCHAR(100),       -- 'critical'|'high'|'medium'|'low'
    engram_sync_id      VARCHAR(255),       -- Link to Engram observation
    engram_synced_at    TIMESTAMP,          -- When synced
);
```

---

## REST API Routes

### Timeline API

**GET /api/audit/projects/{project_id}/timeline**

Returns full development timeline (all phases, decisions, gates, artifacts).

```bash
# Get timeline for project
curl "http://localhost:8001/api/audit/projects/abc123/timeline?limit=100"

# Response
[
  {
    "event_type": "phase_started",
    "event_at": "2026-04-12T09:00:00Z",
    "description": "Phase 18 execution started",
    "phase_number": 18
  },
  {
    "event_type": "decision_made",
    "event_at": "2026-04-12T10:15:00Z",
    "description": "Decision: Async messaging strategy",
    "phase_number": 18
  },
  {
    "event_type": "gate_evaluated",
    "event_at": "2026-04-12T11:30:00Z",
    "description": "brain_7_approval gate: passed",
    "phase_number": 18
  },
  {
    "event_type": "phase_completed",
    "event_at": "2026-04-12T14:00:00Z",
    "description": "Phase 18 completed (45K tokens, commit abc123)",
    "phase_number": 18
  }
]
```

### Phase Details API

**GET /api/audit/projects/{project_id}/phase/{phase_num}/details**

Deep dive into phase with decisions, gates, artifacts, metrics.

```bash
curl "http://localhost:8001/api/audit/projects/abc123/phase/18/details"

# Response
{
  "phase_execution": {
    "id": "exec-123",
    "phase_number": 18,
    "status": "completed",
    "started_at": "2026-04-12T09:00:00Z",
    "completed_at": "2026-04-12T14:00:00Z",
    "duration_seconds": 18000,
    "backend_used": "claude",
    "tokens_consumed": 45000,
    "output_summary": "Phase 18 Wave 3 complete..."
  },
  "decisions": [
    {
      "title": "Async messaging strategy",
      "decision_type": "technical",
      "confidence": 0.85,
      "rationale": "Improves scalability...",
      "chosen_option": "Use message queue (RabbitMQ)",
      "alternatives": "Kafka, AWS SQS",
      "impact_level": "high",
      "made_by": "Brain #1",
      "status": "approved"
    }
  ],
  "verification_gates": [
    {
      "gate_type": "brain_7_approval",
      "gate_name": "Phase 18 output validation",
      "status": "passed",
      "score": 0.92,
      "evaluation_notes": "Architecture solid, risk flags resolved"
    },
    {
      "gate_type": "test_coverage",
      "status": "passed",
      "result": { "actual": 85, "required": 80 }
    }
  ],
  "artifacts": [
    {
      "artifact_type": "plan",
      "name": "Phase 18 Backend Plan",
      "file_path": ".planning/phases/18-multi-channel/PLAN.md",
      "git_commit_hash": "abc123...",
      "created_by": "Brain #4"
    }
  ],
  "metrics": [
    {
      "metric_name": "test_coverage",
      "metric_value": 85.5,
      "metric_unit": "%",
      "target_value": 80,
      "status": "pass"
    }
  ]
}
```

### Decision Recording API

**POST /api/audit/projects/{project_id}/phase/{phase_num}/decision**

Record a new decision.

```bash
curl -X POST "http://localhost:8001/api/audit/projects/abc123/phase/18/decision" \
  -H "Content-Type: application/json" \
  -d '{
    "decision_type": "technical",
    "title": "Async messaging strategy",
    "rationale": "Improves scalability and decouples services",
    "chosen_option": "RabbitMQ message queue",
    "alternatives": "Kafka, AWS SQS, Apache Pulsar",
    "confidence": 0.85,
    "impact_level": "high",
    "tags": ["architecture", "scalability", "messaging"]
  }'
```

### Decision Listing API

**GET /api/audit/projects/{project_id}/decisions**

Query decisions with filters.

```bash
# All pending decisions
curl "http://localhost:8001/api/audit/projects/abc123/decisions?status=pending"

# High-impact decisions
curl "http://localhost:8001/api/audit/projects/abc123/decisions?impact_level=high"

# Low-confidence decisions
curl "http://localhost:8001/api/audit/projects/abc123/decisions?confidence_min=0.0&confidence_max=0.6"
```

### Verification Gates API

**GET /api/audit/projects/{project_id}/phase/{phase_num}/gates**

Get all quality gates for a phase.

```bash
curl "http://localhost:8001/api/audit/projects/abc123/phase/18/gates"

# Response
[
  {
    "id": "gate-123",
    "gate_type": "test_coverage",
    "gate_name": "Unit test coverage >= 80%",
    "status": "passed",
    "score": 0.855,
    "result": { "actual": 85.5, "required": 80 }
  },
  {
    "gate_type": "security_scan",
    "status": "passed",
    "result": { "vulnerabilities": 0, "critical": 0 }
  },
  {
    "gate_type": "brain_7_approval",
    "status": "passed",
    "evaluated_by": "Brain #7",
    "score": 0.92
  }
]
```

### Sessions API

**GET /api/audit/projects/{project_id}/sessions**

List development sessions.

```bash
curl "http://localhost:8001/api/audit/projects/abc123/sessions?phase_number=18"

# Response
[
  {
    "id": "session-1",
    "phase_number": 18,
    "session_date": "2026-04-12T09:00:00Z",
    "duration_minutes": 180,
    "status": "completed",
    "tasks_completed": 8,
    "tasks_total": 10,
    "commits_count": 3,
    "discoveries": "Discovered WebSocket bottleneck under load...",
    "blockers": "Async timeout handling edge case",
    "next_steps": "Implement circuit breaker, add load testing"
  }
]
```

### Metrics API

**GET /api/audit/projects/{project_id}/metrics**

Query niche-specific KPIs.

```bash
# All software metrics for Phase 18
curl "http://localhost:8001/api/audit/projects/abc123/metrics?niche=software&phase_number=18"

# Response
[
  {
    "metric_name": "test_coverage",
    "metric_value": 85.5,
    "metric_unit": "%",
    "target_value": 80,
    "status": "pass"
  },
  {
    "metric_name": "cyclomatic_complexity",
    "metric_value": 8.2,
    "metric_unit": "score",
    "target_value": 10,
    "status": "pass"
  },
  {
    "metric_name": "security_vulnerabilities",
    "metric_value": 0,
    "metric_unit": "count",
    "target_value": 0,
    "status": "pass"
  }
]
```

### Artifacts API

**GET /api/audit/projects/{project_id}/artifacts**

List generated files (plans, specs, tests, docs).

```bash
curl "http://localhost:8001/api/audit/projects/abc123/artifacts?artifact_type=plan&phase_number=18"
```

### Audit Log API

**GET /api/audit/projects/{project_id}/audit-log**

Compliance audit trail (immutable).

```bash
curl "http://localhost:8001/api/audit/projects/abc123/audit-log?action_type=phase_completed&limit=50"

# Response
[
  {
    "action_type": "phase_started",
    "actor": "user:rafael",
    "actor_type": "user",
    "description": "Phase 18 execution started",
    "phase_number": 18,
    "severity": "info",
    "created_at": "2026-04-12T09:00:00Z"
  },
  {
    "action_type": "decision_made",
    "actor": "Brain #1",
    "actor_type": "brain",
    "description": "Decision: Async messaging strategy",
    "phase_number": 18,
    "severity": "info"
  },
  {
    "action_type": "phase_completed",
    "actor": "system",
    "actor_type": "system",
    "description": "Phase 18 completed",
    "phase_number": 18,
    "severity": "info",
    "created_at": "2026-04-12T14:00:00Z"
  }
]
```

### Project Summary API

**GET /api/audit/projects/{project_id}/summary**

Executive overview of project health.

```bash
curl "http://localhost:8001/api/audit/projects/abc123/summary"

# Response
{
  "total_phases": 18,
  "phases_completed": 15,
  "phases_in_progress": 1,
  "average_phase_duration_hours": 5.2,
  "decision_approval_rate": 0.94,
  "average_decision_confidence": 0.82,
  "gate_pass_rate": 0.96,
  "total_artifacts": 42,
  "total_sessions": 23,
  "total_session_hours": 115,
  "latest_discoveries": [
    "WebSocket bottleneck under load (Phase 18)",
    "useContext edge case in nested components (Phase 17)"
  ],
  "current_blockers": [
    "Async timeout handling (in progress)",
    "Cross-region sync optimization (blocked by Phase 19)"
  ]
}
```

---

## Engram ↔ PostgreSQL Sync

### How It Works

1. **During Phase Execution:** Brain agents make decisions, saved to Engram via `mem_save()`
2. **Phase Completion:** Orchestrator calls `engram_sync.sync_decisions_to_db()`
3. **Sync Process:**
   - Query Engram for decisions (type=decision, type=bugfix)
   - Parse metadata (title, rationale, alternatives, confidence)
   - Find phase_execution_id by timestamp + phase_number
   - Upsert into decisions table with engram_link reference
   - Mark as synced in Engram
4. **Result:** Decisions available in PostgreSQL + cross-session linkage to Engram

### Example: Sync Phase 18 Decisions

```python
# At end of Phase 18 execution
from apps.api.services.engram_sync import EngramSyncService

sync_service = EngramSyncService()
results = await sync_service.sync_decisions_to_db(
    org_id=uuid.UUID("..."),
    project_id=uuid.UUID("..."),
    phase_number=18
)

print(f"Synced {results['synced_count']} decisions")
print(f"Failed: {results['failed_count']}")
print(f"Skipped (already synced): {results['skipped_count']}")
for decision in results['new_decisions']:
    print(f"  - {decision['title']} (engram_id={decision['engram_id']})")
```

### Configuration

In `.planning/.mm-flow/config.py`:

```python
ENGRAM_SYNC_ENABLED = True                  # Enable/disable syncing
ENGRAM_SYNC_BATCH_SIZE = 100                # Max items per sync
ENGRAM_SYNC_ON_PHASE_COMPLETION = True      # Auto-sync at phase end
```

---

## Integration with State Machine

The state machine calls `record_phase_execution()` to persist history:

```python
# In orchestrator or phase completion handler
from .planning/.mm-flow.state_machine import StateMachine

state_machine = StateMachine(
    org_id="...", project_id="...", workspace_id="...", db_url="..."
)

# Record phase completion
phase_exec_id = state_machine.record_phase_execution(
    phase_number=18,
    status="completed",
    backend_used="claude",
    tokens_consumed=45000,
    tokens_input=32000,
    tokens_output=13000,
    output_summary="Phase 18 Wave 3 complete: messaging architecture finalized",
    git_commit_hash="abc123def456...",
    triggered_by="user:rafael"
)

# phase_exec_id can now be used to link decisions/gates/artifacts
```

---

## Niche Metrics Configuration

Define metrics per niche in `.planning/.mm-flow/config.py`:

```python
NICHE_METRICS = {
    "software": {
        "metrics": [
            {"name": "test_coverage", "unit": "%", "target": 80, "weight": 0.3},
            {"name": "code_review_time", "unit": "hours", "target": 24, "weight": 0.2},
            # ...
        ]
    },
    "saas": {
        "metrics": [
            {"name": "deployment_success_rate", "unit": "%", "target": 99, "weight": 0.3},
            {"name": "uptime", "unit": "%", "target": 99.9, "weight": 0.4},
            # ...
        ]
    },
    "hardware": {
        "metrics": [
            {"name": "manufacturing_yield", "unit": "%", "target": 95, "weight": 0.4},
            # ...
        ]
    },
}
```

---

## Common Queries

### Find all pending decisions

```sql
SELECT * FROM decisions
WHERE org_id = $1 AND project_id = $2 AND status = 'pending'
ORDER BY created_at DESC;
```

### Phase execution timeline

```sql
SELECT
    phase_number,
    status,
    started_at,
    completed_at,
    duration_seconds,
    tokens_consumed,
    backend_used
FROM phase_executions
WHERE org_id = $1 AND project_id = $2
ORDER BY phase_number DESC, execution_number DESC;
```

### Failed verification gates

```sql
SELECT
    phase_execution_id,
    gate_type,
    gate_name,
    status,
    retry_count,
    evaluation_notes
FROM verification_gates
WHERE org_id = $1 AND project_id = $2 AND status = 'failed'
ORDER BY completed_at DESC;
```

### Decision confidence analysis

```sql
SELECT
    decision_type,
    COUNT(*) as total,
    AVG(confidence) as avg_confidence,
    MIN(confidence) as min_confidence,
    MAX(confidence) as max_confidence
FROM decisions
WHERE org_id = $1 AND project_id = $2 AND status = 'approved'
GROUP BY decision_type;
```

### Audit log for compliance

```sql
SELECT
    created_at,
    action_type,
    actor,
    actor_type,
    description,
    severity
FROM audit_log
WHERE org_id = $1 AND project_id = $2
  AND created_at >= $3  -- start date
  AND created_at <= $4  -- end date
ORDER BY created_at DESC;
```

---

## Files Created/Updated

### New Files

1. **docker/postgres/mm-flow-audit.sql** — Extended audit trail schema
   - 8 audit tables (phase_executions, decisions, dev_sessions, verification_gates, artifacts, phase_metrics, audit_log, brain_feedback)
   - 1 config table (niche_metrics_config)
   - 2 views (phase_execution_timeline, session_summary)
   - RLS policies for org isolation

2. **apps/api/routers/audit.py** — REST API routes
   - 11 endpoints for timeline, decisions, gates, metrics, sessions, artifacts, audit log, brain feedback
   - Pydantic models for request/response validation
   - OpenAPI documentation

3. **apps/api/services/engram_sync.py** — Engram ↔ PostgreSQL sync service
   - EngramSyncService: query Engram, parse, upsert to DB
   - PhaseExecutionRecorder: record phase execution to audit trail
   - Helper functions for decision/feedback parsing and linkage

4. **.planning/AUDIT-TRAIL-GUIDE.md** — This documentation

### Updated Files

1. **.planning/.mm-flow/state_machine.py** — Added `record_phase_execution()` method
   - Persists phase execution metadata to phase_executions table
   - Auto-creates audit_log entries
   - Returns phase_execution_id for linking decisions/gates

2. **.planning/.mm-flow/config.py** — Added niche metrics config
   - NICHE_METRICS: extensible per-niche KPIs
   - ENGRAM_SYNC_*: sync configuration
   - Gate retry settings

3. **.planning/MM-FLOW-ARCHITECTURE.md** — Added Pillar 4: Audit Trail & Governance
   - Schema overview
   - API endpoint documentation
   - Engram sync integration
   - Example execution flow
   - Compliance features

---

## Next Steps (Phase A Integration)

1. **Database Setup:**
   - Run `docker/postgres/mm-flow-audit.sql` to create audit tables
   - Verify RLS policies work with org_id isolation

2. **API Integration:**
   - Include `apps/api/routers/audit.py` in FastAPI app startup
   - Register routes: `app.include_router(audit.router)`

3. **Engram Sync Configuration:**
   - Configure Engram client API keys in environment
   - Set ENGRAM_SYNC_ENABLED = True in config.py
   - Test sync with sample decisions

4. **State Machine Integration:**
   - Call `state_machine.record_phase_execution()` after phase completion
   - Pass execution metadata (backend, tokens, commit hash, summary)
   - Verify phase_execution_id is returned and usable

5. **Testing:**
   - Unit test: Engram sync parsing and DB upsert
   - Integration test: phase execution → decision sync → timeline query
   - RLS test: verify org isolation (Project A cannot see Project B data)

---

## Architecture Decisions

### Why PostgreSQL for Audit Trail?

- **Immutable audit_log:** Append-only for compliance
- **RLS isolation:** org_id prevents cross-org data leakage
- **Fast queries:** Indexed for timeline/metrics analysis
- **Integrates with state machine:** Same DB as phase_executions
- **Extensible:** Add new tables without code changes

### Why Engram Sync Instead of Direct Writes?

- **Separation of concerns:** Brains save to Engram (mem_save), orchestrator syncs to DB
- **Async-friendly:** Can batch sync at phase end without blocking execution
- **Cross-session wisdom:** Engram is long-term memory, DB is short-term
- **Flexible:** Can toggle sync on/off without code changes

### Why Niche-Specific Metrics?

- **Software != SaaS != Hardware:** Different KPIs matter
- **Extensible:** New niches added via config, not code
- **Weighted:** Metrics have importance weights for scoring
- **Comparison:** Can compare phases across niches (if needed)

### Why Immutable Audit Log?

- **Compliance:** Cannot tamper with audit trail
- **Root cause analysis:** Full history of what happened, when, by whom
- **Traceability:** Link actions to decisions/gates/phases
- **Legal:** Defensible in audits/disputes

---

## Troubleshooting

### Engram Sync Failures

**Problem:** "Failed to sync decision X: decision not found in phase_execution"

**Solution:** Ensure phase_execution_id is set before syncing. Check timestamps align.

**Problem:** "Already synced (skipped_count=42)"

**Solution:** Decisions already have engram_link set. This is normal on re-runs.

### RLS Permission Denied

**Problem:** "ERROR: new row violates row-level security policy"

**Solution:** Verify `mm_flow.org_id` session variable is set before queries.

```python
with conn.cursor() as cur:
    cur.execute("SET LOCAL mm_flow.org_id = %s", (str(org_id),))
    # Now queries respect RLS
```

### API 404 on Audit Routes

**Problem:** Audit routes return 404

**Solution:** Verify router is included in main.py:

```python
from apps.api.routers import audit
app.include_router(audit.router)
```

---

## Performance Tips

- **Index queries:** phase_executions indexed on (org_id, project_id, phase_number)
- **Pagination:** Use limit/offset for large result sets (audit log)
- **Batch sync:** Engram sync in batches (ENGRAM_SYNC_BATCH_SIZE)
- **Archive old data:** Consider partitioning audit_log by date for large projects

---

**Last updated:** 2026-04-12
**Status:** Ready for Phase A implementation
