# Adaptive Onboarding Harness Runtime Contract

## Índice

1. Estado canónico
2. Propósito
3. Decisión central
4. Invariante universal
5. Objetivos y no-objetivos
6. Modos de onboarding
7. Arquitectura
8. Contrato de entrada
9. Artifacts universales
10. Pipeline obligatorio
11. Multi-pass Gap Loop
12. Delegación y reassessment
13. Domain Adapter Contract
14. Software Onboarding Adapter
15. Marketing Adapter
16. Finance Adapter
17. Security Assurance Plane
18. Readiness y resultados
19. Persistencia y lineage
20. Activación y stop rules
21. Integración con runtime actual
22. Criterios de aceptación
23. Estado de implementación
24. Referencias

## 1. Estado canónico

- **Estado de decisión:** aprobado
- **Estado de diseño:** canonizado
- **Estado de planificación:** planificado en `.planning/changes/adaptive-onboarding-harness-runtime/`
- **Estado de implementación:** no implementado
- **Primary harness ID previsto:** `project-adoption-lead`
- **Gap loop ID previsto:** `multi-pass-gap-loop`
- **Readiness verifier ID previsto:** `onboarding-readiness`
- **Objective slug:** `adaptive-onboarding-harness-runtime`

Este documento define el contrato futuro y no afirma que el runtime exista.

## 2. Propósito

Transformar cualquier iniciativa, proyecto o corpus desde su estado actual hacia
un estado operacional confiable, aunque sea:

- una idea nueva
- un repositorio existente
- un proyecto incompleto
- un proyecto bloqueado
- un proyecto terminado que necesita auditoría
- una iniciativa de software, marketing, finanzas u otro nicho

El harness debe producir una línea base verificable, un mapa de gaps, una ruta
de cierre y un handoff reanudable.

## 3. Decisión central

> Onboarding se implementa como un supervisor universal de adopción, readiness
> y cierre de gaps, compuesto con adapters de dominio. No implementa todo el
> trabajo internamente y no se limita a software.

AI-DLC Discovery y MM-flow Discovery forman el primer Software Domain Adapter.
No constituyen el core universal.

## 4. Invariante universal

El mismo modelo sirve para cualquier dominio:

```text
Current State
-> Target State
-> Gap Registry
-> Prioritized Execution Waves
-> Delegated Execution
-> Reassessment
-> Readiness Verdict
```

La diferencia entre dominios vive en:

- fuentes esperadas
- policies
- threat models
- readiness dimensions
- execution harnesses
- artifacts proyectados

## 5. Objetivos y no-objetivos

### 5.1 Objetivos

- adoptar proyectos nuevos o existentes
- reconstruir estado real desde evidencia
- detectar gaps en múltiples pasadas especializadas
- diferenciar ausencia, contradicción, riesgo y deuda
- derivar waves ejecutables por dependencia
- delegar a harnesses especializados
- reevaluar después de cada wave
- verificar readiness contra target state
- capturar aprendizaje reusable para Core + Project Adapter

### 5.2 No-objetivos

- ser un agente universal que ejecuta todo
- forzar entrevistas completas en proyectos ya entendidos
- asumir que todo proyecto contiene código
- reemplazar domain experts o human approvals
- declarar completion por promedio si hay blockers críticos
- crear un workflow distinto por cada nicho
- confundir mejora opcional con gap bloqueante

## 6. Modos de onboarding

| Mode | Condición de entrada | Resultado esperado |
| --- | --- | --- |
| `greenfield` | idea sin operación previa | target state y primera ruta operacional |
| `brownfield-adoption` | proyecto existente no administrado | baseline, drift y adoption plan |
| `completion` | proyecto parcial | gap waves hasta completion criteria |
| `rescue` | proyecto bloqueado o inconsistente | recovery plan y estado estabilizado |
| `audit-improvement` | proyecto declarado terminado | readiness verdict y improvement backlog |
| `continuation` | proyecto ya administrado | refresh de gaps y siguiente objective |
| `migration` | proyecto migrado de otro sistema | lineage, mapping y operating handoff |

El mode se determina por evidencia y estado, no sólo por la frase del usuario.

## 7. Arquitectura

```text
Project / Initiative Input
  -> Mode and Domain Classifier
  -> Evidence Intake
  -> Current-State Analyzer
  -> Target-State Builder
  -> Multi-Pass Gap Loop
  -> Domain Adapter
  -> Security Assurance Plane
  -> Readiness Verifier
  -> Execution-Wave Planner
  -> Harness Delegation
  -> Reassessment Loop
  -> Final Verdict and Handoff
```

Composición prevista:

```yaml
primary_harness: project-adoption-lead
supporting_harnesses:
  - evidence-intake
  - current-state-analyzer
  - gap-auditor
  - domain-adapter
  - security-assurance
  - onboarding-readiness
  - recovery-fixer
```

## 8. Contrato de entrada

El onboarding recibe un `OnboardingRequest` con:

- `case_id`
- `project_id`
- `declared_goal`
- `domain_hint`
- `mode_hint`
- `source_roots`
- `target_outcomes`
- `constraints`
- `jurisdictions`
- `stakeholders`
- `approval_policy`
- `time_budget`
- `iteration_budget`
- `memory_hints`

Hints no son decisiones. El classifier debe confirmarlos o explicar por qué los
reemplaza.

## 9. Artifacts universales

El core produce contratos estructurados, luego cada adapter los proyecta a
formatos de dominio:

- `OnboardingProfile`
- `EvidenceRegistry`
- `CurrentStateSnapshot`
- `TargetStateDefinition`
- `GapRegistry`
- `ReadinessAssessment`
- `ExecutionWavePlan`
- `DelegationRecord`
- `ReassessmentDelta`
- `OperationalHandoff`

Campos mínimos de `OnboardingProfile`:

```yaml
case_id: string
domain: string
mode: string
current_state_version: string
target_state_version: string
active_adapter: string
security_profile_id: string
readiness_status: string
iteration: 0
```

## 10. Pipeline obligatorio

### Stage 1: Detect

Detecta workspace, dominio, mode, fuentes y estado previo.

**Gate:** route explicable y no ambigua.

### Stage 2: Evidence Intake

Inventaría repositorios, documentos, datos, assets, métricas, decisiones y
fuentes externas.

**Gate:** evidencia suficiente para reconstruir estado o preguntas explícitas.

### Stage 3: Target Definition

Define qué significa `done`, `ready` o `improved` para este caso.

**Gate:** target state aprobado o derivado de canon vigente.

### Stage 4: Current-State Reconstruction

Reconstruye realidad, no sólo intención declarada.

**Gate:** snapshot versionado con evidencia y confidence.

### Stage 5: Multi-Pass Gap Analysis

Compara current state con target state usando lentes especializadas.

**Gate:** gaps deduplicados, clasificados y priorizados.

### Stage 6: Readiness Classification

Determina blockers, warnings, deuda e improvement opportunities.

**Gate:** verdict explicado y security veto aplicado.

### Stage 7: Completion Roadmap

Agrupa gaps en waves por dependencia, riesgo y valor.

**Gate:** cada wave tiene owner, harness, evidence y completion criteria.

### Stage 8: Delegated Execution

Selecciona el harness de dominio adecuado. Onboarding supervisa; no suplanta al
executor especializado.

Cuando la wave requiere producir o modificar artifacts, puede delegar a
`adaptive-delivery-lead`. Audit/readiness-only modes no dependen de ejecutar
producción.

**Gate:** resultado del harness delegado verificado.

### Stage 9: Reassessment

Actualiza snapshot y gaps con delta, no con reconstrucción ciega.

**Gate:** progreso medible o recovery/escalation.

### Stage 10: Final Verification

Compara estado final con target, policies y risk acceptance.

**Gate:** no blockers abiertos y evidencia suficiente.

### Stage 11: Canonization and Handoff

Persiste artifacts, decisions, learnings, next actions y mejoras candidatas al
core.

**Gate:** otro actor puede continuar sin memoria de chat.

## 11. Multi-pass Gap Loop

Cada pasada tiene una rúbrica distinta:

| Pass | Lens | Pregunta principal |
| --- | --- | --- |
| 1 | evidence | ¿Qué fuente requerida falta o no es confiable? |
| 2 | structure | ¿Qué componente, ownership o dependencia falta? |
| 3 | domain | ¿Qué regla específica del nicho no está cubierta? |
| 4 | security/risk | ¿Qué amenaza, abuso o control falta? |
| 5 | execution | ¿Qué bloquea llegar al target state? |
| 6 | measurement | ¿Cómo se demuestra éxito y continuidad? |

No se permite una pasada genérica de “buscar más problemas”.

Cada gap incluye:

- `gap_id`
- `lens`
- `category`
- `severity`
- `evidence_refs`
- `target_requirement`
- `status`
- `blocking`
- `recommended_harness`
- `owner`
- `dependencies`
- `acceptance_criteria`

## 12. Delegación y reassessment

```text
assess
-> select highest-value dependency-ready wave
-> compose domain harness
-> execute
-> verify
-> persist delta
-> reassess
```

Onboarding mantiene ownership sobre readiness y continuity. El harness delegado
mantiene ownership sobre implementación de su dominio.

Ejemplos:

| Gap | Harness delegado |
| --- | --- |
| product intent | product discovery |
| architecture | architecture planner |
| software implementation | adaptive-delivery-lead + software-delivery adapter |
| UI/UX | ui-ux-delivery |
| security remediation | security remediation harness |
| campaign strategy | marketing execution harness |
| financial control | finance governance harness |

## 13. Domain Adapter Contract

Todo adapter declara:

- `adapter_id`
- supported domains y modes
- expected evidence types
- target-state schema extensions
- readiness dimensions
- domain gap lenses
- security overlay
- required approvals
- available execution harnesses
- artifact projections
- completion criteria

El core no contiene reglas regulatorias o técnicas específicas del nicho.

## 14. Software Onboarding Adapter

El piloto de software compone:

```text
AI-DLC Discovery
-> Product-Definition intent and constraints
-> reverse engineering for brownfield
-> open-questions join barrier
-> intent/reality reconciliation
-> MM-flow roadmap and objective package
-> delegated implementation/verification
```

AI-DLC mantiene ownership de `Product-Definition/`. MM-flow mantiene ownership
de `.planning/roadmap/` y `.planning/changes/`.

Este harness define y valida el adapter contract. La implementación productiva
pertenece al objective separado `software-onboarding-domain-adapter`.

## 15. Marketing Adapter

Dimensiones candidatas:

- market y audience evidence
- value proposition
- brand consistency
- channel strategy
- campaign/content inventory
- funnel y conversion measurement
- consent, tracking y platform access
- claims y reputational risk

El adapter se planifica después de validar el software pilot.

## 16. Finance Adapter

Dimensiones candidatas:

- financial objective
- risk tolerance y horizon
- jurisdiction
- data quality y reconciliation
- controls y approvals
- model assumptions
- audit trail
- reporting y continuity
- fraud, privacy y compliance

Requiere human approval y fuentes regulatorias versionadas. No produce advice
autónomo fuera de policy.

## 17. Security Assurance Plane

Security es transversal y tiene poder de veto. El contrato completo vive en:

- `docs/canonical/112-DOMAIN-AWARE-SECURITY-ASSURANCE-PLANE.md`

El onboarding debe proyectar un `SecurityProfile` en cada wave y bloquear
readiness ante riesgos critical/high no tratados.

## 18. Readiness y resultados

Estados finales:

- `ready-to-operate`
- `ready-with-warnings`
- `needs-discovery`
- `needs-completion`
- `needs-recovery`
- `needs-improvement`
- `blocked`
- `escalated`

Readiness no es un promedio simple. Un veto de seguridad, compliance o decisión
humana mantiene el caso bloqueado.

## 19. Persistencia y lineage

Persistir:

- versions de current/target state
- evidence sources y confidence
- gap lifecycle
- execution waves y delegations
- verification evidence
- security findings y risk acceptance
- readiness verdicts
- checkpoints
- local learnings
- core promotion candidates

Postgres conserva estructura; Markdown conserva artifacts humanos; memoria
conserva decisions/learnings/checkpoints; el grafo deriva relaciones.

## 20. Activación y stop rules

Activar cuando:

- un proyecto se incorpora a MasterMind
- se necesita reconstruir estado o completion path
- se solicita auditoría o rescue
- el proyecto carece de baseline confiable

No activar para una tarea aislada dentro de un proyecto ready.

Stop rules:

- no critical gaps abiertos
- readiness threshold satisfecho
- dos pasadas sin nuevos gaps materiales
- iteration budget agotado
- decisión humana requerida
- costo marginal supera valor esperado

## 21. Integración con runtime actual

Reusar:

- Harness Library y MultiHarnessSelector
- RunBundle composition
- shared RunBundle stage execution
- project state y artifact lineage
- planning bridge
- memory runtime
- verification/recovery primitives
- doctrine projection

Gaps a cerrar:

- onboarding schemas
- mode/domain classifier
- adapter registry
- multi-pass gap executor
- execution-wave supervisor
- reassessment delta
- readiness verifier
- security assurance integration
- integración de los stages de onboarding con `run-bundle-stage-executor`

## 22. Criterios de aceptación

- el mismo core procesa greenfield, brownfield, completion y audit
- software, marketing y finance se modelan como adapters, no forks
- gaps tienen evidence, target requirement y ownership
- loop converge por stop rules
- onboarding delega ejecución y reevalúa resultados
- security veto bloquea readiness cuando corresponde
- artifacts y estado permiten reanudación
- software onboarding adapter integra AI-DLC Discovery y MM-flow Discovery sin duplicar ownership
- behavioral cases positivos y negativos pasan

## 23. Estado de implementación

### Disponible hoy

- External Project Adoption model
- AI-DLC Discovery
- MM-flow Discovery
- reverse engineering rules
- Gap Detection Loop
- generic harness composition primitives
- project state, planning y memory foundations

### Pendiente

- `project-adoption-lead`
- universal onboarding contracts
- adapter registry
- multi-pass gap runtime
- execution-wave delegation/reassessment
- onboarding readiness verifier
- security assurance plane runtime
- software pilot adapter
- marketing y finance adapters

## 24. Referencias

- `docs/canonical/13-EXTERNAL-PROJECT-ADOPTION-MODEL.md`
- `docs/canonical/46-OBJECTIVE-DISCOVERY-SOURCES-AND-RECONCILIATION.md`
- `docs/canonical/63-MASTERMIND-CORE-ARCHITECTURE.md`
- `docs/canonical/71-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/80-GAP-DETECTION-AND-CLARIFICATION-LOOP.md`
- `docs/canonical/103-MULTI-HARNESS-COMPOSITION-AND-AGENT-HARNESSES-COMPLIANCE.md`
- `docs/canonical/113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`
- `docs/canonical/114-ADAPTIVE-DELIVERY-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/112-DOMAIN-AWARE-SECURITY-ASSURANCE-PLANE.md`
- `docs/canonical/decision-records/DR-010-ADAPTIVE-ONBOARDING-CORE-AND-DOMAIN-ADAPTERS.md`
- `.planning/changes/adaptive-onboarding-harness-runtime/`

## Key Learnings:

1. Onboarding universaliza current state -> target state, no un stack específico.
2. El supervisor cierra gaps delegando, verificando y reevaluando.
3. Los nichos escalan mediante adapters y policies, no copiando el workflow.
