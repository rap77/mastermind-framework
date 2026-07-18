# DR-010 — Adaptive Onboarding Core and Domain Adapters

## 1. Decision Metadata

- **Decision ID:** DR-010
- **Date:** 2026-07-14
- **Status:** Approved
- **Related project:** MasterMind
- **Related capability:** Project Adoption and Completion
- **Related objective:** `adaptive-onboarding-harness-runtime`

## 2. Problem Statement

Un onboarding limitado a ideas de software no puede adoptar repositorios
existentes, rescatar proyectos incompletos, auditar proyectos terminados ni
operar iniciativas de marketing, finanzas y otros nichos.

## 3. Options Considered

### Option A — Un harness diferente por dominio

- **Benefits:** cada workflow puede optimizarse localmente
- **Risks:** duplica intake, gap tracking, readiness, persistence y recovery
- **Rejected:** escala por copia, no por composición

### Option B — Un onboarding universal monolítico

- **Benefits:** un solo entrypoint
- **Risks:** acumula reglas incompatibles y context bloat
- **Rejected:** mezcla core con conocimiento de nicho

### Option C — Core universal más domain adapters

- **Benefits:** contracts estables, especialización sin duplicación, reuso de
  gaps/readiness/delegation
- **Risks:** requiere un adapter registry y contracts estrictos
- **Selected:** separa invariantes universales de reglas de dominio

## 4. Final Decision

MasterMind implementará `project-adoption-lead` como supervisor universal. El
core reconciliará current state, target state, gaps, execution waves y readiness.
Los dominios aportarán evidence types, policies, dimensions y harnesses mediante
adapters.

AI-DLC Discovery y MM-flow Discovery constituirán el primer Software Onboarding
Adapter. Es distinto del `software-delivery` adapter, que ejecuta producción y
verificación después del onboarding.
Marketing y Finanzas se agregarán después de validar el core.

## 5. Consequences

- onboarding puede procesar greenfield, brownfield, completion, rescue y audit
- el core delega ejecución; no se convierte en executor universal
- Gap Registry y readiness son compartidos entre nichos
- cada adapter puede evolucionar sin modificar el supervisor
- seguridad se integra mediante una assurance plane transversal

## 6. Reversal Conditions

Revisar si:

- los dominios no pueden compartir current/target/gap/readiness contracts
- el overhead de adapters supera el reuse demostrado
- el runtime multi-harness cambia su unidad de composición

## 7. Links / Artifacts

- `docs/canonical/111-ADAPTIVE-ONBOARDING-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/112-DOMAIN-AWARE-SECURITY-ASSURANCE-PLANE.md`
- `.planning/changes/adaptive-onboarding-harness-runtime/`

## Key Learnings:

1. El invariante universal es reconciliar current state con target state.
2. Terminar un proyecto requiere delegación y reassessment, no un agente gigante.
3. Los nichos escalan como adapters versionados.
