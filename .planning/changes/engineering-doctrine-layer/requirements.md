# Requirements — engineering-doctrine-layer

## Problem / Purpose
The read side of the doctrine layer already exists:
`GET /api/projects/{project_id}/tasks/{task_id}/doctrine-projection` reads doctrine from
`project.metadata_json["doctrine"]` and `task.metadata_json["doctrine"]`, and one test passes.

The write side is missing — there is no typed API endpoint to set project-level doctrine.
Without it, operators and agents cannot programmatically define the doctrine that governs
a project's execution; they would have to manually patch the untyped metadata_json blob.

## Stakeholders / Users
- Primary: agents that set doctrine on a project before executing tasks
- Secondary: human operators configuring methodology and rules for a project via the API

## Scope
- Add `PATCH /api/projects/{project_id}/doctrine` endpoint to set project-level doctrine.
- The endpoint merges the provided doctrine fields into `project.metadata_json["doctrine"]`.
- A typed `DoctrineUpdateRequest` schema is required (methodology, methodology_reason,
  required_phases, mandatory_rules, recommended_rules, architecture_constraints, quality_gates).
- Add a service method `update_project_doctrine(project_id, request)` in `ProjectOverviewService`.
- Add at least one integration test covering the write → read cycle (PATCH then GET projection).

## Out of Scope
- Dedicated doctrine tables in SQLite or PostgreSQL (stored in metadata_json JSONB for now).
- Task-level doctrine write endpoint (deferred — project-level is the primary use case).
- Enforcement engine / phase gates (deferred to a future objective).
- Doctrine versioning or audit log (deferred).

## Non-negotiables
- The backend is the authority — no direct metadata_json manipulation from clients.
- The PATCH endpoint must be auth-gated (use existing `get_current_user_any` dependency).
- Do not break the existing `GET doctrine-projection` test.
- Follow existing route and service patterns in `project_overview.py`.

## Objective-level Acceptance Criteria
- [ ] `PATCH /api/projects/{project_id}/doctrine` endpoint exists and is auth-gated.
- [ ] Request body is typed via `DoctrineUpdateRequest` (not raw dict).
- [ ] Service method `update_project_doctrine` merges doctrine into `metadata_json["doctrine"]`.
- [ ] At least one test covers the PATCH → GET doctrine-projection round-trip.
- [ ] All existing doctrine tests still pass.
