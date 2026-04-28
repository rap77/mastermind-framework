# MasterMind v3.1 — Technical Debt

**Created:** 2026-04-28
**Last updated:** 2026-04-28

---

## H2: test_cors_configuration — Root Cause

**File:** `apps/api/tests/api/test_app.py::test_cors_configuration`
**Gap reference:** V31-GAPS.md H2
**Current status:** RESOLVED (commit `300d0742`, 2026-03-24)

### What failed

The test sent an OPTIONS preflight request with `Origin: http://example.com`.
The CORS middleware correctly rejected it because `example.com` is not in
`ALLOWED_ORIGINS` (which defaults to `http://localhost:3001,http://localhost:3000`).

CORS spec prohibits `allow_credentials=True` with wildcard origins, so the middleware
uses an explicit allowlist. Any origin not in the list gets no `access-control-allow-origin`
header — which is the correct behavior, not a bug.

### Root cause

Test was asserting that ANY `OPTIONS` request returns `access-control-allow-origin`,
regardless of origin. This misunderstands how CORS works:

```
# WRONG assumption in original test
OPTIONS http://example.com  →  200 with access-control-allow-origin  (invalid)

# CORRECT behavior
OPTIONS http://localhost:3000  →  200 with access-control-allow-origin  (valid)
OPTIONS http://example.com     →  200 without access-control-allow-origin  (rejected)
```

### Fix applied

Changed test to use `http://localhost:3000` (an explicitly allowed origin):

```python
# Before (wrong origin — correctly rejected by CORS)
headers={"Origin": "http://example.com", ...}

# After (allowed origin — passes through)
headers={"Origin": "http://localhost:3000", ...}
```

### Lesson

CORS with `allow_credentials=True` REQUIRES an explicit origin allowlist. Never use
`*` + credentials. Tests must use origins that are actually in the allowlist.

---

## H3: test_get_brain — Root Cause

**File:** `apps/api/tests/unit/test_brain_registry.py::test_get_brain`
**Gap reference:** V31-GAPS.md H3
**Current status:** RESOLVED (commit `7dc9e4e4`, 2026-03-20 or earlier)

### What failed

The test called `get_brain(1)` and asserted `brain_1["name"] == "Product Strategy"`.
The failure was that the brain registry (`brains.yaml`) either did not exist, had a
different name for brain ID 1, or the `get_brain()` function had not been implemented
yet at the time of the gap audit.

### Root cause

The gap was a **timing artifact**: `test_get_brain` was written as part of the
`feat(06-01)` commit that created `GET /api/brains` endpoint. At the time V31-GAPS.md
was authored (2026-04-28), the audit referenced Phase 07 failures without checking
whether those failures were already closed.

The test passes today because:
1. `brain_registry.py` exists with `get_brain(brain_id: int)` implemented
2. `brains.yaml` has brain ID 1 named `"Product Strategy"` with `status: "active"`
3. All 8 brain configurations are loaded correctly from YAML

### Current state

`test_get_brain` passes — `get_brain(1)` returns:
```python
{"id": 1, "name": "Product Strategy", "status": "active", ...}
```

No action required. Document only for completeness.

---

## H1: 9 tech-debt items from v2.1

**Source:** `.planning/RETROSPECTIVE.md`
**Current status:** Unaudited — details not surfaced in V31-GAPS.md

See `.planning/RETROSPECTIVE.md` for the full list.

---

## A2: Frontend Test Verification Results

**Date:** 2026-04-28
**Task reference:** A2 (Frontend Test Verification)
**Vitest version:** 4.1.0

### Run summary

```
Test Files: 88 passed (88)
     Tests: 849 passed (849)
  Duration: 29.13s
```

### Result

**ALL 849 tests pass.** No failures, no tests to skip, no categorization needed.

### Observations

- `act()` warnings are present in several test files (UnifiedInboxPage, simulation-playflow,
  FlowToolbar) — these are React testing warnings, not failures. They indicate state updates
  happening outside `act()` wrappers but do not cause test failures in vitest.
- `jsx` prop warning from react-virtuoso mock is cosmetic — the mock passes `jsx={true}` to a
  DOM element. This is pre-existing and doesn't affect test outcomes.
- All 88 test files cover: messaging, strategy-vault, flow-designer, engine-room, command-center,
  stores, lib utilities, simulation, nexus, auth, and scripts.

### Failing tests categorized

None. Zero failures as of 2026-04-28.

### Non-arreglable tests skipped

None. No skips required.

---

## Database Architecture Debt (C1)

**Gap reference:** V31-GAPS.md C1
**Current status:** Partially addressed in A1.2 (dual-write cleanup)

The `DualWriteDatabaseConnection` class was removed from `database.py` on 2026-04-28
(commit during A1 task execution) as dead code — it was never imported or called
anywhere in the codebase.

### Remaining work

The application still uses SQLite (aiosqlite) for all runtime data, not PostgreSQL.
The `config.py` has `postgres_dsn` configured, and `costs.py` / `mm_flow` / `orchestrator`
use `asyncpg` directly for PostgreSQL access, but the main API routes
(`DatabaseConnection` in `app.py`, `auth.py`, `analytics.py`, etc.) still use SQLite.

The full SQLite → PostgreSQL migration for the main API persistence layer is tracked
as gap C1 and remains outstanding for v3.1.

**Impact:** Production data is ephemeral (in-memory SQLite `:memory:`). No persistence
survives restarts. PostgreSQL integration exists only in cost metrics and mm_flow subsystems.
