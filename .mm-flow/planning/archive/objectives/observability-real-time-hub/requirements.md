# Requirements — observability-real-time-hub

## Problem / Purpose
The historical “observability + real-time hub” phase was broad and already
landed infrastructure across Rust, Python, and the web layer, but the current
objective package is too vague to execute safely. In the current repo, the most
immediate product-facing gap is that `/project-state` has live SSE refresh and
the web app already has a reusable `BrainStatusFeed`, yet the project-state
surface still does not expose read-only brain-event observability directly.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.
- Phase 1 scope is limited to making existing real-time brain-event visibility
  available from the `/project-state` UI by reusing current web and Rust
  surfaces.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- Do not replace the current `/project-state` SSE refresh model.
- Do not redesign the Rust WebSocket protocol, Ghost Mode, or tracing stack.
- Do not add Prometheus/Datadog export wiring in this slice.
- Do not create a new backend observability API if the existing `/ws/events`
  feed is enough for an initial read-only panel.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
