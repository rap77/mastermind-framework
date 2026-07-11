# Requirements — knowledge-ingestion-manual

## Problem / Purpose
Knowledge Ingestion (Manual)

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: humans preparing distilled FUENTE sources for domain_knowledge ingestion

## Scope
- Deliver the smallest coherent slice that proves the manual ingestion path is auditable and deterministic.
- Preserve backend-authority boundaries and the current incremental architecture.
- Initial slice: validate the preview-first manual ingestion flow for distilled FUENTE sources.

## Out of Scope
- No automated embedding writes in this objective.
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- No knowledge base redesign or vector-store migration.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [x] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [x] The manual ingestion preview contract is validated end-to-end.
- [x] Validation commands are documented and usable by another model or human operator.
