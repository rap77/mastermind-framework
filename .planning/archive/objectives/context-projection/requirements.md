# Requirements — context-projection

## Problem / Purpose
Provide the smallest execution-ready context projection slice for project-state tasks.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver task-level and doctrine-level context projections from structured project state.
- Keep the slice read-only and backend-authoritative.
- Preserve the current incremental architecture and existing API/service boundaries.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- No broader dashboard rebuild, streaming layer, or model-only continuity path.
- Do not bypass backend services with direct model/database access.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective is constrained to `TaskContextProjectionResponse` and `DoctrineProjectionResponse` as the initial slice.
- [ ] The projection is derived from structured project state and stays backend-authoritative.
- [ ] Validation commands are documented and usable by another model or human operator.
