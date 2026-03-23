---
phase: 07-the-nexus
plan: 01
subsystem: api
tags: [fastapi, pydantic, react-flow, graph-endpoint, tdd, pytest]

# Dependency graph
requires:
  - phase: 06-command-center
    provides: FastAPI task endpoints with executions table
provides:
  - "GET /api/tasks/{id}/graph returns layout_positions field (null)"
  - "GraphEdge serializes as {source, target} — React Flow compatible"
  - "4 pytest tests covering BE-02 contract"
affects: [07-02, 07-03, frontend-nexus-canvas]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "React Flow edge field parity: source/target instead of from/to in Pydantic models"
    - "layout_positions: None pattern — backend field stub for future server-driven layout (Phase 08)"
    - "TDD RED/GREEN for API contract changes: tests written first, implementation second"

key-files:
  created: []
  modified:
    - apps/api/mastermind_cli/api/routes/tasks.py
    - apps/api/tests/api/test_executions.py

key-decisions:
  - "GraphEdge drops from_node/alias pattern entirely — source/target direct fields match React Flow Edge type"
  - "layout_positions always returns null for now — client computes dagre layout; field exists for Phase 08 backend-driven layout"
  - "test_graph_edges_use_source_target_fields uses db_path fixture (tmp_path) for direct sqlite patch — avoids mocking, tests real persistence"

patterns-established:
  - "BE-02 contract: { nodes[], edges[{source,target}], max_level, max_parallelism, layout_positions: null }"
  - "Pre-existing test failures documented in deferred-items.md — out of scope, not fixed"

requirements-completed: [BE-02]

# Metrics
duration: 5min
completed: 2026-03-22
---

# Phase 07 Plan 01: The Nexus — Graph Endpoint React Flow Compatibility Summary

**`GET /api/tasks/{id}/graph` now returns `{source, target}` edges and `layout_positions: null` field — fully BE-02 compliant for React Flow**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-22T15:33:43Z
- **Completed:** 2026-03-22T15:38:53Z
- **Tasks:** 2 (TDD: 1 RED + 1 GREEN)
- **Files modified:** 2

## Accomplishments
- `GraphEdge` model updated from `from_node`/`to` aliases to `source`/`target` direct fields — React Flow `Edge` type compatible
- `TaskGraphResponse` extended with `layout_positions: dict[str, dict[str, float]] | None = None` — BE-02 required field
- Both empty-graph and graph-with-nodes returns updated to include `layout_positions=None`
- 4 pytest tests added covering: valid shape, null layout_positions, source/target edges, 404 for unknown task

## Task Commits

Each task was committed atomically:

1. **TDD RED: Failing tests for BE-02 contract** - `f83d0c7` (test)
2. **TDD GREEN: Implementation + test fix** - `6e8fb4b` (feat)

**Plan metadata:** (see final commit below)

_TDD tasks had 2 commits: failing tests first, then implementation_

## Files Created/Modified
- `apps/api/mastermind_cli/api/routes/tasks.py` — GraphEdge fields renamed, TaskGraphResponse extended with layout_positions, edge-building loop updated, both returns updated
- `apps/api/tests/api/test_executions.py` — TestTaskGraphBE02 class with 4 graph tests

## Decisions Made
- **GraphEdge field rename (no alias):** Removed `from_node: str = Field(..., alias="from")` + `to: str` pattern entirely. Direct `source: str` and `target: str` fields are simpler, clearer, and eliminate the confusing alias. The old `from` JSON key was incompatible with React Flow anyway.
- **layout_positions always None:** Backend does not compute layout in v2.1 — client uses dagre. The field exists per BE-02 for future server-driven layout (Phase 08 roadmap item). Intentionally null, not absent.
- **Test uses db_path fixture:** The `test_graph_edges_use_source_target_fields` test patches `flow_config` directly in SQLite. Uses the `db_path` fixture (conftest tmp_path) so the patch hits the same DB the test client uses — no mocking needed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Fixed test DB path in source/target test**
- **Found during:** Task 2 — writing the `test_graph_edges_use_source_target_fields` test
- **Issue:** Plan said "use real test DB, no mocks" — initial draft used `os.environ.get("MM_DB_PATH", "/tmp/mastermind_test.db")` which would NOT hit the per-test `tmp_path` DB used by the `client` fixture
- **Fix:** Changed test signature to `async def test_graph_edges_use_source_target_fields(self, client, auth_headers, db_path)` and used the `db_path` fixture value directly for the sqlite connection
- **Files modified:** `apps/api/tests/api/test_executions.py`
- **Verification:** Test passes with `db_path` fixture — sqlite patch and HTTP client share same DB
- **Committed in:** `6e8fb4b` (GREEN commit)

---

**Total deviations:** 1 auto-fixed (Rule 2 — missing critical)
**Impact on plan:** Fix necessary for test correctness. Without it the sqlite patch would target a different file than the test client, making the test unreliable (would always return empty edges regardless of flow_config). No scope creep.

## Issues Encountered
- Two pre-existing test failures discovered during full suite run: `test_cors_configuration` (test_app.py) and `test_get_brain` (test_brain_registry.py). Both verified as pre-existing via `git stash`. Documented in `deferred-items.md`. Not fixed (out of scope).

## Next Phase Readiness
- BE-02 contract closed — frontend can now consume `GET /api/tasks/{id}/graph` directly with React Flow
- `layout_positions: null` signals client to compute dagre layout (already the planned frontend behavior)
- Ready for 07-02: NexusCanvas React Flow component that consumes this endpoint

---
*Phase: 07-the-nexus*
*Completed: 2026-03-22*
