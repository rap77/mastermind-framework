# Capability Registry Schema

## 1. Propósito

Bajar el capability registry a un esquema persistible en Postgres para que MasterMind pueda registrar, consultar y versionar capacidades de forma estructurada.

## 2. Tesis central

El registry debe poder servir como:

- catálogo operativo
- fuente de selección para el orquestador
- historial de adopción y deprecación
- base para policy checks

## 3. Entidades principales

### 3.1 capabilities

Tabla principal de capacidades vivas.

Campos sugeridos:

- `id`
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
- `created_at`
- `updated_at`

### 3.2 capability_versions

Historial de versiones y cambios.

Campos sugeridos:

- `id`
- `capability_id`
- `version`
- `change_summary`
- `change_type`
- `source_ref`
- `created_at`

### 3.3 capability_relationships

Relaciones entre capacidades.

Campos sugeridos:

- `id`
- `from_capability_id`
- `to_capability_id`
- `relation_type`
- `reason`
- `strength`
- `created_at`

Relation types:

- `uses`
- `requires`
- `replaces`
- `compatible_with`
- `conflicts_with`
- `derived_from`

### 3.4 capability_policy_links

Vínculo entre capabilities y policies.

Campos sugeridos:

- `id`
- `capability_id`
- `policy_key`
- `policy_state`
- `reason`
- `created_at`

### 3.5 capability_usage_events

Eventos de uso para aprendizaje y depuración.

Campos sugeridos:

- `id`
- `capability_id`
- `session_id`
- `project_id`
- `objective_id`
- `harness_selected`
- `loop_selected`
- `outcome`
- `notes`
- `created_at`

## 4. Índices recomendados

- `capability_key` unique
- `kind`
- `state`
- `project_scope`
- `niche_scope`
- `source_ref`
- `created_at`
- `capability_relationships(from_capability_id, relation_type)`
- `capability_relationships(to_capability_id, relation_type)`

## 5. Operaciones mínimas

### 5.1 Register capability

Crear una capability nueva con metadata completa.

### 5.2 Update capability

Cambiar metadata viva sin perder historial.

### 5.3 Version capability

Registrar un cambio importante con versión nueva.

### 5.4 Link capability

Relacionar capacidades entre sí.

### 5.5 Query capability

Buscar por objetivo, restricciones, scope, riesgo, estado o tipo.

### 5.6 Record usage

Guardar eventos de selección y resultado.

## 6. Query patterns

El registry debe responder preguntas como:

- “qué capability sirve para este objective”
- “qué capability funciona sin MCP”
- “qué harness soporta verification y recovery”
- “qué brains están activos para este niche”
- “qué capability fue adoptada desde Hermes”

## 7. Versioning rules

- No sobrescribir una capability importante sin versión.
- No perder source_ref al versionar.
- Toda deprecación debe explicar la razón.
- Toda adopción debe dejar rastro del origen.

## 8. Integración con selección

El selector de harnesses consulta el registry antes de:

- elegir harness
- elegir loop
- habilitar MCP
- activar review separado
- decidir escalación

## 9. Integración con memory

Los usage events y decisions alimentan la Memory Layer para:

- aprender qué capabilities se usan
- detectar patrones de selección
- reducir redescubrimiento
- mejorar recomendaciones futuras

## 10. Integración con source registry

Cada capability debe poder trazar su fuente a:

- repo externo
- decisión interna
- doc canónico
- issue / PR / commit

## 11. No-goals

- no permitir que el registry quede como JSON libre sin relaciones
- no duplicar toda la lógica en código hardcoded
- no mezclar capabilities con state runtime
- no usar el registry como log crudo de eventos
