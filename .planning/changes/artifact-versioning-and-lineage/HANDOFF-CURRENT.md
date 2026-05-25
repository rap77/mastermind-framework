# Handoff — artifact-versioning-and-lineage

## Current objective
- `artifact-versioning-and-lineage`

## Decisions already made
- `version_id` surrogate PK en `artifact_versions` en lugar de `artifact_id` como PK — correcto porque múltiples versiones por `artifact_id` requieren surrogate. `UniqueConstraint("artifact_id", "version")` garantiza unicidad.
- `artifact_type` y `link_type` son `String(64)` sin CHECK constraint — consistente con el patrón del codebase (`Task.status`, etc.). Riesgo I-1 del code review: valores inválidos persisten silenciosamente.
- Sesiones en tests usan `session_factory()` bare (sin `with`) — ResourceWarnings esperados, I-2 del code review. No bloqueante.

## Completed tasks
- [x] AV1: Schema foundation — 9 pytest passed, code review PASS (0 Critical, 2 Important, 3 Suggestions no-bloqueantes).
  - `ArtifactVersion`, `ArtifactLink` modelos en `project_state/models/artifact.py`
  - `ArtifactRepository` en `project_state/repositories/artifacts.py`
  - Tests en `tests/api/test_artifact_lineage.py`

## Blockers / risks
- Ninguno. AV1 desbloqueó AV2.

## Exact next recommended task
- `AV2` — Lineage service: `get_artifact_lineage()` + `ArtifactLineageResponse` schema.

## Validation commands
- cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_artifact_lineage.py
