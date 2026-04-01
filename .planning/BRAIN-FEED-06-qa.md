# BRAIN-FEED-06 — QA Domain Feed

> Written by Brain #6 (QA/DevOps). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-03-28

---

## Test Infrastructure

- `uv run pytest` must run from `apps/api/` — running from project root fails with pre-existing `ModuleNotFoundError` for `mastermind_cli`
- Vitest over Jest — ESM-native, better Next.js 16 integration
- `websocket-metrics.ts` with `WS_SLOS` — define guardrail metrics before implementing

---

## Baseline Anchors

- Adversarial baseline delta_velocity=4 signal: `@xyflow/react v12 nodeInternals` + `IntersectionObserver` was an unprompted Senior insight from Brain #4 — genuine delta_velocity=4 output not in the ticket. This is the stretch target for Phase 11 agent comparison.
- Current test suite state: 575 backend (apps/api/) + 407 frontend (apps/web/) — established Phase 08 completion baseline

---

## Anti-patterns (QA)

- `uv run pytest` from project root → use `cd apps/api && uv run pytest` (pre-existing conftest discovery issue)

---

## 2026-03-31 — Phase 12 QA Evaluation: Autonomous Agent Restructuring

### Verified Insights

**Test Suite Count Correction (verified by collection):**
- Domain feed said 575 backend. Actual count as of 2026-03-31: `589 tests collected` (cd apps/api && uv run pytest --collect-only -q)
- Update the baseline anchor: **589 backend + 407 frontend**. The feed was stale by 14 tests from Phase 12 experience/schema tests already written.

**startup_event() gap — CONFIRMED:**
- `create_experience_schema()` exists in `database.py` (line 305) and is tested offline in `tests/e2e/test_experience_logging.py`
- It is NOT yet wired into `startup_event()` in `app.py` — this is the plan item to add
- There are ZERO existing tests for `startup_event()` behavior (grep confirmed: no `startup_event` matches in tests/)
- Gap: test_app_startup_creates_experience_table must be added before closing phase

**asyncio.create_task() vs BackgroundTasks — CONFIRMED risk:**
- `asyncio.create_task()` is currently only used in `cancellation.py` and `stateless_coordinator.py` — NOT in `tasks.py`
- `tasks.py` has explicit TODO: "Integrate with Coordinator.orchestrate() in Task 2"
- The plan proposes `asyncio.create_task()` inside a route handler — this creates orphan tasks
- Correct pattern for FastAPI: `BackgroundTasks` parameter injection — testable via `httpx.AsyncClient` + mock on the background function

**GET /api/experiences/{brain_id} — IDOR risk confirmed:**
- Existing `brains.py` correctly scopes by `user_id` (WHERE user_id = current_user.id)
- The proposed endpoint is brain-scoped, not user-scoped — this is an IDOR if brain_ids are predictable
- Test required: user_b cannot read user_a's experiences for same brain_id

**aiosqlite transaction isolation — CONFIRMED gap:**
- The existing `DatabaseConnection` context manager does NOT use explicit transactions (`async with db.begin()`)
- `tasks.py` does `await db.conn.commit()` manually after each mutation
- task_runner.py mid-flight crash scenario: partial write + no explicit transaction = corrupt state
- Test required: mock StatelessCoordinator to raise after first DB write, assert zero rows in experience_records

**brain_memory.py CLI in CI — pattern established:**
- Use `pytest` + `monkeypatch` to set `MM_DB_PATH` to `tmp_path / "test.db"` before import
- Do NOT test via subprocess for unit coverage — use direct function call with AsyncMock on ExperienceLogger
- Subprocess test is acceptable for exit_code contract only (CLI arg validation)

### Deferred Items

- 📅 Embedding_stub column: NULL today, pgvector in v3.0. No test needed now beyond the existing NULL acceptance test.
- 📅 WebSocket broadcast in task_runner.py: WS_SLOS guardrail metrics should be defined before Phase 13 if WS broadcast is added to task completion path.
