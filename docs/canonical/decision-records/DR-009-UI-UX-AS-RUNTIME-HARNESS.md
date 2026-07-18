# DR-009 — UI/UX as a Runtime Harness

## 1. Decision Metadata

- **Decision ID:** DR-009
- **Date:** 2026-07-14
- **Status:** Approved
- **Related project:** MasterMind
- **Related niche:** UI/UX, Frontend, Multi-Harness Runtime
- **Related objective:** `ui-ux-harness-runtime`

## 2. Problem Statement

MasterMind necesita coordinar diseño, prototipado, implementación frontend,
accesibilidad, motion y validación runtime. Instalar skills no define cuándo se
ejecutan, en qué orden, qué gates aplican ni cómo se persiste la evidencia.

## 3. Decision Type

- [x] Architecture
- [x] Runtime orchestration
- [x] Capability routing
- [x] Quality policy

## 4. Options Considered

### Option A — Mantener sólo skills auto-activadas

- **Benefits:** mínimo esfuerzo
- **Risks:** routing implícito, sin stages, gates, recovery ni auditabilidad
- **Rejected:** no satisface el Harness Runtime Contract

### Option B — Crear una metodología UI/UX separada

- **Benefits:** lifecycle propio completo
- **Risks:** duplica planning, estado y metodología principal
- **Rejected:** fragmenta la fuente de verdad

### Option C — Registrar UI/UX como Role Harness del runtime principal

- **Benefits:** selección determinista, composición con verification/recovery,
  reuse de project state y continuidad
- **Risks:** requiere cerrar bundle-to-execution wiring y resolver skills externas
- **Selected:** preserva una sola arquitectura de control

## 5. Final Decision

MasterMind implementará `ui-ux-delivery` como Role Harness seleccionado por
`ObjectiveProfile`. Usará `ui-ux-verifier` y `recovery-fixer` como supporting
harnesses cuando corresponda.

Las skills externas son capacidades atómicas. No son el harness y no pueden
reemplazar sus stages ni gates.

## 6. Consequences

- `.mm-flow/harness-library/` será la fuente de verdad runtime.
- `.opencode/skills/ui-ux-routing/` será sólo un adapter interactivo.
- producción UI requerirá evidencia renderizada cuando las herramientas estén
  disponibles.
- el runtime deberá resolver skills instaladas con source path y content hash.
- no se declarará completado hasta que el RunBundle gobierne ejecución real.

## 7. Reversal Conditions

Revisar esta decisión si:

- el runtime multi-harness es reemplazado por otro contrato canónico
- Agent Harnesses deja de ser el formato de composición
- UI/UX requiere un servicio aislado por razones de seguridad o infraestructura

## 8. Links / Artifacts

- `docs/canonical/110-UI-UX-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/71-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/103-MULTI-HARNESS-COMPOSITION-AND-AGENT-HARNESSES-COMPLIANCE.md`
- `.planning/changes/ui-ux-harness-runtime/`

## Key Learnings:

1. Auto-activar skills no equivale a ejecutar un harness.
2. UI/UX debe usar el mismo selector, envelope y memory contract del proyecto.
3. La evidencia runtime forma parte del deliverable, no es una mejora opcional.
