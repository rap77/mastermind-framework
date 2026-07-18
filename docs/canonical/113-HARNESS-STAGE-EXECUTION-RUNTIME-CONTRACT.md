# Harness Stage Execution Runtime Contract

## Índice

1. Estado canónico
2. Propósito
3. Decisión central
4. Alcance y límites
5. Posición en la arquitectura
6. Contratos del runtime
7. Stage graph
8. Semántica de ejecución
9. Gates y approvals
10. Evidencia
11. Estado, checkpoint y resume
12. Safe replanning
13. Review como package type
14. Recovery
15. Persistencia y auditabilidad
16. Seguridad
17. Integración con el runtime actual
18. Criterios de aceptación
19. Estado de implementación
20. Referencias

## 1. Estado canónico

- **Estado de la decisión:** aprobado
- **Estado del diseño:** canonizado
- **Estado de planificación:** ejecutado en `.planning/changes/harness-stage-execution-runtime/`
- **Estado de implementación:** implementado
- **Runtime component ID:** `run-bundle-stage-executor`
- **Objective slug:** `harness-stage-execution-runtime`

La foundation compartida gobierna ejecuciones reales mediante RunBundles
validados. Los harnesses consumidores de dominio siguen siendo objetivos
independientes y no forman parte de esta implementación.

## 2. Propósito

Cerrar el gap entre un `RunBundle` seleccionado y validado y una ejecución real,
ordenada, observable, reanudable y gobernada por ese bundle.

La foundation debe ser reutilizable por:

- Adaptive Delivery
- UI/UX Delivery
- Adaptive Onboarding
- futuros harnesses con stages y gates

## 3. Decisión central

> MasterMind tendrá un único runtime genérico para ejecutar stage graphs de
> RunBundles. Los harnesses declaran stages y semántica de dominio; el executor
> sólo controla orden, gates, estado, evidencia, resume y recovery transitions.

No se implementará un executor diferente dentro de cada harness.

## 4. Alcance y límites

### 4.1 Responsabilidades

- validar que el bundle está aprobado para ejecución
- cargar el stage graph materializado
- resolver el próximo stage elegible
- aplicar prerequisites, policies y gates
- invocar la capability seleccionada
- registrar resultados, evidencia y transiciones
- detener, recuperar, replanificar o escalar
- persistir checkpoints reanudables

### 4.2 No-responsabilidades

- decidir qué significa producir software, una campaña o un modelo financiero
- inventar stages que el harness no declaró
- reemplazar al `MultiHarnessSelector`
- reemplazar al domain adapter
- aprobar evidencia que no fue producida
- convertir summaries en prueba de ejecución

## 5. Posición en la arquitectura

```text
ObjectiveProfile
  -> MultiHarnessSelector
  -> HarnessCompositionPlan
  -> RunBundleComposer
  -> RunBundleValidator
  -> RunBundleStageExecutor
       -> StageGraph
       -> StageRunner
       -> GateEvaluator
       -> EvidenceRecorder
       -> CheckpointStore
       -> RecoveryRouter
  -> ExecutionEnvelope
  -> project state + planning + memory
```

`HarnessRunExecutor` conserva la integración con project adapters y coordinator,
pero debe entregar el `RunBundle` al `RunBundleStageExecutor`. El coordinator no
puede ignorar silenciosamente el bundle seleccionado.

## 6. Contratos del runtime

### 6.1 StageDefinition

```yaml
stage_id: string
name: string
required: boolean
prerequisites: []
capability_refs: []
input_artifact_types: []
output_artifact_types: []
gate_policy: string
approval_policy: string
recovery_policy: string
max_attempts: 1
```

### 6.2 StageDecision

```yaml
stage_id: string
decision: execute | skip | block
rationale: string
decided_by: selector | policy | human
risk: low | medium | high | critical
affected_artifacts: []
```

### 6.3 StageResult

```yaml
stage_id: string
status: passed | failed | blocked | skipped | needs_review | needs_recovery
attempt: 1
artifact_refs: []
evidence_refs: []
finding_refs: []
started_at: timestamp
completed_at: timestamp
next_stage_ids: []
```

### 6.4 ApprovalRecord

```yaml
approval_id: string
scope: stage | plan | artifact | run
decision: approved | changes_requested | rejected | expired
actor: string
rationale: string
artifact_versions: []
decided_at: timestamp
expires_at: timestamp | null
```

### 6.5 StageGraph

```yaml
schema_version: "1"
graph_id: string
bundle_id: string
profile_ref: string
entry_stage_ids: []
exit_stage_ids: []
nodes:
  - stage: StageDefinition
edges:
  - from_stage_id: string
    to_stage_id: string
    on_status: [passed]
loops:
  - loop_id: string
    member_stage_ids: []
    entry_stage_id: string
    entry_condition_ref: string
    exit_condition_ref: string
    max_iterations: integer
    checkpoint_each_iteration: true
    exhausted_action: needs_recovery | blocked | escalated
canonicalization_version: "jcs-v1"
content_hash: "sha256:<digest>"
```

`nodes` y `edges` usan IDs únicos. Array order es significativo sólo donde el
contract lo declara; scheduling se deriva de edges y desempata por `stage_id`.
Un graph con loops declarados debe ser acíclico después de colapsar cada loop en
un supernode.

Antes de RFC 8785/JCS, el runtime normaliza arrays semánticamente unordered:

- `nodes` por `stage_id`
- `edges` por `(from_stage_id, to_stage_id, on_status)` y `on_status` ordenado
- `loops` por `loop_id` y `member_stage_ids` ordenado
- capabilities por `(capability_id, version)`
- policies por `(policy_id, version)`
- artifact contracts por `(artifact_type, version)`

Todo orden semánticamente significativo se representa con un campo `ordinal` o
con edges; nunca depende de la posición incidental de un array. Después se
calcula SHA-256 sobre JSON RFC 8785/JCS excluyendo `content_hash` e incluyendo
graph, profile/version, capabilities, policies y artifact contract. El mismo
input semántico debe producir el mismo digest en cualquier runtime compatible.

## 7. Stage graph

El bundle debe materializar un directed acyclic graph por default. Un loop sólo
se admite cuando declara:

- condición de entrada
- condición de salida
- límite de intentos o budget
- checkpoint por iteración
- recovery/escalation al agotar el límite

Cada stage opcional debe tener un `StageDecision`. Omitirlo sin registro es un
estado inválido.

El validator rechaza:

- prerequisites inexistentes
- ciclos no declarados
- capabilities requeridas ausentes
- output requerido sin productor
- gate o recovery policy desconocida
- review requerido sin reviewer elegible

## 8. Semántica de ejecución

1. validar bundle y permisos
2. cargar checkpoint compatible o iniciar run
3. resolver stages dependency-ready
4. aplicar policy y approval preconditions
5. ejecutar una capability con contexto mínimo
6. capturar artifacts y evidencia
7. evaluar gate
8. persistir resultado y checkpoint en la misma transición
9. continuar, revisar, recuperar, replanificar o bloquear
10. emitir `ExecutionEnvelope`

Una capability no seleccionada por el bundle no puede ejecutarse por inferencia
del modelo.

## 9. Gates y approvals

Los gates son determinísticos cuando el criterio lo permite. La aprobación
humana es una policy, no un hardcode universal.

Se requiere aprobación explícita cuando:

- la policy del harness la exige
- existe side effect externo o destructivo
- cambia un contrato aprobado
- el riesgo es high/critical
- se acepta riesgo residual
- el domain adapter exige segregación de funciones

El perfil AI-DLC puede exigir approval por cada Construction stage. Otros
perfiles pueden agrupar approvals sin cambiar el executor.

## 10. Evidencia

Un `EvidenceRecord` mínimo contiene:

```yaml
evidence_id: string
check_id: string
performed: boolean
method: command | tool | inspection | human-attestation
result: pass | fail | inconclusive | skipped
summary: string
command_or_procedure: string | null
tool:
  id: string
  version: string | null
environment:
  name: string
  configuration_refs: []
exit_status: integer | null
artifact_refs: []
metrics:
  - name: string
    actual: number | string
    expected: number | string | null
    unit: string | null
    passed: boolean | null
detail_schema_ref: string | null
details_ref: string | null
limitations: []
recorded_at: timestamp
```

`passed` es una proyección derivada: `performed == true && result == pass`. Los
consumidores no guardan un segundo boolean canónico. UI/UX usa `details_ref` para
viewport, accessibility o browser evidence; software usa command, tool,
environment, metrics y report refs. Un detalle de dominio requiere schema
versionado mediante `detail_schema_ref`, por lo que la normalización no pierde
información ni convierte `details` libres en autoridad.

Reglas:

- un check no ejecutado no pasa
- una instrucción de ejecución no equivale a ejecución
- un summary sin references no satisface un gate
- la evidencia debe vincularse a las versiones evaluadas
- datos sensibles se referencian o redactan; no se copian a logs

## 11. Estado, checkpoint y resume

El runtime mantiene dos niveles:

- **run/stage state:** ubicación y transición del workflow
- **step/artifact state:** progreso fino dentro del plan ejecutado

`RunCheckpoint` debe incluir:

- run, bundle y objective IDs
- bundle content hash
- active stage y attempt
- completed/skipped/blocked stages
- artifact y evidence refs
- pending approvals
- budget consumido y restante
- recovery/replan state
- next eligible stages

Al reanudar, un bundle hash incompatible obliga a safe replanning; no continúa
con contexto viejo.

### 11.1 Autoridad y atomicidad

Project state es el store autoritativo de `StageResult`, `RunCheckpoint`,
artifact/evidence refs y transition outbox. El executor propone la transición;
project state la confirma. MM-flow y memory son proyecciones downstream, no
checkpoint authorities paralelas.

La transacción autoritativa escribe en este orden lógico:

1. validar expected checkpoint version
2. insertar StageResult y evidence/artifact refs
3. actualizar RunCheckpoint
4. insertar outbox events para `.planning` y memory
5. commit único

Idempotency key:

```text
(run_id, bundle_hash, stage_id, attempt, transition_sequence)
```

La key es unique. Repetir una transición devuelve el resultado persistido sin
duplicar side effects ni checkpoints.

Después del commit, projectors actualizan `.planning` y memory. Si una
proyección falla, se reintenta desde outbox; el checkpoint autoritativo no se
revierte. `.run-bundles` es input inmutable y nunca almacena live progress.

Capabilities con side effects externos reciben la misma idempotency key. Si el
resultado externo queda desconocido, el stage pasa a `needs_recovery`; no se
reintenta a ciegas.

## 12. Safe replanning

Agregar, quitar, reiniciar o reordenar stages requiere un `ReplanRecord`:

- cambio solicitado y motivo
- impacto sobre dependencies y artifacts
- artifacts invalidados o archivados
- approvals invalidados
- nuevo bundle/version
- confirmación requerida por policy
- punto seguro de reanudación

Replanning nunca reescribe el historial anterior.

## 13. Review como package type

`review` debe existir como package type separado de `verification`.

- verification determina cumplimiento contra criterios
- review busca defectos, riesgos y desacuerdos con fresh context
- approval toma una decisión autorizada

El selector debe poder componer review como supporting harness cuando riesgo,
subjectivity, policy o segregation of duties lo exijan.

## 14. Recovery

Acciones soportadas:

- `retry`: mismo stage, causa transitoria y budget disponible
- `patch`: corrección local con nueva evidencia
- `replan`: cambia route/stages/artifacts afectados
- `rollback`: revierte side effects cuando existe estrategia segura
- `escalate`: requiere decisión o capability externa
- `stop`: cierre explícito sin seguir ejecutando

Cada acción conserva attempt history. No existen retries ilimitados.

## 15. Persistencia y auditabilidad

Persistir:

- bundle/version/hash y selection rationale
- stage decisions y transitions
- invocaciones de capabilities
- artifact lineage
- evidence y findings
- approval prompts y decisions
- recovery y replan records
- checkpoints y final envelope

Destinos:

- project state para estado autoritativo, transaction, outbox y lineage
- `.planning` como proyección de continuidad operacional
- memory layer como proyección de decisiones, learnings y checkpoints
- `.run-bundles` como input inmutable/materialización efímera auditable

## 16. Seguridad

- el bundle y manifests se validan como input no confiable
- paths deben quedar dentro de roots permitidos
- write/network/tool permissions se aplican antes de cada stage
- secrets y payloads sensibles no se persisten en audit/evidence
- security veto puede bloquear cualquier transición aplicable
- una aprobación no puede elevar permisos fuera de project policy

## 17. Integración con el runtime actual

### Reutilizable

- `FileSystemHarnessCatalog`
- `MultiHarnessSelector`
- `RunBundleComposer`
- `RunBundleValidator`
- `HarnessRunExecutor`
- `HarnessCore`
- `MemoryRuntimeWriter`

### Gaps a cerrar

- entregar el bundle validado al executor/coordinator
- materializar stage metadata en el bundle
- agregar stage, evidence, approval, checkpoint y replan models
- agregar package type `review`
- ejecutar supporting harnesses en el punto declarado
- persistir estado fino y reanudar por bundle hash

## 18. Criterios de aceptación

La foundation está implementada sólo si:

- el bundle controla realmente stages y capabilities
- prerequisites y skips son observables
- gates no aceptan evidencia faltante
- review y verification permanecen separados
- checkpoint reanuda el próximo stage correcto
- safe replanning invalida outputs dependientes
- recovery es bounded
- UI/UX, onboarding y delivery pueden usar el mismo executor
- los runs existentes sin stage graph conservan una ruta compatible explícita
- unit, integration y behavioral routing tests pasan

## 19. Estado de implementación

### Disponible hoy

- stage graph, evidence, approval, checkpoint y replan contracts tipados
- selección, composición y validación de RunBundles con content hash determinista
- stage scheduling y gates determinísticos con capability isolation
- wiring de RunBundle a `HarnessRunExecutor` y coordinator
- checkpoint/resume autoritativo con idempotencia y expected-version concurrency
- projection outbox, side-effect recovery y safe replanning bounded
- package type `review` separado de verification y approval
- ruta de compatibilidad explícita para ejecuciones sin stage graph
- fixtures UI/UX, onboarding y delivery sobre un único executor contract

### Evidencia de cierre

- `tests/integration/test_stage_execution_consumers.py`
- `tests/unit/test_multi_harness_pipeline.py`
- `tests/unit/test_harness_run_executor.py`
- behavioral routing cases de `.mm-flow/harness-library/routing-cases.yaml`
- discovery contract de `.planning/changes/harness-stage-execution-runtime/`

Los runtime contracts específicos de UI/UX, onboarding y Adaptive Delivery
permanecen planificados en sus propios objectives; consumen esta foundation sin
trasladar semántica de dominio al executor.

## 20. Referencias

- `docs/canonical/71-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/103-MULTI-HARNESS-COMPOSITION-AND-AGENT-HARNESSES-COMPLIANCE.md`
- `docs/canonical/110-UI-UX-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/111-ADAPTIVE-ONBOARDING-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/114-ADAPTIVE-DELIVERY-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/decision-records/DR-012-SHARED-RUN-BUNDLE-STAGE-EXECUTION.md`
- `.planning/changes/harness-stage-execution-runtime/`

## Key Learnings:

1. Seleccionar un RunBundle no sirve si ese bundle no gobierna la ejecución.
2. El executor comparte control flow, no semántica de dominio.
3. Evidencia, review y approval son contratos distintos.
