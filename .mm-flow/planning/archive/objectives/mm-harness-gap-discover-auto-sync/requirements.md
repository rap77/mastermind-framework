# Requirements — mm-harness-gap-discover-auto-sync

## Problem / Purpose
Harness gap discover auto-sync

## T1 Boundary Decision
- This objective is **not** a full automatic lifecycle framework for every objective command.
- The first coherent slice should auto-synchronize the gap registry when `discover --existing --objective` materializes an objective package.
- Phase 1 should stay narrow:
  - successful objective package creation should attempt exact-slug registry sync
  - sync should reuse the existing deterministic `sync-objective` behavior
- Phase 1 should **not** yet:
  - hook roadmap generation
  - auto-register gaps
  - fail objective package creation just because no matching gap exists

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators relying on artifacts instead of chat memory

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- No semantic matching.
- No broad auto-sync across every command in this slice.
- No discover failure caused only by missing/non-matching gap entries.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep artifacts as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
