# Capability Registry Service

## 1. Propósito

Definir el servicio que registra, consulta, versiona y relaciona capacidades de MasterMind.

## 2. Tesis central

> El registry es útil solo si puede responder qué capacidad existe, cuál conviene y por qué cambió.

## 3. Responsabilidad

El servicio debe:

- registrar capabilities
- versionar capabilities
- relacionar capabilities
- consultar capabilities
- aplicar policy links
- registrar usage events
- exponer respuestas para el selector de harnesses

## 4. Inputs

### 4.1 RegisterCapabilityRequest

- `capability_key`
- `kind`
- `name`
- `description`
- `owner`
- `project_scope`
- `niche_scope`
- `inputs_schema`
- `outputs_schema`
- `prerequisites`
- `cost_profile`
- `risk_profile`
- `state`
- `version`
- `source_ref`
- `tags`
- `requires_mcp`
- `requires_checker`

### 4.2 QueryCapabilityRequest

- `objective`
- `project_id`
- `phase_id`
- `niche_scope`
- `kind`
- `risk_level`
- `token_budget`
- `requires_mcp`
- `requires_checker`
- `state_filter`
- `tags`

### 4.3 RelateCapabilityRequest

- `from_capability_key`
- `to_capability_key`
- `relation_type`
- `reason`
- `strength`

### 4.4 RecordCapabilityUsageRequest

- `capability_key`
- `session_id`
- `project_id`
- `objective_id`
- `harness_selected`
- `loop_selected`
- `outcome`
- `notes`

## 5. Outputs

### 5.1 CapabilityRecord

- `capability_id`
- `capability_key`
- `kind`
- `name`
- `description`
- `state`
- `version`
- `source_ref`
- `risk_profile`
- `cost_profile`
- `tags`

### 5.2 CapabilityQueryResult

- `capabilities`
- `reasons`
- `policy_flags`
- `recommended_capability`
- `alternatives`
- `gaps`

### 5.3 UsageRecord

- `event_id`
- `capability_key`
- `session_id`
- `project_id`
- `objective_id`
- `outcome`
- `created_at`

## 6. Service operations

### 6.1 Register capability

Crear una capability nueva si no existe o versionarla si ya existe.

### 6.2 Update capability

Cambiar metadata activa sin destruir historial.

### 6.3 Version capability

Crear una versión nueva para cambios significativos.

### 6.4 Link capability

Relacionar dos capacidades con una relación formal.

### 6.5 Query capability

Buscar capabilities por objetivo, restricciones, riesgo, estado o compatibilidad.

### 6.6 Record usage

Guardar cómo se usó una capability y con qué resultado.

## 7. Decision rules

- Si la capability existe pero está deprecated, no debe ser recomendada por defecto.
- Si una capability requiere MCP y el contexto no lo permite, debe filtrarse.
- Si una capability requiere checker separado y no lo hay, debe degradarse o bloquearse.
- Si varias capacidades cumplen, preferir la más simple.
- Si la state no es compatible con la policy, excluirla.

## 8. Policy integration

El servicio debe consultar policies para:

- scope
- write permissions
- MCP access
- review requirement
- risk ceiling

## 9. Memory integration

El servicio debe aprender de:

- usage events
- deprecation reasons
- selection outcomes
- source adoption history

## 10. Source integration

Cuando una capability viene de una fuente externa, el service debe conservar:

- source_ref
- snapshot_ref
- delta note
- adoption decision

## 11. Query patterns

El servicio debe responder preguntas como:

- “qué capability está activa para este niche”
- “qué capability reemplaza a esta otra”
- “qué capability sirve para implementar este harness”
- “qué capability requiere MCP”
- “qué capability fue aprendida desde Hermes”

## 12. No-goals

- no exponer SQL crudo
- no mezclar capacidad con runtime state
- no borrar versiones previas
- no devolver capabilities sin metadata suficiente
- no usar el registry como log de texto libre

## 13. Relación con otros docs

- `68-CAPABILITY-REGISTRY-SPEC.md`
- `69-CAPABILITY-REGISTRY-SCHEMA.md`
- `73-HARNESS-SELECTOR-SERVICE.md`
- `67-HARNESS-SELECTION-POLICY.md`
