# DR-011 — Security as a Cross-Cutting Assurance Plane

## 1. Decision Metadata

- **Decision ID:** DR-011
- **Date:** 2026-07-14
- **Status:** Approved
- **Related project:** MasterMind
- **Related capability:** Security, Risk and Readiness
- **Related objective:** `domain-security-assurance-plane`

## 2. Problem Statement

Una policy genérica de seguridad no cubre amenazas, controles, evidencia,
jurisdicciones ni risk acceptance de software, marketing, finanzas y futuros
dominios. Una checklist final tampoco puede bloquear stages anteriores.

## 3. Options Considered

### Option A — Skill única de seguridad

- **Benefits:** fácil de invocar
- **Risks:** mezcla policy, domain knowledge y verification
- **Rejected:** no ofrece independencia ni auditabilidad suficiente

### Option B — Seguridad dentro de cada adapter

- **Benefits:** máxima especialización
- **Risks:** reglas globales duplicadas y readiness inconsistente
- **Rejected:** fragmenta governance

### Option C — Assurance plane transversal con overlays

- **Benefits:** baseline uniforme, especialización por dominio y verifier separado
- **Risks:** requiere SecurityProfile y evidence contracts
- **Selected:** preserva veto global sin perder contexto de nicho

## 4. Final Decision

MasterMind separará:

- `policy-security-assurance` para obligaciones
- `SecurityProfile` para dominio, proyecto y jurisdicción
- `security-assurance` para verificación independiente

Los hallazgos vivirán en el Gap Registry universal con `lens: security`.
Critical/high findings podrán bloquear readiness. Risk acceptance requerirá
owner, aprobación, evidencia y expiry.

## 5. Consequences

- seguridad aplica en cada stage relevante
- checks no ejecutados no cuentan como compliant
- reglas regulatorias requieren fuentes versionadas
- software, marketing y finance agregan overlays sin fork del core
- security remediation se delega a harnesses especializados

## 6. Reversal Conditions

Revisar si:

- una regulación exige aislamiento físico/lógico por dominio
- el Gap Registry no puede representar risk lifecycle adecuadamente
- un verifier externo obligatorio reemplaza el contrato interno

## 7. Links / Artifacts

- `docs/canonical/112-DOMAIN-AWARE-SECURITY-ASSURANCE-PLANE.md`
- `docs/canonical/111-ADAPTIVE-ONBOARDING-HARNESS-RUNTIME-CONTRACT.md`
- `.planning/changes/domain-security-assurance-plane/`

## Key Learnings:

1. Security policy, domain context y evidence verification son responsabilidades distintas.
2. Readiness de seguridad tiene veto y no se promedia.
3. Risk acceptance sin expiry se convierte en deuda invisible permanente.
