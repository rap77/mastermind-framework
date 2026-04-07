# Brain #7 Systems-Level Evaluation — Phase 15 Plans

> **Evaluator:** Brain #7 (Growth/Data — Balfour, Kohavi, Munger)
> **Date:** 2026-04-06T12:15:00Z
> **Context:** 4 plans for Rust Control Plane implementation
> **Domain outputs:** N/A (direct plan evaluation, not domain agent synthesis)

---

## CROSS-DOMAIN REALITY

**Plans evaluated:**
- 15-01: PostgreSQL foundation + Rust project (4 tasks)
- 15-02: JWT auth + RBAC migration (5 tasks)
- 15-03: SQLite → PostgreSQL dual-write migration (5 tasks)
- 15-04: Immutable event sourcing (5 tasks)

**Points of agreement across plans:**
- All 4 plans use Strangler Fig Pattern (incremental migration)
- All preserve existing Python behavior (30min tokens, bcrypt, refresh rotation)
- All include rollback mechanisms (Plan 15-03 has explicit rollback scenarios)
- All maintain test coverage (620 tests passing requirement)

**Points of tension:**
- Plan 15-03 dual-write period duration: unspecified risk window
- Plan 15-04 event sourcing complexity: replay feature may be over-engineering
- Plan 15-02 RBAC complexity: 3 roles (admin, user, org_admin) vs current single-user system

**Shared assumptions (second-order risks hide here):**
- PostgreSQL performance will be adequate (no load testing specified)
- Rust learning curve won't block execution (Phase 13 showed 6.2x velocity, but that was prototype)
- Dual-write consistency is sufficient (no conflict resolution strategy)
- Event replay feature is needed (no usage data or user requirement)

---

## SECOND-ORDER CONCERNS

### 1. Planning Fallacy — Task Durations Look Optimistic

**Plan 15-01 (Task 2):** "Create PostgreSQL migration script with all 7 tables"
- **Risk:** SQLx compile-time verification requires correct PostgreSQL type matching. First-time Rust + SQLx integration will encounter type mismatches (UUID, TIMESTAMPTZ, JSONB).
- **Realistic duration:** 2-3 hours (not 1 hour as implied)
- **Second-order effect:** Delay cascades to Plan 15-02 (auth depends on users/sessions tables)

**Plan 15-02 (Task 4):** "Implement Axum middleware for JWT auth"
- **Risk:** Axum middleware pattern (State extractor, Layer, FromRequest parts) has learning curve. Extracting Claims from JWT + AuthenticatedRequest struct + error handling will take iterations.
- **Realistic duration:** 3-4 hours (not 2 hours as implied)
- **Second-order effect:** If middleware blocks, Plan 15-03 dual-write can't protect auth endpoints

**Plan 15-03 (Task 3):** "Implement dual-write coordinator"
- **Risk:** Arc<Mutex<Connection>> for SQLite in async Rust is an anti-pattern. rusqlite is sync-only, but mixing sync SQLite with async PostgreSQL creates runtime blocking issues.
- **Realistic duration:** 4-5 hours (not 2 hours as implied)
- **Second-order effect:** Blocking SQLite writes will starve PostgreSQL async pool, degrading overall performance

**Plan 15-04 (Task 2):** "Implement immutable event store"
- **Risk:** Mutation triggers (prevent UPDATE/DELETE) will break existing tests that expect to modify activity_log. Need to verify which tests write to activity_log and fix them.
- **Realistic duration:** 2-3 hours (not 1 hour as implied)
- **Second-order effect:** Test failures will block migration if not fixed before dual-write

### 2. Omission Bias — Missing Elements That Will Block Execution

**Missing from Plan 15-01:** PostgreSQL connection pool sizing
- **Gap:** PgPool::connect() uses default parameters. No max_connections, connection_timeout, or idle_timeout specified.
- **Risk:** Under heavy load, PostgreSQL will exhaust connections (default is often 10-20). Rust control plane will fail before Python agent runtime.
- **Fix:** Add PgPool::builder() with .max_connections(20) and .acquire_timeout(Duration::from_secs(5))

**Missing from Plan 15-02:** JWT secret management
- **Gap:** Hardcoded SECRET_KEY in Python (existing technical debt). Plan 15-02 doesn't specify how Rust loads JWT secret (ENV_VAR? Vault? Config file?).
- **Risk:** Production deployment will fail with hardcoded secret or missing env var.
- **Fix:** Add Task 6: "Configure JWT_SECRET from environment variable with validation error on startup"

**Missing from Plan 15-03:** Dual-write conflict resolution
- **Gap:** What happens when SQLite write succeeds but PostgreSQL write fails? Or vice versa? Plan 15-03 doesn't specify conflict handling.
- **Risk:** Data inconsistency during dual-write period. rollback plan mentions "investigate inconsistency" but doesn't specify how to detect or resolve.
- **Fix:** Add transactional dual-write with compensating transactions (Saga pattern)

**Missing from Plan 15-04:** Event replay authorization
- **Gap:** /audit/replay/:session_id endpoint requires auth (middleware), but who can replay which sessions? Can user A replay user B's session?
- **Risk:** IDOR vulnerability — any authenticated user can replay any session.
- **Fix:** Add authorization check: user can only replay their own sessions (user_id match in JWT claims vs session owner)

### 3. Systems Thinking — Feedback Loops Between Plans

**Feedback loop 1: Dual-write performance → Auth latency → User experience**
- **Plan 15-03** dual-write coordinator blocks on SQLite (sync) + PostgreSQL (async)
- **Plan 15-02** auth endpoints (login, refresh) write to sessions table via dual-write
- **Effect:** If SQLite blocks (even 100ms), login/refresh endpoints degrade
- **Measurement needed:** P95 latency for POST /api/auth/login and POST /api/auth/refresh during dual-write period
- **Threshold:** P95 < 500ms (current Python baseline is ~200ms)

**Feedback loop 2: Event sourcing → PostgreSQL storage → Query performance**
- **Plan 15-04** creates 1 event per brain operation (4 event types)
- **Plan 15-01** PostgreSQL has no partitioning strategy for activity_log
- **Effect:** activity_log grows unbounded. Temporal queries degrade as table size increases (BRIN index helps but doesn't fix scan size)
- **Measurement needed:** Query latency for time-range queries as activity_log grows (1K, 10K, 100K events)
- **Threshold:** P95 < 100ms for 1000 events (current spec), but what about 100K events?
- **Fix:** Add partitioning strategy (by month) in Plan 15-04 Task 3

**Feedback loop 3: RBAC complexity → Migration risk → Rollback likelihood**
- **Plan 15-02** adds 3 roles (admin, user, org_admin) + organization_id
- **Plan 15-03** dual-write migrates existing users (all have role='user' by default)
- **Effect:** No existing users have admin role. First admin creation requires direct PostgreSQL manipulation (no UI, no endpoint).
- **Risk:** Production deployment will have zero admin users. System unusable until someone manually INSERTs admin user.
- **Fix:** Add Task 6 to Plan 15-02: "Create seed admin user script for initial deployment"

### 4. Over-engineering Risk — What Won't Be Used

**Event replay feature (Plan 15-04 Task 4):**
- **Claim:** "Event replay is possible for debugging/analysis"
- **Reality:** No user requirement for replay. No dashboard UI planned. No API consumers identified.
- **Risk:** Building unused feature. Replay query (payload->>'session_id') is expensive without proper indexing.
- **Recommendation:** Defer replay to Phase 16 (Observability) when actual use case emerges

**RBAC 3-role system (Plan 15-02 Task 1):**
- **Claim:** "RBAC per organization (user.role field)"
- **Reality:** Current system is single-user (no organizations). org_admin role has no permissions defined.
- **Risk:** Building multi-tenant auth before multi-tenant requirements.
- **Recommendation:** Simplify to 2 roles (admin, user) for Phase 15. Add org_admin in Phase 17 (Multi-channel Gateway) when organizations are implemented

**BRIN indexes (Plan 15-04 Task 3):**
- **Claim:** "BRIN index for time-series data (< 100ms for 1000 events)"
- **Reality:** BRIN is optimal for tables > 1M rows. activity_log will have < 100K events in Phase 15.
- **Risk:** Premature optimization. B-tree index would be simpler and performant for current scale.
- **Recommendation:** Use B-tree index now. Add BRIN in Phase 16 when activity_log grows beyond 1M events

### 5. Acceptance Criteria Quality — Vague/Unmeasurable Criteria

**"Temporal queries work efficiently" (Plan 15-04):**
- **Problem:** "Efficiently" is subjective. Plan specifies "< 100ms for 1000 events" but doesn't specify:
  - What about 10K events? 100K events?
  - What about concurrent queries (10 simultaneous users)?
  - What about complex queries (brain_id + time range + event_type)?
- **Fix:** Specify SLI: "P95 latency for time-range queries < 100ms at 10K events, < 500ms at 100K events"

**"Zero data loss" (Plan 15-03):**
- **Problem:** "Zero data loss" is binary but not verifiable during migration. How do we know no data was lost?
- **Fix:** Specify verification: "Row count verification: COUNT(*) from SQLite = COUNT(*) from PostgreSQL for all 7 tables. Hash verification: MD5(column) for 100 random rows per table matches."

**"All 620 tests pass" (all plans):**
- **Problem:** Test count includes unit tests + integration tests. Which tests verify migration correctness?
- **Fix:** Add specific test requirement: "New migration tests added: test_dual_write_consistency(), test_rollback_to_sqlite(), test_postgresql_read_after_migration()"

---

## METRIC PROPOSALS — What Would Detect If This Is Going Wrong

### System-Level Metrics (Not Per-Plan Metrics)

**Metric 1: Dual-write latency degradation**
- **SLI:** P95 latency for writes during dual-write period
- **Threshold:** < 500ms for auth endpoints, < 1s for task creation
- **Why detects system risk:** If dual-write blocks, users will notice slow login/refresh before data inconsistency appears
- **Measurement:** Add tracing span for dual-write operations (SQLite write time + PostgreSQL write time)

**Metric 2: PostgreSQL connection pool exhaustion**
- **SLI:** PgPool active connections / max_connections ratio
- **Threshold:** < 80% sustained (alert if > 90% for > 5 minutes)
- **Why detects system risk:** Connection pool exhaustion is silent killer. Queries queue up, timeouts cascade, system appears "slow" but not "down"
- **Measurement:** sqlx::PgPool has .size() method to track active/idle connections

**Metric 3: Data consistency drift**
- **SLI:** Row count difference between SQLite and PostgreSQL
- **Threshold:** 0 difference (alert if any table has COUNT mismatch)
- **Why detects system risk:** Dual-write creates consistency risk. Early detection prevents compounding errors
- **Measurement:** Scheduled job every 5 minutes to run verify_consistency() endpoint

**Metric 4: Event sourcing append-only violation**
- **SLI:** Number of UPDATE/DELETE attempts on activity_log (should be 0)
- **Threshold:** 0 violations (alert if any mutation attempt occurs)
- **Why detects system risk:** Mutation attempts indicate someone is trying to modify events (either bug or unauthorized access)
- **Measurement:** PostgreSQL trigger logs RAISE EXCEPTION events

---

## CASCADE RISK ANALYSIS

### If Plan 15-03 Dual-Write Fails:

**Subsystem failure chain:**
1. Dual-write coordinator blocks (SQLite lock contention)
2. Auth endpoints (Plan 15-02) timeout (login/refresh depend on sessions table)
3. Users cannot authenticate (401 errors on protected routes)
4. Python agent runtime cannot create tasks (auth required)
5. System appears "down" even though Rust control plane is running

**Recovery:** Plan 15-03 rollback plan (switch reads back to SQLite) works, but requires restart of Rust control plane (downtime)

### If Plan 15-02 JWT Secret Leaks:

**Subsystem failure chain:**
1. JWT secret compromised (hardcoded in env var or logs)
2. Attacker generates forged tokens for any user
3. RBAC bypassed (attacker claims admin role)
4. Attacker accesses /audit endpoints (Plan 15-04) and reads all activity_log
5. Attacker replays sessions (IDOR vulnerability) and accesses sensitive data

**Recovery:** Rotate JWT secret immediately, invalidate all sessions (DELETE FROM sessions), force all users to re-login (downtime = user action required)

### If Plan 15-04 Event Sourcing Performance Degrades:

**Subsystem failure chain:**
1. activity_log grows to 100K+ events without partitioning
2. Temporal queries take > 1s (BRIN index insufficient)
3. /audit/brain/:id endpoint times out (Python coordinator uses this for brain history)
4. Dashboard (Phase 14 analytics) cannot load brain performance data
5. Operators cannot see which brains are failing (observability lost)

**Recovery:** Add partitioning (by month) to activity_log, rebuild indexes (downtime = maintenance window)

---

## VERDICT

### APPROVED_WITH_CONDITIONS

**Approval rationale:**
- Plans follow Strangler Fig Pattern correctly (incremental migration, rollback mechanisms)
- Phase 13 validated Rust velocity advantage (6.2x faster)
- PostgreSQL + JWT migration is necessary for v3.0 architecture
- Event sourcing provides valuable audit trail

**Conditions to fix before execution:**

1. **Add PostgreSQL connection pool sizing (Plan 15-01 Task 3)**
   - Use PgPool::builder() with .max_connections(20), .acquire_timeout(5s)
   - Add connection pool metrics (active/idle/count) to /health endpoint

2. **Simplify RBAC to 2 roles (Plan 15-02 Task 1)**
   - Remove org_admin role (no permissions defined, no multi-tenant requirements yet)
   - Add seed admin user creation script for initial deployment
   - Add JWT_SECRET environment variable validation on startup

3. **Add dual-write conflict resolution (Plan 15-03 Task 3)**
   - Implement Saga pattern with compensating transactions
   - Add dual-write latency SLI (P95 < 500ms) and alerting
   - Add consistency verification job (every 5 minutes)

4. **Defer event replay to Phase 16 (Plan 15-04 Task 4)**
   - Remove /audit/replay/:session_id endpoint from Phase 15
   - Keep /audit/activity and /audit/brain/:id endpoints (sufficient for current needs)
   - Add partitioning strategy (by month) for activity_log in Task 3 instead

5. **Clarify acceptance criteria (all plans)**
   - Specify SLI for temporal queries: P95 < 100ms at 10K events, < 500ms at 100K events
   - Add verification: Row count + hash verification for migration
   - Add specific migration tests: test_dual_write_consistency(), test_rollback_to_sqlite()

6. **Add IDOR fix to Plan 15-04 Task 4**
   - Add authorization check: user can only query activity_log for their own sessions
   - Add user_id filter to /audit/brain/:id endpoint (filter by organization_id if org_admin)

**Risk level:** Medium (conditions are blocking but straightforward to fix)

**Estimated delay to address conditions:** 2-3 hours to revise plans

**Second-order risk if conditions ignored:** Dual-write performance degradation will cause auth timeouts before data inconsistency appears. Users will notice "system is slow" before operators realize migration is failing.

---

## EVIDENCE CITATION

**Phase 13 validation:** STATE.md lines 88-92 show Rust velocity 6.2x faster than Python, supporting Rust migration decision.

**Strangler Fig Pattern:** BRAIN-FEED.md lines 115-117 document anti-pattern of Big Bang rewrite, supporting incremental migration approach.

**Existing technical debt:** STATE.md line 123-124 shows SECRET_KEY hardcoded in Python, justifying JWT_SECRET environment variable requirement.

**Multi-tenant requirements gap:** ROADMAP.md shows organizations table in Plan 15-02 but Phase 17 (Multi-channel Gateway) is when multi-tenant features are needed, supporting deferral of org_admin role.

---

*Evaluation complete. Ready for orchestrator decision on conditions.*
