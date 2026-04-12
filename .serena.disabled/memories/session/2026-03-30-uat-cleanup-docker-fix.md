# Session: UAT Cleanup + Docker Port Fix

**Date:** 2026-03-30
**Branch:** feat/v2.2-brain-agents
**Context:** 84% — paused mid Phase 03 UAT

## Work Done

### UAT Files Corrected
- Phase 01: 4/5 → 5/5 (mitigated gap → pass)
- Phase 02: 4/5 → 5/5 (mitigated gap → pass, duplicate Gaps section removed)
- Phase 04: status testing → complete, result format normalized (**PASSED** → pass), Test 3 → skip
- Phase 11 VALIDATION.md: nyquist_compliant: false → true, all 12 tasks pending → green, wave_0_complete: true

### Phase 03 UAT Resumed (3/12 → 9/12)
| Test | Result |
|------|--------|
| 4. Refresh token rotation | pass |
| 5. Task creation | pass (POST /api/tasks, field: brief only required) |
| 6. Session isolation | skip (no /api/auth/register, single-user) |
| 7. WebSocket | pass (HTTP 101) |
| 8. DAG graph | pass (empty arrays, not 404) |
| 9. Dashboard HTML | pass |
| 12. Audit log | pass (audit_log table, 14 rows) |

### Docker Port Fix
- **Bug:** API_URL=http://api:8000 but port mapping was 8001:8000 (host:container). Internal Docker calls worked but marketing cluster wasn't loading — root cause TBD (may have been a different issue)
- **Fix:** Unified to 8001 everywhere: Dockerfile EXPOSE+CMD, docker-compose ports+healthcheck+API_URL
- **Commit:** `fix(docker): use port 8001 consistently`

## Pending (Phase 03 UAT)
- Test 10: Export from dashboard (manual UI)
- Test 11: Responsive design 375px (manual UI)
- CSS issue: marketing cluster looks "different" — purple/glow vs cyan/scan — may be Tailwind dynamic class purge

## Key Findings
- `/api/tasks` requires only `brief` field (flow is string|null, not object)
- API_URL in Docker web container: now http://api:8001
- audit_log table columns: id, user_id, endpoint, method, request_hash, response_status, timestamp
- MM_DB_PATH=/app/data/mastermind.db (NOT /app/mastermind.db)
- Ports: API=8001, Web=3001

## Next Session
/clear → resume Phase 03 UAT (Tests 10+11 + CSS issue) → close UAT → /gsd:plan-phase 12
