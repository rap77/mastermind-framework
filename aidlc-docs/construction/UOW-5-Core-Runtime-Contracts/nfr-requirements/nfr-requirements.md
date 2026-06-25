# NFR Requirements — UOW-5 Core Runtime Contracts

## Purpose

Definir las cualidades operativas mínimas que debe cumplir el núcleo de
contratos runtime para que MasterMind pueda operar con multi-harness y
multi-loop sin perder determinismo, continuidad ni control de costo/riesgo.

## 1. Performance

### NFR-P5.1 — Selección barata
- La construcción de `TaskProfile`, la resolución de capabilities y la
  selección de loop deben agregar overhead pequeño y estable frente a la tarea
  ejecutada.
- El slice inicial no debe requerir llamadas remotas para seleccionar loops o
  capacidades.

### NFR-P5.2 — Costo fijo acotado
- Tareas simples no deben pagar el costo de un runtime complejo innecesario.
- La selección debe preferir el camino de menor overhead compatible con el
  nivel de riesgo y verificabilidad.

### NFR-P5.3 — Decisión predecible
- La complejidad temporal de selección debe crecer linealmente con el número de
- harnesses/capabilities registradas en el MVP.
- El release inicial debe mantener un inventario pequeño, explícito y
  testeable.

## 2. Security

### NFR-S5.1 — Control bounded obligatorio
- Todo loop debe tener límites explícitos de iteraciones, tiempo, costo o tool
  interactions.
- No pueden existir loops abiertos por default.

### NFR-S5.2 — Sin autoaprobación riesgosa
- Cambios no triviales o de alto riesgo no deben autoaprobarse por el mismo
  actor que los ejecuta.
- El sistema debe poder exigir verificación y/o review independiente.

### NFR-S5.3 — Continuidad sin fuga
- El envelope, task profile y artifacts persistidos deben preservar contexto
  suficiente para retomar trabajo sin incluir secretos innecesarios.

## 3. Availability and Continuity

### NFR-A5.1 — Continuidad cross-session
- `TaskProfile`, `ExecutionEnvelope` y artifacts asociados deben permitir que
  otra sesión, modelo o backend retome el trabajo con mínima pérdida de
  contexto útil.

### NFR-A5.2 — Continuidad cross-model/backend
- El slice inicial debe diseñarse para soportar cambio de backend/modelo sin
  redescubrir decisiones críticas.
- La continuidad debe depender de estado persistido, no de transcript vivo.

### NFR-A5.3 — Degradación segura
- Si el `CapabilityRegistry` o alguna capability no puede resolverse con
  seguridad, la selección debe degradar a un camino más conservador o detenerse,
  no a uno más permisivo.

## 4. Reliability and Determinism

### NFR-R5.1 — Selección determinista
- Dado el mismo `TaskProfile`, el mismo inventario y la misma configuración, la
  selección de loops/harnesses debe ser idéntica.

### NFR-R5.2 — Envelope estable
- El `ExecutionEnvelope` debe tener shape estable desde el MVP para evitar que
  cada caller/harness invente su propio contrato.

### NFR-R5.3 — Recovery bounded
- La recuperación debe seguir una escalera fija:
  1. retry
  2. patch
  3. replan
  4. escalate/stop
- El sistema debe detectar no-progreso y evitar repetir la misma estrategia
  fallida indefinidamente.

## 5. Maintainability and Testability

### NFR-M5.1 — Registro tipado y extensible
- `HarnessRegistry` y `CapabilityRegistry` deben ser extensibles sin reescribir
  el `Coordinator`.
- Agregar una capability nueva no debe requerir cambiar la semántica de las ya
  existentes.

### NFR-M5.2 — Testabilidad aislada
- Deben existir tests unitarios para:
  - clasificación de `TaskProfile`
  - selección de `LoopPolicy`
  - validación del `ExecutionEnvelope`
  - decisiones de `RecoveryHarness`

### NFR-M5.3 — Integración incremental
- El primer slice debe integrarse sin romper governance, budget ni memory eval
  ya existentes.
- La adopción debe ser gradual: primero contrato + selección, luego verificación,
  review y recovery más ricos.

## 6. Operability

### NFR-O5.1 — Razones explicables
- La selección de loop/harness debe dejar evidencia suficiente para explicar
  por qué se eligió ese camino.

### NFR-O5.2 — Payloads observables
- Los envelopes deben poder resumirse para status, checkpoints y handoffs sin
  parseo ambiguo.

### NFR-O5.3 — Inventario útil
- El `CapabilityRegistry` debe servir para selección real, no solo para
  documentación o inspección manual.

## 7. Success Thresholds for UOW-5

- El sistema clasifica consistentemente tareas simples/medias/complejas en los
  tests del MVP.
- El loop selector elige el camino mínimo suficiente sin introducir loops
  complejos en tareas simples.
- Todos los outcomes relevantes pueden expresarse mediante `ExecutionEnvelope`.
- Cambios no triviales pueden exigir maker-checker o verification independiente
  sin rediseñar el caller.
