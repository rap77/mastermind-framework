# Tasks — memory-layer-v1

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Keep the slice surgical: contract + storage ownership first.
- Use TDD inside each implementation slice.
- Update this file and the handoff when a task is completed or blocked.

## ML1: Define Memory Layer domain contract

### Purpose

Introduce a first-party memory contract so the rest of MasterMind stops depending conceptually on Engram.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/memory_layer/contracts.py`
- `apps/api/mastermind_cli/memory_layer/models.py`
- `apps/api/tests/unit/`

### Validation Commands

- `cd apps/api && . .venv/bin/activate && pytest -q tests/unit -k memory_layer`

### Acceptance Criteria

- [ ] `MemoryStore` exists with the minimum methods defined in the design.
- [ ] `MemoryItem`, `MemorySearchResult`, and `MemoryContextBundle` exist.
- [ ] Contract tests define the expected behavior of the store surface.

## ML2: Add EngramMemoryStore adapter

### Purpose

Hide Engram behind the Memory Layer contract so no new flow talks to external memory directly.

### Depends On
ML1

### Parallelizable
no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/memory_layer/store_engram.py`
- `apps/api/services/engram_sync.py`
- `apps/api/tests/unit/`

### Validation Commands

- `cd apps/api && . .venv/bin/activate && pytest -q tests/unit -k 'engram and memory_layer'`

### Acceptance Criteria

- [ ] `EngramMemoryStore` implements the contract methods needed for the first slice.
- [ ] Engram-specific payload shapes are mapped into internal memory models.
- [ ] No new caller outside the adapter depends on raw Engram tool semantics.

## ML3: Implement PostgresMemoryStore minimum viable

### Purpose

Own the first persistent backend for memory items, summaries, and preferences.

### Depends On
ML1

### Parallelizable
yes

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/memory_layer/store_postgres.py`
- `apps/api/mastermind_cli/memory_layer/service.py`
- `apps/api/mastermind_cli/project_state/database/` or migration surface to add tables
- `apps/api/tests/integration/`

### Validation Commands

- `cd apps/api && . .venv/bin/activate && pytest -q tests/integration -k memory_layer`

### Acceptance Criteria

- [ ] The minimum memory tables exist.
- [ ] `PostgresMemoryStore` supports save/get/list/search basic flows.
- [ ] Integration tests prove items, session summaries, and preferences can be persisted and retrieved.

## ML4: Migrate first surfaces to MemoryService

### Purpose

Move the first real framework flows onto the new memory abstraction.

### Depends On
ML2, ML3

### Parallelizable
no

### Files / Areas Likely Touched

- `apps/api/...` callers that currently save session summaries / learnings / preferences
- `apps/api/mastermind_cli/memory_layer/service.py`
- targeted tests for migrated surfaces

### Validation Commands

- `cd apps/api && . .venv/bin/activate && pytest -q tests/unit tests/integration -k 'memory_layer or summary or preference or learning'`

### Acceptance Criteria

- [ ] At least one session summary flow uses `MemoryService`.
- [ ] At least one learning/fix flow uses `MemoryService`.
- [ ] At least one preference flow uses `MemoryService`.
- [ ] The flows no longer depend conceptually on Engram.

## ML5: Close Phase 1–2 slice

### Purpose

Refresh continuity artifacts and leave the package ready for the retrieval phase.

### Depends On
ML4

### Parallelizable
no

### Files / Areas Likely Touched

- `.planning/changes/memory-layer-v1/HANDOFF-CURRENT.md`
- `.planning/changes/memory-layer-v1/todo.md`

### Validation Commands

- Review acceptance criteria in `requirements.md`, `design.md`, and this task file.

### Acceptance Criteria

- [ ] Handoff reflects exact completion state and next recommended task.
- [ ] Remaining work is explicitly queued for hybrid retrieval and eval phases.
