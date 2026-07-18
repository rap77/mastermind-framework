# Requirements — harness-stage-execution-runtime

## Problem / Purpose

MasterMind puede seleccionar, componer y validar un `RunBundle`, pero ese bundle
todavía no gobierna la ejecución del coordinator. UI/UX, onboarding y Adaptive
Delivery requieren el mismo mecanismo de stages, gates, evidence, checkpoint,
resume y recovery.

El objetivo es implementar una foundation única y domain-agnostic que ejecute
stage graphs declarados por los harnesses.

## Stakeholders / Users

- maintainers del runtime y MM-flow
- autores de harnesses y domain adapters
- agentes que ejecutan capabilities seleccionadas
- reviewers, approvers y operadores
- proyectos que requieren runs auditables y reanudables

## Scope

- typed stage, decision, result, evidence, approval y replan contracts
- stage graph materializado en RunBundle
- structural/behavioral graph validation
- ordered execution y prerequisite resolution
- bundle-to-coordinator wiring
- package type y routing para `review`
- gate evaluation y policy-driven approvals
- checkpoint/resume por bundle hash
- bounded recovery y safe replanning
- persistence, lineage y audit integration
- legacy compatibility path para runs sin stage graph

## Out of Scope

- definir stages específicos de UI/UX, onboarding o delivery
- seleccionar domain adapters
- implementar producción de software
- reemplazar `MultiHarnessSelector`
- crear otro project management system
- activar objectives consumidores automáticamente
- ejecutar builds durante la implementación de este plan

## Non-negotiables

- RunBundle validado gobierna stages y capabilities reales
- executor no contiene domain logic
- optional stage registra `skipped` con rationale
- un check no ejecutado no produce pass
- review, verification y approval permanecen separados
- stage result y checkpoint se persisten en la misma transición
- retries y loops son bounded
- replan invalida artifacts/approvals dependientes
- secrets y payloads sensibles no entran en evidence/audit
- `multi-channel-gateway` permanece objective activo hasta decisión explícita

## Functional Requirements

- [x] Modelar StageDefinition, StageDecision, StageResult y StageGraph.
- [x] Modelar EvidenceRecord, ApprovalRecord, RunCheckpoint y ReplanRecord.
- [x] Validar prerequisites, cycles, outputs, capabilities y policies.
- [x] Materializar stage metadata y content hash en RunBundle.
- [x] Ejecutar sólo capabilities seleccionadas y dependency-ready.
- [x] Integrar el bundle con HarnessRunExecutor/coordinator.
- [x] Seleccionar supporting review harnesses por policy/risk.
- [x] Persistir transitions, evidence, approvals y checkpoints.
- [x] Reanudar sólo con bundle/profile compatibles.
- [x] Aplicar recovery y safe replanning bounded.

## Quality Requirements

- determinismo en selección del próximo stage
- contracts tipados y backward-compatible donde existe consumo real
- tests de unit, integration y behavioral routing
- no domain-specific imports en el executor
- errores estructurados y accionables
- audit append-only y lineage versionado

## Objective-level Acceptance Criteria

- [x] Un RunBundle controla el orden efectivo del run.
- [x] Stages inválidos fallan antes de side effects.
- [x] Gate sin evidencia no permite transición aprobada.
- [x] Review puede componerse separado de verification.
- [x] Checkpoint reanuda el próximo stage/attempt correcto.
- [x] Bundle hash incompatible activa replan o block.
- [x] Recovery no supera attempts/budget.
- [x] UI/UX, onboarding y delivery pueden consumir la misma API.
- [x] Existing non-stage runs usan una compatibility route explícita.
- [x] Planning, canonical status y test evidence quedan alineados.
