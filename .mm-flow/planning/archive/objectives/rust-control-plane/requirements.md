# Requirements — rust-control-plane

## Problem / Purpose
The broader Rust control-plane objective is too large to take in one step. The
auth surface slice, explicit AI-worker boundary slice, metrics latency slice,
email thread-id normalization slice, DLQ test-contract slice, typed
AI-worker startup/runtime seam slice, retained-client runtime slice, first
typed dispatch slice, degraded-runtime fail-closed slice, post-dispatch
success-semantics slice, durable success-audit slice, durable failure-audit
slice, AI-worker audit-taxonomy slice, audit-query ergonomics slice, and
audit-convenience decision slice are now closed, so the next smallest coherent
slice is to decide whether this Rust objective still has a material gap or is
ready to close.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without
  rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental
  architecture.
- Phase 16 scope is limited to clarifying whether the current Rust control-plane
  objective still has a remaining material gap after the AI-worker audit work.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- Do not redesign retry policy, DLQ semantics, or the full readiness contract.
- Do not broaden this into general warning cleanup across the Rust crate.
- Do not reopen degraded-mode error handling unless a validation failure proves
  it regressed.
- Do not change the newly clarified meaning of `messages.status = completed`
  unless tests prove another contract is required.
- Do not remove the new durable success-audit record unless a narrower audit
  surface replaces it.
- Do not remove the new durable failure-audit record unless a narrower audit
  surface replaces it.
- Do not introduce a broad new audit API if a narrow filter on existing audit
  surfaces is sufficient.
- Do not broaden audit filtering beyond `message_id` / `trace_id` unless tests
  prove a concrete lookup workflow still remains awkward.
- Do not create a dedicated AI-worker convenience surface unless existing audit
  filters demonstrably fail a concrete operator workflow.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
