# Requirements — project-state-mvp

## Problem / Purpose
Project State MVP

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Extend the current `project_state` thin slice without breaking existing endpoints or `/project-state` UI.
- Prefer incremental backend + UI enhancements over large rewrites.
- Keep PostgreSQL as the target architecture and avoid expanding legacy sqlite paths.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
