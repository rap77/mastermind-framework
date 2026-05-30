# Tasks — collaboration-rbac

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

## T1: Define and stabilize the slice

### Purpose
Clarify the exact objective boundary and produce an execution-ready planning package before implementation begins.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- `.planning/changes/collaboration-rbac/requirements.md`
- `.planning/changes/collaboration-rbac/design.md`
- `.planning/changes/collaboration-rbac/tasks.md`
- `.planning/changes/collaboration-rbac/HANDOFF-CURRENT.md`

### Validation Commands
- Review requirements/design/tasks package for consistency with `docs/canonical/23-COLLABORATION-AND-RBAC-MODEL.md`.

### Acceptance Criteria
- [x] requirements.md has concrete scope: Participant model, ParticipantRole enum, repository, API endpoints, tests.
- [x] design.md has file-level specifics: exact file paths, class names, endpoint signatures.
- [x] Out-of-scope is explicit: no frontend, no Rust, no permission enforcement middleware in this slice.
- [x] Existing architecture constraints documented: SQLite-string enum pattern, composite PK rationale.

## T2: Implement the smallest coherent deliverable

### Purpose
Land the participant model, repository, API, and tests as described in the refined design.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/api/mastermind_cli/project_state/models/participant.py` (new)
- `apps/api/mastermind_cli/project_state/models/__init__.py` (add Participant export)
- `apps/api/mastermind_cli/project_state/repositories/participants.py` (new)
- `apps/api/mastermind_cli/project_state/schemas/participants.py` (new)
- `apps/api/mastermind_cli/api/routes/project_participants.py` (new)
- `apps/api/mastermind_cli/api/app.py` (register new router)
- `apps/api/tests/api/test_project_participants.py` (new)

### Validation Commands
```bash
cd apps/api
uv run pytest tests/api/test_project_participants.py -v
uv run pytest --tb=short -q
```

### Acceptance Criteria
- [x] `ps_participants` table created by `initialize_database()`.
- [x] `POST /api/projects/{project_id}/participants` → 201 with ParticipantResponse.
- [x] `GET /api/projects/{project_id}/participants` → 200 with ParticipantListResponse.
- [x] `DELETE /api/projects/{project_id}/participants/{participant_id}` → 204.
- [x] Invalid role → 422.
- [x] All new tests pass. Full suite stays green.

## T3: Close the continuity loop

### Purpose
Refresh handoff and validation context for the next model/session.

### Depends On
T2

### Parallelizable
no

### Files / Areas Likely Touched
- `.planning/changes/collaboration-rbac/HANDOFF-CURRENT.md`
- `.planning/changes/collaboration-rbac/tasks.md`
- `.planning/changes/collaboration-rbac/todo.md`

### Validation Commands
- Refresh handoff and rerun discovery contract check.

### Acceptance Criteria
- [ ] Handoff notes are refreshed with next recommended work.
- [ ] Validation commands are documented and pass.
