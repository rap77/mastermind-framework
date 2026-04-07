# Phase 15 Planning Summary

**Date:** 2026-04-06
**Planner:** GSD Planner (autonomous mode)
**Phase:** 15 - Rust Control Plane
**Plans Created:** 4 plans in 4 waves

## Overview

Phase 15 migrates state management, authentication, and event sourcing from Python (SQLite + jose) to Rust (PostgreSQL + Axum middleware). This follows the Strangler Fig Pattern validated in Phase 13, where Rust velocity was 6.2x faster than Python.

## Plans Created

### Plan 15-01: PostgreSQL Foundation + Rust Project Structure (Wave 1)

**Objective:** Establish PostgreSQL 16 + pgvector and Rust control plane project

**Key Tasks:**
1. Create Rust control plane project structure (Cargo.toml, src/main.rs)
2. Create PostgreSQL migration script with all 7 schemas
3. Implement database connection pool in Rust (PgPool)
4. Integrate PostgreSQL with Axum health check endpoint

**Requirements:** RCP-01 (PostgreSQL migration)

**Dependencies:** None (Wave 1)

**Key Deliverables:**
- PostgreSQL 16 + pgvector running in Docker Compose
- Rust project scaffolded with SQLx for compile-time verification
- All 7 tables created (users, sessions, api_keys, tasks, executions, experience_records, activity_log)
- Health check endpoint returning {"status": "healthy"}

### Plan 15-02: JWT Auth + RBAC Migration (Wave 2)

**Objective:** Migrate JWT authentication from Python (jose) to Rust (Axum middleware)

**Key Tasks:**
1. Add RBAC schema migration (role + organization_id columns)
2. Implement JWT token generation and validation (jsonwebtoken crate)
3. Implement refresh token rotation (CVE-2025-29927 mitigation)
4. Implement Axum middleware for JWT auth
5. Implement auth endpoints (login, refresh, logout)

**Requirements:** RCP-02 (JWT auth + RBAC)

**Dependencies:** 15-01 (PostgreSQL foundation)

**Key Deliverables:**
- JWT auth fully functional in Rust
- 30min access token, 24h refresh token (matches Python)
- Refresh token rotation (old sessions deleted)
- Axum middleware validates JWT on protected routes
- RBAC per organization enforced (user.role field)

### Plan 15-03: SQLite → PostgreSQL Migration via Dual-Write (Wave 3)

**Objective:** Migrate all SQLite data to PostgreSQL with zero downtime

**Key Tasks:**
1. Inspect SQLite database and create migration script
2. Implement SQLite → PostgreSQL data migration
3. Implement dual-write coordinator (SQLite + PostgreSQL)
4. Update Python database layer to use dual-write
5. Run migration verification and document rollback plan

**Requirements:** RCP-01 (PostgreSQL migration)

**Dependencies:** 15-01 (PostgreSQL foundation)

**Key Deliverables:**
- All 7 tables migrated from SQLite to PostgreSQL
- Dual-write operational (writes to both, reads from PostgreSQL)
- Zero data loss (row counts verified)
- All 620 Python tests pass (zero regressions)
- Rollback plan documented and tested

### Plan 15-04: Immutable Event Sourcing (Wave 4)

**Objective:** Implement immutable event sourcing for activity_log with temporal queries

**Key Tasks:**
1. Implement event sourcing core module (BrainEvent model)
2. Implement immutable event store with append-only semantics
3. Add optimized indexes for temporal queries (BRIN indexes)
4. Implement audit log API endpoints
5. Integrate event emission into Python coordinator

**Requirements:** RCP-03 (Event sourcing)

**Dependencies:** 15-01, 15-02, 15-03 (PostgreSQL + Auth + Migration)

**Key Deliverables:**
- Every brain operation creates event in activity_log
- Events immutable (UPDATE/DELETE blocked by triggers)
- Temporal queries performant (< 100ms for 1000 events)
- Event replay functional for debugging/analysis
- Audit trail spans all services (Rust + Python)

## Wave Structure

| Wave | Plans | Dependencies | Autonomous |
|------|-------|--------------|------------|
| 1 | 15-01 | None | Yes |
| 2 | 15-02 | 15-01 | Yes |
| 3 | 15-03 | 15-01 | Yes |
| 4 | 15-04 | 15-01, 15-02, 15-03 | Yes |

**Parallelization:** 15-02 and 15-03 can run in parallel (both depend only on 15-01)

## Requirements Coverage

| Requirement | Plan | Status |
|-------------|------|--------|
| RCP-01 | 15-01, 15-03 | Addressed |
| RCP-02 | 15-02 | Addressed |
| RCP-03 | 15-04 | Addressed |

**Coverage:** 3/3 requirements mapped ✓

## Success Criteria

1. ✅ PostgreSQL 16 + pgvector running with all 7 tables
2. ✅ JWT auth fully functional in Rust (30min access + 24h refresh)
3. ✅ All SQLite data migrated to PostgreSQL (zero data loss)
4. ✅ Dual-write operational (zero regressions)
5. ✅ Event sourcing operational (immutable log, temporal queries)
6. ✅ All 620 existing tests pass

## Estimated Duration

- **Plan 15-01:** ~2 hours (PostgreSQL setup + Rust project)
- **Plan 15-02:** ~3 hours (JWT auth + RBAC + middleware)
- **Plan 15-03:** ~3 hours (Migration + dual-write + verification)
- **Plan 15-04:** ~2 hours (Event sourcing + audit API)

**Total:** ~10 hours (4 waves, can parallelize 15-02 + 15-03)

## Risk Mitigation

1. **Data Loss Risk:** Dual-write strategy allows instant rollback to SQLite
2. **Auth Regression:** Preserve Python jose implementation until Rust fully validated
3. **Performance Degradation:** BRIN indexes for time-series data, query performance monitoring
4. **Test Failures:** Each plan includes verification steps, rollback if > 0 failures

## Rollback Strategy

Each plan has independent rollback:
- **15-01:** Stop PostgreSQL, continue with SQLite
- **15-02:** Switch Python routes back to jose implementation
- **15-03:** Dual-write allows instant rollback (set READ_SOURCE=sqlite)
- **15-04:** Disable event emission, keep activity_log read-only

## Next Steps

Execute: `/mm:execute-phase 15`

**Recommended execution order:**
1. Run 15-01 (PostgreSQL foundation) — must complete first
2. Run 15-02 and 15-03 in parallel (both depend only on 15-01)
3. Run 15-04 after 15-02 and 15-03 complete

**Clear context first:** `/clear` before executing to start with fresh context window

---

**Planning Complete:** 2026-04-06
**Plans Ready:** 4/4
**All Requirements Mapped:** Yes ✓
**Wave Structure:** Optimized for parallel execution ✓
