# Requirements — adaptive-delivery-harness-runtime

## Problem / Purpose

El Implementation Harness actual está definido como software-only y no modela
delivery reusable entre dominios. AI-DLC aporta un Construction loop maduro,
pero sus stages y artifacts no deben filtrarse al core universal.

El objetivo es implementar `adaptive-delivery-lead` como supervisor de
DeliveryUnits, producción, verificación, integración, assurance y handoff,
delegando control técnico al shared stage executor y semántica a domain adapters.

## Stakeholders / Users

- owners de objectives listos para delivery
- maintainers y operadores de MasterMind
- domain experts, producers, reviewers y approvers
- onboarding harness que delega execution waves
- AI-DLC users entrando en Construction

## Scope

- AdaptiveDeliveryRequest y readiness profile
- DeliveryUnit y dependency graph
- adaptive route planning por unit/concern
- plan-before-production contract
- per-unit delivery loop
- Domain Delivery Adapter Contract y registry
- integration and acceptance verdict
- verification, review, security y approval composition
- bounded recovery y safe replanning
- persistence, lineage, checkpoint, resume y handoff
- cross-domain conformance fixtures

## Out of Scope

- implementar adapters completos de marketing o finanzas
- implementar software production dentro del core
- reemplazar AI-DLC Inception, onboarding o discovery
- duplicar el shared stage executor
- desplegar o monitorear artifacts
- activar este objective automáticamente
- ejecutar builds durante esta planificación

## Non-negotiables

- un único Role Harness primario: `adaptive-delivery-lead`
- domain producers se resuelven como adapter capabilities
- core domain-agnostic y adapters versionados
- cada requirement in-scope tiene unit y acceptance path
- stages opcionales registran decisión y rationale
- todo run mutante usa plan-before-production
- unit y integration acceptance requieren evidencia
- security verdict mantiene veto independiente
- recovery/replan son bounded y auditables
- handoff permite resume sin chat history

## Functional Requirements

- [ ] Validar readiness, permissions, adapter y checkpoint.
- [ ] Crear DeliveryUnits con ownership, contracts y dependencies.
- [ ] Decidir execute/skip/block por concern stage y unidad.
- [ ] Resolver adapters por domain/mode/capabilities.
- [ ] Producir y aprobar plans según policy.
- [ ] Ejecutar units dependency-ready end-to-end.
- [ ] Verificar artifacts de unidad e integración.
- [ ] Componer verification, review, security y approvals.
- [ ] Aplicar recovery y safe replanning con invalidation.
- [ ] Persistir route, units, evidence, verdicts y checkpoint.

## Quality Requirements

- unit scheduling determinístico
- no imports ni términos software-only en el core
- adapter conformance tests
- evidence-backed acceptance
- structured errors para blocked/escalated paths
- compatibility con runtime envelope y planning bridge

## Objective-level Acceptance Criteria

- [ ] Objective listo produce un DeliveryRoutePlan validado.
- [ ] Unit graph bloquea dependencies no satisfechas.
- [ ] Mutating production no comienza sin plan/policy gate.
- [ ] Un RunBundle gobierna el loop real.
- [ ] Integration verdict se basa en evidencia.
- [ ] Verification, review, security y approval son independientes.
- [ ] Replan invalida outputs y approvals downstream.
- [ ] Checkpoint reanuda unit/stage/step correctos.
- [ ] Software y un fixture no-software satisfacen el adapter contract.
- [ ] Existing harness routing permanece compatible.
