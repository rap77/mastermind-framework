# Design — software-delivery-domain-adapter

## Architecture / Boundaries

```text
AI-DLC Workflow Planning or Standalone Software Objective
  -> Adaptive Delivery Request
  -> SoftwareDeliveryAdapter
       -> SoftwareUnitMapper
       -> SoftwareConcernStageMapper
       -> MethodologyRouter (SDD/TDD/minimal)
       -> SoftwareProductionPlanner
       -> SoftwareProducerCapabilities
       -> SoftwareIntegrationVerifier
       -> SoftwareSecurityOverlay
       -> AIDLCTelemetryProjection
  -> Adaptive Delivery Integration Verdict
  -> Operations Handoff
```

- AI-DLC owns macro lifecycle, workflow decisions and strict profile approvals
- Adaptive Delivery owns units, route, integration and acceptance
- adapter owns software mapping and capabilities
- MM-flow owns execution progress, checkpoints and handoff
- security assurance owns independent security verdict

## Technical Approach

### Versioned profile

Register `software-delivery` and `aidlc-construction` with source version/commit,
stage mappings, strict approval policy and state/audit projections.

### Unit and stage translation

Translate service/module/feature/migration work into DeliveryUnits. Map AI-DLC
Functional, NFR and Infrastructure stages onto universal concern stages without
changing the core.

### Methodology routing

Choose SDD, TDD or minimal delivery based on requirements maturity, risk,
verifiability and policy. Clean Code/SOLID/security remain policies; patterns
remain references/capabilities.

### Production plan and file safety

Create explicit plans with exact paths and steps. Brownfield checks existence,
uses repository conventions and modifies in-place. Greenfield follows approved
architecture and technology decisions.

### Evidence-backed integration

Execute applicable static, unit, integration, contract, E2E, performance and
security checks. Record commands/procedures, environment, exit status, reports
and limitations. Never infer pass from instruction documents.

### AI-DLC continuity

Project typed state into `aidlc-docs/aidlc-state.md` and append approval/audit
events without creating a competing operational ledger.

## Dependencies

- `adaptive-delivery-harness-runtime`
- `harness-stage-execution-runtime`
- `domain-security-assurance-plane`
- `docs/canonical/115-SOFTWARE-DELIVERY-DOMAIN-ADAPTER.md`
- existing AI-DLC rules and MM-flow planning bridge

## Validation Strategy

- adapter contract and profile mapping tests
- unit/stage/artifact ownership cases
- methodology routing matrix
- greenfield and brownfield file-safety tests
- evidence-backed verifier tests including instruction-only negative case
- strict approval/state/audit/resume tests
- security veto and Operations handoff tests
- existing routing regressions
- contract checks, JSON, ruff and targeted pytest; no build in planning

## Important Tradeoffs

- versioned AI-DLC mapping requires maintenance but prevents hidden drift
- evidence execution costs more than templated summaries but proves behavior
- strict approvals slow AI-DLC runs but remain profile-specific
- preserving Markdown projections adds synchronization work but keeps human auditability
- Operations handoff avoids claiming unsupported deployment behavior

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| upstream AI-DLC drift | high | pinned profile version and delta review |
| adapter duplicates onboarding | high | explicit intake vs delivery ownership |
| build/test reports fabricated | critical | evidence schema and negative tests |
| brownfield duplicate artifacts | high | existence checks and repository scans |
| methodology overload | medium | minimal-route selector |
| stale approvals after changes | high | artifact/version invalidation |
| Operations scope creep | high | explicit handoff-only contract |

## Context Notes

- Objective planned, not active.
- Adaptive Delivery and stage execution must complete first.
- Security assurance is required before acceptance-sensitive execution.
- `software-onboarding-domain-adapter` remains a separate intake/reconciliation objective.
- `multi-channel-gateway` remains active/recommended.
