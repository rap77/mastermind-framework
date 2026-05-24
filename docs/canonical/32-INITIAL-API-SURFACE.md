# Initial API Surface

## 1. Propósito

Definir la primera superficie API mínima para exponer estado de proyecto, tareas, decisiones, checkpoints, costos y actividad en tiempo casi real.

---

## 2. Tesis central

> La primera API no debe intentar cubrir todo el framework; debe servir al dashboard inicial, a la continuidad de tareas y a la observabilidad básica del runtime.

---

## 3. Objetivos del primer slice API

Permitir:

- listar proyectos
- consultar estado actual de un proyecto
- consultar tareas y dependencias
- consultar runs y checkpoints
- consultar decisiones
- consultar costos/tokens agregados
- consultar activity feed reciente
- obtener context projection y doctrine projection mínimas

---

## 4. Endpoints mínimos recomendados

### Projects
- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `GET /api/projects/{project_id}/overview`

### Tasks
- `GET /api/projects/{project_id}/tasks`
- `GET /api/tasks/{task_id}`
- `GET /api/tasks/{task_id}/dependencies`
- `GET /api/tasks/{task_id}/context-projection`
- `GET /api/tasks/{task_id}/doctrine-projection`

### Runs & checkpoints
- `GET /api/projects/{project_id}/runs/active`
- `GET /api/runs/{run_id}`
- `GET /api/tasks/{task_id}/checkpoints/latest`

### Decisions
- `GET /api/projects/{project_id}/decisions`
- `GET /api/decisions/{decision_id}`

### Cost & telemetry
- `GET /api/projects/{project_id}/cost-summary`
- `GET /api/projects/{project_id}/token-usage`

### Activity
- `GET /api/projects/{project_id}/activity-feed`

---

## 5. Respuestas mínimas clave

### Project Overview
Debe devolver al menos:
- project identity
- current status
- active tasks count
- blocked tasks count
- latest checkpoint
- latest decision
- cost summary
- ETA summary si existe

### Task Detail
Debe devolver al menos:
- identity
- status
- owner
- dependencies
- latest checkpoint
- next step
- active run si existe

### Context Projection
Debe devolver:
- task objective
- state summary
- blockers
- critical decisions
- relevant artifacts
- next step

### Doctrine Projection
Debe devolver:
- active methodology
- mandatory rules
- quality gates
- exception policy

---

## 6. Principios de diseño

1. Optimizar para lectura y observabilidad primero.
2. Priorizar respuestas agregadas útiles para dashboard.
3. Mantener detalle profundo en endpoints drill-down.
4. Diseñar pensando en WebSocket o streaming futuro.

---

## 7. Qué NO meter todavía

- mutaciones complejas de workflow completo
- edición de toda la doctrina por API
- replay avanzado
- simulación de schedules
- administración completa RBAC si todavía no existe backend sólido

---

## 8. Próximos artefactos recomendados

1. `33-DASHBOARD-REALTIME-EVENTS.md`
2. `35-WEBSOCKET-EVENT-CONTRACT.md`
3. `36-INITIAL-BACKEND-IMPLEMENTATION-PLAN.md`

## Key Learnings:

1. La primera API debe servir sobre todo a observabilidad, continuidad y dashboard.
2. Context projection y doctrine projection merecen endpoints explícitos.
3. El diseño inicial debe favorecer lectura agregada antes que mutación compleja.
