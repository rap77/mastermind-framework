# Design — adaptive-delivery-harness-runtime

## Architecture / Boundaries

```text
AdaptiveDeliveryRequest
  -> DeliveryReadinessEvaluator
  -> DeliveryUnitDecomposer
  -> DomainDeliveryAdapterResolver
  -> AdaptiveRoutePlanner
  -> UnitDeliveryOrchestrator
       -> RunBundleStageExecutor
       -> Domain Producer Capabilities
       -> Unit Verifier
  -> IntegrationAcceptanceService
  -> Assurance and Review
  -> Recovery or Safe Replan
  -> DeliveryEnvelope and Handoff
```

- adaptive-delivery-lead owns delivery lifecycle and unit graph
- domain adapter owns vocabulary, artifacts, capabilities and policies
- shared foundation owns stage control flow
- producer capability owns artifact creation/modification
- verifier/reviewer/security own independent verdicts
- MM-flow owns operational progression and handoff

## Technical Approach

### Readiness and unit contracts

Add typed request, readiness, DeliveryUnit, route plan and integration verdict
models. Reject ambiguous objectives or missing acceptance criteria before
production.

### Domain adapter registry

Resolve adapters deterministically from explicit domain/mode first, then
evidence-based inference. Adapter declares decomposition, stage mapping,
artifact types, capabilities, policies and verification strategies.

### Route planning

Select concern stages per unit as execute/skip/block with prerequisites, risk,
rationale and depth. A stage that executes keeps its artifact contract.

### Unit delivery

Process dependency-ready units end-to-end. Every mutating unit receives a
versioned production plan and policy-driven approval before side effects.

### Integration acceptance

Aggregate unit results only after checking contracts, dependencies, requirement
coverage, quality thresholds, security and residual risk. Blockers are not
averaged into a passing score.

### Recovery and persistence

Use shared recovery/replan primitives. Persist unit/stage/step progress, artifact
lineage, evidence, approvals and checkpoint.

## Dependencies

- `harness-stage-execution-runtime`
- `domain-security-assurance-plane`
- `engineering-doctrine-layer`
- `artifact-versioning-and-lineage`
- `docs/canonical/114-ADAPTIVE-DELIVERY-HARNESS-RUNTIME-CONTRACT.md`
- existing planning bridge, multi-harness runtime and project state

## Validation Strategy

- unit tests for readiness, units, dependencies and route decisions
- adapter registry/conformance tests
- production-plan and approval policy tests
- unit loop scheduling tests
- integration acceptance and blocker cases
- security veto, review and recovery/replan cases
- cross-domain fixtures and existing routing regressions
- contract checks, JSON, ruff and targeted pytest; no build

## Important Tradeoffs

- adapters add contract overhead but prevent domain forks
- unit-first execution may serialize dependencies but improves traceability
- mandatory production plans add friction only to mutating runs
- strict AI-DLC approvals remain a profile, avoiding universal approval fatigue
- independent verdicts prevent convenient but unsafe aggregate scoring

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| core becomes software-specific | critical | non-software fixture and import rules |
| onboarding and delivery compete | high | onboarding finds/delegates gaps; delivery executes selected work |
| domain producer becomes second role | high | adapter capability contract and selector tests |
| endless unit/recovery loop | high | DAG, attempts and budgets |
| false integration pass | critical | evidence contract and independent vetoes |
| stale replan artifacts | high | dependency invalidation and versioned approvals |

## Context Notes

- Objective planned, not active.
- Shared stage execution and security assurance must complete first.
- Software adapter is a separate downstream objective.
- Onboarding can audit without delivery; when it delegates production, Adaptive Delivery is the execution boundary.
- `multi-channel-gateway` remains active/recommended.
