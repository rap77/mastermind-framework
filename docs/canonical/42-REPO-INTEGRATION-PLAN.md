# Repo Integration Plan

## 1. Propósito

Mapear el thin slice MVP diseñado en la documentación canónica hacia la estructura real actual de `apps/api`, para reducir riesgo al pasar a implementación.

---

## 2. Hallazgos principales del backend actual

### Estado actual observado

- FastAPI ya existe en `mastermind_cli/api/app.py`
- ya existen rutas de tasks, executions, analytics, brains, websocket
- existe una capa de estado simple en `mastermind_cli/state/`
- la persistencia actual principal del slice visible está apoyada en `aiosqlite`
- la app ya tiene patrones de routers, services y models reutilizables

### Implicación

No conviene crear un backend paralelo desde cero.

Conviene:

1. **extender** la arquitectura actual
2. **introducir una nueva capa de project state** de forma incremental
3. **migrar** desde SQLite simple hacia el modelo híbrido planeado, sin romper el flujo existente

---

## 3. Módulos actuales relevantes

### API / App
- `apps/api/mastermind_cli/api/app.py`
- `apps/api/mastermind_cli/api/routes/`
- `apps/api/mastermind_cli/api/services/`
- `apps/api/mastermind_cli/api/models/`
- `apps/api/mastermind_cli/api/websocket.py`

### Estado / Persistencia actual
- `apps/api/mastermind_cli/state/database.py`
- `apps/api/mastermind_cli/state/models.py`
- `apps/api/mastermind_cli/state/repositories.py`

### Runtime / Orchestration / Memory
- `apps/api/mastermind_cli/mm_flow/`
- `apps/api/mastermind_cli/orchestration/`
- `apps/api/mastermind_cli/orchestrator/`
- `apps/api/mastermind_cli/memory/`
- `apps/api/mastermind_cli/experience/`
- `apps/api/mastermind_cli/rag/`

---

## 4. Recomendación de integración

## A. Mantener `mastermind_cli/api/` como entrypoint principal

No mover la app principal.

## B. Introducir un nuevo subdominio explícito

Crear algo como:

- `apps/api/mastermind_cli/project_state/`

con submódulos:

- `database/`
- `models/`
- `repositories/`
- `services/`
- `projections/`
- `schemas/`

## C. Mantener `mastermind_cli/state/` para legacy/simple runtime state

y usar `project_state/` para el nuevo thin slice del MVP.

---

## 5. Estructura propuesta concreta

```text
apps/api/mastermind_cli/project_state/
  __init__.py
  database/
    __init__.py
    base.py
    session.py
  models/
    __init__.py
    project.py
    artifact.py
    task.py
    run.py
    checkpoint.py
    decision.py
    token_usage.py
  repositories/
    __init__.py
    projects.py
    tasks.py
    checkpoints.py
    decisions.py
    telemetry.py
  services/
    __init__.py
    project_overview.py
    tasks.py
    checkpoints.py
    decisions.py
    telemetry.py
    activity_feed.py
  projections/
    __init__.py
    context_projection.py
    doctrine_projection.py
  schemas/
    __init__.py
    overview.py
    task_detail.py
    checkpoint.py
    decision.py
    telemetry.py
```

---

## 6. Qué reutilizar del backend actual

### Reutilizar
- FastAPI app factory en `api/app.py`
- routers pattern existente
- websocket router existente
- models Pydantic pattern de `api/models/`
- background task flow donde convenga

### No reutilizar directamente como base final
- el `state/database.py` actual como motor del nuevo project state
- el task schema SQLite actual como diseño final del MVP

---

## 7. Primeros cambios concretos recomendados

### Paso 1
Crear el paquete `mastermind_cli/project_state/`.

### Paso 2
Definir un `base.py` y sesión async SQLAlchemy/Postgres para el nuevo slice.

### Paso 3
Implementar los primeros modelos:
- Project
- Artifact
- Task
- TaskDependency
- TaskRun
- Checkpoint
- DecisionRecord
- TokenUsageEvent

### Paso 4
Implementar los primeros repositorios:
- ProjectsRepository
- TasksRepository
- CheckpointsRepository
- DecisionsRepository
- TelemetryRepository

### Paso 5
Implementar los primeros services:
- ProjectOverviewService
- TaskService
- CheckpointService
- TelemetryService

### Paso 6
Agregar nuevos routers read-side, por ejemplo:
- `api/routes/project_state.py`
- `api/routes/project_overview.py`

---

## 8. Estrategia de convivencia inicial

Durante el primer slice, pueden convivir:

- SQLite legacy state (`mastermind_cli/state/`)
- Postgres project state (`mastermind_cli/project_state/`)

### Regla

El nuevo dashboard, projections y telemetría deben leer del nuevo `project_state/`.

El estado legacy puede seguir existiendo temporalmente para flows antiguos.

---

## 9. Riesgos de integración a evitar

### Riesgo 1
Intentar reemplazar toda la persistencia actual de golpe.

### Riesgo 2
Mezclar project state nuevo dentro de `state/` sin separar responsabilidades.

### Riesgo 3
Acoplar las nuevas projections a SQLite legacy.

### Riesgo 4
No definir claramente qué rutas nuevas son source of truth del dashboard MVP.

---

## 10. Recomendación de primer slice real

Si hubiera que empezar hoy mismo, haría esto:

1. crear `project_state/`
2. agregar sesión async SQLAlchemy para Postgres
3. crear migración 001
4. crear modelos `Project`, `Task`, `Checkpoint`, `DecisionRecord`, `TokenUsageEvent`
5. crear `ProjectOverviewService`
6. exponer `GET /api/projects/{project_id}/overview`

Eso ya validaría gran parte de la arquitectura.

---

## 11. Próximos artefactos recomendados

1. `43-FIRST-CODE-CHANGESET-PLAN.md`
2. `44-PROJECT-STATE-SQLALCHEMY-MODEL-SPECS.md`

## Key Learnings:

1. El backend actual ya ofrece varios patrones reutilizables; no hace falta reconstruir FastAPI desde cero.
2. La mejor integración es añadir un nuevo subdominio `project_state/` y dejar `state/` como legado temporal.
3. El primer endpoint clave para validar la dirección es `project overview`, apoyado por Postgres y servicios nuevos.
