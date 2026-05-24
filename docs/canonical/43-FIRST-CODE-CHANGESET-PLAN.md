# First Code Changeset Plan

## 1. Propósito

Definir el primer changeset de código recomendado para aterrizar el thin slice MVP sin intentar implementar demasiadas piezas a la vez.

---

## 2. Tesis central

> El primer changeset debe validar la nueva dirección arquitectónica con el menor número posible de piezas: nuevo subdominio `project_state`, sesión Postgres, modelos base, overview service y un endpoint útil.

---

## 3. Objetivo del primer changeset

Al finalizar este changeset, el sistema debería poder:

- conectarse al nuevo backend Postgres del slice `project_state`
- persistir entidades base del proyecto
- construir un overview básico de proyecto
- exponer `GET /api/projects/{project_id}/overview`

---

## 4. Alcance incluido

### A. Nuevo paquete
Crear:

- `apps/api/mastermind_cli/project_state/`

### B. Infraestructura mínima de BD
Crear:

- sesión async SQLAlchemy/Postgres
- base declarativa
- wiring mínimo de configuración

### C. Modelos iniciales
Crear:

- `Project`
- `Task`
- `Checkpoint`
- `DecisionRecord`
- `TokenUsageEvent`

### D. Repositorios mínimos
Crear:

- `ProjectsRepository`
- `TasksRepository`
- `CheckpointsRepository`
- `DecisionsRepository`
- `TelemetryRepository`

### E. Servicio inicial
Crear:

- `ProjectOverviewService`

### F. Router inicial
Crear:

- `GET /api/projects/{project_id}/overview`

---

## 5. Alcance excluido

No incluir todavía:

- DoctrineProjectionService completo
- ContextProjectionService completo
- WebSocket realtime completo
- RBAC completo
- pgvector
- migrations avanzadas de lineage/versioning
- dashboard frontend completo

---

## 6. Archivos probables a crear

### Nuevo subdominio
- `apps/api/mastermind_cli/project_state/__init__.py`
- `apps/api/mastermind_cli/project_state/database/base.py`
- `apps/api/mastermind_cli/project_state/database/session.py`
- `apps/api/mastermind_cli/project_state/models/project.py`
- `apps/api/mastermind_cli/project_state/models/task.py`
- `apps/api/mastermind_cli/project_state/models/checkpoint.py`
- `apps/api/mastermind_cli/project_state/models/decision.py`
- `apps/api/mastermind_cli/project_state/models/token_usage.py`
- `apps/api/mastermind_cli/project_state/repositories/projects.py`
- `apps/api/mastermind_cli/project_state/repositories/tasks.py`
- `apps/api/mastermind_cli/project_state/repositories/checkpoints.py`
- `apps/api/mastermind_cli/project_state/repositories/decisions.py`
- `apps/api/mastermind_cli/project_state/repositories/telemetry.py`
- `apps/api/mastermind_cli/project_state/services/project_overview.py`
- `apps/api/mastermind_cli/project_state/schemas/overview.py`

### Integración API
- `apps/api/mastermind_cli/api/routes/project_overview.py`
- posible ajuste en `apps/api/mastermind_cli/api/app.py`
- posible ajuste en `apps/api/mastermind_cli/api/dependencies.py`

### Migración
- ubicación a definir según herramienta elegida

---

## 7. Orden recomendado dentro del changeset

1. crear paquete `project_state/`
2. crear base y sesión DB
3. definir modelos base
4. crear repositorios mínimos
5. crear schema de response
6. crear `ProjectOverviewService`
7. crear router
8. registrar router en app
9. agregar pruebas mínimas

---

## 8. Pruebas mínimas esperadas

### Unit
- `ProjectOverviewService` arma el overview correctamente con datos de prueba

### Integration
- endpoint `/api/projects/{project_id}/overview` responde 200
- responde 404 si el proyecto no existe

### Contract
- response schema estable con los campos mínimos esperados

---

## 9. Riesgos a evitar

### Riesgo 1
Intentar modelar todas las tablas del diseño final en el primer commit.

### Riesgo 2
Mezclar SQLite legacy con el nuevo ORM Postgres dentro del mismo repositorio de estado.

### Riesgo 3
Intentar servir context projection completa desde el primer endpoint.

### Riesgo 4
No definir un response schema claro para overview.

---

## 10. Criterio de éxito

El changeset está bien si:

- existe el nuevo subdominio `project_state/`
- el overview sale desde Postgres
- el endpoint funciona
- las pruebas mínimas pasan
- no se rompe el backend existente

---

## 11. Próximo changeset sugerido

Después de este:

1. `TaskService` + task detail endpoint
2. `CheckpointService` + latest checkpoint endpoint
3. `TelemetryService` + cost summary endpoint

---

## 12. Relación con la estrategia general

Este changeset valida de forma pequeña pero real:

- Project State como nueva fuente de verdad
- Backend service boundary
- nuevo subdominio desacoplado del estado legacy
- read-side inicial del dashboard

## Key Learnings:

1. El primer changeset debe probar la arquitectura con una vertical pequeña pero real.
2. `project_state/` + overview endpoint es el mejor primer corte para validar la dirección.
3. Si el primer corte intenta cubrir demasiadas piezas, aumenta mucho el riesgo de fricción e inconsistencia.
