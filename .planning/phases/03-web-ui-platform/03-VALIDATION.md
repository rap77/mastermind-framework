---
phase: 3
slug: web-ui-platform
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-13
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0+ with pytest-asyncio |
| **Config file** | `pyproject.toml` (tool.pytest section) |
| **Quick run command** | `pytest tests/api/test_websocket.py -x -v` |
| **Full suite command** | `pytest tests/ -v --cov=mastermind_cli --cov-report=term-missing` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/api/ -x -v` (run API tests only)
- **After every plan wave:** Run `pytest tests/ -v --cov` (full suite with coverage)
- **Before `/gsd:verify-work`:** Full suite must be green + E2E tests passing + performance benchmarks meet requirements
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | UI-01 | smoke | `pytest tests/api/test_app.py::test_app_creates -x` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | UI-02 | integration | `pytest tests/api/test_auth.py::test_login_success -x` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | UI-03 | integration | `pytest tests/api/test_auth.py::test_refresh_token_rotation -x` | ❌ W0 | ⬜ pending |
| 03-01-04 | 01 | 1 | UI-07 | integration | `pytest tests/api/test_audit.py::test_audit_log_created -x` | ❌ W0 | ⬜ pending |
| 03-01-05 | 01 | 1 | UI-08 | integration | `pytest tests/api/test_sessions.py::test_concurrent_requests_isolated -x` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | UI-06 | integration | `pytest tests/api/test_executions.py::test_export_json -x` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 2 | UI-10 | e2e | `playwright test tests/e2e/execution.spec.ts --project=Desktop` | ❌ W0 | ⬜ pending |
| 03-02-03 | 02 | 2 | ARCH-03 | unit | `pytest tests/unit/test_orchestrator.py::test_coordinator_isolation -x` | ✅ P2 | ⬜ pending |
| 03-02-04 | 02 | 2 | PERF-02 | performance | `pytest tests/perf/test_db_queries.py::test_query_latency -x --benchmark-only` | ❌ W0 | ⬜ pending |
| 03-03-01 | 03 | 3 | UI-04 | integration | `pytest tests/api/test_websocket.py::test_websocket_connects -x` | ❌ W0 | ⬜ pending |
| 03-03-02 | 03 | 3 | PAR-08 | integration | `pytest tests/api/test_websocket.py::test_progress_updates -x` | ❌ W0 | ⬜ pending |
| 03-03-03 | 03 | 3 | PERF-03 | performance | `pytest tests/perf/test_websocket.py::test_broadcast_latency -x --benchmark-only` | ❌ W0 | ⬜ pending |
| 03-04-01 | 04 | 4 | UI-05 | e2e | `playwright test tests/e2e/mobile.spec.ts --project=Mobile` | ❌ W0 | ⬜ pending |
| 03-04-02 | 04 | 4 | UI-09 | e2e | `playwright test tests/e2e/graph.spec.ts --project=Desktop` | ❌ W0 | ⬜ pending |
| 03-04-03 | 04 | 4 | PERF-04 | e2e | `playwright test tests/e2e/perf.spec.ts --project=Desktop` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/api/test_app.py` — FastAPI app creation, route mounting (stubs for UI-01)
- [ ] `tests/api/test_auth.py` — Login, refresh token rotation, password hashing (stubs for UI-02, UI-03)
- [ ] `tests/api/test_websocket.py` — WebSocket connection, broadcast, reconnection (stubs for UI-04, PAR-08)
- [ ] `tests/api/test_executions.py` — CRUD operations, export endpoints (stubs for UI-06)
- [ ] `tests/api/test_audit.py` — Audit log creation, querying (stubs for UI-07)
- [ ] `tests/api/test_sessions.py` — Multi-user isolation, concurrent requests (stubs for UI-08)
- [ ] `tests/perf/test_db_queries.py` — Query latency benchmarks (stubs for PERF-02, requires pytest-benchmark)
- [ ] `tests/perf/test_websocket.py` — Broadcast latency benchmarks (stubs for PERF-03)
- [ ] `tests/e2e/mobile.spec.ts` — Mobile responsiveness tests (stubs for UI-05)
- [ ] `tests/e2e/graph.spec.ts` — React Flow rendering tests (stubs for UI-09)
- [ ] `tests/e2e/execution.spec.ts` — End-to-end execution flow (stubs for UI-10)
- [ ] `tests/e2e/perf.spec.ts` — Page load performance tests (stubs for PERF-04)
- [ ] `playwright.config.ts` — Playwright configuration for E2E tests
- [ ] `uv add --dev pytest-asyncio httpx-ws pytest-benchmark playwright` — Framework install

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

All phase behaviors have automated verification through pytest and Playwright E2E tests.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (14 test files to create)
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
