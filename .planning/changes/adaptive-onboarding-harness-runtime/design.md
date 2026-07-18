# Design — adaptive-onboarding-harness-runtime

## Architecture / Boundaries

```text
OnboardingRequest
  -> ModeDomainClassifier
  -> EvidenceInventoryService
  -> CurrentStateAnalyzer
  -> TargetStateBuilder
  -> MultiPassGapAnalyzer
  -> ReadinessService
  -> ExecutionWavePlanner
  -> HarnessDelegator
       -> RunBundleStageExecutor
  -> ReassessmentService
  -> FinalVerdict and Handoff
```

- core owns lifecycle, readiness and continuity
- domain adapter owns domain schema/rules/projections
- delegated harness owns execution result
- security assurance owns security verdict
- project state owns structured persistence
- Markdown owns human-readable canonical artifacts

## Technical Approach

### Universal models

Add typed contracts for request/profile, evidence, current/target snapshots,
gaps, readiness, waves, delegation and reassessment delta.

### Mode/domain classifier

Prefer explicit manifests and existing state. Text inference is fallback and
must emit rationale. Incidental domain words cannot select an adapter.

### Multi-pass gap runtime

Run evidence, structure, domain, security/risk, execution and measurement
lenses. Deduplicate by stable identity plus target requirement. Enforce max
iterations and no-new-material-gap stop rules.

### Adapter registry

Each adapter declares evidence types, schema extensions, readiness dimensions,
security overlay, required approvals, execution harnesses and projections.

### Delegation

Wave planner selects dependency-ready gaps. HarnessDelegator composes a
RunBundle and records delegation lineage. Result returns to reassessment.

### Software adapter seam

- AI-DLC Discovery writes `Product-Definition/`
- reverse engineering supplies brownfield evidence
- open questions join resolves contradictions
- MM-flow writes roadmap/objective packages
- mutating waves delegate to `adaptive-delivery-lead` plus a domain delivery adapter
- read-only waves may delegate directly to specialized verification/review harnesses

This objective validates the onboarding adapter contract with a fixture. The
production Software Onboarding Adapter belongs to the separate
`software-onboarding-domain-adapter` roadmap objective.

### Security

Consume `domain-security-assurance-plane` contracts. Security verdict can block
readiness independently from aggregate quality.

## Dependencies

- `domain-security-assurance-plane`
- `harness-stage-execution-runtime`
- `engineering-doctrine-layer`
- `artifact-versioning-and-lineage`
- `project-state-mvp`
- `docs/canonical/111-ADAPTIVE-ONBOARDING-HARNESS-RUNTIME-CONTRACT.md`
- existing AI-DLC Discovery, MM-flow Discovery and multi-harness runtime

## Validation Strategy

- unit tests for classifier, state contracts, gaps, stop rules, readiness, waves
- behavioral cases for every onboarding mode
- adapter contract tests
- integration greenfield and brownfield software cases
- security veto and missing-adapter paths
- existing harness routing regressions
- contract checks and ruff, without build

## Important Tradeoffs

- domain adapters reduce duplication but require strict contracts
- delegation adds orchestration complexity but prevents monolithic agents
- target-state approval can slow intake but avoids endless “improvement” loops
- software pilot validates core before marketing/finance implementation

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| endless gap loop | high | bounded passes and stop rules |
| false readiness | critical | evidence gates and vetoes |
| domain leakage into core | high | adapter contract tests |
| duplicate sources of truth | high | explicit artifact ownership |
| execution supervisor becomes executor | high | delegation boundary |
| stale current state | medium | versioned delta reassessment |

## Context Notes

- Objective planned, not active.
- Security and shared stage execution objectives must complete first.
- Software/Marketing/Finance onboarding adapters remain separate roadmap work.
