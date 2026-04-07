# Phase 15 — Plan Review Context
> Generated: 2026-04-06T12:00:00Z
> Iteration: 1
> Purpose: Full context for Brain #7 plan validation

---

## IMPLEMENTED REALITY

From BRAIN-FEED.md:
- **Stack:** Next.js 16, React 19, Python 3.14, uv (not pip), pnpm (not npm)
- **Architecture:** Brain Agent Architecture (v2.2) — 7 autonomous subagents
- **Delta-Velocity:** T1 baseline 210-270s, T1 > 300s = unprofitable
- **Active constraints:** No npm/pip, Brain #7 dispatched AFTER domain brains
- **Phase 13 validated:** Rust velocity 6.2x faster than Python (50 min vs 8 hours), Rust LOC 0.29x Python (616 vs 2,114 lines)

From STATE.md:
- **Current position:** Phase 14 complete, ready for Phase 15
- **PostgreSQL 16 + pgvector:** Already validated in Phase 13
- **Rust prototype:** 616 LOC, 10 tests, 3 gRPC services working
- **Escape hatch:** NOT triggered — full Rust implementation approved

---

## PLAN SUMMARIES

### Plan 15-01: PostgreSQL foundation + Rust project (4 tasks)
**Goal:** Establish PostgreSQL 16 + pgvector foundation and Rust control plane project structure

**Key components:**
- Create Rust control plane with SQLx, Axum, Tokio
- PostgreSQL 16 + pgvector migration script (7 tables: users, sessions, api_keys, tasks, executions, experience_records, activity_log)
- Connection pool pattern established
- Health check endpoint

**Technical decisions:**
- SQLx compile-time query verification (not sqlx-cli migrations)
- JSONB for JSON columns (faster queries)
- TIMESTAMPTZ for timestamps (timezone-aware)
- gen_random_uuid() for UUID generation
- Foreign key constraints (SQLite doesn't enforce)

---

### Plan 15-02: JWT auth + RBAC migration (5 tasks)
**Goal:** Migrate JWT authentication + RBAC from Python (jose) to Rust (Axum middleware)

**Key components:**
- JWT token generation/validation (jsonwebtoken crate)
- Refresh token rotation (CVE-2025-29927 mitigation)
- Axum middleware for route protection
- RBAC per organization (user.role field: admin, user, org_admin)
- Auth endpoints (login, refresh, logout)

**Preserving Python behavior:**
- 30min access token, 24h refresh token
- Refresh token rotation on every refresh
- bcrypt for password hashing
- Session management with rotation_count

**Technical decisions:**
- jsonwebtoken crate (not jose-jwt)
- bcrypt crate for password hashing
- Claims struct with sub, username, role, organization_id, exp, iat
- AuthenticatedRequest extractor for middleware

---

### Plan 15-03: SQLite → PostgreSQL migration (5 tasks)
**Goal:** Migrate all SQLite data to PostgreSQL via dual-write strategy (zero downtime)

**Key components:**
- Dual-write coordinator (write to both SQLite and PostgreSQL)
- Read from PostgreSQL after migration
- Data consistency checks (row count verification)
- Rollback plan documented and tested

**Strangler Fig Pattern:**
- Incremental migration, NOT Big Bang rewrite
- Dual-write allows rollback if PostgreSQL has issues
- Zero downtime — system remains operational during migration

**Technical decisions:**
- rusqlite for SQLite access from Rust
- DualWriteRepository with Arc<Mutex<Connection>> for SQLite
- Verification endpoint for data consistency
- Rollback scenarios documented (data inconsistency, performance degradation, critical bug)

---

### Plan 15-04: Immutable event sourcing (5 tasks)
**Goal:** Implement immutable event sourcing for activity_log with temporal query support

**Key components:**
- BrainEvent model (brain_started, brain_completed, brain_routed, brain_failed)
- Append-only event store with UPDATE/DELETE triggers (prevents mutation)
- BRIN indexes for temporal queries (< 100ms for 1000 events)
- Audit API endpoints (GET /audit/activity, /audit/brain/:id, /audit/replay/:session_id)
- Python coordinator integration via gRPC

**PostgreSQL features:**
- JSONB for payload storage (fast queries)
- BRIN indexes for time-series data (created_at)
- Partial indexes for common query patterns
- Triggers for enforcing immutability

**Event types:**
- brain_started: session_id, brief, flow_config
- brain_completed: session_id, duration_ms, result
- brain_routed: session_id, from_brain, to_brain, reason
- brain_failed: session_id, error, stage

---

## CODE SNIPPETS

### Phase 13 validated metrics
- Rust velocity vs Python: **0.10x** (6.2x faster, 50 min vs 8 hours)
- Rust LOC vs Python: **0.29x** (616 vs 2,114 lines)
- Rust test cycle: **0.23x** (0.89s vs 3.85s)
- Escape hatch: NOT triggered

### Existing Python JWT (Phase 3)
- python-jose[cryptography]
- 30min access token, 24h refresh token
- Refresh token rotation on every refresh
- bcrypt for password hashing

### PostgreSQL validation (Phase 13)
- Port 5433 (host), 5432 (container)
- asyncpg already added to pyproject.toml
- Connection pattern established in Rust (PgPool)

---

## WHAT I NEED FROM BRAIN #7

Evaluate these 4 plans using your Systems Thinker lens (Balfour, Kohati, Munger):

### 1. Planning Fallacy
What are we underestimating?
- Task durations look optimistic?
- Integration complexity between Rust + Python?
- Migration edge cases?

### 2. Omission Bias
What's missing that will block execution?
- Error handling patterns?
- Monitoring/observability during migration?
- Testing coverage gaps?

### 3. Systems Thinking
Feedback loops between plans?
- Plan 15-03 (dual-write) affects Plan 15-02 (auth)?
- Plan 15-04 (event sourcing) depends on Plan 15-01 (PostgreSQL)?
- Rollback plans coordinated across all 4 plans?

### 4. Over-engineering risk
What won't be used?
- RBAC too complex for current needs?
- Event replay feature necessary?
- Dual-write period too long?

### 5. Acceptance criteria quality
Are done criteria verifiable?
- "All 620 tests pass" — measurable ✅
- "Zero data loss" — verifiable ✅
- "Temporal queries work efficiently" — what's the threshold? ⚠️

**Be specific about WHICH plan and WHICH task.**

---

## VERDICT

**Response format:**

```markdown
## Brain #7 Evaluation

### Planning Fallacy
[Identify underestimations by plan/task]

### Omission Bias
[Identify missing elements by plan/task]

### Systems Thinking
[Identify feedback loops by plan/task]

### Over-engineering Risk
[Identify unnecessary complexity by plan/task]

### Acceptance Criteria Quality
[Identify vague/missing criteria by plan/task]

### Verdict
APPROVED | APPROVED_WITH_CONDITIONS | REJECTED_REVISE

[If CONDITIONS/REJECTED, specify what to fix before execution]
```
