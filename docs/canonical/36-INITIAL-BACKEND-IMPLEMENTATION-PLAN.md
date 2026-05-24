# Initial Backend Implementation Plan

## 1. Propósito

Definir el primer plan de implementación backend para aterrizar el thin slice del Project State, Context Projection, Token Telemetry y Dashboard API.

---

## 2. Tesis central

> La primera implementación backend debe validar el ciclo operativo mínimo: proyecto → tarea → run → checkpoint → decisión → telemetría → overview/dashboard.

---

## 3. Objetivo del primer slice

Construir una base que permita:

- persistir proyectos y tareas
- registrar runs y checkpoints
- registrar decisiones
- registrar uso de tokens/costo
- servir overview, task detail, context projection y doctrine projection
- emitir eventos realtime mínimos

---

## 4. Fases recomendadas

### Fase 1 — Schema and persistence

Implementar:

- migración inicial Postgres
- modelos/entidades del slice base
- repositorios mínimos

Tablas objetivo:

- `projects`
- `artifacts`
- `tasks`
- `task_dependencies`
- `task_runs`
- `checkpoints`
- `decision_records`
- `token_usage_events`

### Fase 2 — Read-side services

Implementar servicios para:

- `get_project_overview`
- `get_task_detail`
- `get_latest_checkpoint`
- `get_cost_summary`
- `list_activity_feed`

### Fase 3 — Projection services

Implementar:

- `build_task_context_projection`
- `build_task_doctrine_projection`

### Fase 4 — Realtime events

Emitir al menos:

- `task_started`
- `task_blocked`
- `checkpoint_created`
- `decision_created`
- `token_usage_updated`

### Fase 5 — Thin dashboard integration

Conectar el frontend a:

- overview
- tasks
- checkpoints
- decisions
- cost
- activity feed

---

## 5. Orden técnico sugerido

1. migraciones
2. modelos
3. repositorios
4. servicios read-side
5. projection services
6. API endpoints
7. WebSocket feed mínimo
8. dashboard MVP

---

## 6. Principios de implementación

1. Leer primero, mutar después.
2. Optimizar por visibilidad operativa inicial.
3. No intentar implementar Brain Factory completo en este slice.
4. Priorizar estado, continuidad y costo.

---

## 7. Riesgos a evitar

- meter RBAC completo demasiado pronto
- construir demasiadas mutaciones antes de tener read-side sólido
- acoplar dashboard a logs crudos
- mezclar demasiado runtime multi-provider en el primer slice

---

## 8. Señal de éxito

El slice está bien cuando un humano puede:

- ver un proyecto
- ver tareas activas/bloqueadas
- ver el último checkpoint
- ver decisiones recientes
- ver costo/tokens básicos
- retomar una tarea con contexto proyectado

---

## 9. Próximos artefactos recomendados

1. `37-MVP-DASHBOARD-SCREEN-MAP.md`
2. `38-AGENT-TOOLS-CATALOG.md`
3. `39-INITIAL-MIGRATION-BREAKDOWN.md`

## Key Learnings:

1. El primer backend útil debe optimizar por observabilidad y continuidad, no por amplitud funcional.
2. Projection services son una pieza central, no un detalle posterior.
3. El orden correcto es schema → services → projections → API → realtime → dashboard.
