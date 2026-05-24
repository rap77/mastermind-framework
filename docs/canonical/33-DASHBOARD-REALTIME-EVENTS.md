# Dashboard Realtime Events

## 1. Propósito

Definir los eventos mínimos en tiempo casi real que el dashboard debe recibir para reflejar actividad operacional sin depender de polling excesivo.

---

## 2. Tesis central

> La UI debe enterarse de lo importante cuando ocurre: cambios de tarea, checkpoints, decisiones, switches de backend, bloqueos y costos acumulados.

---

## 3. Eventos mínimos recomendados

### A. Project status events
- `project_status_changed`
- `project_eta_updated`

### B. Task events
- `task_started`
- `task_paused`
- `task_blocked`
- `task_resumed`
- `task_completed`

### C. Run events
- `run_started`
- `run_status_changed`
- `run_completed`

### D. Checkpoint events
- `checkpoint_created`

### E. Decision events
- `decision_created`
- `decision_status_changed`

### F. Runtime events
- `backend_switched`
- `window_exhausted`
- `waiting_for_window`

### G. Telemetry events
- `token_usage_updated`
- `cost_threshold_reached`

---

## 4. Payload mínimo común

Todo evento debería incluir al menos:

- `event_id`
- `event_type`
- `project_id`
- `occurred_at`
- `actor_type`
- `actor_id`
- `summary`
- `payload`

---

## 5. Casos de uso clave para la UI

### Overview
Actualizar:
- status general
- tarea actual
- blockers
- costo acumulado

### Activity Feed
Agregar eventos recientes en orden temporal.

### Task detail
Actualizar checkpoint, estado, owner y next step.

### Cost view
Actualizar tokens/costo casi en tiempo real.

### Runtime view
Actualizar backend activo, switches y agotamiento de ventanas.

---

## 6. Principios

1. Solo emitir eventos que cambien comprensión operativa.
2. El payload debe ser resumible y drill-down friendly.
3. Los eventos deben ser consumibles por UI y audit trail.
4. La realtime layer complementa la consulta REST, no la sustituye.

---

## 7. Qué NO hacer

- emitir cada detalle interno irrelevante
- convertir logs crudos en eventos UI
- mezclar notificaciones humanas con auditoría sin separación clara

---

## 8. Próximos artefactos recomendados

1. `35-WEBSOCKET-EVENT-CONTRACT.md`
2. `36-INITIAL-BACKEND-IMPLEMENTATION-PLAN.md`
3. `37-MVP-DASHBOARD-SCREEN-MAP.md`

## Key Learnings:

1. El tiempo real útil no es todo lo que ocurre, sino lo que cambia el entendimiento del operador.
2. Task, decision, checkpoint, runtime y cost events son el núcleo mínimo.
3. La capa realtime debe diseñarse como complemento del estado estructurado, no como fuente principal de verdad.
