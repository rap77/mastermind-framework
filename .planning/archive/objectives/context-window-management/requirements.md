# Requirements — context-window-management

## Problem / Purpose
El Window Scheduler ya clasifica el fit de una carga declarada, pero no posee un
presupuesto de contexto por capas ni puede construir un payload seguro para un
backend candidato. Como resultado, un switch puede basarse en capacidad,
disponibilidad y policy sin demostrar que el contexto requerido sobreviva al
cambio.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Modelar un presupuesto de contexto por niveles: core required,
  decision-critical, supporting y nice-to-have, más output esperado.
- Validar el fit contra el perfil de capacidad del backend existente.
- Empaquetar contexto en orden de prioridad sin descartar niveles críticos en
  silencio.
- Exigir compresión explícita o bloquear/escalar cuando el backend candidato no
  pueda conservar el contexto necesario.
- Integrar el resultado de fit/packing en la decisión de switch del Window
  Scheduler sin reemplazar sus políticas de disponibilidad o riesgo.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- No provider-specific tokenizer integration ni estimación remota de tokens.
- No compresión generativa real: este objective produce una decisión y payload
  estructurado; el productor de summaries queda detrás de una capacidad futura.
- No cambio automático de backend cuando el fit sea unsafe o requiera pérdida de
  contexto crítico.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.
- Core required y decision-critical nunca se eliminan para hacer caber un
  payload; si no caben, el resultado es bloqueado o requiere compresión
  explícita.
- La elegibilidad por context fit se compone con las políticas existentes; no
  las reemplaza ni las promedia.
- Los switches deben conservar checkpoint, objetivo y siguiente paso mediante
  referencias estructuradas, no history completo por defecto.

## Functional Requirements
- [ ] El runtime representa perfil de capacidad, presupuesto por capas y output
  esperado con contratos tipados e inmutables.
- [ ] El packager prioriza core, decisiones, artefactos obligatorios, memoria y
  luego historial opcional de forma determinística.
- [ ] Un fit `does_not_fit` o `unsafe_fit` no habilita un switch automático sin
  una estrategia explícita de compresión, replanificación o escalación.
- [ ] El scheduler puede evaluar candidatos con el presupuesto de la tarea antes
  de seleccionar un backend.

## Quality Requirements
- Determinismo para el mismo perfil, presupuesto y conjunto de segmentos.
- Validación de límites negativos, segmentos duplicados y referencias vacías en
  el boundary.
- Tests unitarios para fit, packing, compresión requerida y rechazo de pérdida
  crítica; tests de integración para switch seguro.

## Objective-level Acceptance Criteria
- [ ] Un perfil y presupuesto tipados producen un verdict de fit coherente con
  los cuatro estados canónicos.
- [ ] El payload empaquetado conserva siempre core/decision-critical y explica
  cualquier compresión u omisión opcional.
- [ ] Un candidato sin capacidad suficiente no se selecciona automáticamente.
- [ ] Los flujos existentes de Window Scheduler continúan verdes.
