# Requirements — collaboration-rbac

## Problem / Purpose

The `project_state` module tracks projects, tasks, runs, and artifacts but has no concept of *who is participating* and *what they are allowed to do*. Without a participant model, ownership (e.g., `owner_type`/`owner_id` on `ps_tasks`) is an unvalidated string and cannot be governed. This objective introduces the minimal participation model: a `ps_participants` table, a `ParticipantRole` enum, and a CRUD API — the foundation the RBAC model in `docs/canonical/23-COLLABORATION-AND-RBAC-MODEL.md` requires.

## Canonical Reference

- `docs/canonical/23-COLLABORATION-AND-RBAC-MODEL.md` — authoritative design

## Stakeholders / Users

- Primary: repository maintainers and future execution models assigning tasks to humans or agents
- Secondary: human operators using the `/api/projects/{id}` console

## Scope

Implement the **participant model** inside the existing `project_state` module:

1. `Participant` SQLAlchemy model → `ps_participants` table (project_id FK, participant_id string, participant_type `human|agent`, role enum, joined_at)
2. `ParticipantRole` enum: `owner | architect | implementer | reviewer | approver | observer` (human); `planner | executor | critic | evaluator | synthesizer` (agent)
3. `ParticipantsRepository` — `add`, `list_by_project`, `get`, `remove` operations
4. Pydantic schemas: `AddParticipantRequest`, `ParticipantResponse`, `ParticipantListResponse`
5. REST endpoints under `/api/projects/{project_id}/participants` (POST, GET, DELETE `/{participant_id}`) registered in `app.py`
6. Unit tests for the repository and API endpoints following the existing test pattern in `tests/api/`

## Out of Scope

- No front-end changes in this slice.
- No Rust control plane changes — participant state lives in Python/SQLite first.
- No permission enforcement middleware — that is the *next* slice after participants exist.
- Do not touch existing `ps_tasks.owner_id` / `owner_type` columns.

## Non-negotiables

- Follow the exact same SQLAlchemy + repository + FastAPI pattern established by `Project`, `Task`, and `ProjectsRepository`.
- All new endpoints require `get_current_user_any` auth dependency (same as existing `/api/projects` routes).
- Keep the backend as the authority for state, validation, and auditability.
- No unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria

- [ ] `ps_participants` table is created by `initialize_database()` without migration scripts.
- [ ] `POST /api/projects/{project_id}/participants` adds a participant with a valid role.
- [ ] `GET /api/projects/{project_id}/participants` returns the participant list.
- [ ] `DELETE /api/projects/{project_id}/participants/{participant_id}` removes a participant.
- [ ] Invalid roles return HTTP 422.
- [ ] All new endpoints are covered by tests that pass under `uv run pytest tests/api/test_project_participants.py`.
- [ ] Existing test suite (`uv run pytest`) stays green (0 new failures).
