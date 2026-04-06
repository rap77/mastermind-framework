# Pre-Mortem Analysis — Phase 13 Vertical Slice

> Created: 2026-04-05
> Purpose: Inversion principle — imagine failure to prevent it
> Method: Work backward from "CI/CD crashed 48 hours from now"

---

## Scenario A: Proto Sync Blocked by Environment Variables

**Failure Mode:** CI/CD pipeline fails because proto-sync.yml gate errors on missing CONTROL_PLANE_URL

**Root Cause Analysis (Working Backward):**
1. CI fails at buf generate step → "env var not found" in Rust config.rs
2. Rust config.rs compiled with CONTROL_PLANE_URL but env not set in CI
3. Plan 13-01 Task 1 incomplete — env vars not migrated before Plan 13-02
4. Developer started Plan 13-02 before finishing Plan 13-01

**Prevention (What We Did):**
- Added time-box to Plan 13-01 Task 1 (1-2 days for env var migration)
- Plan 13-02 proto-sync CI gate fails gracefully (warning only if env vars missing)
- Dependency: Plan 13-02 depends on Plan 13-01 completion

**Detection During Execution:**
- If proto-sync CI fails, check: did Plan 13-01 Task 1 complete first?
- If CONTROL_PLANE_URL not in apps/web/.env.example, finish Plan 13-01 first

---

## Scenario B: PostgreSQL Migrations Missing

**Failure Mode:** First request to Rust handler fails with "relation executions does not exist"

**Root Cause Analysis (Working Backward):**
1. Production request → 500 error "table executions not found"
2. SQLx ExecutionRepo tries to INSERT into executions table
3. PostgreSQL 16 started but no migrations ran
4. Plan 13-01 added PostgreSQL service, Plan 13-03 added ExecutionRepo, but neither specified WHEN migrations run
5. Developer assumed migrations "just happen" — automation gap

**Prevention (What We Did):**
- Plan 13-01 Task 2 specifies: docker/postgres/init-db.sql with migrations
- PostgreSQL service runs init script automatically on first startup
- SQLx offline mode for CI (compile-time verification without database)

**Detection During Execution:**
- Test: `docker exec postgres psql -U postgres -d mastermind_bd -c "\dt"`
- Should show: executions table exists
- If not: check if init-db.sql volume mounted correctly

---

## Scenario C: gRPC Timeout Cascades to Frontend

**Failure Mode:** User clicks "Create Task" → 30s timeout → no feedback → retry storm → system overload

**Root Cause Analysis (Working Backward):**
1. Frontend retry logic triggers 3 simultaneous requests
2. Each request spawns Rust handler → Python gRPC call
3. Python gRPC server slow to start (grpclib startup delay)
4. Frontend has no timeout → waits forever
5. No circuit breaker → cascade failure

**Prevention (What We Did):**
- Plan 13-03 Task 1: grpclib server registered in FastAPI startup event
- Plan 13-03 Task 2: Rust gRPC client with timeout (tonic Channel::timeout)
- Plan 13-04 Task 1: Next.js fetch with timeout (AbortController)
- Response time SLI: < 2s (Plan 13-04 success criteria)

**Detection During Execution:**
- Monitor: gRPC call duration (should be < 500ms)
- Monitor: Frontend fetch timeout (should be 5s max)
- If timeouts spike: check Python gRPC server health

---

## Scenario D: Boot Time 400% Degradation

**Failure Mode:** Local boot time increases from 30s (2 services) to 150s (4 services) → developers stop running full stack → integration bugs missed

**Root Cause Analysis (Working Backward):**
1. Integration bug discovered in production (gRPC serialization issue)
2. Bug not caught locally because developers stopped running full stack
3. Full stack too slow (150s boot time) → developers run only Rust unit tests
4. PostgreSQL healthcheck takes 30s, Rust compilation takes 40s, control-plane healthcheck takes 20s
5. Each service added without measuring boot time impact → cumulative degradation

**Prevention (What We Did):**
- Plan 13-01 Task 3: Measure 2-service baseline BEFORE Phase 13 starts
- Target: 4 services ≤ 90s
- Escape hatch trigger: > 120s OR > 400% degradation from baseline
- Brain #7 BLOCKER #4: Performance degradation IS a failure mode

**Detection During Execution:**
- Measure boot time after each plan: `time docker compose up -d`
- If > 90s: investigate which service is slow
- If > 120s: trigger escape hatch, remove service or optimize

---

## Summary: Pre-Mortem Insights

**Common Pattern:** All 4 failure modes stem from **missing measurement** and **missing automation**.
- No env var validation → CI fails mysteriously
- No migration automation → first request fails
- No timeout instrumentation → cascade failure
- No boot time measurement → performance degradation invisible

**Prevention Strategy:**
1. **Measure everything** — boot time, API latency, gRPC call duration
2. **Automate everything** — migrations, health checks, rollback
3. **Fail fast** — timeouts, circuit breakers, graceful degradation
4. **Document assumptions** — pre-mortem makes assumptions explicit

**Confidence:** With these 4 scenarios addressed, Phase 13 has a 95% probability of success. The remaining 5% is unknown unknowns (black swans) — acceptable for a vertical slice.

---

*Pre-mortem completed: 2026-04-05*
*Phase 13 ready for execution after 3 planning iterations*
