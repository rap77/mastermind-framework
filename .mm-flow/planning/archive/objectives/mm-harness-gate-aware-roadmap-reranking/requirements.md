# Requirements — mm-harness-gate-aware-roadmap-reranking

## Problem / Purpose

The harness already surfaces gate status in roadmap artifacts and blocks later at
activation/discover time, but the roadmap recommendation itself can still point
at a gate-blocked objective when a lower-priority gate-ready objective exists.

Today this creates unnecessary operator churn:

- roadmap says objective A is recommended
- activation blocks because objective A is `NOT_RUN`, `NEEDS_INPUT`, or `FAILED`
- the operator must interpret artifacts manually even though objective B is
  already ready to activate

This objective makes roadmap recommendation itself gate-aware.

## Stakeholders / Users

- **Primary:** maintainers evolving the MasterMind harness
- **Secondary:** operators using `/mm:discover --roadmap --existing` and
  `/mm:activate-next-objective`
- **Tertiary:** future automation that expects recommended objectives to be
  directly actionable

## Scope

### In Scope

- adjust roadmap recommendation so it prefers gate-ready objectives among
  candidates that are otherwise `ready_now`
- define what “gate-ready” means for roadmap selection
- preserve gate visibility in roadmap artifacts for blocked candidates
- keep activation/discover gate checks as downstream safety nets

### Out of Scope

- do not redesign the full objective priority model
- do not hide gate-blocked objectives from the roadmap entirely
- do not remove activation/discover blocking even when reranking improves
  recommendations

## Non-negotiables

- `.mm-flow/commands/mm/*.py` remains the source of truth
- gate-ready objectives should be preferred, not fabricated
- roadmap should still show blocked candidates and their gate status
- deterministic priority order should remain intact inside the gate-ready pool

## Decisions Already Implied

- `PASSED` and `NO_CANONICAL` are activation-ready
- `NOT_RUN`, `NEEDS_INPUT`, and `FAILED` are not activation-ready
- gate-aware reranking is a recommendation improvement, not a replacement for
  activation/discover safety checks

## Objective-level Acceptance Criteria

- [ ] roadmap recommendation prefers a gate-ready objective when a
      higher-priority candidate is gate-blocked
- [ ] roadmap artifacts still expose gate status for blocked candidates
- [ ] activation follows the reranked recommendation without breaking existing
      gate-safety behavior
