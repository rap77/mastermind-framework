# Handoff — artifact-versioning-and-lineage

## Current objective
- `artifact-versioning-and-lineage`

## Decisions already made
- `version_id` surrogate PK en `artifact_versions` en lugar de `artifact_id` como PK — correcto porque múltiples versiones por `artifact_id` requieren surrogate. `UniqueConstraint("artifact_id", "version")` garantiza unicidad.
- `artifact_type` y `link_type` son `String(64)` sin CHECK constraint — consistente con el patrón del codebase (`Task.status`, etc.). Riesgo I-1 del code review: valores inválidos persisten silenciosamente.
- Sesiones en tests usan `session_factory()` bare (sin `with`) — ResourceWarnings esperados, I-2 del code review. No bloqueante.

## Completed tasks
- [x] AV1: Schema foundation — artifact_versions + artifact_links
- [x] AV2: Lineage service — get_artifact_lineage()
- [x] AV3: Lineage read endpoint

## Blockers / risks
- Ninguno. AV1 desbloqueó AV2.

## Exact next recommended task
- Objective package has no pending root tasks.

## Validation commands
- cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_artifact_lineage.py
