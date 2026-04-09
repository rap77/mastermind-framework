# Rollback Plan: Dual-Write Migration

## Overview

This document outlines rollback procedures for the SQLite → PostgreSQL dual-write migration implemented in Phase 15 Plan 15-03.

## Scenarios

### Scenario 1: Data Inconsistency Detected

**Trigger:** Row counts differ between SQLite and PostgreSQL

**Actions:**
1. Stop dual-write (set `DUAL_WRITE_ENABLED=false` in env)
2. Switch reads back to SQLite (set `READ_SOURCE=sqlite`)
3. Investigate inconsistency using logs
4. Fix root cause
5. Re-enable dual-write

**Commands:**
```bash
# Switch back to SQLite
export READ_SOURCE=sqlite
export DUAL_WRITE_ENABLED=false
systemctl restart rust-control-plane
```

**Verification:**
```bash
# Verify SQLite is primary
curl http://localhost:8080/health | jq .database
# Expected: "sqlite" or "postgresql" depending on implementation
```

### Scenario 2: PostgreSQL Performance Degradation

**Trigger:** Query latency > 500ms (P95)

**Actions:**
1. Check PostgreSQL slow query log
2. Add missing indexes
3. If no improvement, switch reads back to SQLite
4. Keep dual-write enabled (still migrating data)

**Commands:**
```bash
# Check slow queries
docker compose exec postgres psql -U postgres -d mastermind_bd -c \
  "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Switch reads back
export READ_SOURCE=sqlite
```

**Performance Baseline:**
- P50 latency: < 100ms
- P95 latency: < 500ms
- P99 latency: < 1000ms

### Scenario 3: Complete Rollback Required

**Trigger:** Critical bug in PostgreSQL layer

**Actions:**
1. Stop dual-write
2. Switch all operations back to SQLite
3. Drop PostgreSQL tables (keep database)
4. Fix bug
5. Restart migration from Task 1

**Commands:**
```bash
# Complete rollback
export DUAL_WRITE_ENABLED=false
export READ_SOURCE=sqlite

# Drop PostgreSQL tables (keep database)
docker compose exec postgres psql -U postgres -d mastermind_bd -c \
  "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Re-run migrations
cd rust_control_plane
psql -h localhost -p 5433 -U postgres -d mastermind_bd -f migrations/001_initial_postgresql.sql
psql -h localhost -p 5433 -U postgres -d mastermind_bd -f migrations/002_activity_log_event_sourcing.sql
psql -h localhost -p 5433 -U postgres -d mastermind_bd -f migrations/003_add_rbac.sql
```

## Verification Steps

After rollback:

1. **All 620 tests pass**
   ```bash
   cd apps/api
   uv run pytest tests/ -v
   # Expected: 620 passed, 0 failed
   ```

2. **SQLite is primary read/write source**
   ```bash
   # Verify SQLite operations work
   sqlite3 mastermind.db "SELECT COUNT(*) FROM tasks;"
   ```

3. **PostgreSQL is stopped or tables dropped**
   ```bash
   docker compose exec postgres psql -U postgres -d mastermind_bd -c "\dt"
   # Expected: No tables found (if dropped)
   ```

4. **Zero data loss**
   ```bash
   # Verify row counts
   sqlite3 mastermind.db "SELECT 'tasks', COUNT(*) FROM tasks UNION ALL SELECT 'executions', COUNT(*) FROM executions;"
   ```

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Data inconsistency | Low | High | Dual-write verification every 5 minutes |
| Performance degradation | Medium | Medium | P95 latency monitoring, read source switching |
| Critical bug in PostgreSQL | Low | High | Complete rollback procedure documented |
| Lost commits during rollback | Low | High | Git history preserves all commits |

## Success Criteria

Rollback is successful when:
- [ ] All 620 Python tests pass
- [ ] SQLite is primary read/write source
- [ ] Zero data loss (row counts verified)
- [ ] PostgreSQL is stopped or tables dropped
- [ ] No errors in application logs

## Post-Rollback Actions

1. Document root cause of failure
2. Update this rollback plan with lessons learned
3. Re-test migration with fixes applied
4. Schedule retry migration window

## Related Documentation

- Plan 15-03: SQLite → PostgreSQL dual-write migration
- Migration script: `rust_control_plane/src/db/migration.rs`
- Dual-write coordinator: `rust_control_plane/src/db/dual_write.rs`
- Python integration: `apps/api/mastermind_cli/state/database.py`

---

**Phase:** 15 (Rust Control Plane)
**Plan:** 15-03 (SQLite to PostgreSQL Dual-Write)
**Created:** 2026-04-07
**Status:** Ready for execution
