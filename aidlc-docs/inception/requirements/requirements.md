# Requirements — Multi-Harness Architecture

## Intent Analysis Summary

- **User request**: ejecutar la fase de inception para el módulo Multi-Harness Architecture usando `Product-Definition/` como fuente primaria.
- **Request type**: new feature / architectural enhancement sobre sistema brownfield.
- **Scope estimate**: múltiples componentes.
- **Complexity estimate**: compleja.
- **Requirements depth**: comprehensive.

## Problem Statement

MasterMind necesita evolucionar desde slices aislados de governance, budget y
memory eval hacia un **núcleo multi-harness y multi-loop** que:

- opere agnósticamente al modelo/harness sin perder continuidad
- preserve memoria y contexto útil entre sesiones y cambios de proveedor
- seleccione el mínimo control suficiente según complejidad y riesgo
- verifique resultados con evidencia ejecutable, no solo con texto persuasivo
- siente los fundamentos para el target state tipo ECC sin inflar prematuramente
  la superficie del sistema

## Functional Requirements

### FR-1 — Governance interceptor previo al Coordinator
- El sistema debe interceptar intenciones antes de `Coordinator.orchestrate()`.
- El interceptor debe emitir un veredicto `allow`, `deny` o `pause_and_ask`.
- El interceptor no debe requerir cambios en los callers existentes de `Coordinator.orchestrate()`.
- El interceptor debe registrar evidencia de cada decisión.

### FR-2 — Policy gate SAL determinístico
- Debe bloquear operaciones destructivas fuera de scope.
- Debe bloquear writes a producción sin dry-run y aprobación explícita.
- Debe bloquear pushes/merges/releases a `main/master` sin aprobación.
- Debe bloquear exposición de secretos.
- Debe pausar cambios grandes o sensibles para aprobación.

### FR-3 — Budget enforcement por tarea y sesión
- Debe soportar tiers `conservative`, `standard`, `generous`.
- El tier default es `standard` con 100K por tarea y 500K por sesión.
- Debe emitir warning al 80% del presupuesto por tarea.
- Debe pedir aprobación al 100% del presupuesto por tarea.
- Debe detener limpiamente la sesión al 100% del presupuesto de sesión.
- Debe denegar tool calls individuales que proyecten >2x el budget por tarea.

### FR-4 — Persistencia durable de consumo y evidencia
- El consumo de tokens y las decisiones de governance deben sobrevivir reinicios.
- El formato MVP para budget tracking y evidence chain será append-only JSON Lines.
- Debe ser parseable para morning reports y meta-loop.
- La migración objetivo futura es PostgreSQL como runtime store primario.

### FR-5 — Memory Eval Harness v1
- Debe medir retrieval quality con métricas como recall@k y MRR.
- Debe comenzar con corpus estable: `docs/canonical/ + docs/design/ + root docs`.
- Debe mantener qrels sellados.
- El primer set de qrels debe priorizar decisiones, fixes, temporal correctness y estado de componente.
- La integración inicial del scorer debe ser un script standalone en CI.

### FR-6 — Overnight Mode cauteloso
- Debe ejecutar una tarea por vez.
- Debe escribir checkpoint después de cada tarea.
- Debe reevaluar presupuesto, fallos recientes, backend disponible y necesidad de aprobación antes de continuar.
- Debe pausar tras 2-3 fallos consecutivos o al cruzar límites de costo/riesgo.
- Debe generar morning report y checkpoint de reanudación.

### FR-7 — Meta-loop controlado
- Debe ejecutar chequeo ligero post-sesión y análisis estructural semanal.
- Debe poder proponer reglas nuevas a partir de patrones de fallo.
- Debe auto-aplicar solo reglas menores, determinísticas, reversibles y cubiertas por regression tests.
- Debe requerir aprobación humana para reglas de ejecución, costo, scope, seguridad o governance.

### FR-8 — Registration/backward compatibility
- `Coordinator` debe aceptar governance por constructor con default `None`.
- Debe poder deshabilitarse en tests.
- Debe permitir componer múltiples policies en orden definido.

### FR-9 — Overnight resume protocol
- Siempre debe persistir checkpoint de overnight.
- Debe generar morning report.
- No debe reintentar automáticamente tareas conocidas como fallidas sin revisión humana.

### FR-10 — Rust boundary
- El primer release del harness debe vivir en Python.
- Rust solo se considerará para gates determinísticos que demuestren ser bottleneck real o enforcement crítico de runtime.

### FR-11 — Multi-harness core explícito
- El sistema debe modelar explícitamente harnesses especializados, al menos:
  - Orchestrator
  - Context & Memory
  - Execution
  - Verification
  - Review
  - Recovery
  - Observability & Audit
- Cada harness debe tener responsabilidades, inputs, outputs y límites claros.
- El sistema no debe depender de un “super agente” monolítico para todas las labores.

### FR-12 — Multi-loop explícito
- El sistema debe soportar múltiples loops de control, al menos:
  - Tool Loop
  - Goal Loop
  - Verification Loop
  - Reflection Loop
  - Recovery Loop
  - Review Loop
  - Heartbeat Loop
- El loop no debe ser fijo para toda tarea.
- Cada loop debe declarar:
  - criterio de validación
  - criterio de aceptación
  - criterio de finalización
  - criterio de escalación

### FR-13 — Loop selection policy
- El sistema debe seleccionar el loop mínimo suficiente según complejidad,
  riesgo y verificabilidad de la tarea.
- Tareas simples y determinísticas no deben entrar en loops complejos.
- Tareas complejas o de alto riesgo deben poder componer múltiples loops.

### FR-14 — Envelope contract único
- Todo harness o fase relevante debe devolver un envelope tipado con al menos:
  - status
  - summary
  - artifacts
  - risks
  - next_actions
  - verification
  - recovery
- El orquestador no debe depender de prosa libre para decidir el siguiente paso.

### FR-15 — Maker-checker split
- El agente/harness que implementa no debe ser el único verificador de su propio resultado.
- El sistema debe separar producción de artefacto y validación final al menos
  para cambios medianos, grandes o de riesgo elevado.
- Debe existir un camino formal para review adversarial o fresh-context review.

### FR-16 — Capability registry
- El sistema debe mantener un inventario consultable de capacidades:
  harnesses, loops, brains, skills, MCPs, commands, verificadores y políticas
  de recovery.
- Cada capability debe incluir metadatos de uso, costo, riesgo,
  prerequisitos y compatibilidad.
- El registro debe permitir selección dinámica por objetivo y constraints de la tarea.

### FR-17 — Continuidad cross-model / cross-harness
- El sistema debe poder continuar trabajo cuando un modelo o backend se quede
  sin créditos, presupuesto o disponibilidad.
- La continuidad debe apoyarse en checkpoint, memory y estado exportable, no en
  chat memory volátil.
- Debe preservar suficiente contexto para retomar sin redescubrir decisiones clave.

### FR-18 — Foundations for learning loop
- El sistema debe capturar observaciones estructuradas de ejecución, fallos,
  fixes y outcomes para habilitar aprendizaje futuro.
- La primera etapa de aprendizaje debe ser read-only o gated.
- La promoción automática de reglas o cambios de comportamiento debe permanecer
  fuera del primer slice.

## Resolved Open Questions

| Open Question | Decision |
|---|---|
| OQ-1 SAL Gate pattern | **Middleware/interceptor class** separada, inyectada antes del Coordinator |
| OQ-2 Budget persistence | **JSON Lines append-only** para MVP; migración futura a PostgreSQL |
| OQ-3 Meta-loop trigger | **Hybrid**: post-sesión ligero + análisis estructural semanal |
| OQ-4 Qrel generation | **Semi-automatizado + validación humana** |
| OQ-5 Eval scorer integration | **Standalone script** separado de pytest regular |
| OQ-6 Governance registration | **Constructor injection** con defaults backward-compatible |
| OQ-7 Evidence chain format | **JSON Lines append-only**; migración futura a PostgreSQL |
| OQ-8 Overnight resume | **Checkpoint + morning report + review humana** |

## Non-Functional Requirements

### NFR-1 — Determinismo
- Las decisiones de policy gate deben ser código, no prompts LLM.

### NFR-2 — Bajo overhead
- Governance + budget enforcement no debe consumir >5% del budget total de una tarea.

### NFR-3 — Auditabilidad
- Toda decisión de governance y budget debe ser trazable y replayable.

### NFR-4 — Continuidad
- Otro modelo/backend debe poder retomar desde checkpoint sin depender de chat memory.

### NFR-5 — Seguridad
- Debe haber interceptación del 100% de acciones de alto riesgo.

### NFR-6 — Testabilidad
- Cada policy debe poder testearse en aislamiento.
- El eval harness debe producir scorecards JSON comparables en CI.

### NFR-7 — Evolutividad
- La arquitectura debe permitir extraer piezas a Rust o a servicios separados si la medición futura lo justifica.

### NFR-8 — Observabilidad estructurada
- Los estados de ejecución, verificación, recovery y continuidad deben ser
  reconstruibles a partir de artifacts persistidos.

### NFR-9 — Progressive disclosure
- El sistema debe limitar carga de contexto innecesaria y recuperar solo lo
  relevante para la tarea actual.

### NFR-10 — Control bounded
- Todo loop debe tener límites explícitos de iteraciones, costo, tiempo o tool interactions.

## Success Criteria

- Recall@5 del eval harness >= 0.80 en baseline inicial.
- Reducción de token waste de al menos 30% frente al baseline sin budget enforcement.
- 0 incidentes por acciones destructivas en overnight cautious mode.
- 100% de acciones de alto riesgo interceptadas por governance.
- Paquetes de evaluación que bloqueen degradaciones en CI.
- Recuperación sin pérdida de continuidad cuando un backend/modelo quede indisponible.
- Selección consistente del loop mínimo suficiente en tareas simples, medias y complejas.

## Out of Scope for This Slice

- runtime eval online
- multi-backend scheduler completo con z.ai/OpenRouter operativos
- migración temprana de policy gates a Rust
- corpus inicial con planning/audit/handoffs ruidosos
- OS completo estilo ECC con HUD, billing, marketplace o paridad cross-harness total
- auto-promoción write-enabled de nuevas reglas o skills

## Key Architectural Implications

- La inserción natural del governance harness es el borde de `Coordinator`.
- La primera persistencia debe ser simple, durable y legible.
- El eval harness se valida mejor sobre corpus estable antes de incorporar artefactos operacionales volátiles.
- Multi-harness y multi-loop deben modelarse explícitamente en diseño, no solo
  como comportamiento implícito del orquestador.
- El capability registry debe convertirse en una fuente de verdad para
  selección dinámica de herramientas y procesos.
