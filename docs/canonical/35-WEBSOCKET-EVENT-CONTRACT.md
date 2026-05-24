# WebSocket Event Contract

## 1. Propósito

Definir el contrato mínimo de eventos realtime entre backend y dashboard para reflejar actividad del proyecto, runtime y costos en tiempo casi real.

---

## 2. Tesis central

> El contrato de eventos debe ser estable, resumible y orientado a cambios operativos relevantes, no a streaming indiscriminado de logs.

---

## 3. Envelope común

Todo evento WebSocket debería incluir:

- `event_id`
- `event_type`
- `project_id`
- `occurred_at`
- `actor_type`
- `actor_id`
- `summary`
- `payload`
- `trace_id` opcional

---

## 4. Eventos mínimos

### Project
- `project_status_changed`
- `project_eta_updated`

### Task
- `task_started`
- `task_paused`
- `task_blocked`
- `task_resumed`
- `task_completed`

### Run
- `run_started`
- `run_status_changed`
- `run_completed`

### Checkpoint
- `checkpoint_created`

### Decision
- `decision_created`
- `decision_status_changed`

### Runtime
- `backend_switched`
- `window_exhausted`
- `waiting_for_window`
- `context_fit_warning`

### Telemetry
- `token_usage_updated`
- `cost_threshold_reached`

---

## 5. Payload rules

### Regla 1
El payload debe ser pequeño y orientado a UI.

### Regla 2
Debe incluir ids para drill-down REST.

### Regla 3
No debe reemplazar el audit log ni el estado persistido.

### Regla 4
Debe poder resumirse en activity feed.

---

## 6. Ejemplo

```json
{
  "event_id": "evt-204",
  "event_type": "backend_switched",
  "project_id": "mastermind",
  "occurred_at": "2026-05-23T02:15:00-04:00",
  "actor_type": "system",
  "actor_id": "window-scheduler",
  "summary": "Switched from claude-sub-01 to codex-sub-01 after window exhaustion",
  "payload": {
    "run_id": "night-run-001",
    "task_id": "task-finance-f2-refinement",
    "from_backend": "claude-sub-01",
    "to_backend": "codex-sub-01",
    "checkpoint_id": "chk-099"
  }
}
```

---

## 7. Principios

1. Tiempo real útil > verbosity.
2. Evento resumen + drill-down posterior.
3. Consistencia con audit trail y REST.
4. Evolución compatible del contract.

---

## 8. Próximos artefactos recomendados

1. `36-INITIAL-BACKEND-IMPLEMENTATION-PLAN.md`
2. `37-MVP-DASHBOARD-SCREEN-MAP.md`
3. `38-AGENT-TOOLS-CATALOG.md`

## Key Learnings:

1. El WebSocket debe transmitir cambios operativos relevantes, no logs crudos.
2. Un envelope común simplifica dashboard, feed y observabilidad.
3. El contrato realtime debe complementar el estado persistido, no competir con él.
