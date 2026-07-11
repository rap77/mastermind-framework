# Requirements — multi-channel-gateway

## Problem / Purpose
Attach reliability semantics to the existing canonical inbound event contract for multi-channel messages.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances reliability on the existing canonical inbound event contract.
- Preserve backend-authority boundaries and the current incremental architecture.
- Initial slice: idempotency / verification semantics around the canonical inbound contract already modeled in `apps/api/routers/canonical_events.py`.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- No full inbox rebuild, provider-complete integrations, or new queue/storage layer in the first slice.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [x] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [x] Validation commands are documented and usable by another model or human operator.
