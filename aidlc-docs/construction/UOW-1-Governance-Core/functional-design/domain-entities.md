# Domain Entities — UOW-1 Governance Core

## 1. Intention

### Description
Representa la acción normalizada que se quiere ejecutar.

### Fields
- `action`: acción pedida (`edit_file`, `run_command`, `push_branch`, etc.)
- `targets`: lista de archivos, rutas, servicios o endpoints afectados
- `scope`: etiqueta de scope esperado para la tarea
- `estimated_risk`: riesgo inferido (`low`, `medium`, `high`, `critical`)
- `estimated_tokens`: opcional; consumo estimado si aplica
- `requires_network`: bool
- `requires_write`: bool
- `requires_production_access`: bool

## 2. TaskContext

### Description
Contexto operativo y de negocio de la tarea actual.

### Fields
- `task_id`
- `session_id`
- `allowed_paths`
- `sensitive_paths`
- `task_type`
- `approval_state`
- `dry_run_enabled`
- `production_mode`

## 3. PolicyVerdict

### Description
Resultado de una policy o del interceptor.

### Values
- `allow`
- `deny`
- `pause_and_ask`

## 4. PolicyResult

### Description
Resultado estructurado de una policy individual.

### Fields
- `policy_name`
- `verdict`
- `reason_code`
- `human_reason`
- `matched_targets`

## 5. AuditEvent

### Description
Evento append-only de evaluación.

### Fields
- `event_id`
- `timestamp`
- `session_id`
- `task_id`
- `intention_snapshot`
- `policy_name`
- `verdict`
- `reason_code`
- `reason_text`

## 6. GovernanceDecision

### Description
Consolidación final que consume el caller.

### Fields
- `final_verdict`
- `triggering_policy`
- `audit_event_ref`
- `next_action`

## 7. PolicySet

### Description
Colección ordenada de policies evaluables.

### Invariants
- orden estable
- políticas puras respecto al veredicto
- sin side effects salvo por el audit posterior gestionado por el interceptor

## Relationships

- `TaskContext` contextualiza una `Intention`
- una `PolicySet` evalúa una `Intention` usando `TaskContext`
- cada evaluación produce uno o más `PolicyResult`
- el interceptor consolida los `PolicyResult` en una `GovernanceDecision`
- cada `GovernanceDecision` referencia al menos un `AuditEvent`
