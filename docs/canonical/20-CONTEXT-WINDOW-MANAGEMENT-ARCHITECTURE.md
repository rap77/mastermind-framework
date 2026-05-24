# Context Window Management Architecture

## 1. Propósito

Definir cómo MasterMind debe manejar las diferencias de ventana de contexto entre modelos, cuentas y proveedores para evitar degradación de calidad, pérdida de continuidad y fallos evitables durante la orquestación.

---

## 2. Problema real

Los modelos no solo difieren en calidad, costo o disponibilidad. También difieren en:

- ventana máxima de contexto
- cantidad útil real antes de degradarse
- capacidad de output
- tolerancia a instrucciones largas
- rendimiento con historiales extensos

Eso afecta directamente:

- qué backend es elegible para una tarea
- cuándo conviene resumir
- cuándo conviene hacer checkpoint
- cuándo conviene cambiar de backend
- cómo debe empaquetarse el contexto antes de reanudar trabajo

---

## 3. Principio rector

> La ventana de contexto no debe tratarse como un detalle incidental del modelo, sino como una restricción operativa de primer nivel del runtime.

---

## 4. Decisión conceptual

MasterMind debe introducir una capacidad de **Context Budget Management** en el core runtime.

Esta capacidad debe trabajar junto al Window Scheduler y no separada de él.

---

## 5. Qué debe resolver

### A. Model Capability Awareness

Saber para cada backend:

- context window máxima teórica
- output window estimada
- budget operativo recomendado
- comportamiento con contextos largos

### B. Task Context Sizing

Estimar cuánto contexto necesita una tarea.

### C. Context Packing

Decidir qué entra realmente al prompt/runtime payload.

### D. Context Compression

Resumir o destilar historial cuando ya no cabe completo.

### E. Context-Safe Switching

Al cambiar de backend, adaptar el contexto al budget del backend entrante.

---

## 6. Componentes principales

### A. Model Capability Registry

Debe extender el Provider Registry con campos como:

- `max_context_window`
- `recommended_working_window`
- `max_output_window`
- `long_context_quality`
- `compression_preference`

### B. Context Budget Estimator

Estima para una tarea:

- contexto mínimo necesario
- contexto ideal
- contexto opcional
- output esperado

### C. Context Packager

Construye el payload de contexto en capas:

1. system / doctrine
2. task objective
3. current checkpoint
4. mandatory artifacts
5. relevant memory
6. optional history

### D. Context Compressor

Cuando el contexto excede el budget disponible, genera:

- summaries
- distilled state
- key decisions
- unresolved questions
- artifact references

### E. Context Fit Evaluator

Evalúa si el backend actual o candidato puede manejar la carga de contexto de forma segura.

### F. Resume Context Builder

Al retomar en otro backend, reconstruye un contexto mínimo viable para continuidad.

---

## 7. Regla clave de elegibilidad

La elegibilidad de un backend no depende solo de:

- disponibilidad
- costo
- riesgo

También depende de:

- **fitness de contexto**

### Nueva regla

> Un backend disponible pero sin capacidad razonable para cargar el contexto necesario no debe considerarse elegible sin compresión o replanificación explícita.

---

## 8. Niveles de contexto

### Nivel 1 — Core Required Context

Lo mínimo sin lo cual la tarea no puede continuar.

Ejemplos:

- objetivo actual
- checkpoint
- constraints activas
- siguiente paso

### Nivel 2 — Decision-Critical Context

Contexto importante para evitar errores de juicio.

Ejemplos:

- decisiones previas
- objeciones pendientes
- riesgos abiertos

### Nivel 3 — Supporting Context

Ayuda, pero no es indispensable.

Ejemplos:

- historial largo
- discusiones previas extensas
- referencias menos inmediatas

### Nivel 4 — Nice-to-Have Context

Contexto valioso solo si sobra budget.

---

## 9. Estrategia de packing

El runtime debería aplicar este orden:

1. incluir contexto núcleo
2. incluir decisiones críticas
3. incluir artefactos obligatorios
4. incluir memoria relevante
5. incluir historial opcional solo si queda budget

---

## 10. Estrategias de compresión

### A. Summarization by Layer

Resumir historial por capas:

- decisiones tomadas
- estado actual
- riesgos abiertos
- próximos pasos

### B. Artifact-First Retrieval

En vez de arrastrar todo el historial, referenciar artefactos canónicos.

### C. Brain-Specific Compression

Cada brain puede necesitar distinta compresión.

### D. Switch-Time Rehydration

Cuando cambia el backend, reconstruir el contexto para el budget nuevo en lugar de copiar el contexto previo tal cual.

---

## 11. Relación con el Window Scheduler

El Window Scheduler debe consultar Context Budget Management antes de cada switch.

### Antes de pasar de backend A a backend B, debe responder:

- ¿cabe el contexto actual en B?
- ¿cabe solo después de compresión?
- ¿qué partes deben priorizarse?
- ¿el costo cognitivo de compresión hace inviable el switch?

---

## 12. Estados útiles de contexto

### `fits_cleanly`
El contexto cabe sin cambios relevantes.

### `fits_with_compression`
Cabe si se resume o reordena.

### `unsafe_fit`
Cabe técnicamente pero con demasiado riesgo de degradación.

### `does_not_fit`
No cabe razonablemente.

---

## 13. Impacto en el flujo de trabajo

Las ventanas de contexto pueden influir en el workflow de varias maneras:

### Caso 1
Una tarea compleja requiere dividirse antes de continuar.

### Caso 2
Un backend más barato está disponible, pero no tiene budget suficiente.

### Caso 3
El sistema debe crear un checkpoint más fuerte antes del switch.

### Caso 4
El sistema debe transformar historial en estado estructurado reutilizable.

---

## 14. Guardrails

- no cambiar a un backend que requiera compresión destructiva para una tarea crítica
- no arrastrar historial completo por costumbre
- no confundir longitud máxima teórica con longitud útil real
- si la compresión reduce demasiado contexto crítico, pausar y escalar

---

## 15. Data model mínimo sugerido

```yaml
model_context_profile:
  backend_id: "codex-sub-01"
  max_context_window: 200000
  recommended_working_window: 120000
  max_output_window: 32000
  long_context_quality: "medium"
  compression_preference: "artifact_first"
```

```yaml
context_budget_estimate:
  task_id: "task-finance-f2-refinement"
  core_required_tokens: 12000
  decision_critical_tokens: 8000
  supporting_tokens: 14000
  nice_to_have_tokens: 20000
  expected_output_tokens: 6000
```

```yaml
context_fit_assessment:
  backend_id: "zai-sub-01"
  fit_state: "fits_with_compression"
  compression_required: true
  risk_level: "medium"
  recommended_strategy: "summarize_history_keep_decisions"
```

---

## 16. Decisiones canónicas sugeridas

### Decisión 1
La capacidad de contexto es parte de la elegibilidad de backend.

### Decisión 2
La continuidad entre backends requiere reempaquetado inteligente, no simple copiado de historial.

### Decisión 3
El runtime debe priorizar artefactos y estado estructurado por encima de transcript bruto.

### Decisión 4
La compresión debe ser trazable y revisable en tareas críticas.

---

## 17. Relación con otros artefactos

- `16-WINDOW-SCHEDULER-ARCHITECTURE.md`
- `17-EXECUTION-MODES-POLICY.md`
- `19-WINDOW-SCHEDULER-DATA-SCHEMA.md`
- `14-MINIMAL-MEMORY-RULES.md`
- `15-MINIMAL-ORCHESTRATION-PATH.md`

---

## 18. Próximos artefactos recomendados

1. `DR-004-CONTEXT-BUDGET-STRATEGY.md`
2. `21-CONTEXT-PACKING-POLICY.md`
3. `22-BACKEND-CAPABILITY-PROFILE-SCHEMA.md`

## Key Learnings:

1. Las ventanas de contexto influyen directamente en elegibilidad, switching y continuidad de tareas.
2. El runtime necesita gestionar budget de contexto como una restricción de primer nivel, no como detalle del modelo.
3. El cambio entre backends debe implicar reempaquetado y compresión inteligente del contexto, no arrastre ciego de historial.
