# Capability Registry Spec

## 1. Propósito

Definir el registro canónico de capacidades de MasterMind para que el orquestador pueda descubrir y seleccionar brains, harnesses, loops, skills, MCPs, policies y verificadores sin depender de conocimiento hardcoded.

## 2. Tesis central

> El registry no es un inventario pasivo. Es el mapa operativo que permite elegir la capacidad correcta con el menor control suficiente.

## 3. Qué registra

El registry debe indexar al menos:

- brains
- harnesses
- loops
- skills
- MCPs
- policies
- verifiers
- source adapters
- memory projections
- recovery actions

## 4. Objetos canónicos

### 4.1 Capability

Entidad generalizable para cualquier cosa ejecutable o invocable por MasterMind.

Campos conceptuales:

- `capability_id`
- `kind`
- `name`
- `description`
- `owner`
- `project_scope`
- `niche_scope`
- `inputs`
- `outputs`
- `prerequisites`
- `cost_profile`
- `risk_profile`
- `supported_loops`
- `supported_harnesses`
- `requires_mcp`
- `requires_checker`
- `state`
- `version`
- `source_ref`
- `tags`

### 4.2 HarnessCapability

Especializa `Capability` para workflows.

Ejemplos:

- Discovery Harness
- AI-DLC Harness
- Research Harness
- Design Harness
- Implementation Harness
- Verification Harness
- Review Harness
- Recovery Harness
- Archive Harness
- Maintenance Harness

### 4.3 LoopCapability

Especializa `Capability` para loops de control.

Ejemplos:

- Tool Loop
- Goal Loop
- Verification Loop
- Reflection Loop
- Recovery Loop
- Review Loop
- Heartbeat Loop

### 4.4 BrainCapability

Especializa `Capability` para cerebros.

Campos adicionales:

- `brain_domain`
- `brain_niche`
- `brain_role`
- `model_preferences`
- `memory_scope`

### 4.5 MCPCapability

Especializa `Capability` para herramientas MCP.

Campos adicionales:

- `server_name`
- `tool_names`
- `auth_mode`
- `safety_constraints`
- `write_allowed`

## 5. Metadatos mínimos

Cada capability debe declarar:

- propósito
- costo esperado
- riesgo
- prerequisitos
- salida esperada
- compatibilidad
- versión
- source_ref
- estado

## 6. Estados

- `active`
- `experimental`
- `deprecated`
- `blocked`
- `candidate`

## 7. Relaciones

El registry debe poder expresar relaciones entre capacidades:

- capability A usa capability B
- capability A reemplaza capability B
- capability A requiere capability B
- capability A es compatible con capability B
- capability A entra en conflicto con capability B

## 8. Query model

El orquestador debe poder consultar:

### 8.1 Por objetivo

“¿Qué capability resuelve mejor esta tarea?”

### 8.2 Por restricciones

“¿Qué capability funciona con dry-run, sin write, y con baja latencia?”

### 8.3 Por contexto

“¿Qué capability es válida para este niche, brain y phase?”

### 8.4 Por recuperación

“¿Qué capability sirve para retry, rollback o replan?”

## 9. Policy coupling

El selector de harnesses debe usar el registry junto con policies, no de forma aislada.

Ejemplos:

- una capability puede existir pero estar deshabilitada por policy
- una capability puede estar activa pero no permitida en cierto scope
- una capability puede requerir checker separado

## 10. Memory coupling

El registry debe poder escribir y leer:

- learning events
- usage history
- adoption decisions
- deprecation reasons

## 11. Source coupling

Cada capability debe poder rastrearse a una fuente:

- repo externo
- decisión interna
- doc canónico
- issue / PR / commit

## 12. MCP coupling

MCP no es un detalle de integración: es una categoría de capability.

Por seguridad:

- el registry debe distinguir tools de lectura y escritura
- el registry debe declarar constraints de autenticación
- el registry debe ser consultado antes de exponer una tool al modelo

## 13. Selección mínima suficiente

La selección debe priorizar:

1. simplicidad
2. seguridad
3. verificabilidad
4. reuso
5. costo de tokens

## 14. No-goals

- no convertir el registry en un mega-config opaco
- no exponer almacenamiento crudo como capability
- no usar capability sin metadata de riesgo
- no permitir selección sin policy check

## 15. Relación con los otros docs

- `63-MASTERMIND-CORE-ARCHITECTURE.md`
- `64-HARNESS-LIBRARY-AND-LOOP-TAXONOMY.md`
- `65-MEMORY-AND-CONTEXT-ARCHITECTURE.md`
- `66-SOURCE-REGISTRY-AND-DELTA-PROTOCOL.md`
- `67-HARNESS-SELECTION-POLICY.md`
