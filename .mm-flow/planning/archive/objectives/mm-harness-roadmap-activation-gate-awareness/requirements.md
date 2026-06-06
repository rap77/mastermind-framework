# Requirements — mm-harness-roadmap-activation-gate-awareness

## Problem / Purpose

The harness now enforces `objective-context-check` on the direct objective
materialization path:

- `context-to-canonical`
- `objective-context-check`
- `discover --existing --objective <slug>`

But roadmap and activation surfaces still behave as if gate state does not
exist. Today the system can still:

- recommend an objective in roadmap outputs without surfacing its gate state
- tell the operator to run `/mm:activate-next-objective` even when queued
  canonical objectives may still be blocked by `NOT_RUN`, `NEEDS_INPUT`, or
  `FAILED`
- fail late inside activation/discover rather than giving queue-aware guidance

This objective extends gate awareness from the direct objective path into the
roadmap / activation layer.

## Stakeholders / Users

- **Primary:** maintainers evolving MasterMind into a stronger harness
- **Secondary:** operators using roadmap generation and `/mm:activate-next-objective`
- **Tertiary:** future automation that needs queue-level readiness signals

## Scope

### In Scope

- Define how roadmap/activation surfaces reason about gate status for queued
  canonical objectives
- Surface gate status or queue readiness in at least one roadmap artifact
- Add preflight behavior to `activate-next-objective` when the recommended
  objective has a matching canonical objective with unsatisfied gate status
- Keep the direct objective gate logic as the source of truth; do not duplicate
  validation rules
- Refresh handoff/docs so another model knows when queue activation is safe

### Out of Scope

- Do not redesign the entire roadmap ranking model
- Do not introduce a global lifecycle database/state machine
- Do not force every roadmap objective to require a canonical objective
- Do not replace `discover` / `activate-next-objective` with a new command

## Non-negotiables

- The gate remains model/runtime agnostic
- `.mm-flow/commands/mm/*.py` remains the source of truth
- Queue-level guidance must not contradict direct objective discover guidance
- Enforcement should remain incremental and safe for existing projects
- Another model/operator must be able to infer why activation is blocked

## Decisions Already Implied

- Direct objective discover already blocks on unsatisfied gate status when a
  matching canonical objective exists
- The next safe step is not broad blocking everywhere; it is queue-aware
  signaling and targeted activation preflight
- Roadmap outputs may need to distinguish general readiness (`ready_now`) from
  gate readiness for canonical objectives

## Objective-level Acceptance Criteria

- [ ] roadmap or handoff artifacts surface gate-aware queue readiness for at
      least one relevant path
- [ ] `activate-next-objective` does not fail opaquely when the recommended
      objective has a canonical objective blocked by gate status
- [ ] guidance distinguishes `PASSED|FAILED|NEEDS_INPUT|NOT_RUN` or an explicit
      equivalent at the queue/activation layer
- [ ] direct objective discover behavior remains unchanged and compatible
