# Session 2026-03-17 — Playwright/asyncio Separation

## Commit
`e54c51e` - wip: playwright e2e separation complete, 48 test stubs pending decision

## What Was Done

### Solution Implemented (3 changes)
1. **`pyproject.toml`** — Added `--ignore=tests/e2e` to `addopts`. E2E never run with plain `pytest`.
2. **3 smoke test files** — `pytestmark = pytest.mark.e2e` (was `pytest.mark.skip`)
3. **`.github/workflows/ci.yml`** — Level 3 no longer runs e2e. Added Level 4 (`workflow_dispatch` only)
   that installs Playwright, starts uvicorn, waits for health, then runs `pytest tests/e2e/ -m e2e`.

### Why
conftest.py magic was rejected. Explicit `--ignore` in config > runtime socket detection.
Separate CI process = no event loop cross-contamination possible.

## Test Results
Full suite (excluding e2e): **422 passed, 48 failed, 5 skipped**

## Remaining 48 Failures

### tests/api/ — 38 stubs
`raise AssertionError("Test stub: X")` — production code EXISTS in `mastermind_cli/api/`
Files: test_app.py, test_audit.py, test_auth.py, test_executions.py, test_sessions.py, test_websocket.py

### tests/perf/ — 8 stubs
Files: test_db_queries.py, test_websocket_perf.py

### Real failures — 2
- `test_web_auth_with_database` (integration) — not investigated
- `test_parse_follow_up_basic` (orchestrator) — not investigated

## Decision Pending
User wants to fix ALL 48. Options: A) implement all stubs, B) skip stubs + fix 2 real, C) xfail + gradual.
No decision made — user paused before choosing.

## Commits Pending Push
9 commits not yet pushed to GitHub (e54c51e + 8 prior)
