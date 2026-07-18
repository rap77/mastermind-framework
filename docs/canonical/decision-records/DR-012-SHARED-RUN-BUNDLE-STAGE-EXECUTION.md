# DR-012 — Shared RunBundle Stage Execution

## 1. Decision Metadata

- **Decision ID:** DR-012
- **Date:** 2026-07-14
- **Status:** Approved
- **Related project:** MasterMind
- **Related capability:** Harness Runtime Execution
- **Related objective:** `harness-stage-execution-runtime`

## 2. Problem Statement

El runtime selecciona, compone y valida RunBundles, pero el coordinator no usa
ese bundle para gobernar stages reales. UI/UX, onboarding y delivery planifican
control flow similar y podrían terminar implementando executors incompatibles.

## 3. Options Considered

### Option A — Executor dentro de cada harness

- **Benefits:** optimización local inmediata
- **Risks:** duplica gates, checkpoint, evidence, resume y recovery
- **Rejected:** genera tres runtimes con semántica operacional divergente

### Option B — Coordinator interpreta prosa de HARNESS.md

- **Benefits:** cambio inicial pequeño
- **Risks:** no determinístico, no tipado y difícil de auditar
- **Rejected:** el bundle seguiría sin ser un contrato ejecutable

### Option C — Foundation compartida de stage execution

- **Benefits:** control uniforme, bundle gobernante, reuse y evidencia comparable
- **Risks:** requiere stage contracts y una migration path compatible
- **Selected:** comparte mecanismos sin mezclar semántica de dominio

## 4. Final Decision

MasterMind implementará `run-bundle-stage-executor` como foundation única. Los
harnesses declararán stage graphs, capabilities, gates y policies. El executor
controlará orden, transiciones, evidence, approvals, checkpoints, recovery y
safe replanning.

`review` se agregará como package type distinto de `verification`.

## 5. Consequences

- UI/UX, onboarding y delivery dependerán del mismo runtime
- `HarnessRunExecutor` deberá pasar el bundle validado al executor/coordinator
- los manifests requerirán stage metadata versionada
- legacy runs necesitarán una ruta compatible explícita
- domain logic no podrá filtrarse dentro del executor

## 6. Reversal Conditions

Revisar si:

- el estándar Agent Harnesses incorpora un runtime incompatible obligatorio
- dos consumidores demuestran semánticas de control irreconciliables
- el costo del graph contract supera reuse y auditabilidad medidos

## 7. Links / Artifacts

- `docs/canonical/113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`
- `docs/canonical/103-MULTI-HARNESS-COMPOSITION-AND-AGENT-HARNESSES-COMPLIANCE.md`
- `.planning/changes/harness-stage-execution-runtime/`

## Key Learnings:

1. Un bundle validado que no gobierna ejecución es sólo packaging.
2. Control flow compartido y domain semantics deben permanecer separados.
3. Review, verification y approval no son sinónimos.
