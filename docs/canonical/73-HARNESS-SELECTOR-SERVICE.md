# Harness Selector Service

## 1. Propósito

Definir el servicio que decide qué harness y qué loop debe usar MasterMind para una tarea concreta.

## 2. Tesis central

> El selector no “elige por gusto”. Evalúa contexto, restricciones y costo para resolver con el menor control suficiente.

## 3. Responsabilidad

El servicio debe:

- interpretar el objetivo
- consultar el Capability Registry
- consultar la Memory Layer
- consultar el Source Registry cuando aplique
- aplicar policies de seguridad y scope
- seleccionar harness + loop
- devolver razones y alternativas descartadas

## 4. Inputs

Campos conceptuales:

- `request_id`
- `objective`
- `project_id`
- `phase_id`
- `brain_id`
- `scope`
- `risk_level`
- `token_budget`
- `approval_state`
- `context_refs`
- `source_refs`
- `memory_hints`
- `available_tools`
- `execution_mode`

## 5. Outputs

Campos conceptuales:

- `selected_harness`
- `selected_loop`
- `selected_brain`
- `reasons`
- `risks`
- `policy_checks`
- `memory_refs_used`
- `source_refs_used`
- `alternatives_rejected`
- `next_actions`
- `requires_review`
- `requires_mcp`

## 6. Decision pipeline

### Step 1 — Classify objective

Determinar si la tarea es:

- discovery
- research
- design
- implementation
- verification
- review
- recovery
- archive
- maintenance

### Step 2 — Check constraints

Revisar:

- scope
- risk
- budget
- approval
- write permissions
- need for fresh context
- need for MCP

### Step 3 — Query registry

Buscar capacidades compatibles por:

- kind
- state
- niche
- project scope
- loop compatibility
- cost
- risk
- checker requirements

### Step 4 — Query memory

Traer:

- precedentes
- decisiones previas
- preferencias relevantes
- lessons learned
- source summaries

### Step 5 — Query source registry

Si la tarea toca una fuente externa, traer:

- capabilities detectadas
- anti-patterns
- deltas recientes
- adoption decisions

### Step 6 — Rank candidates

Ordenar por:

- simplicidad
- seguridad
- verificabilidad
- costo de tokens
- reusabilidad
- compatibilidad con scope
- necesidad de checker

### Step 7 — Select minimum sufficient harness

Elegir la opción más simple que cumpla el objetivo.

### Step 8 — Emit selection envelope

Devolver razones, riesgos y alternativas descartadas.

## 7. Selection rules

- Si hay ambigüedad alta, preferir Discovery Harness.
- Si hay investigación externa, preferir Research Harness.
- Si hay arquitectura o contrato, preferir Design Harness.
- Si hay cambio de código, preferir Implementation Harness.
- Si hay riesgo alto, añadir Review Harness.
- Si hay fallo, activar Recovery Harness.
- Si el objetivo es trivial, usar Tool Loop o Maintenance Harness.
- Si el cambio requiere estructura end-to-end, AI-DLC Harness puede ganar.

## 8. Fallbacks

Si no hay suficiente información:

1. devolver `needs_discovery`
2. pedir más contexto
3. usar Discovery Harness

Si no hay capacidad compatible:

1. marcar `blocked`
2. explicar qué falta
3. recomendar el siguiente harness o acción

## 9. Policy integration

El selector no puede ignorar:

- approval policy
- write policy
- MCP policy
- risk policy
- scope policy

## 10. Memory integration

El selector debe poder reutilizar:

- decisiones previas
- patrones exitosos
- preferencias del usuario
- proyectos similares

## 11. Source integration

Cuando la tarea involucre fuentes externas, el selector debe poder consultar:

- snapshots
- deltas
- anti-patterns
- adoption decisions

## 12. Token minimization

El selector debe favorecer la decisión que minimice:

- prompts largos
- múltiples reintentos
- redescubrimiento
- context dumps

## 13. Observability

Cada selección debe registrar:

- harness elegido
- loop elegido
- razones
- alternativas descartadas
- tokens estimados
- outcome posterior

## 14. No-goals

- no seleccionar sin metadata
- no ocultar el motivo de la selección
- no usar siempre AI-DLC
- no usar review por defecto en cambios triviales
- no llamar a source registry si la tarea no toca fuentes externas

## 15. Relación con los demás docs

- `63-MASTERMIND-CORE-ARCHITECTURE.md`
- `64-HARNESS-LIBRARY-AND-LOOP-TAXONOMY.md`
- `65-MEMORY-AND-CONTEXT-ARCHITECTURE.md`
- `66-SOURCE-REGISTRY-AND-DELTA-PROTOCOL.md`
- `67-HARNESS-SELECTION-POLICY.md`
- `68-CAPABILITY-REGISTRY-SPEC.md`
- `69-CAPABILITY-REGISTRY-SCHEMA.md`
- `70-MEMORY-SCHEMA.md`
- `71-HARNESS-RUNTIME-CONTRACT.md`
