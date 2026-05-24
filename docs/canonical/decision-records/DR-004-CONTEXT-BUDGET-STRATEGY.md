# DR-004 — Context Budget Strategy

## 1. Decision Metadata

- **Decision ID:** DR-004
- **Date:** 2026-05-23
- **Status:** Approved
- **Related project:** MasterMind
- **Related niche:** Runtime / Multi-LLM / Continuity
- **Related phase / workflow:** MVP Runtime Strategy

## 2. Problem Statement

MasterMind quiere operar entre múltiples modelos y proveedores, pero cada backend tiene capacidades distintas de ventana de contexto y desempeño bajo contextos largos.

Sin una estrategia explícita, el sistema puede:

- elegir backends técnicamente disponibles pero contextualmente inadecuados
- perder continuidad al cambiar de modelo
- degradar calidad por contextos sobredimensionados
- sobrecargar prompts con historial bruto innecesario

## 3. Decision Type

- [x] Runtime / LLM Ops
- [x] Architecture
- [x] Continuity / Memory

## 4. Why This Decision Is Needed

La estrategia multi-backend ya no depende solo de ventanas de suscripción. También depende de capacidad de contexto y de cómo se empaqueta el trabajo al cambiar entre modelos.

## 5. Options Considered

### Option A — Treat context window as implementation detail

- **Description:** manejar límites de contexto ad hoc dentro de cada integración.
- **Benefits:** menos diseño upfront
- **Risks:** inconsistencia, errores de continuidad, decisiones pobres de switching

### Option B — Introduce first-class Context Budget Management

- **Description:** tratar el budget de contexto como capacidad central del runtime, ligada a elegibilidad, compresión y reanudación.
- **Benefits:** switching más seguro, mejor continuidad, mejor uso multi-modelo
- **Risks:** más complejidad de diseño inicial

### Option C — Force all tasks into ultra-small context packets always

- **Description:** diseñar todo el sistema para contexto mínimo extremo sin distinguir tareas ni modelos.
- **Benefits:** simplicidad aparente
- **Risks:** pérdida de riqueza de contexto y peor juicio en tareas complejas

## 6. Participating Brains

- Agent Runtime & LLM Ops Brain
- Platform Architecture Brain
- Knowledge Distillation Brain
- Governance & Safety Brain

## 7. Positions by Brain

### Agent Runtime & LLM Ops Brain

- **Position:** Strongly favors Option B
- **Main argument:** la elegibilidad real de backend depende de budget de contexto, no solo de disponibilidad
- **Confidence:** High
- **Main concern:** switching sin context fit assessment romperá continuidad

### Platform Architecture Brain

- **Position:** Supports Option B
- **Main argument:** esto debe vivir en core, junto al scheduler, no disperso en adapters
- **Confidence:** High
- **Main concern:** no duplicar lógica de packing en muchos lugares

### Knowledge Distillation Brain

- **Position:** Supports Option B
- **Main argument:** el sistema ya está orientado a artefactos y estado estructurado; eso favorece compresión inteligente
- **Confidence:** High
- **Main concern:** la compresión no debe borrar decisiones críticas ni doctrina relevante

### Governance & Safety Brain

- **Position:** Supports Option B with controls
- **Main argument:** si la compresión es agresiva y no trazable, puede introducir errores silenciosos
- **Confidence:** High
- **Main concern:** tareas críticas deben poder pausar si el contexto no cabe sin degradación peligrosa

## 8. Objections / Cross-Critique

- Runtime rechazó Option A por convertir un constraint central en lógica incidental.
- Governance objetó cualquier compresión no trazable en tareas sensibles.
- Distillation objetó tratar transcript bruto como mecanismo primario de continuidad.

## 9. Missing Evidence / Open Gaps

- No existe todavía una packing policy formal.
- No existe aún schema formal de capability profiles por backend.
- Falta definir heurísticas de “unsafe fit”.

## 10. Final Decision

- **Selected option:** Option B
- **Decision owner:** Agent Runtime & LLM Ops Brain
- **Decision rationale:** MasterMind debe tratar el contexto como presupuesto operativo de primer nivel, con evaluación de fit, compresión controlada y reempaquetado al cambiar de backend.

## 11. Veto / Conditional Approval

- **Was there a veto?** No
- **Who could veto?** Governance & Safety Brain, Evaluator
- **Conditions before action:**
  1. definir arquitectura de manejo de contexto
  2. definir política de packing
  3. no permitir switches críticos con context fit inseguro sin escalación

## 12. Action Gates

- Gate 1: documento de arquitectura de context budget
- Gate 2: policy de packing y compresión
- Gate 3: schema de capability profile por backend

## 13. Action Taken

- **Action status:** Partially operationalized
- **Action description:** Se adopta Context Budget Management como capacidad del core runtime y se crea la arquitectura canónica inicial.

## 14. Reversal Conditions

Revisar esta decisión si:

- el costo de packing/compression supera consistentemente su beneficio
- los modelos convergen a ventanas suficientemente homogéneas
- los adapters reales no muestran sensibilidad fuerte a context windows

## 15. Learning Capture

- **Observation:** la continuidad entre modelos depende más de contexto bien estructurado que de transcript bruto.
- **Pattern:** disponibilidad sin context fit no equivale a backend realmente utilizable.
- **Heuristic candidate:** si una tarea no puede conservar objetivo, decisiones críticas y siguiente paso dentro del budget, el switch debe tratarse como inseguro.

## 16. Links / Artifacts

- `docs/canonical/20-CONTEXT-WINDOW-MANAGEMENT-ARCHITECTURE.md`
- `docs/canonical/16-WINDOW-SCHEDULER-ARCHITECTURE.md`
- `docs/canonical/19-WINDOW-SCHEDULER-DATA-SCHEMA.md`

## Key Learnings:

1. La capacidad real de un backend depende también de su fit de contexto.
2. El runtime debe preferir estado estructurado y artefactos antes que arrastre indiscriminado de historial.
3. La compresión de contexto debe ser controlada, trazable y sensible al riesgo de la tarea.
