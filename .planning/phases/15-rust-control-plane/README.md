# Phase 15: Rust Control Plane

**Goal:** State management, auth, and event sourcing migrated to Rust with PostgreSQL

**Plans:** 4 plans in 4 waves

- **15-01**: PostgreSQL 16 + pgvector foundation + Rust project structure
- **15-02**: JWT auth + RBAC migrated from Python to Rust (Axum middleware)
- **15-03**: SQLite → PostgreSQL migration via dual-write strategy
- **15-04**: Immutable event sourcing for activity_log with temporal queries

**Dependencies:**
- Phase 13 (Vertical Slice validation) — COMPLETE
- PostgreSQL 16 + pgvector validated
- Rust velocity 6.2x faster than Python

**Requirements Addressed:**
- RCP-01: SQLite migrates to PostgreSQL 16 + pgvector via dual-write
- RCP-02: JWT auth + RBAC migrated to Rust with refresh token rotation
- RCP-03: Immutable activity_log via event sourcing for audit trail

**Success Criteria:**
1. All SQLite data migrated to PostgreSQL (zero data loss)
2. JWT auth fully functional in Rust (30min access + 24h refresh)
3. Event sourcing operational (immutable log, temporal queries)
4. All 620 existing tests pass (zero regressions)

**Tech Stack:**
- Rust: Axum 0.7 + Tokio 1.x + sqlx (PostgreSQL)
- Python: FastAPI + asyncpg (dual-write coordinator)
- Database: PostgreSQL 16 + pgvector (migrate from SQLite)
- Auth: JWT with refresh rotation (preserve existing behavior)

**Key Constraints:**
- Strangler Fig Pattern — incremental migration, NOT Big Bang rewrite
- Zero downtime — dual-write during migration
- All existing 1048 tests must pass (631 backend + 407 frontend + 10 new)
- Preserve existing JWT behavior (30min access + 24h refresh rotation)

**Execution Order:**
1. Wave 1 (15-01): PostgreSQL foundation + Rust project structure
2. Wave 2 (15-02): JWT auth + RBAC (depends on 15-01)
3. Wave 3 (15-03): SQLite migration + dual-write (depends on 15-01)
4. Wave 4 (15-04): Event sourcing (depends on 15-01, 15-02, 15-03)

**Estimated Duration:** 8-12 hours (4 waves, ~2-3 hours each)

**Rollback Plan:**
- Each plan has independent rollback (documented in 15-03-ROLLBACK_PLAN.md)
- Dual-write allows instant rollback to SQLite if issues found
- JWT auth rollback: switch Python routes back to jose implementation
- Event sourcing rollback: disable event emission, keep activity_log read-only
