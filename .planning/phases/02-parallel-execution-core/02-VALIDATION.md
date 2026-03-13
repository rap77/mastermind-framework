---
phase: 02
slug: parallel-execution-core
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-13
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2+ + pytest-asyncio 0.24.0+ |
| **Config file** | pyproject.toml (existing) |
| **Quick run command** | `pytest tests/unit/ -x -q` |
| **Full suite command** | `pytest tests/ -v --cov=mastermind_cli --cov-report=term-missing` |
| **Estimated runtime** | ~45 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/unit/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v --cov=mastermind_cli`
- **Before `/gsd:verify-work`:** Full suite must be green + coverage >80% on new code
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | PAR-01 | unit | `pytest tests/unit/test_dependency_resolver.py::test_cycle_detection -x` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | PAR-01 | unit | `pytest tests/unit/test_dependency_resolver.py::test_execution_order -x` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | PAR-02 | integration | `pytest tests/integration/test_parallel_execution.py::test_concurrent_execution -x` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 2 | PAR-09 | unit | `pytest tests/unit/test_task_executor.py::test_no_threading_used -x` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 1 | PAR-03 | integration | `pytest tests/integration/test_database_operations.py::test_create_and_retrieve_task -x` | ❌ W0 | ⬜ pending |
| 02-03-02 | 03 | 2 | PAR-05 | unit | `pytest tests/unit/test_task_state_models.py::test_status_transitions -x` | ❌ W0 | ⬜ pending |
| 02-03-03 | 03 | 3 | PAR-07 | integration | `pytest tests/integration/test_parallel_execution.py::test_config_persistence -x` | ❌ W0 | ⬜ pending |
| 02-04-01 | 04 | 1 | PAR-04 | unit | `pytest tests/unit/test_cancellation.py::test_grace_period_checkpoint -x` | ❌ W0 | ⬜ pending |
| 02-04-02 | 04 | 2 | PAR-06 | unit | `pytest tests/unit/test_task_executor.py::test_error_message_formatting -x` | ❌ W0 | ⬜ pending |
| PERF-01 | 02-04 | 3 | PERF-01 | integration | `pytest tests/integration/test_parallel_execution.py::test_speedup_factor -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/unit/test_dependency_resolver.py` — Kahn's algorithm stubs (PAR-01)
- [ ] `tests/unit/test_task_executor.py` — TaskGroup execution stubs (PAR-02, PAR-09)
- [ ] `tests/unit/test_task_state_models.py` — Pydantic model stubs (PAR-05, PAR-06)
- [ ] `tests/unit/test_cancellation.py` — Grace period stubs (PAR-04)
- [ ] `tests/integration/test_parallel_execution.py` — End-to-end flow stubs (PAR-02, PERF-01, PAR-07)
- [ ] `tests/integration/test_database_operations.py` — SQLite CRUD stubs (PAR-03)
- [ ] `tests/conftest.py` — shared fixtures (aiosqlite in-memory DB, mock MCP client)
- [ ] `uv add --dev pytest-asyncio faker` — async test dependencies

*Wave 0 complete when all test files exist with stub tests that compile (import errors OK).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Grace period timing | PAR-04 | Requires manual timing verification (5s window) | Run cancellation test, verify ~5s delay before hard kill |
| Speedup factor | PERF-01 | Requires performance baseline measurement | Run sequential vs parallel, measure 3-10x improvement |
| SQLite WAL mode | PAR-03 | Database configuration inspection | Check `PRAGMA journal_mode` returns `wal` |

*Most behaviors have automated verification. Manual tests are for timing/performance validation.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (7 test files + conftest + dependencies)
- [ ] No watch-mode flags (pytest -x uses fail-fast, not watch mode)
- [ ] Feedback latency < 60s (quick unit test runs)
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 complete

**Approval:** pending

---

## Notes

**Phase 2 specifics:**
- Async testing requires pytest-asyncio plugin
- SQLite tests use in-memory database (`:memory:`) for isolation
- Speedup tests need sequential baseline (use fixture to measure)
- Cancellation tests need timing verification (use `asyncio.sleep()` mock for deterministic testing)

**Wave 0 strategy:**
Create stub tests first (import errors allowed). This enables planning phase to proceed with full verification map. Tests will be filled in during execution phase.
