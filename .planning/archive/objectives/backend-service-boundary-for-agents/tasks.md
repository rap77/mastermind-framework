# Tasks — backend-service-boundary-for-agents

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
Agregar `POST /api/projects/{project_id}/tasks/{task_id}/token-usage` para que agentes registren
consumo de tokens via service layer. Cierra el único gap de escritura identificado en el audit de T1.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- apps/api/mastermind_cli/project_state/schemas/overview.py (`RecordTokenUsageRequest`)
- apps/api/mastermind_cli/project_state/services/project_overview.py (`record_token_usage` method)
- apps/api/mastermind_cli/api/routes/project_overview.py (POST endpoint)
- apps/api/tests/api/test_project_write_side.py (TDD tests)

### Validation Commands
- cd apps/api && uv run pytest tests/api/test_project_write_side.py -q
- cd apps/api && uv run pytest tests/api/test_project_activity_feed.py tests/api/test_project_runs.py -q

### Acceptance Criteria
- [ ] `POST /api/projects/{project_id}/tasks/{task_id}/token-usage` retorna 201 con el evento.
- [ ] El service method `record_token_usage` va a través del `TelemetryRepository` existente.
- [ ] Tests cubren: creación exitosa, task no encontrada (404), project no encontrado (404).
- [ ] Tests de regresión pasan sin cambios.

## T3: Close the continuity loop

### Purpose
Refresh handoff and validation context for the next model/session.

### Depends On
T2

### Parallelizable
no

### Files / Areas Likely Touched
- HANDOFF-CURRENT.md
- tasks.md
- todo.md

### Validation Commands
- Refresh handoff and rerun discovery contract check.

### Acceptance Criteria
- [ ] Handoff notes are refreshed with next recommended work.
- [ ] Validation commands are documented and pass.
