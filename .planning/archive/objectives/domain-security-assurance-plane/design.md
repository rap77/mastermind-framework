# Design — domain-security-assurance-plane

## Architecture / Boundaries

```text
DoctrineProjection
  -> SecurityProfileBuilder
  -> DomainOverlayRegistry
  -> AssetDataClassifier
  -> SecurityGapAnalyzer
  -> ControlEvidenceVerifier
  -> SecurityReadinessPolicy
  -> RiskAcceptanceService
  -> Persistence and lineage
```

- builder compone requirements; no verifica controles
- verifier observa evidence; no acepta riesgo
- risk acceptance exige authority humana
- domain adapter declara overlay; no cambia baseline
- project state persiste metadata, no secrets

## Technical Approach

### Profile composition

Precedencia:

```text
global baseline
< domain overlay
< jurisdiction overlay
< project constraints
< approved exception
```

Conflictos que reducen seguridad requieren approval explícito.

### Gap integration

Extender el gap contract con `lens`, threat, impact, likelihood, controls,
residual risk, treatment, approval y review date.

### Verification

Separar applicability, expected evidence, observed evidence y verdict. N/A debe
tener razón; skipped no equivale a compliant.

### Risk acceptance

Lifecycle:

```text
proposed -> approved -> active -> expired -> reopened
```

### Domain overlays

Implementar schemas y fixtures mínimos para software, marketing y finance. No
codificar regulación detallada hasta conectar Source Registry.

## Dependencies

- `engineering-doctrine-layer`
- `artifact-versioning-and-lineage`
- `docs/canonical/112-DOMAIN-AWARE-SECURITY-ASSURANCE-PLANE.md`
- existing capability, verification, recovery and project-state primitives

## Validation Strategy

- unit tests para profile composition, gaps, verifier y risk acceptance
- behavioral cases por dominio y severity
- integration test profile -> finding -> verdict -> persistence
- regression de capability/harness selection
- ruff y type checking aplicable, sin build

## Important Tradeoffs

- overlays mínimos prueban arquitectura sin fingir compliance exhaustivo
- un Gap Registry evita duplicación, pero requiere schema extensible
- veto aumenta fricción, pero evita readiness falso
- evidence externalizada reduce exposición de datos sensibles

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| checklist genérica | high | domain overlays + threat context |
| stale regulation | critical | source version and review cadence |
| false pass | critical | unperformed != compliant |
| permanent exceptions | high | mandatory expiry and reopen |
| sensitive evidence leakage | critical | redaction and reference-only storage |

## Context Notes

- Objective implementation complete; SAP7 validation evidence is green.
- It is a prerequisite for `adaptive-onboarding-harness-runtime`.
- The plane exposes reusable contracts and persistence; automatic attachment to
  every onboarding run remains a downstream integration concern.
