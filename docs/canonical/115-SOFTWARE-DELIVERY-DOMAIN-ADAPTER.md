# Software Delivery Domain Adapter

## Índice

1. Estado canónico
2. Propósito
3. Baseline upstream
4. Decisión central
5. Alcance y límites
6. Mapping de contratos
7. Perfil AI-DLC Construction
8. Delivery units de software
9. Stage mapping
10. Planning y producción
11. Brownfield y greenfield
12. SDD, TDD y engineering doctrine
13. Build and Test con evidencia
14. Security assurance
15. Approval, state y audit
16. Session continuity y safe changes
17. Operations seam
18. Contrato de salida
19. Integración con MasterMind
20. Criterios de aceptación
21. Estado de implementación
22. Referencias

## 1. Estado canónico

- **Estado de la decisión:** aprobado
- **Estado del diseño:** canonizado
- **Estado de planificación:** planificado en `.planning/changes/software-delivery-domain-adapter/`
- **Estado de implementación:** no implementado
- **Adapter ID previsto:** `software-delivery`
- **AI-DLC profile ID previsto:** `aidlc-construction`
- **Objective slug:** `software-delivery-domain-adapter`

## 2. Propósito

Traducir el contrato universal de Adaptive Delivery a software delivery real,
preservando los invariantes valiosos de AI-DLC Construction y fortaleciendo su
verification contract.

## 3. Baseline upstream

Fuente evaluada:

- repository: `awslabs/aidlc-workflows`
- version: `1.0.1`
- commit: `d34bb7adfb4c58aa59bbb46494957f6169121b2b`
- fecha de evaluación: 2026-07-14

El lifecycle upstream contiene:

- Inception
- Construction
- Operations, actualmente placeholder

Construction procesa cada Unit of Work mediante stages condicionales de diseño,
Code Generation obligatorio y Build and Test global obligatorio.

## 4. Decisión central

> AI-DLC conserva ownership del macro lifecycle y delega Construction a
> Adaptive Delivery usando el Software Delivery Adapter. MM-flow conserva el
> control operacional, checkpoints y handoffs.

No se forkearán las reglas upstream dentro del core universal. El profile
`aidlc-construction` versiona el mapping y sus approval policies.

## 5. Alcance y límites

### Incluye

- greenfield y brownfield software delivery
- units, stories/requirements, contracts y dependencies
- functional, NFR y infrastructure concerns
- code/test/docs/deployment artifact production
- SDD/TDD selection
- build, tests e integration evidence
- software security overlay
- AI-DLC state, approvals, audit y continuity mapping

### Excluye

- AI-DLC Inception implementation
- deployment/monitoring como Operations ya soportado
- platform-specific hardcoding en el core
- certification o penetration testing implícito
- afirmar pass si sólo se generaron instrucciones

## 6. Mapping de contratos

| Adaptive Delivery | Software Delivery |
| --- | --- |
| DeliveryUnit | service, module, feature slice, migration o bounded change |
| behavior design | Functional Design |
| quality/risk requirements | NFR Requirements |
| assurance design | NFR Design |
| realization environment | Infrastructure Design |
| production plan | Code Generation Plan |
| production | code, tests, docs, config y deployment artifacts |
| unit verification | unit/static/component checks |
| integration acceptance | build, integration, contract, E2E, performance y security checks |

## 7. Perfil AI-DLC Construction

El profile declara:

```yaml
profile_id: aidlc-construction
adapter_id: software-delivery
approval_policy: strict
unit_strategy: complete-one-unit-before-next
required_stages:
  - production-planning
  - production
  - integration-acceptance
conditional_stages:
  - functional-design
  - nfr-requirements
  - nfr-design
  - infrastructure-design
state_projection: aidlc-docs/aidlc-state.md
audit_projection: aidlc-docs/audit.md
```

Workflow Planning decide `EXECUTE | SKIP` por stage, registra rationale/risk y
respeta prerequisites. Si un stage ejecuta, produce todos sus artifacts; depth
adapta detalle, no elimina el contract.

## 8. Delivery units de software

Cada unit registra:

- assigned requirements/stories
- source locations y ownership
- interfaces/contracts
- data entities y migrations
- dependencies on other units
- architecture constraints
- security/NFR requirements
- test strategy y acceptance criteria

Las dependencies deben estar satisfechas antes de producción o declararse mocks
temporales con invalidation policy.

## 9. Stage mapping

### Functional Design

Modela business logic, rules, domain entities, data flow y UI behavior aplicable.

### NFR Requirements

Define thresholds medibles de performance, scalability, availability, security,
reliability, maintainability y usability, además de technology decisions.

### NFR Design

Traduce NFRs a patterns y logical components. No duplica SecurityProfile.

### Infrastructure Design

Mapea logical components a environments, compute, storage, messaging,
networking, observability y shared infrastructure.

### Code Generation

Se traduce a production planning + production. El nombre se conserva en el
profile AI-DLC por compatibilidad, pero producción puede modificar artifacts
existentes y no sólo generar archivos nuevos.

### Build and Test

Se traduce a software integration and acceptance con evidencia ejecutada.

## 10. Planning y producción

El SoftwareProductionPlan incluye:

- numbered steps y checkboxes
- exact target paths
- files to modify/create
- story/requirement traceability
- unit context y dependencies
- implementation and test steps
- docs/config/migration/deployment artifacts aplicables
- verification commands o procedures
- rollback considerations

Production:

- carga el próximo step incompleto
- valida target path y permissions
- modifica in-place cuando corresponde
- marca step y associated requirements en la misma interacción
- registra artifact versions
- se detiene ante desviación material

## 11. Brownfield y greenfield

### Brownfield

- usar estructura y conventions existentes
- revisar reverse-engineering evidence
- modificar archivos in-place
- impedir copias como `_new`, `_modified` o duplicados equivalentes
- ejecutar regression checks proporcionales al impacto

### Greenfield

- materializar estructura aprobada
- no inventar framework sin technology decision
- mantener unit boundaries y integration strategy
- producir bootstrap mínimo suficiente

## 12. SDD, TDD y engineering doctrine

- AI-DLC define macro lifecycle
- SDD puede gobernar spec-before-production dentro de una unit
- TDD puede gobernar el production loop
- Clean Code, SOLID, architecture y security son policies/doctrine
- design patterns son references/capabilities seleccionadas por necesidad

El adapter compone el método mínimo suficiente; no fuerza SDD/TDD completos para
cambios triviales si policy y riesgo no lo justifican.

## 13. Build and Test con evidencia

El upstream describe ejecución, pero su procedimiento detallado genera sobre
todo instruction files y un summary templado. MasterMind fortalece el contract.

Cada check ejecutado registra:

- command/procedure y tool version
- environment y relevant configuration
- exit status
- pass/fail/inconclusive
- counts, thresholds o findings
- artifact/report/log refs
- limitations y skipped rationale

Estos campos se normalizan en el `EvidenceRecord` canónico de
`113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`. `command_or_procedure`,
`tool`, `environment`, `exit_status`, `metrics` y `artifact_refs` viven en el
record compartido; detalles stack-specific usan `detail_schema_ref` y
`details_ref`.

Matriz adaptable:

| Check | Default |
| --- | --- |
| syntax/type/static analysis | según stack |
| unit tests | required cuando existe behavior ejecutable |
| integration tests | required para interactions entre units |
| contract tests | required para published contracts cuando existe tooling |
| E2E | required para critical user flows cuando es viable |
| performance | required si hay NFR threshold |
| security | definido por SecurityProfile |
| build/package | requerido sólo cuando el proyecto realmente lo usa y policy permite ejecutarlo |

Una instruction file puede ser artifact útil, pero jamás evidence de pass.

## 14. Security assurance

El adapter consume el software overlay de `SecurityProfile`:

- authentication/authorization
- input and output validation
- secrets y dependency hygiene
- data classification y privacy
- supply chain
- infrastructure/IaC
- logging y safe failure
- threat-driven tests

`security-assurance` conserva veto independiente. Findings critical/high no se
promedian con test coverage.

## 15. Approval, state y audit

El profile AI-DLC preserva:

- approval del code generation plan
- approval del produced unit
- approval de cada Construction stage ejecutado
- stage-level state
- step-level plan progress
- raw approval response y timestamp en audit

MasterMind además vincula approvals a artifact versions y bundle hash. Cambiar
el artifact aprobado invalida el record afectado.

## 16. Session continuity y safe changes

Resume:

1. leer structured state y AI-DLC projection
2. identificar unit, stage y step activos
3. verificar bundle/profile hashes
4. cargar dependencies y artifacts relevantes
5. continuar desde el próximo step elegible

Agregar, saltar o reiniciar stages exige impact analysis, confirmación según
policy, invalidation de downstream outputs y audit append-only.

## 17. Operations seam

Operations upstream sigue siendo placeholder. El adapter sólo emite un handoff:

- releasable/not releasable verdict
- deployment artifact refs
- residual risks
- operational prerequisites
- recommended operations harness

No ejecuta deployment, monitoring ni incident management por implicación.

## 18. Contrato de salida

```yaml
adapter_id: software-delivery
profile_id: aidlc-construction | standard-software
unit_results: []
modified_artifacts: []
created_artifacts: []
test_artifacts: []
deployment_artifacts: []
verification_evidence: []
integration_verdict: {}
security_verdict: {}
approval_records: []
aidlc_state_projection: string | null
operations_handoff: {}
```

## 19. Integración con MasterMind

Paquetes previstos:

```text
.mm-flow/harness-library/roles/adaptive-delivery-lead/
.mm-flow/harness-library/lifecycle/software-delivery/
.mm-flow/harness-library/verification/software-integration-verifier/
.mm-flow/harness-library/review/software-reviewer/
.mm-flow/harness-library/recovery/recovery-fixer/
```

El adapter aporta capabilities al primary role; no se selecciona como segundo
Role Harness.

## 20. Criterios de aceptación

El adapter está implementado sólo si:

- satisface el Domain Delivery Adapter contract
- mapea AI-DLC units/stages sin perder approvals ni traceability
- greenfield y brownfield behavior están probados
- production sigue un plan versionado
- SDD/TDD selection es explícita y justificable
- tests/build checks producen evidencia real o skipped/blocked explícito
- security veto funciona
- resume continúa unit/stage/step correctos
- safe changes invalidan outputs dependientes
- Operations permanece handoff, no capability ficticia
- rutas existentes no regresan

## 21. Estado de implementación

### Disponible hoy

- reglas locales AI-DLC v1.0.0/1.0.1-style para Construction
- implementation-lead mínimo
- software registry entries y shared skills básicas
- verification/recovery primitives
- project adapter y planning bridge

### Pendiente

- Adaptive Delivery core y stage executor
- software adapter/profile models
- AI-DLC state/audit projection
- evidence-backed integration verifier
- review package type
- SDD/TDD routing
- brownfield/greenfield and continuity tests

## 22. Referencias

- `https://github.com/awslabs/aidlc-workflows/tree/d34bb7adfb4c58aa59bbb46494957f6169121b2b`
- `.aidlc-rule-details/common/process-overview.md`
- `.aidlc-rule-details/construction/code-generation.md`
- `.aidlc-rule-details/construction/build-and-test.md`
- `docs/canonical/76-AI-DLC-HARNESS-SPEC.md`
- `docs/canonical/112-DOMAIN-AWARE-SECURITY-ASSURANCE-PLANE.md`
- `docs/canonical/113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`
- `docs/canonical/114-ADAPTIVE-DELIVERY-HARNESS-RUNTIME-CONTRACT.md`
- `.planning/changes/software-delivery-domain-adapter/`

## Key Learnings:

1. AI-DLC Construction aporta invariantes de control, no un core cross-domain.
2. Build instructions no son build evidence.
3. Operations debe permanecer un seam hasta existir un harness operacional real.
