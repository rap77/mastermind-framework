# Business Rules — UOW-5 Core Runtime Contracts

## Rule Group 1 — Task Profiling

### BR-5.1
Toda tarea debe derivar un `TaskProfile` antes de seleccionar loops o
capabilities.

### BR-5.2
Si la tarea no puede clasificarse con seguridad, el sistema debe degradar a una
política más conservadora, no a la más laxa.

## Rule Group 2 — Loop Selection

### BR-5.3
El sistema debe usar el **mínimo control suficiente** para resolver la tarea.

### BR-5.4
Tareas simples y determinísticas no deben entrar en graph/review/recovery loops
innecesarios.

### BR-5.5
Tareas complejas, riesgosas o no totalmente predecibles pueden componer
múltiples loops.

### BR-5.6
Todo loop debe declarar criterios de:
- validación
- aceptación
- finalización
- escalación

## Rule Group 3 — Maker-Checker

### BR-5.7
El mismo actor/harness que implementa no debe ser el único que se autoaprueba
en cambios no triviales.

### BR-5.8
Si la tarea es mediana, grande, riesgosa o tiene impacto sistémico, debe poder
activarse `ReviewLoop` o `VerificationLoop` independiente.

## Rule Group 4 — Envelope Contract

### BR-5.9
Todo harness/fase relevante debe devolver `ExecutionEnvelope`.

### BR-5.10
Un envelope sin `status` o sin información de `verification`/`recovery` cuando
aplique debe considerarse inválido.

### BR-5.11
El orquestador no debe depender de resúmenes narrativos para decidir continuidad.

## Rule Group 5 — Capability Registry

### BR-5.12
Toda capability registrada debe tener metadatos mínimos de:
- categoría
- objetivo
- costo relativo
- riesgo relativo
- prerequisitos
- compatibilidad

### BR-5.13
El registro debe permitir excluir capabilities incompatibles con el task
profile o el harness activo.

### BR-5.14
El registro no debe convertirse en un inventario ornamental; debe ser consumido
por la selección real.

## Rule Group 6 — Recovery

### BR-5.15
Todo recovery debe seguir una escalera bounded:
1. retry local
2. patch local
3. replan
4. escalate/stop

### BR-5.16
No se debe repetir indefinidamente la misma estrategia fallida.

### BR-5.17
Si no hay progreso observable, el sistema debe escalar o detenerse.

## Rule Group 7 — Continuity

### BR-5.18
La continuidad cross-model/backend debe apoyarse en artifacts persistidos y no
en chat memory volátil.

### BR-5.19
El envelope y el task profile deben contener suficiente estado para retomar una
tarea sin redescubrir decisiones críticas.

## Rule Group 8 — Bounded Control

### BR-5.20
Cada loop debe tener límites explícitos de iteraciones, tiempo, costo o tool
interactions.

### BR-5.21
Las tareas de baja complejidad no deben pagar el costo fijo de loops complejos
salvo evidencia clara de necesidad.
