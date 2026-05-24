# Agent Tools Catalog

## 1. Propósito

Definir el catálogo inicial de capacidades semánticas que MasterMind debería exponer a agentes a través del backend, y opcionalmente vía MCP.

---

## 2. Tesis central

> Las tools de agentes deben expresar intención de dominio y workflow, no operaciones crudas sobre almacenamiento.

---

## 3. Categorías iniciales

### A. Project visibility tools

- `get_project_overview(project_id)`
- `list_project_active_tasks(project_id)`
- `list_project_blocked_tasks(project_id)`
- `get_project_cost_summary(project_id)`

### B. Task continuity tools

- `get_task_detail(task_id)`
- `get_task_context_projection(task_id)`
- `get_task_doctrine_projection(task_id)`
- `get_latest_checkpoint(task_id)`
- `create_checkpoint(task_id, summary, next_step)`

### C. Decision tools

- `list_project_decisions(project_id)`
- `get_decision_detail(decision_id)`
- `record_decision(project_id, task_id, title, rationale, metadata)`

### D. Runtime tools

- `record_backend_switch(run_id, from_backend, to_backend, reason, checkpoint_id)`
- `record_window_exhausted(run_id, backend_id, estimated_reset_at)`
- `pause_run(run_id, reason)`

### E. Telemetry tools

- `record_token_usage(project_id, task_id, run_id, provider, model, usage)`
- `get_project_token_usage(project_id)`

### F. Collaboration tools

- `record_handoff(task_id, from_actor, to_actor, reason, checkpoint_id)`
- `list_task_participants(task_id)`

---

## 4. Tool design rules

1. Una tool debe ser específica y semántica.
2. Debe validar inputs a través del backend.
3. Debe generar auditoría si muta estado.
4. Debe devolver respuesta útil para continuidad, no solo ack vacío.

---

## 5. Qué evitar

- `run_sql`
- `update_any_entity`
- `mutate_state_with_raw_payload`
- tools que mezclen demasiadas responsabilidades

---

## 6. Orden recomendado de implementación

### Primera ola
- `get_project_overview`
- `get_task_detail`
- `get_task_context_projection`
- `get_task_doctrine_projection`
- `create_checkpoint`
- `record_decision`
- `record_token_usage`

### Segunda ola
- `record_backend_switch`
- `pause_run`
- `record_handoff`
- `list_project_blocked_tasks`

### Tercera ola
- herramientas de runtime más avanzadas
- herramientas de replay o simulation
- tools de doctrine override y approvals

---

## 7. Señal de calidad

Una tool está bien diseñada si:

- un agente puede usarla sin conocer el schema interno
- la intención es obvia por el nombre
- el output sirve para continuar el trabajo
- la mutación queda auditada

---

## 8. Próximos artefactos recomendados

1. `39-INITIAL-MIGRATION-BREAKDOWN.md`
2. `40-MVP-READ-MODEL-QUERIES.md`
3. `41-BACKEND-SERVICE-CATALOG.md`

## Key Learnings:

1. Las tools buenas encapsulan workflow y dominio, no detalles de almacenamiento.
2. Checkpoint, projection, decision y telemetry tools son el primer núcleo valioso.
3. El catálogo ayuda a diseñar el backend pensando en capacidades reales para agentes.
