# Domain Entities — UOW-5 Core Runtime Contracts

## 1. TaskProfile

### Description
Perfil normalizado de la tarea usado para selección de loops y capabilities.

### Fields
- `task_id`
- `complexity`: `simple | medium | complex`
- `risk_level`: `low | medium | high | critical`
- `verifiability`: `low | medium | high`
- `subjectivity`: `low | medium | high`
- `requires_write`
- `requires_network`
- `requires_fresh_context`
- `requires_checker`
- `acceptance_mode`: `deterministic | mixed | subjective`

## 2. HarnessDefinition

### Description
Definición tipada de un harness soportado.

### Fields
- `harness_id`
- `name`
- `purpose`
- `responsibilities`
- `supported_loops`
- `required_inputs`
- `output_contract`
- `constraints`

## 3. LoopPolicy

### Description
Política de control elegida para una tarea.

### Fields
- `base_loop`
- `additional_loops`
- `max_iterations`
- `time_budget_ms`
- `tool_budget`
- `requires_review`
- `requires_verification`
- `recovery_policy_id`

## 4. CapabilityDefinition

### Description
Entrada del inventario dinámico de capacidades.

### Fields
- `capability_id`
- `category`: `harness | loop | brain | skill | mcp | command | verifier | recovery_policy`
- `label`
- `goal_tags`
- `cost_level`
- `risk_level`
- `prerequisites`
- `compatible_harnesses`
- `compatible_task_classes`
- `requires_fresh_context`
- `requires_checker`

## 5. CapabilitySet

### Description
Conjunto de capabilities seleccionadas para la tarea actual.

### Fields
- `harnesses`
- `loops`
- `brains`
- `skills`
- `mcps`
- `commands`
- `verifiers`
- `recovery_policies`

## 6. ExecutionEnvelope

### Description
Contrato canónico de salida entre harnesses/fases.

### Fields
- `status`: `success | warning | error`
- `summary`
- `artifacts`
- `risks`
- `next_actions`
- `verification`
- `recovery`

## 7. VerificationPayload

### Description
Parte del envelope que representa validación y aceptación.

### Fields
- `performed`
- `passed`
- `checks`
- `acceptance_criteria_satisfied`
- `evidence_refs`

## 8. RecoveryPayload

### Description
Parte del envelope que representa recoverabilidad.

### Fields
- `retryable`
- `suggested_action`: `retry | patch | replan | escalate | stop`
- `attempt_count`
- `failure_class`
- `reason`

## 9. RecoveryDecision

### Description
Resultado estructurado del Recovery Harness.

### Fields
- `action`
- `reason`
- `updated_loop_policy`
- `escalate_to_human`

## Relationships

- `TaskProfile` alimenta a `LoopPolicy`
- `HarnessDefinition` restringe loops compatibles
- `CapabilityDefinition` compone `CapabilitySet`
- `ExecutionEnvelope` comunica el outcome de ejecución
- `VerificationPayload` y `RecoveryPayload` permiten decidir continuidad
