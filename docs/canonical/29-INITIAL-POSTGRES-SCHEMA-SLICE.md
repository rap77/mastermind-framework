# Initial Postgres Schema Slice

## 1. Propósito

Definir el primer slice de esquema Postgres que conviene implementar para validar la arquitectura de estado, contexto, costos y colaboración sin construir todo el sistema de una vez.

---

## 2. Tesis central

> El primer esquema implementable debe cubrir estado actual, tareas, checkpoints, decisiones y telemetría básica; no hace falta empezar con todo el modelo final.

---

## 3. Objetivo del thin slice

Permitir que MasterMind pueda:

- registrar proyectos
- registrar artefactos básicos
- ejecutar tareas y runs
- guardar checkpoints
- registrar decisiones
- registrar uso de tokens/costos
- construir una primera proyección de contexto
- alimentar un dashboard básico

---

## 4. Tablas recomendadas para Phase 1

### A. `projects`

Campos mínimos:

- `project_id` (pk)
- `name`
- `status`
- `adapter_id`
- `metadata JSONB`
- `created_at`
- `updated_at`

### B. `artifacts`

Campos mínimos:

- `artifact_id` (pk)
- `project_id` (fk)
- `artifact_type`
- `title`
- `path`
- `content_markdown`
- `metadata JSONB`
- `created_at`
- `updated_at`

### C. `tasks`

Campos mínimos:

- `task_id` (pk)
- `project_id` (fk)
- `parent_task_id` (nullable)
- `title`
- `status`
- `priority`
- `owner_type`
- `owner_id`
- `metadata JSONB`
- `constraints JSONB`
- `completion_criteria JSONB`
- `created_at`
- `updated_at`

### D. `task_dependencies`

Campos mínimos:

- `dependency_id` (pk)
- `task_id` (fk)
- `depends_on_task_id` (fk)
- `dependency_type`
- `created_at`

### E. `task_runs`

Campos mínimos:

- `run_id` (pk)
- `project_id` (fk)
- `task_id` (fk)
- `actor_type`
- `actor_id`
- `status`
- `started_at`
- `ended_at` (nullable)
- `metadata JSONB`

### F. `checkpoints`

Campos mínimos:

- `checkpoint_id` (pk)
- `project_id` (fk)
- `task_id` (fk)
- `run_id` (nullable fk)
- `context_summary JSONB`
- `resume_state JSONB`
- `next_step_summary`
- `created_at`

### G. `decision_records`

Campos mínimos:

- `decision_id` (pk)
- `project_id` (fk)
- `task_id` (nullable fk)
- `title`
- `status`
- `rationale_markdown`
- `metadata JSONB`
- `created_at`

### H. `token_usage_events`

Campos mínimos:

- `usage_event_id` (pk)
- `project_id` (fk)
- `task_id` (nullable fk)
- `run_id` (nullable fk)
- `provider`
- `model`
- `auth_mode`
- `prompt_tokens`
- `completion_tokens`
- `estimated_cost`
- `metadata JSONB`
- `created_at`

---

## 5. Tablas recomendadas para Phase 1.5

Cuando el thin slice ya funcione:

- `project_participants`
- `task_time_events`
- `policy_rules`
- `scheduler_events`
- `artifact_versions`
- `artifact_embeddings`

---

## 6. Relaciones mínimas críticas

- `projects` → `artifacts`
- `projects` → `tasks`
- `tasks` → `task_dependencies`
- `tasks` → `task_runs`
- `tasks` → `checkpoints`
- `tasks` → `decision_records`
- `tasks` / `task_runs` → `token_usage_events`

---

## 7. Primeras consultas que debe soportar

### Estado actual del proyecto
- proyecto
- tareas activas
- tareas bloqueadas
- última decisión
- último checkpoint

### Estado actual de una tarea
- owner actual
- status
- dependencias
- checkpoint vigente
- siguiente paso

### Costos básicos
- tokens y costo por proyecto
- tokens y costo por tarea
- tokens y costo por provider/model

### Continuidad
- último run
- último checkpoint
- última decisión relacionada

---

## 8. Qué NO meter aún en el primer slice

- RBAC completo
- simulation/replay avanzado
- lineage total
- embeddings de todo
- scheduler completo multi-provider
- analytics predictivo complejo

---

## 9. Principios

1. El primer slice debe ser pequeño pero útil.
2. Debe soportar contexto, costo y estado actual.
3. Debe dejar espacio natural para crecer sin rediseño radical.
4. Debe priorizar consultas del dashboard y proyección de contexto.

---

## 10. Resultado esperado

Con este slice implementado, MasterMind ya debería poder:

- saber qué pasa en un proyecto
- retomar una tarea sin depender del historial del proveedor
- medir uso básico de tokens/costo
- mostrar un dashboard inicial útil

---

## 11. Próximos artefactos recomendados

1. `30-DASHBOARD-INFORMATION-ARCHITECTURE.md`
2. `31-DOCTRINE-PROJECTION-FORMAT.md`
3. `32-INITIAL-API-SURFACE.md`

## Key Learnings:

1. El primer slice implementable debe optimizar por utilidad operativa, no por completitud.
2. Proyectos, tareas, runs, checkpoints, decisiones y token usage forman el núcleo mínimo valioso.
3. Si el schema inicial no soporta dashboard y context projection, es demasiado abstracto para servir al MVP.
