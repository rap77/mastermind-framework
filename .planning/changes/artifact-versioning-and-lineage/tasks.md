# Tasks — artifact-versioning-and-lineage

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

## AV1: Schema foundation — artifact_versions + artifact_links

### Purpose
Crear las tablas SQLAlchemy `artifact_versions` y `artifact_links` en el dominio `project_state`, con sus repositorios básicos. Sin este paso no hay nada que vincular.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- apps/api/mastermind_cli/project_state/models/artifact.py (nuevo)
- apps/api/mastermind_cli/project_state/models/__init__.py
- apps/api/mastermind_cli/project_state/repositories/artifacts.py (nuevo)
- apps/api/mastermind_cli/project_state/repositories/__init__.py
- apps/api/tests/api/test_artifact_lineage.py (nuevo, TDD)

### Validation Commands
- cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_artifact_lineage.py

### Acceptance Criteria
- [x] Modelos `ArtifactVersion` y `ArtifactLink` existen y son importables desde `project_state.models`.
- [x] `initialize_database()` crea ambas tablas sin errores.
- [x] `ArtifactRepository` expone `create_version()` y `create_link()`.
- [x] Tests cubren creación y lectura básica de ambas entidades.

## AV2: Lineage service — get_artifact_lineage()

### Purpose
Exponer un método de servicio que dado un `artifact_id` retorne el grafo causal: versiones del artefacto y sus links a tareas, decisiones y checkpoints. Es la capa semántica entre repo y API.

### Depends On
AV1

### Parallelizable
no

### Files / Areas Likely Touched
- apps/api/mastermind_cli/project_state/services/project_overview.py
- apps/api/mastermind_cli/project_state/schemas/overview.py (ArtifactLineageResponse)
- apps/api/tests/api/test_artifact_lineage.py

### Validation Commands
- cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_artifact_lineage.py

### Acceptance Criteria
- [ ] `ProjectOverviewService.get_artifact_lineage(artifact_id)` retorna `ArtifactLineageResponse | None`.
- [ ] La respuesta incluye `artifact_id`, `versions`, y `links` con relaciones a task/decision/checkpoint cuando existen.
- [ ] Tests cubren: artefacto con links, artefacto sin links, artefacto inexistente (None).

## AV3: Lineage read endpoint

### Purpose
Exponer el lineage via HTTP para que sea consultable por agentes, modelos y el dashboard. Cierra el loop del objetivo — el lineage es consultable y trazable desde fuera del proceso.

### Depends On
AV1, AV2

### Parallelizable
no

### Files / Areas Likely Touched
- apps/api/mastermind_cli/api/routes/project_overview.py
- apps/api/tests/api/test_artifact_lineage.py

### Validation Commands
- cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_artifact_lineage.py
- cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_activity_feed.py tests/api/test_project_runs.py

### Acceptance Criteria
- [ ] `GET /api/projects/{project_id}/artifacts/{artifact_id}/lineage` retorna 200 con el grafo causal.
- [ ] Retorna 404 si el artefacto no existe en el proyecto.
- [ ] Los tests de regresión (activity_feed, project_runs) pasan sin cambios.
