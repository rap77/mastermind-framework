# Window Scheduler Data Schema

## 1. Propósito

Definir el schema mínimo de datos que debe usar el Window Scheduler para operar de forma consistente, auditable y reusable en el core.

---

## 2. Principio rector

> El schema debe ser suficiente para disponibilidad, switching, continuidad y reporte, sin depender de detalles locales de un Project Adapter.

---

## 3. Entidades mínimas

### A. Backend Session

Representa una cuenta/backend utilizable por el runtime.

```yaml
backend_session:
  backend_id: "claude-sub-01"
  provider: "claude"
  account_id: "personal-main"
  auth_mode: "subscription"
  model_family: "claude"
  priority: 10
  cost_tier: "low"
  risk_tier: "medium"
  overnight_allowed: true
  automatic_switch_allowed: true
  human_confirmation_required: false
  enabled: true
```

### B. Availability State

Representa el estado temporal actual de un backend.

```yaml
availability_state:
  backend_id: "claude-sub-01"
  state: "active"
  window_started_at: "2026-05-23T00:05:00-04:00"
  window_exhausted_at: null
  estimated_reset_at: null
  estimation_source: "explicit|heuristic|manual"
  estimation_confidence: "high|medium|low|unknown"
  last_verified_at: "2026-05-23T01:10:00-04:00"
```

### C. Run Policy

Representa la política activa para una ejecución.

```yaml
run_policy:
  run_id: "night-run-001"
  project_id: "mastermind"
  adapter_id: "finance-trading-pilot"
  execution_mode: "hybrid"
  overnight_mode: true
  max_switches_per_run: 6
  allow_paid_api_fallback: false
  require_human_for_high_risk_actions: true
  max_cost_tier: "medium"
  pause_on_low_confidence_reset: true
```

### D. Scheduler Event

Representa un evento auditable del scheduler.

```yaml
scheduler_event:
  event_id: "evt-204"
  run_id: "night-run-001"
  project_id: "mastermind"
  task_id: "task-finance-f2-refinement"
  type: "backend_switch"
  from_backend: "claude-sub-01"
  to_backend: "codex-sub-01"
  reason: "window_exhausted"
  checkpoint_id: "chk-099"
  execution_mode: "hybrid"
  estimated_reset_at: "2026-05-23T07:14:00-04:00"
  decision_outcome: "switched"
  eligibility_basis: "next subscription backend allowed by policy"
  next_step_summary: "resume expert pack refinement"
  created_at: "2026-05-23T02:15:00-04:00"
```

### E. Scheduler Checkpoint

Representa el punto mínimo de reanudación.

```yaml
scheduler_checkpoint:
  checkpoint_id: "chk-099"
  run_id: "night-run-001"
  project_id: "mastermind"
  task_id: "task-finance-f2-refinement"
  step_id: "step-3"
  context_summary: "Refined finance F2 expert set; pending coverage validation"
  artifacts:
    - "docs/canonical/examples/finance/F2-QUANT-RESEARCH-BRAIN-SPEC.md"
    - "docs/canonical/examples/finance/03-FINANCE-TEAM-INTERACTION-PROTOCOL.md"
  next_step_summary: "validate expert coverage against anti-overfitting heuristics"
  created_at: "2026-05-23T02:14:30-04:00"
```

---

## 4. Relaciones mínimas

- `backend_session.backend_id` ↔ `availability_state.backend_id`
- `run_policy.run_id` ↔ `scheduler_event.run_id`
- `scheduler_event.checkpoint_id` ↔ `scheduler_checkpoint.checkpoint_id`
- `scheduler_event.project_id` ↔ `run_policy.project_id`

---

## 5. Reglas canónicas

### Regla 1
No puede existir `backend_switch` sin `checkpoint_id`.

### Regla 2
No puede existir checkpoint sin `next_step_summary`.

### Regla 3
Toda estimación de reset debe registrar `estimation_source` y `estimation_confidence`.

### Regla 4
Todo run debe tener una `run_policy` explícita o heredada.

---

## 6. Campos opcionales recomendados

### Backend Session
- `tags`
- `notes`
- `daily_quota_hint`

### Availability State
- `cooldown_reason`
- `retry_after_seconds`

### Scheduler Event
- `error_code`
- `warning_level`
- `operator_note`

### Scheduler Checkpoint
- `decision_refs`
- `memory_refs`
- `resume_constraints`

---

## 7. Límites del schema

Este schema no define:

- transcript completo
- contenido doctrinal de brains
- detalles internos del adapter
- representación de costos exactos por proveedor

Solo define el mínimo reusable del scheduler.

---

## 8. Próximos artefactos recomendados

1. `20-RUN-POLICY-EXAMPLES.md`
2. `21-BACKEND-REGISTRY-CONFIG-GUIDE.md`

## Key Learnings:

1. El Window Scheduler necesita pocas entidades, pero muy bien acopladas: backend, availability, policy, event y checkpoint.
2. La confianza del sistema depende de que reset estimations y checkpoints queden explícitamente estructurados.
3. El schema del core debe permanecer neutral respecto al dominio del adapter.
