# Initial Migration Breakdown

## 1. Propósito

Definir el desglose inicial de migraciones para implementar el thin slice backend sin meter todo el modelo completo desde el primer paso.

---

## 2. Tesis central

> Las migraciones iniciales deben seguir el mismo orden del slice MVP: estado del proyecto, tareas, continuidad, decisiones y telemetría básica.

---

## 3. Orden recomendado de migraciones

### Migration 001 — Projects and artifacts

Crear:

- `projects`
- `artifacts`

Objetivo:
- tener entidad proyecto
- persistir artefactos markdown con metadata

### Migration 002 — Tasks and dependencies

Crear:

- `tasks`
- `task_dependencies`

Objetivo:
- modelar tareas, subtareas y dependencias

### Migration 003 — Runs and checkpoints

Crear:

- `task_runs`
- `checkpoints`

Objetivo:
- soportar continuidad y reanudación

### Migration 004 — Decisions

Crear:

- `decision_records`

Objetivo:
- persistir decisiones y rationales

### Migration 005 — Token telemetry

Crear:

- `token_usage_events`

Objetivo:
- medir tokens, provider, modelo y costo básico

### Migration 006 — Read-model helpers

Agregar índices, foreign keys y columnas adicionales necesarias para overview y queries frecuentes.

---

## 4. Principios

1. Cada migración debe dejar el sistema en un estado útil.
2. Las foreign keys críticas deben entrar temprano.
3. Índices de overview y task detail deben entrar antes del dashboard.
4. No meter pgvector en el primer corte si aún no hay retrieval activo.

---

## 5. Qué puede esperar

### Phase 1.5
- `project_participants`
- `task_time_events`
- `scheduler_events`
- `artifact_versions`
- `artifact_embeddings`

---

## 6. Señal de éxito

Cuando las migraciones permitan levantar:

- overview de proyecto
- detail de tarea
- checkpoint latest
- decisiones recientes
- cost summary básico

## Key Learnings:

1. Las migraciones deben seguir el flujo operativo real, no solo la taxonomía del dominio.
2. Projects, tasks, runs, checkpoints, decisions y telemetry forman el primer corte útil.
3. Lo importante al inicio es habilitar observabilidad y continuidad, no completitud del modelo.
