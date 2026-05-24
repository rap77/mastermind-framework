# DR-005 — Model Access Through Backend Services

## 1. Decision Metadata

- **Decision ID:** DR-005
- **Date:** 2026-05-23
- **Status:** Approved
- **Related project:** MasterMind
- **Related niche:** Runtime / Project State / Governance
- **Related phase / workflow:** MVP Implementation Boundary

## 2. Problem Statement

MasterMind necesita decidir cómo los modelos y agentes accederán al estado del proyecto, registros operativos y artefactos persistidos en Postgres.

La decisión clave es si deben:

- acceder directamente a la base de datos
- usar MCP como acceso libre a datos
- o interactuar mediante una capa backend con servicios y tools semánticas

## 3. Decision Type

- [x] Architecture
- [x] Runtime / LLM Ops
- [x] Governance / Control

## 4. Why This Decision Is Needed

Sin esta decisión:

- los agentes podrían saltarse reglas de negocio
- se vuelve más difícil imponer audit trail consistente
- aumenta el riesgo de corrupción de estado
- se debilitan permisos, validaciones y gates

## 5. Options Considered

### Option A — Direct model/database access

- **Description:** permitir que modelos o tools emitan queries o mutaciones directas a la BD.
- **Benefits:** flexibilidad, prototipado rápido
- **Risks:** inseguro, difícil de auditar, alto riesgo de inconsistencias

### Option B — MCP as direct data bridge

- **Description:** exponer herramientas MCP cercanas al almacenamiento, con poco dominio de negocio en el medio.
- **Benefits:** simple para agentes, rápido para integración
- **Risks:** bypass parcial del workflow, validaciones débiles, acoplamiento alto

### Option C — Backend services as authority, MCP as semantic interface

- **Description:** el backend controla la lógica, validaciones y persistencia; los modelos acceden mediante capacidades semánticas, opcionalmente expuestas por MCP.
- **Benefits:** consistencia, auditabilidad, permisos claros, extensibilidad
- **Risks:** más diseño upfront

## 6. Participating Brains

- Platform Architecture Brain
- Agent Runtime & LLM Ops Brain
- Governance & Safety Brain
- Product Operations Brain

## 7. Positions by Brain

### Platform Architecture Brain

- **Position:** Strongly favors Option C
- **Main argument:** el backend debe ser la autoridad del estado y el boundary estable del sistema
- **Confidence:** High
- **Main concern:** acceso directo a datos rompería Core + Project Adapter y degradaría mantenibilidad

### Agent Runtime & LLM Ops Brain

- **Position:** Favors Option C
- **Main argument:** los modelos necesitan tools semánticas, no acceso arbitrario a tablas
- **Confidence:** High
- **Main concern:** exponer operaciones demasiado cercanas a SQL haría al runtime frágil y difícil de gobernar

### Governance & Safety Brain

- **Position:** Strongly favors Option C
- **Main argument:** permisos, gates, excepciones y auditoría requieren una capa central de validación
- **Confidence:** High
- **Main concern:** acceso libre a BD o a un MCP demasiado bajo nivel sería un bypass de governance

### Product Operations Brain

- **Position:** Supports Option C
- **Main argument:** tools semánticas hacen el sistema más usable y predecible para humanos y agentes
- **Confidence:** High
- **Main concern:** el diseño de tools debe ser lo bastante expresivo para no empujar a workarounds inseguros

## 8. Objections / Cross-Critique

- Governance rechazó Option A como incompatible con auditabilidad seria.
- Runtime rechazó Option B si MCP se convierte en pseudo-SQL encubierto.
- Platform Architecture pidió separar claramente almacenamiento, servicios y tools.

## 9. Missing Evidence / Open Gaps

- Aún no existe un catálogo inicial de backend services.
- Falta definir el contract realtime/WebSocket.
- Falta plan de implementación backend inicial.

## 10. Final Decision

- **Selected option:** Option C
- **Decision owner:** Platform Architecture Brain
- **Decision rationale:** el backend será la autoridad del estado, validación y auditoría; los modelos accederán mediante capacidades semánticas, preferiblemente expuestas por services y opcionalmente entregadas vía MCP.

## 11. Veto / Conditional Approval

- **Was there a veto?** No
- **Who could veto?** Governance & Safety Brain, Evaluator
- **Conditions before action:**
  1. no exponer operaciones tipo `run_sql`
  2. definir boundary explícito de backend services
  3. asegurar que tools escriban siempre a través del backend

## 12. Action Gates

- Gate 1: documento de service boundary para agentes
- Gate 2: contract de eventos realtime
- Gate 3: plan inicial de implementación backend

## 13. Action Taken

- **Action status:** Approved for canonical implementation
- **Action description:** MasterMind adopta backend services como camino principal para acceso de modelos al estado del proyecto. MCP, si se usa, actuará como interfaz de tools semánticas y no como bypass de la base de datos.

## 14. Reversal Conditions

Revisar esta decisión si:

- el backend se vuelve excesivamente rígido para la productividad de agentes
- aparecen casos legítimos donde una tool directa de bajo nivel sea más segura o verificable
- la capa semántica resulta demasiado pobre para operar el sistema

## 15. Learning Capture

- **Observation:** los modelos trabajan mejor con tools semánticas que con acceso crudo a datos.
- **Pattern:** autoridad de estado, validación y auditoría deben vivir juntas.
- **Heuristic candidate:** si una tool suena como SQL o row mutation genérica, probablemente está en el nivel incorrecto.

## 16. Links / Artifacts

- `docs/canonical/21-PROJECT-STATE-OPERATIONAL-MEMORY-ARCHITECTURE.md`
- `docs/canonical/27-POSTGRES-HYBRID-DATA-MODEL.md`
- `docs/canonical/32-INITIAL-API-SURFACE.md`

## Key Learnings:

1. Los modelos no deben acceder directamente a la BD del core.
2. MCP sí sirve, pero como interfaz de tools semánticas sobre servicios backend.
3. La autoridad de estado, validación y auditoría debe permanecer en el backend.
