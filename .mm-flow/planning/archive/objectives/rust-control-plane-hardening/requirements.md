# Requirements — rust-control-plane-hardening

## Problem / Purpose
The canonical Rust control plane still has at least one critical auth defect in
its refresh-token flow: it appears to re-hash the presented refresh token and
then tries to match that new bcrypt hash by equality in the `sessions` table.

Because bcrypt is salted, that lookup cannot work reliably. Before expanding
the Rust control plane further, the first hardening slice should restore a
correct and testable refresh-token rotation path.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without
  rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental
  architecture.
- In phase 1, focus specifically on the Rust refresh-token lookup/rotation
  path.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- Do not solve worker/gRPC, migration hygiene, or DLQ gaps in this first slice.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
