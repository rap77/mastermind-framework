# Requirements — software-delivery-domain-adapter

## Problem / Purpose

Adaptive Delivery necesita un primer adapter productivo que traduzca sus
contratos universales a software sin perder AI-DLC Construction, SDD/TDD,
brownfield safety, build/test evidence ni security assurance.

El objetivo es implementar `software-delivery` y el profile
`aidlc-construction`, manteniendo AI-DLC como macro lifecycle y MM-flow como
control plane operacional.

## Stakeholders / Users

- software teams y maintainers
- AI-DLC users y approvers
- agents que modifican código, tests, docs e infraestructura
- reviewers, security verifiers y release operators
- onboarding que delega software completion waves

## Scope

- Software Delivery Adapter Contract implementation
- AI-DLC Construction profile v1.0.1 mapping
- software DeliveryUnit decomposition y artifact ownership
- Functional/NFR/Infrastructure concern mappings
- versioned code generation/production plans
- greenfield y brownfield production rules
- SDD/TDD/doctrine routing
- evidence-backed build/test/integration verifier
- software security overlay integration
- AI-DLC approvals, state, audit, continuity y safe changes
- Operations handoff seam

## Out of Scope

- AI-DLC Inception implementation
- deployment, monitoring o incident response
- certificar seguridad/compliance
- hardcodear frameworks o cloud providers
- reemplazar `software-onboarding-domain-adapter`
- asumir que instruction files son execution evidence
- activar este objective antes del core

## Non-negotiables

- adapter y onboarding adapter tienen ownership distinto
- AI-DLC approval/state/audit invariants se preservan
- software-specific semantics permanecen fuera del core
- brownfield modifica in-place y evita duplicate files
- mutating work sigue un plan versionado
- tests/build checks reportan evidencia real o skipped/blocked
- security veto permanece independiente
- Operations es handoff, no capability ficticia
- resume valida unit/stage/step y hashes
- no build durante la creación de estos artifacts de planificación

## Functional Requirements

- [ ] Registrar adapter/profile con version y mappings.
- [ ] Mapear AI-DLC UOWs, stages, artifacts y approvals.
- [ ] Resolver software capabilities y methodology routes.
- [ ] Producir plans con paths, steps y traceability.
- [ ] Aplicar greenfield/brownfield file rules.
- [ ] Ejecutar y capturar software verification evidence.
- [ ] Aplicar SecurityProfile software overlay.
- [ ] Proyectar state/audit sin duplicar source of truth.
- [ ] Reanudar y replanificar con invalidation segura.
- [ ] Emitir operations handoff explícito.

## Quality Requirements

- adapter conformance y versioning
- stack detection based on repository evidence
- no hardcoded credentials, private endpoints or production secrets
- targeted regression matrix for supported software paths
- clear inconclusive/skipped semantics
- compatibility with AI-DLC artifact ownership

## Objective-level Acceptance Criteria

- [ ] AI-DLC Construction route produce el mismo unit/stage intent con typed state.
- [ ] Strict approvals se aplican en el profile, no en el core.
- [ ] Brownfield no crea archivos duplicados.
- [ ] SDD/TDD selection es explícita y justificable.
- [ ] Build/test verdict contiene command/procedure, environment y result evidence.
- [ ] Instruction-only artifacts no generan pass.
- [ ] Security blocker impide acceptance.
- [ ] Resume y safe workflow changes preservan audit/lineage.
- [ ] Operations termina en handoff.
- [ ] Existing software/product routing permanece compatible.
