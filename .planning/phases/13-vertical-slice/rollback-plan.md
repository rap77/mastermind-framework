# Rollback Plan — Phase 13 Vertical Slice

**Purpose:** Document escape hatch scenarios and rollback procedures (Brain #7 Condition)

## Escape Hatch Triggers

### Trigger 1: Rust Velocity < 0.5x Python

**Metrics to monitor:**
- Time to implement: Rust hours / Python hours (target: ≥ 0.5x)
- Test cycle time: Rust seconds / Python seconds (target: ≤ 2.0x)

**If triggered at midpoint (after Plan 13-03):**
```bash
# Delete Rust Control Plane
rm -rf apps/control-plane/

# Delete generated proto code
rm -rf apps/control-plane/src/proto/
rm -rf apps/api/mastermind_cli/proto/
rm -rf apps/web/src/proto/

# KEEP proto source (single source of truth)
# proto/mastermind/v1/brain_runtime.proto stays

# Revert docker-compose.yml (remove control-plane service)
git checkout HEAD~1 docker-compose.yml

# KEEP PostgreSQL service (Phase 14 may need it)
```

**Contract Rollback (if frontend already shipped):**
- **Option A:** Revert `apps/web/src/app/actions/tasks.ts` (restore FASTAPI_URL) — use if frontend still in dev
- **Option B:** Add Python compatibility layer at `/api/tasks/auto` (proxies to `/api/tasks`) — use if frontend in production

### Trigger 2: Boot Time > 120 seconds

**Symptoms:**
- `docker compose up -d` takes > 120s to reach all services healthy
- Degradation > 400% from baseline (2 services → 4 services)

**If triggered:**
1. Investigate service dependencies (check `depends_on` conditions)
2. Check PostgreSQL healthcheck interval (may need adjustment)
3. If unfixable → Follow Trigger 1 rollback procedure
4. Document root cause in `velocity-baseline.md`

### Trigger 3: grpclib Install Fails (> 2 days setup time)

**Symptoms:**
- `uv add grpclib` fails repeatedly
- Compilation errors in grpclib dependencies
- Total setup time > 2 days

**If triggered:**
1. Record in `velocity-baseline.md` as "setup overhead"
2. Continue with **mock gRPC** for validation:
   - Skip Python gRPC server implementation
   - Use Rust mock gRPC client for testing
   - Document in 13-03-SUMMARY.md
3. Full gRPC implementation deferred to Phase 15

### Trigger 4: PostgreSQL Migration Fails

**Symptoms:**
- PostgreSQL service fails to start
- Migration scripts fail to apply
- Connection errors from Rust or Python

**If triggered:**
```bash
# Drop PostgreSQL service from docker-compose.yml
docker compose down postgres
# Edit docker-compose.yml, remove postgres service + volumes

# Python continues on SQLite (no changes)
# Rust ExecutionRepo removed from plans (skip Task 3 of Plan 13-03)

# Document in 13-03-SUMMARY.md
```

## Performance Degradation Failure Mode (Brain #7 Blocker #4)

**Half-life failure is still failure:**
- If Boot Time > 120s OR degrades > 400% from baseline → **TRIGGER escape hatch**
- If Rust Velocity > 2.0x Python (not just < 0.5x) → **TRIGGER escape hatch**

**These triggers catch "slow failure" not just "fast failure"**

## Rollback Verification

After rollback, verify system still works:
```bash
# Python tests still pass
cd apps/api && uv run pytest tests/api/test_auto_task.py -x

# Frontend still works (if Option B rollback)
curl -X POST http://localhost:8001/api/tasks/auto \
  -H "Content-Type: application/json" \
  -d '{"brief":"test rollback"}'

# Docker compose starts without errors
docker compose up -d
docker compose ps  # All services healthy
```

## Decision Record

After rollback, document in STATE.md:
- Date and time of rollback
- Trigger that caused rollback
- Metrics that triggered escape hatch
- Alternative approach chosen (e.g., "Rust only for WebSocket Hub")

## Recovery Plan

If rollback occurs, Phase 13 is considered **complete with escape hatch activated**.
- Proceed to Phase 14 (Knowledge Distillation) — can run in parallel
- Phase 15 (Rust Control Plane) scope reduced based on rollback decision
- Update ROADMAP.md with reduced Rust scope
