# Session 2026-04-01 — Fase 3 Complete, Fase 4 Pending

## What Was Done

### Commits this session (in order)
- `ffc1c51` — docs(brain-feed): 7-brain evaluation findings (uncommitted from prev session)
- `e982059` — feat(agent-restructuring): Fase 3 — API ↔ execution real
- `19781ce` — chore: continue-here updated (Fase 3 done, Fase 4 next)
- `wip commit` — Fase 4 paused at wsStore decision

### Fase 3 — Implemented Files
- **NEW**: `apps/api/mastermind_cli/api/services/task_runner.py`
  - `run_brain_task(task_id, brief, flow, db_path)` coroutine
  - `BRAIN_ID_MAP: {1: "brain-01-product", ..., 7: "brain-07-growth"}`
  - FastAPI BackgroundTasks pattern (NOT asyncio.create_task)
  - `CancelledError` caught explicitly alongside Exception
  - `Brief()` inside try block — catches Pydantic ValidationError
  - `_PassthroughMCPClient` — satisfies MCPClient protocol for background context
  - ExperienceLogger.log_execution() called per brain on success
- **MODIFIED**: `apps/api/mastermind_cli/api/routes/tasks.py`
  - `BackgroundTasks` injected into `create_task()`
  - `background_tasks.add_task(run_brain_task, ...)` — resolves TODO:98
- **NEW**: `apps/api/tests/api/test_task_runner.py` (7 tests)
- **NEW**: `apps/api/tests/api/test_experiences_route.py` (4 tests)

### Suite Status
589 passed, 8 skipped, 3 RED stubs (Phase 12 — intentional)

## Key Discoveries (save time next session)

1. **Brief validation**: `Brief(problem_statement=...)` requires 3+ words. "Test brief" = 2 words → ValidationError. Use "Test brief input".
2. **pydantic-mypy init_typed=true**: Must pass `context=""` and `target_audience=None` explicitly even though they have defaults — mypy requires it.
3. **MCPIntegration != MCPClient protocol**: `MCPIntegration` has `query_brain()` but not `query_notebooklm()`. Created `_PassthroughMCPClient` adapter.
4. **Brief() must be inside try**: If outside, ValidationError from existing tests (audit, sessions) with short briefs ("Query test") propagates and breaks those tests.
5. **Patch path**: `mastermind_cli.api.services.task_runner.create_stateless_coordinator` (not StatelessCoordinator — it's not imported directly).

## Fase 4 — Next Steps

**Blocker #4**: `wsStore.ts` is a singleton — `taskId: string | null`, one WS connection at a time.
Line 38: `if (socket && get().taskId === taskId) return`
CommandCenterWrapper.tsx:98: `wsStore.connect(result.taskId, token)`

**Decision needed before coding**:
- Option A: Reuse parent task_id — brain_router.py emits WS events to same task_id (zero frontend changes)
- Option B: sub_task_id per brain — refactor wsStore to `Map<taskId, WSConnection>` (breaking change)

**First action**: `/mm:ask-frontend` with the question above, then TDD → `brain_router.py`
