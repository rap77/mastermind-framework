# Domain-Aware Security Assurance Plane

## Índice

1. Estado canónico
2. Propósito
3. Decisión central
4. Modelo de tres capas
5. Arquitectura
6. Security Profile
7. Integración con Gap Registry
8. Security Assurance Loop
9. Gates en onboarding
10. Readiness veto
11. Risk treatment y aceptación
12. Software overlay
13. Marketing overlay
14. Finance overlay
15. Evidencia y verificación
16. Fuentes, jurisdicción y vigencia
17. Persistencia y auditabilidad
18. Integración con runtime
19. Criterios de aceptación
20. Estado de implementación
21. Referencias

## 1. Estado canónico

- **Estado de decisión:** aprobado
- **Estado de diseño:** canonizado
- **Estado de planificación:** ejecutado en `.planning/changes/domain-security-assurance-plane/`
- **Estado de implementación:** implementado y validado como plane reusable
- **Policy ID:** `policy-security-assurance`
- **Verification runtime ID:** `security-assurance`
- **Objective slug:** `domain-security-assurance-plane`

## 2. Propósito

Aplicar seguridad como constraint transversal, adaptada al dominio, jurisdicción,
datos, actores y amenazas reales de cada proyecto.

La capa debe impedir que un proyecto funcional sea declarado ready cuando
mantiene riesgos bloqueantes sin tratamiento ni aprobación.

## 3. Decisión central

> Seguridad se consolida como policy + domain profile + independent verifier.
> No es una checklist genérica, una skill única ni una etapa final opcional.

Policy define obligaciones. Domain profile contextualiza. Verifier exige
evidencia y controla readiness.

## 4. Modelo de tres capas

```text
SecurityProfile
= Global Security Baseline
+ Domain Security Overlay
+ Project Security Constraints
+ Jurisdiction
+ Data Classification
+ Threat Model
```

### Global baseline

Reglas mínimas aplicables a todos los casos: secrets, access control, data
handling, auditability, least privilege, safe failure y supply chain cuando
corresponde.

### Domain overlay

Amenazas, controles, evidencias y approvals propios de software, marketing,
finanzas u otro nicho.

### Project context

Activos reales, usuarios, boundaries, proveedores, jurisdicciones, excepciones
y risk appetite aprobado.

## 5. Arquitectura

```text
Doctrine Projection
  -> Security Profile Builder
  -> Asset and Data Classifier
  -> Threat Model
  -> Security Gap Lens
  -> Control Mapping
  -> Evidence Verifier
  -> Residual Risk Assessment
  -> Security Readiness Verdict
  -> Risk Acceptance / Remediation / Block
```

Composición prevista:

```yaml
policies:
  - policy-security-assurance
supporting_harnesses:
  - security-assurance
conditional_harnesses:
  - security-remediation
  - recovery-fixer
```

## 6. Security Profile

Campos mínimos:

```yaml
security_profile_id: string
project_id: string
domain: string
jurisdictions: []
data_classes: []
critical_assets: []
actors: []
trust_boundaries: []
threat_categories: []
control_sets: []
approval_policy: string
risk_thresholds: {}
source_versions: []
```

El profile se versiona. Un cambio de dominio, jurisdicción, datos o exposición
invalida checks afectados y obliga a reevaluar.

## 7. Integración con Gap Registry

No se crea un backlog de seguridad separado. Los hallazgos se almacenan en el
Gap Registry universal con `lens: security`.

Campos adicionales:

- `threat`
- `asset_refs`
- `likelihood`
- `impact`
- `control_refs`
- `residual_risk`
- `treatment`
- `approval_required`
- `risk_acceptance_id`
- `review_at`

Ejemplo:

```yaml
gap_id: SEC-001
lens: security
domain: finance
category: transaction-authorization
threat: unauthorized-transaction
severity: critical
likelihood: medium
impact: critical
evidence_refs: []
control_refs: [FIN-AUTH-04]
status: open
blocking: true
treatment: mitigate
approval_required: true
```

## 8. Security Assurance Loop

| Pass | Lens | Output |
| --- | --- | --- |
| asset | activos, datos y actores | classified inventory |
| boundary | entradas, permisos y trust boundaries | attack surface map |
| threat | abuso, fraude, manipulación y pérdida | threat records |
| control | prevención, detección, respuesta y recovery | control matrix |
| evidence | prueba real de controles | evidence verdicts |
| residual risk | riesgo posterior al control | treatment decision |

Cada pass usa target requirements y fuentes versionadas. No inventa controles
por analogía débil.

## 9. Gates en onboarding

| Onboarding stage | Security gate |
| --- | --- |
| intake | sensitivity, domain y jurisdiction classified |
| evidence | secrets/PII/regulatory data handling validated |
| target | security outcomes and approvals defined |
| current state | assets and trust boundaries mapped |
| gap loop | security findings classified and owned |
| wave planning | policies attached to delegated work |
| verification | control evidence evaluated |
| readiness | veto and risk acceptance applied |
| handoff | residual risk and review dates persisted |

Security puede detener cualquier stage aplicable.

## 10. Readiness veto

Reglas mínimas:

- critical abierto -> `blocked`
- high abierto -> `blocked` salvo excepción autorizada por policy
- medium -> risk acceptance con owner, expiry y compensating controls
- low -> backlog con owner y review date
- unknown sobre activo sensible -> `escalated`
- check no ejecutado -> no cuenta como compliant

Security readiness no se promedia con product, delivery o quality readiness.

## 11. Risk treatment y aceptación

Tratamientos:

- `mitigate`
- `avoid`
- `transfer`
- `accept`
- `escalate`

`RiskAcceptanceRecord` requiere:

- `risk_id`
- `decision`
- `rationale`
- `owner`
- `scope`
- `approved_by`
- `approved_at`
- `expires_at`
- `compensating_controls`
- `evidence_refs`

Sin expiry no existe aceptación permanente. Al vencer, el gap reabre.

## 12. Software overlay

Dimensiones:

- authentication y authorization
- input validation e injection
- secrets y credential management
- data encryption y retention
- dependency/supply chain
- network e infrastructure exposure
- logging, alerting y incident response
- availability y recovery
- CI/CD integrity
- privacy y misuse cases

El baseline AI-DLC puede alimentar este overlay, pero sus reglas deben quedar
versionadas y verificadas antes de adopción.

## 13. Marketing overlay

Dimensiones:

- PII y customer data
- consent y tracking
- ad platform permissions
- account takeover
- phishing y brand impersonation
- asset provenance
- pixels, scripts y third parties
- provider data sharing
- regulatory claims
- social account continuity

Brand safety y reputational abuse son riesgos de seguridad del dominio.

## 14. Finance overlay

Dimensiones:

- transaction authorization
- segregation of duties
- fraud detection
- data and ledger integrity
- reconciliation
- model risk
- credential and account security
- privacy
- audit trail
- regulatory retention
- incident response
- business continuity

KYC, AML u otras obligaciones se activan por actividad y jurisdicción. Requieren
fuentes regulatorias vigentes y human legal/compliance approval.

## 15. Evidencia y verificación

Cada control registra:

- `control_id`
- `applicability`
- `expected_evidence`
- `observed_evidence`
- `verification_method`
- `performed_at`
- `verifier`
- `passed`
- `limitations`
- `source_version`

La prosa persuasiva no reemplaza evidencia. Un control documentado pero no
implementado se marca `planned`, no `passed`.

## 16. Fuentes, jurisdicción y vigencia

Reglas de dominio o regulatorias deben usar Source Registry:

- source authority
- jurisdiction
- effective date
- snapshot/version
- review cadence
- superseded status

Si una fuente está vencida o contradictoria, el verifier escala y no inventa
una interpretación legal.

## 17. Persistencia y auditabilidad

Persistir:

- SecurityProfile versions
- asset/data classifications
- threat records
- security gaps
- control matrix
- evidence verdicts
- risk acceptances
- exceptions y expiries
- security readiness history
- remediation lineage

Secrets, credentials y raw sensitive payloads nunca se persisten como evidence.

## 18. Integración con runtime

Extender:

- DoctrineProjection para domain/project security profiles
- Capability Registry para policy/verifier/remediation capabilities
- MultiHarness selection para security requirements
- Gap Registry schema para security fields
- VerificationEnvelope para control evidence
- Recovery para security-specific stop conditions
- project state para risk and evidence history

El verifier debe ser independiente del maker cuando el riesgo es high/critical.

## 19. Criterios de aceptación

- todo onboarding recibe un SecurityProfile aplicable
- domain overlays cambian checks sin cambiar el core
- security gaps viven en el Gap Registry universal
- critical/high findings controlan readiness
- risk acceptance requiere owner, approval y expiry
- checks no ejecutados no aprueban
- fuentes regulatorias tienen version y jurisdiction
- evidence excluye secrets y payloads sensibles
- software, marketing y finance routing cases pasan
- project state conserva historial auditable

## 20. Estado de implementación

### Implementado y validado

- `SecurityProfile` versionado con composición determinista y excepciones
  aprobadas explícitas
- registry de overlays para software, marketing y finance con controles distintos
- resolución fail-closed de fuentes versionadas, jurisdicción, vigencia y
  contradicciones
- security findings en el Gap Registry universal con referencias seguras
- assurance loop de seis passes, rubrics distintas y límites de iteración
- control evidence verifier donde missing, skipped, inconclusive y unperformed no
  aprueban
- readiness veto para critical/high y lifecycle de aceptación humana con expiry
- persistencia de historial, checkpoints y remediation lineage sin payloads
  sensibles
- contratos exportados para consumo por otros harnesses y runtimes

### Evidencia de cierre

- 58 tests del dominio security pasan en la suite declarada de SAP7
- 32 tests de regresión del generic harness pasan, incluyendo selector,
  composición, behavioral routing y compatibilidad legacy explícita
- software, marketing y finance resuelven respectivamente controles de auth/input/
  supply chain, consent/customer data/third-party scripts y transaction auth/
  segregation of duties/ledger integrity
- critical y high aplican veto; evidence no ejecutada o no aprobatoria bloquea
- el contract check de `domain-security-assurance-plane` pasa

### Integración downstream

- El attachment automático del profile a cada onboarding run se completa en
  `adaptive-onboarding-harness-runtime`; esta plane entrega los contratos y el
  runtime reusable, pero no declara esa integración downstream como evidencia
  ya ejecutada.
- El routing automático de remediación específica continúa como integración de
  harness posterior; el verifier no ejecuta remediaciones por diseño.

## 21. Referencias

- `.aidlc-rule-details/extensions/security/baseline/security-baseline.md`
- `docs/canonical/22-ENGINEERING-DOCTRINE-LAYER.md`
- `docs/canonical/67-HARNESS-SELECTION-POLICY.md`
- `docs/canonical/71-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/80-GAP-DETECTION-AND-CLARIFICATION-LOOP.md`
- `docs/canonical/111-ADAPTIVE-ONBOARDING-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/decision-records/DR-011-SECURITY-AS-CROSS-CUTTING-ASSURANCE-PLANE.md`
- `.planning/changes/domain-security-assurance-plane/`

## Key Learnings:

1. Policy define obligaciones; profile contextualiza; verifier demuestra.
2. Security readiness tiene veto y no se promedia.
3. Regulación y dominio se agregan como overlays versionados, no prompts fijos.
