# NFR Design Patterns — UOW-5 Core Runtime Contracts

## Purpose

Traducir los NFR de UOW-5 a patrones concretos de runtime para que el slice
`envelope-contract-loop-selector-v1` nazca estable, barato y verificable.

## 1. Deterministic Selection Pipeline

### Pattern
`TaskProfile -> Capability filtering -> Loop selection -> Harness composition`

### Applies To
- NFR-P5.1
- NFR-P5.2
- NFR-R5.1
- NFR-O5.1

### Design Effect
- La clasificación ocurre antes de ejecutar trabajo costoso.
- La selección usa reglas tipadas y orden estable.
- La decisión deja razones estructuradas para debugging y handoff.

## 2. Minimum Sufficient Control

### Pattern
Elegir siempre el loop menos costoso compatible con riesgo, verificabilidad y
subjetividad de la tarea.

### Applies To
- NFR-P5.2
- NFR-S5.1
- NFR-M5.3

### Design Effect
- Tareas simples quedan en `single-pass` o `execute+verify-light`.
- Tareas medias pueden activar `verification loop`.
- Tareas complejas/riesgosas pueden componer `review` y `recovery`.

## 3. Bounded Loop Contract

### Pattern
Todo loop declara límites explícitos de iteraciones, tiempo, herramientas y
criterios de salida.

### Applies To
- NFR-S5.1
- NFR-R5.3

### Design Effect
- No existen loops abiertos por default.
- Cada loop tiene criterios de validación, aceptación, finalización y
  escalación.
- Los callers pueden cortar ejecución por política, no por intuición.

## 4. Maker-Checker Separation

### Pattern
Separar ejecución de validación/review cuando el `TaskProfile` lo exige.

### Applies To
- NFR-S5.2
- NFR-M5.3

### Design Effect
- El mismo actor no se autoaprueba en trabajo no trivial.
- `requires_checker` puede activar `VerificationHarness` o `ReviewHarness`.
- La decisión de checker nace de policy, no del humor del modelo.

## 5. Stable Envelope Contract

### Pattern
Todo harness devuelve un `ExecutionEnvelope` con shape fijo.

### Applies To
- NFR-R5.2
- NFR-A5.1
- NFR-O5.2

### Design Effect
- El orquestador decide continuidad con campos estructurados.
- Status, verification y recovery se vuelven parseables y comparables.
- El mismo contrato sirve para checkpoints, handoffs y status.

## 6. Safe Degradation

### Pattern
Si faltan capabilities o hay clasificación incierta, degradar a una política
conservadora o detener.

### Applies To
- NFR-A5.3
- NFR-S5.3
- NFR-R5.1

### Design Effect
- Nunca se habilita un camino más permisivo por ausencia de datos.
- El sistema puede caer a un harness básico con review obligatorio.
- Si el riesgo sigue incierto, se escala o se detiene.

## 7. Bounded Recovery Ladder

### Pattern
`retry -> patch -> replan -> escalate/stop`

### Applies To
- NFR-R5.3
- NFR-M5.2

### Design Effect
- Recovery no improvisa estrategias.
- Se detecta no-progreso por clase de fallo + contador de intentos.
- La política puede actualizar el loop solo dentro de límites explícitos.

## 8. Persisted Continuity Boundary

### Pattern
Persistir `TaskProfile`, `LoopPolicy`, `ExecutionEnvelope` y referencias de
artifact como frontera de continuidad.

### Applies To
- NFR-A5.1
- NFR-A5.2
- NFR-S5.3

### Design Effect
- Otra sesión/backend puede retomar sin transcript completo.
- El runtime depende de estado persistido y resumible.
- Se evita fuga de secretos manteniendo solo contexto necesario.

## 9. Typed Capability Registry

### Pattern
Inventario tipado y filtrable por objetivo, costo, riesgo y compatibilidad.

### Applies To
- NFR-M5.1
- NFR-O5.3
- NFR-P5.3

### Design Effect
- El inventario deja de ser ornamental.
- La selección puede excluir tools/harnesses incompatibles.
- Nuevas capabilities se agregan sin reescribir el `Coordinator`.

## 10. Incremental Runtime Adoption

### Pattern
Introducir primero contrato + selector + filtros; luego verification/review/
recovery más ricos.

### Applies To
- NFR-M5.3
- NFR-P5.1

### Design Effect
- El rollout no rompe governance, budget ni memory eval.
- El primer valor llega sin paridad ECC completa.
- El slice queda listo para crecer por adapters.
