# Requirements — ui-ux-harness-runtime

## Problem / Purpose

MasterMind dispone de skills de diseño, un UI Design brain y primitives de
multi-harness, pero no tiene un harness UI/UX ejecutable. El runtime puede
seleccionar y validar un RunBundle, pero ese bundle todavía no gobierna la
ejecución del coordinator.

El objetivo es implementar `ui-ux-delivery` como Role Harness determinista para
planificación, prototipado, implementación y review de UI/UX, con verificación
runtime, recovery y persistencia de evidencia.

## Stakeholders / Users

- mantenedores de MasterMind
- agentes y modelos que implementan UI
- diseñadores y frontend engineers que consumen handoffs
- operadores que necesitan trazabilidad del run
- usuarios finales afectados por accesibilidad y usabilidad

## Scope

- clasificar objetivos UI/UX mediante `ObjectiveProfile`
- registrar `ui-ux-delivery` y `ui-ux-verifier`
- seleccionar capabilities por delivery mode
- resolver skills externas instaladas sin asumir paths únicos
- integrar los stages UI/UX con `run-bundle-stage-executor`
- implementar stages, gates, review y bounded recovery
- verificar UI productiva con evidencia runtime
- persistir envelope, artifacts, decisions y checkpoints
- cubrir routing positivo y negativo con behavioral cases

## Out of Scope

- rediseñar la UI actual de MasterMind
- crear un design system nuevo para el producto
- implementar un editor visual o reemplazar Figma
- copiar repos externos completos dentro del monorepo
- crear una metodología UI/UX independiente
- reemplazar Product Strategy, UX Research o Frontend Architecture
- agregar visual regression infrastructure si no existe una baseline confiable
- ejecutar builds durante este objective salvo cambio explícito de política

## Non-negotiables

- `ui-ux-delivery` debe ser un harness runtime, no una skill renombrada
- `.mm-flow/harness-library/` es la fuente de verdad del paquete ejecutable
- `.opencode/skills/ui-ux-routing/` es sólo un adapter interactivo
- el selector debe explicar por qué activó o rechazó el harness
- una palabra aislada no puede activar el harness
- producción UI requiere verificación runtime o limitación explícita
- checks no ejecutados no cuentan como aprobados
- skills requeridas ausentes deben producir failure explícito
- project policy y doctrine tienen precedencia sobre skills externas
- recovery debe ser bounded y observable
- UI/UX no implementa un stage executor paralelo
- ninguna credencial o secret puede persistirse en artifacts

## Functional Requirements

### FR1 — Objective classification

El runtime debe clasificar `domain`, `phase`, `output_type` y `delivery_mode`
para objetivos UI/UX sin romper clasificación software/product existente.

### FR2 — Deterministic selection

El selector debe elegir `ui-ux-delivery` para perfiles UI/UX válidos y
rechazarlo para objetivos backend, infraestructura o documentación incidental.

### FR3 — Delivery modes

Debe soportar:

- `design-system`
- `prototype`
- `production-implementation`
- `review`
- `motion-audit`

### FR4 — Conditional capabilities

El RunBundle debe contener sólo las capabilities requeridas por delivery mode.
No debe cargar todas las skills de diseño por defecto.

### FR5 — Installed skill resolution

El runtime debe resolver skills por ID canónico, path permitido, metadata y
content hash. Project overrides deben tener prioridad sobre globales.

### FR6 — Executable stages

El bundle seleccionado debe gobernar los stages del run y registrar transición,
resultado, evidencia y razón de skip.

### FR7 — UI verification

`production-implementation` debe verificar, cuando aplique:

- desktop y mobile
- keyboard y focus
- semantics y labels
- console errors
- loading, empty y error states
- overflow y contenido largo
- reduced motion

### FR8 — Review and recovery

El runtime debe ejecutar maker-checker según risk/subjectivity y decidir retry,
patch, replan, escalate o blocked ante fallos.

### FR9 — Structured output

El run debe emitir `ExecutionEnvelope` con stages, selected skills,
verification, review, recovery, artifacts, risks y next actions.

### FR10 — Persistence and resumption

El run debe escribir lineage, checkpoint y estado suficiente para reanudar sin
chat history.

## Quality Requirements

- selección pura y testeable
- orden de stages determinista
- no N+1 ni acceso DB directo desde skills
- type hints y docstrings en funciones públicas Python
- validación en boundaries de configuración y filesystem
- errores con causa y safe next action
- tests unitarios, behavioral routing e integración

## Objective-level Acceptance Criteria

- [ ] `ui-ux-delivery` y `ui-ux-verifier` son paquetes válidos del registry.
- [ ] UI/UX profiles seleccionan el harness correcto de forma determinista.
- [ ] Backend profiles no seleccionan capacidades UI/UX.
- [ ] Delivery modes materializan sólo las skills necesarias.
- [ ] Skills externas se resuelven con lineage o fallan explícitamente.
- [ ] El RunBundle gobierna ejecución de stages, no sólo composición.
- [ ] UI verification produce evidencia estructurada.
- [ ] Review y recovery son observables en el envelope.
- [ ] Estado y artifacts se persisten para reanudación.
- [ ] Tests específicos y regresiones del runtime pasan.
- [ ] Docs canónicos y handoff reflejan el estado real de implementación.
