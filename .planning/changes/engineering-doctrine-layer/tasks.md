# Tasks — engineering-doctrine-layer

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

## T1: Define and stabilize the slice

### Purpose
Clarify the exact objective boundary before implementation expands.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- requirements.md
- design.md
- tasks.md

### Validation Commands
- Review requirements/design/tasks package for consistency.

### Acceptance Criteria
- [ ] The exact boundary of the objective is implemented or tightened.
- [ ] Existing architecture constraints are preserved and documented.

## T2: Implement the smallest coherent deliverable

### Purpose
Add the write side of the doctrine layer: `PATCH /api/projects/{project_id}/doctrine`.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/api/mastermind_cli/api/routes/project_overview.py`
- `apps/api/mastermind_cli/project_state/services/project_overview.py`
- `apps/api/tests/api/test_project_doctrine_projection.py`

### Validation Commands
- `cd apps/api && uv run pytest tests/api/test_project_doctrine_projection.py -v`

### Acceptance Criteria
- [ ] `PATCH /api/projects/{project_id}/doctrine` exists and is auth-gated.
- [ ] `DoctrineUpdateRequest` schema is typed (not raw dict).
- [ ] `update_project_doctrine` service method merges doctrine into `metadata_json["doctrine"]`.
- [ ] New test covers the PATCH → GET doctrine-projection write → read cycle.
- [ ] All doctrine tests pass.

## T3: Close the continuity loop

### Purpose
Refresh handoff and validation context for the next model/session.

### Depends On
T2

### Parallelizable
no

### Files / Areas Likely Touched
- `.planning/changes/engineering-doctrine-layer/HANDOFF-CURRENT.md`
- `.planning/changes/engineering-doctrine-layer/tasks.md`
- `.planning/changes/engineering-doctrine-layer/todo.md`

### Validation Commands
- `python3 .claude/commands/mm/discover-contract-check.py --objective engineering-doctrine-layer`
- `python3 .claude/commands/mm/complete-task-handler.py --status`
- `cd apps/api && uv run pytest tests/api/test_project_doctrine_projection.py -v`

### Acceptance Criteria
- [ ] Handoff notes are refreshed with next recommended work.
- [ ] Contract check passes.
- [ ] Doctrine test suite passes.
