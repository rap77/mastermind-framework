# Adaptive Delivery Harness Runtime Contract

## Índice

1. Estado canónico
2. Propósito
3. Decisión central
4. Definiciones y límites
5. Relación con AI-DLC y MM-flow
6. Posición en la arquitectura
7. Activación y selección
8. Contrato de entrada
9. DeliveryUnit
10. Domain Delivery Adapter
11. Pipeline obligatorio
12. Unit Delivery Loop
13. Stage selection y profundidad
14. Plan-before-production
15. Approval policy
16. Integration and Acceptance
17. Assurance y review
18. Recovery y safe replanning
19. Estados y transiciones
20. Contrato de salida
21. Persistencia y lineage
22. Integración con el runtime actual
23. Seguridad y permisos
24. Criterios de aceptación
25. Estado de implementación
26. Referencias

## 1. Estado canónico

- **Estado de la decisión:** aprobado
- **Estado del diseño:** canonizado
- **Estado de planificación:** planificado en `.planning/changes/adaptive-delivery-harness-runtime/`
- **Estado de implementación:** implementado y validado con fixtures de conformance
- **Primary harness ID:** `adaptive-delivery-lead`
- **Objective slug:** `adaptive-delivery-harness-runtime`

## 2. Propósito

Definir el supervisor universal que convierte un objetivo aprobado en unidades
producibles, verificables e integrables sin asumir que toda entrega es software.

```text
delivery intent
  -> route planning
  -> delivery units
  -> per-unit production and verification
  -> cross-unit integration and acceptance
  -> assurance, review, recovery and handoff
```

## 3. Decisión central

> Adaptive Delivery es un Role Harness universal que gobierna unidades,
> dependencias, producción, evidencia y aceptación. La semántica específica
> entra mediante Domain Delivery Adapters y el control técnico de stages se
> delega a la foundation compartida.

`adaptive-delivery-lead` es el único Role Harness primario del run. Un producer
de dominio no se agrega como segundo role supporting.

## 4. Definiciones y límites

### Adaptive Delivery Harness

Supervisor responsable del delivery lifecycle desde readiness hasta handoff.

### DeliveryUnit

Unidad trazable que puede planificarse, producirse, verificarse e integrarse con
dependencies y acceptance criteria propios.

### Domain Delivery Adapter

Traductor versionado que aporta términos, artifacts, capabilities, policies,
quality dimensions, approvals y verification strategies de un dominio.

### Stage Execution Foundation

Runtime genérico definido en `113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`.
Ejecuta el graph; no decide la estrategia de delivery.

### No-objetivos

- reemplazar discovery, onboarding o product strategy
- convertir todos los dominios en software
- ejecutar producción sin plan aprobado por policy
- aceptar artifacts sin evidencia
- duplicar stage executors por harness
- representar Operations de AI-DLC como implementado

## 5. Relación con AI-DLC y MM-flow

```text
AI-DLC Harness
  owns: Inception, requirements, workflow planning, lifecycle approvals
  delegates Construction
          |
          v
Adaptive Delivery Harness
  owns: delivery units, route, production, integration, acceptance
  uses: Software Delivery Adapter for AI-DLC Construction semantics
          |
          v
MM-flow
  owns: operational state, task progression, checkpoints, handoff, archive
```

Adaptive Delivery también puede activarse standalone cuando requirements,
constraints y acceptance criteria ya están listos.

## 6. Posición en la arquitectura

```text
.planning objective
  -> PlanningBridge
  -> DeliveryReadinessProfile
  -> MultiHarnessSelector
  -> adaptive-delivery-lead
  -> DomainDeliveryAdapterResolver
  -> DeliveryRoutePlan
  -> RunBundleStageExecutor
  -> verification + review + security assurance + recovery
  -> DeliveryEnvelope
  -> project state + planning + memory
```

Paquete previsto:

```text
.mm-flow/harness-library/roles/adaptive-delivery-lead/
```

## 7. Activación y selección

Se activa cuando:

- existe un objetivo con acceptance criteria suficientemente definidos
- se requiere producir o modificar artifacts
- hay una o más unidades con dependencies
- la aceptación exige evidencia de unidad o integración
- onboarding delega una execution wave
- AI-DLC entra en Construction

No se activa si:

- falta definir el resultado esperado
- el trabajo es sólo discovery o research
- un Tool Loop determinístico alcanza
- el objetivo no puede mapearse a un domain adapter seguro

## 8. Contrato de entrada

`AdaptiveDeliveryRequest` extiende `HarnessRequest` con:

- `objective_id`
- `delivery_intent`
- `domain`
- `delivery_mode`
- `requirements_refs`
- `constraint_refs`
- `acceptance_criteria`
- `candidate_unit_refs`
- `dependency_refs`
- `target_artifact_types`
- `requires_write`
- `approval_policy`
- `security_profile_ref`
- `budget`
- `checkpoint_ref`

Readiness mínima:

- objective y scope no ambiguos
- acceptance criteria evaluables
- domain adapter resoluble
- permissions compatibles con side effects
- blockers conocidos tratados o escalados

## 9. DeliveryUnit

```yaml
unit_id: string
name: string
objective_ref: string
requirement_refs: []
dependency_unit_ids: []
owned_artifact_types: []
input_contract_refs: []
output_contract_refs: []
acceptance_criteria: []
risk_level: low | medium | high | critical
route_profile: string
status: pending | ready | active | blocked | produced | verified | integrated
```

Una unidad sólo pasa a `ready` cuando sus dependencies y required inputs están
disponibles o explícitamente mocked por policy.

## 10. Domain Delivery Adapter

Cada adapter declara:

- `adapter_id` y version
- supported domains y delivery modes
- unit decomposition rules
- stage vocabulary mapping
- artifact types y ownership
- producer capabilities
- verification strategies
- integration semantics
- policy packs y required approvals
- security overlay
- persistence projections

El adapter no modifica core models ad hoc. Extiende mediante metadata tipada y
versionada.

## 11. Pipeline obligatorio

### Stage 1: Readiness and Resume

Valida request, state, checkpoint, permissions, adapter y artifacts previos.

**Gate:** existe suficiente definición para producir sin inventar scope.

### Stage 2: Delivery Decomposition

Crea o valida DeliveryUnits, ownership, interfaces y dependencies.

**Gate:** cada requisito in-scope tiene unidad y acceptance path.

### Stage 3: Adaptive Route Planning

Decide `execute | skip | block` por concern stage, unidad y policy.

**Gate:** prerequisites y riesgos están explícitos.

### Stage 4: Unit Delivery Loop

Procesa cada unidad dependency-ready hasta produced/verified/blocked.

**Gate:** la unidad no avanza sin artifacts y evidencia requeridos.

### Stage 5: Integration and Acceptance

Evalúa composición entre unidades y objetivo completo.

**Gate:** integration verdict respaldado por evidencia.

### Stage 6: Independent Assurance and Review

Ejecuta verification, review, security y domain assurance según policy.

**Gate:** no quedan findings bloqueantes sin treatment.

### Stage 7: Recovery or Replanning

Aplica retry, patch, replan, rollback o escalate de forma bounded.

**Gate:** no existen loops infinitos ni outputs stale tratados como válidos.

### Stage 8: Handoff and Persistence

Emite envelope, checkpoint, lineage, residual risks y next actions.

**Gate:** el run puede reanudarse sin chat history.

## 12. Unit Delivery Loop

Por cada unidad:

1. cargar unit context y dependencies
2. ejecutar concern stages seleccionados
3. producir plan detallado
4. aplicar approval precondition
5. producir artifacts step-by-step
6. actualizar step y stage state en la misma interacción
7. verificar unidad
8. revisar si corresponde
9. persistir checkpoint
10. liberar unidades dependientes o activar recovery

Las unidades se completan end-to-end; no se ejecuta cada stage en bulk para
todas las unidades salvo que el adapter declare una razón válida.

## 13. Stage selection y profundidad

Concern stages universales:

- behavior/functional design
- quality and risk requirements
- assurance design
- realization environment design
- production planning
- production
- unit verification

Selection es binaria y registrada. Profundidad adapta detalle y rigor, no elimina
artifacts obligatorios de un stage ejecutado.

## 14. Plan-before-production

Todo run mutante requiere un production plan con:

- pasos ordenados
- target artifacts/locations
- requirement traceability
- dependencies y contracts
- verification por paso o unidad
- side effects y rollback considerations
- completion criteria

El executor produce sólo lo declarado. Desviaciones materiales activan replan.

## 15. Approval policy

El core soporta approvals en scopes plan, stage, artifact y run.

Profiles:

- `minimal`: approvals sólo ante side effects/risk gates
- `standard`: plan + final acceptance
- `strict`: cada concern stage + production plan + produced artifact
- `segregated`: maker, reviewer y approver distintos

AI-DLC Construction usa `strict` por default. Finance puede usar `segregated`.
Un adapter no puede debilitar project policy.

## 16. Integration and Acceptance

La aceptación global debe comprobar:

- units completas o exclusiones aprobadas
- interfaces/contracts compatibles
- dependencies satisfechas
- requirements traceados
- quality thresholds cumplidos
- side effects observados
- security verdict aplicable
- residual risks registrados

El resultado es `passed | failed | blocked | conditional`. `conditional` exige
owner, expiry y condiciones explícitas.

## 17. Assurance y review

- verification evalúa criterios declarados
- review busca problemas no cubiertos por checks determinísticos
- security assurance conserva veto independiente
- approval decide si el riesgo y evidencia permiten continuar

No se promedian verdicts bloqueantes para producir una nota aprobatoria.

## 18. Recovery y safe replanning

Recovery clasifica fallos:

- transient execution failure -> retry bounded
- local artifact defect -> patch + reverification
- invalid route/assumption -> replan
- unsafe side effect -> rollback/escalate
- missing capability/evidence -> blocked
- unresolved high/critical risk -> escalate

Replanning realiza impact analysis e invalida artifacts, evidence y approvals
dependientes antes de continuar.

## 19. Estados y transiciones

Estados mínimos:

- `pending`
- `readiness_blocked`
- `route_ready`
- `unit_active`
- `unit_blocked`
- `integration_ready`
- `acceptance_failed`
- `needs_review`
- `needs_recovery`
- `passed`
- `conditional`
- `escalated`

Happy path:

```text
pending -> route_ready -> unit_active -> integration_ready
-> needs_review -> passed -> persisted
```

## 20. Contrato de salida

```yaml
status: success | warning | error
summary: string
adapter_id: string
route_plan_ref: string
unit_results: []
artifacts: []
stage_results: []
integration_verdict: {}
verification: {}
review: {}
security_verdict: {}
recovery: {}
approval_records: []
risks: []
next_actions: []
checkpoint_ref: string
```

## 21. Persistencia y lineage

Persistir:

- request/readiness y adapter version
- decomposition y unit graph
- route decisions
- production plans y progress
- artifact lineage entre requirements, units y outputs
- evidence, findings y approvals
- integration verdict
- recovery/replan history
- checkpoint y final handoff

Markdown sigue siendo canónico para decisiones y planes humanos. Project state
mantiene estado estructurado y lineage.

## 22. Integración con el runtime actual

### Reutilizable

- planning bridge y project adapter
- multi-harness selector/composer/validator
- runtime models y execution envelope
- verification/recovery primitives
- memory writer y artifact repositories

### Implementado

- shared stage executor reutilizado por el unit loop
- delivery request, unit, route y verdict models
- domain delivery adapter contract y registry
- paquete `adaptive-delivery-lead`
- plan-before-production, unit loop e integration acceptance
- assurance independiente, recovery y safe replanning
- persistence, lineage, checkpoint y resume exacto

## 23. Seguridad y permisos

- domain adapter y external artifacts son untrusted inputs
- producción requiere permissions explícitos
- network/write/destructive actions usan policy gates
- secrets no se incluyen en plans, prompts, logs ni evidence
- security profile se aplica por unidad y aceptación global
- risk acceptance exige owner, approver, scope y expiry

## 24. Criterios de aceptación

El harness está implementado sólo si:

- selecciona el adapter correcto con rationale
- produce un unit graph trazable
- respeta dependencies y stage decisions
- exige plan antes de producción mutante
- el RunBundle gobierna la ejecución real
- verifica unidades e integración con evidencia
- separa verification, review, security y approval
- safe replanning invalida outputs dependientes
- checkpoint reanuda unidad/stage/step correctos
- al menos software y un adapter fixture no-software satisfacen el core contract
- no regresa rutas existentes

## 25. Estado de implementación

### Disponible hoy

- AI-DLC y MM-flow como fuentes de lifecycle y control operacional
- selector/composer/validator multi-harness
- shared stage executor y primitives de verification, review y recovery
- delivery request, unit graph, adapter registry y adaptive route planner
- `adaptive-delivery-lead` con plan-before-production y unit loop
- integration acceptance con security/review vetoes independientes
- persistence, lineage, bounded recovery, safe replan y exact resume
- fixtures software y publishing conformes al mismo core contract
- routing regression matrix con selección explícita de Adaptive Delivery

### Pendiente downstream

- adapters productivos de dominio, incluido el Software Delivery Adapter de
  `115-SOFTWARE-DELIVERY-DOMAIN-ADAPTER.md`
- activación operacional de esos adapters según sus propios objetivos y gates

## 26. Referencias

- `docs/canonical/64-HARNESS-LIBRARY-AND-LOOP-TAXONOMY.md`
- `docs/canonical/71-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/76-AI-DLC-HARNESS-SPEC.md`
- `docs/canonical/103-MULTI-HARNESS-COMPOSITION-AND-AGENT-HARNESSES-COMPLIANCE.md`
- `docs/canonical/113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`
- `docs/canonical/115-SOFTWARE-DELIVERY-DOMAIN-ADAPTER.md`
- `docs/canonical/decision-records/DR-013-ADAPTIVE-DELIVERY-CORE-AND-DOMAIN-ADAPTERS.md`
- `.planning/changes/adaptive-delivery-harness-runtime/`

## Key Learnings:

1. El invariante universal es unidad -> producción -> evidencia -> integración.
2. AI-DLC es lifecycle; Adaptive Delivery ejecuta Construction sin reemplazarlo.
3. Los dominios cambian adapters, no el control core.
