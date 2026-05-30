# Design — collaboration-rbac

## Architecture / Boundaries

Follow the existing monorepo split: this slice touches **Python/FastAPI only** — specifically the `project_state` sub-package inside `apps/api/mastermind_cli/`. No Rust, no Next.js changes in this slice.

## Technical Approach

### 1. SQLAlchemy Model: `Participant`

File: `apps/api/mastermind_cli/project_state/models/participant.py`

```python
class ParticipantRole(str, enum.Enum):
    # Human roles
    owner = "owner"
    architect = "architect"
    implementer = "implementer"
    reviewer = "reviewer"
    approver = "approver"
    observer = "observer"
    # Agent roles
    planner = "planner"
    executor = "executor"
    critic = "critic"
    evaluator = "evaluator"
    synthesizer = "synthesizer"

class Participant(Base):
    __tablename__ = "ps_participants"
    # composite PK: (project_id, participant_id)
    # participant_type: "human" | "agent"
    # role: ParticipantRole (String column)
    # joined_at: DateTime(timezone=True)
```

Register in `models/__init__.py` so `initialize_database()` picks it up automatically.

### 2. Repository: `ParticipantsRepository`

File: `apps/api/mastermind_cli/project_state/repositories/participants.py`

Operations: `add(session, project_id, participant_id, participant_type, role)`, `list_by_project(session, project_id)`, `get(session, project_id, participant_id)`, `remove(session, project_id, participant_id) -> bool`.

### 3. Pydantic Schemas

File: `apps/api/mastermind_cli/project_state/schemas/participants.py`

- `AddParticipantRequest(participant_id, participant_type, role)`
- `ParticipantResponse(project_id, participant_id, participant_type, role, joined_at)`
- `ParticipantListResponse(items: list[ParticipantResponse], total: int)`

### 4. REST Endpoints

File: `apps/api/mastermind_cli/api/routes/project_participants.py`

```
POST   /api/projects/{project_id}/participants         → 201 ParticipantResponse
GET    /api/projects/{project_id}/participants         → 200 ParticipantListResponse
DELETE /api/projects/{project_id}/participants/{pid}  → 204 No Content
```

All require `Depends(get_current_user_any)` and `Depends(get_project_state_db_url)`.
Router registered in `app.py` alongside `project_overview_router`.

### 5. Tests

File: `apps/api/tests/api/test_project_participants.py`

- Test happy path for POST, GET, DELETE
- Test invalid role → 422
- Test DELETE non-existent participant → 404
- Use the in-memory SQLite pattern established in `tests/api/test_projects_list_detail.py`

## Dependencies

- Depends on `project-state-mvp` (already `done`): `ps_projects` table, session factory, `get_project_state_db_url` dependency, `get_current_user_any` auth.

## Validation Strategy

```bash
cd apps/api
uv run pytest tests/api/test_project_participants.py -v   # new tests
uv run pytest --tb=short -q                               # full suite
```

## Important Tradeoffs

- **SQLite enum as String**: Store role as a plain string column (not DB-level enum) — matches the pattern in `ps_tasks.status`. Validation happens at the Pydantic layer.
- **Composite PK vs. surrogate**: `(project_id, participant_id)` composite is simpler and avoids an extra UUID column for this slice.
- **No org-level RBAC yet**: Permission enforcement (checking caller role before allowing writes) is the next slice. This slice only stores the participant record.

## Context Notes

- Canonical doc: `docs/canonical/23-COLLABORATION-AND-RBAC-MODEL.md`
- Source of truth: `.planning/SOURCE-OF-TRUTH.md`
- Existing pattern to follow: `apps/api/mastermind_cli/project_state/models/task.py` + `repositories/tasks.py`
- Auth dependency pattern: `mastermind_cli.api.routes.auth.get_current_user_any`
- DB URL dependency: `mastermind_cli.api.dependencies.get_project_state_db_url`
