# DR-003 — Backend Switch Audit Minimums

## 1. Decision Metadata

- **Decision ID:** DR-003
- **Date:** 2026-05-23
- **Status:** Approved
- **Related project:** MasterMind
- **Related niche:** Runtime / Governance / Auditability
- **Related phase / workflow:** MVP Runtime Strategy

## 2. Problem Statement

Después de aprobar la estrategia de failover entre suscripciones y definir la arquitectura del Window Scheduler, MasterMind necesita fijar qué evidencia mínima debe existir cada vez que el sistema cambia de backend.

Sin un mínimo auditable por switch, la automatización nocturna pierde confiabilidad humana y dificulta:

- reconstruir qué pasó
- revisar decisiones automáticas
- detectar errores de continuidad
- saber cuándo y por qué un backend se agotó

## 3. Decision Type

- [x] Governance / Control
- [x] Runtime / LLM Ops
- [x] Auditability

## 4. Why This Decision Is Needed

DR-002 dejó explícito que todo switch debe producir checkpoint y audit event, pero no definió el contenido mínimo.

Este record fija el estándar mínimo reusable del core.

## 5. Options Considered

### Option A — Minimal log line only

- **Description:** registrar solo backend anterior, backend siguiente y timestamp.
- **Benefits:** simple, barato
- **Risks:** insuficiente para reconstrucción, auditoría humana y reanudación confiable

### Option B — Structured switch audit with checkpoint reference

- **Description:** registrar un evento estructurado con contexto mínimo, causa, checkpoint, elegibilidad y estado de continuación.
- **Benefits:** trazabilidad útil, revisión humana viable, debugging mejorado
- **Risks:** algo más de complejidad y disciplina de implementación

### Option C — Full transcript per switch

- **Description:** guardar un volcado completo de toda la conversación/contexto en cada transición.
- **Benefits:** máxima información
- **Risks:** costoso, ruidoso, poco mantenible, puede duplicar contexto innecesariamente

## 6. Participating Brains

- Governance & Safety Brain
- Agent Runtime & LLM Ops Brain
- Product Operations Brain
- Platform Architecture Brain

## 7. Positions by Brain

### Governance & Safety Brain

- **Position:** Strongly favors Option B
- **Main argument:** debe existir trazabilidad suficiente sin caer en sobrecarga documental inútil
- **Confidence:** High
- **Main concern:** un log mínimo tipo línea plana no protege contra ambigüedad operacional

### Agent Runtime & LLM Ops Brain

- **Position:** Favors Option B
- **Main argument:** el scheduler necesita eventos estructurados para diagnosticar disponibilidad, continuidad y fallbacks
- **Confidence:** High
- **Main concern:** registrar demasiado contexto bruto por switch volvería costoso y confuso el sistema

### Product Operations Brain

- **Position:** Supports Option B
- **Main argument:** el operador humano necesita revisar mañana qué pasó sin leer ruido excesivo
- **Confidence:** High
- **Main concern:** un audit log incomprensible erosiona confianza en el modo automático

### Platform Architecture Brain

- **Position:** Supports Option B
- **Main argument:** el esquema debe vivir en el core como contrato estable entre runtime, memory y reporting
- **Confidence:** High
- **Main concern:** no mezclar event schema con detalles locales del Project Adapter

## 8. Objections / Cross-Critique

- Governance rechazó Option A por insuficiente para accountability.
- Runtime rechazó Option C por sobrecarga y duplicación innecesaria.
- Product Operations pidió que el evento tenga estructura legible por humanos y máquinas.

## 9. Missing Evidence / Open Gaps

- Aún no existe un schema formal serializable del evento.
- Aún no existe un morning report template canónico.

## 10. Final Decision

- **Selected option:** Option B
- **Decision owner:** Governance & Safety Brain
- **Decision rationale:** cada switch debe producir un evento estructurado suficiente para continuidad, auditoría y reporte, sin capturar transcripts completos innecesarios.

## 11. Veto / Conditional Approval

- **Was there a veto?** No
- **Who could veto?** Governance & Safety Brain, Evaluator
- **Conditions before action:**
  1. el evento debe referenciar un checkpoint existente
  2. el evento debe registrar causa del cambio
  3. el evento debe indicar decisión tomada: switch, pause, wait o fail

## 12. Action Gates

- Gate 1: definir campos mínimos del `backend_switch` event
- Gate 2: conectar el evento al morning report
- Gate 3: asegurar legibilidad humana y parseabilidad estructurada

## 13. Action Taken

- **Action status:** Approved for canonical use
- **Action description:** MasterMind adopta un estándar mínimo de auditoría por switch con evento estructurado y referencia obligatoria a checkpoint.

## 14. Minimum Required Fields

Todo evento `backend_switch` debe contener como mínimo:

- `event_id`
- `run_id`
- `project_id`
- `task_id` o referencia equivalente
- `from_backend`
- `to_backend`
- `reason`
- `checkpoint_id`
- `created_at`
- `execution_mode`
- `estimated_reset_at` del backend saliente, si aplica
- `decision_outcome` (`switched`, `paused`, `waiting`, `failed`)
- `eligibility_basis` breve del backend entrante
- `next_step_summary`

## 15. Human-Readable Audit Questions

El evento debe permitir responder:

- ¿qué backend se agotó o dejó de usarse?
- ¿a cuál se cambió?
- ¿por qué ocurrió el cambio?
- ¿qué checkpoint protege continuidad?
- ¿cuándo podría volver el backend saliente?
- ¿qué hará el sistema después?

## 16. Reversal Conditions

Revisar esta decisión si:

- el evento mínimo sigue siendo insuficiente para morning review
- el costo de logging se vuelve problemático
- aparecen requirements regulatorios más estrictos para algunos adapters

## 17. Learning Capture

- **Observation:** la auditabilidad útil depende de estructura mínima bien elegida, no de guardar todo.
- **Pattern:** checkpoint + switch event + morning report forman una cadena de confianza operacional.
- **Heuristic candidate:** si un humano no puede reconstruir el motivo y continuidad del cambio en menos de un minuto, el evento está mal diseñado.

## 18. Links / Artifacts

- `docs/canonical/decision-records/DR-002-SUBSCRIPTION-WINDOW-STRATEGY.md`
- `docs/canonical/16-WINDOW-SCHEDULER-ARCHITECTURE.md`
- `docs/canonical/17-EXECUTION-MODES-POLICY.md`

## Key Learnings:

1. No hace falta guardar transcripts completos por cada switch; hace falta un evento estructurado con los campos correctos.
2. El checkpoint y el audit event forman una unidad inseparable para continuidad y trazabilidad.
3. Un buen estándar de auditoría debe servir tanto a máquinas como a humanos en revisión matutina.
