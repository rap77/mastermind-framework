# Requirements — knowledge-distillation

## Problem / Purpose
Historical Phase 14 already implemented key knowledge-distillation backend pieces:
experience logging, template extraction, analytics endpoints, and quality-score
tracking. The current objective package is too broad to execute safely because
the repo no longer has an explicit active slice around the product-facing gap.
The clearest current gap is that these analytics/templates surfaces exist in
the backend, but the current web console does not expose them as a live
operator-facing view.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.
- Phase 1 scope is limited to exposing existing knowledge-distillation signals
  in a current UI surface, reusing existing backend analytics routes where
  possible.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- Do not redesign the distillation pipeline, scoring model, or template
  extraction rules in this slice.
- Do not re-implement historical Phase 14 backend work that already exists.
- Do not introduce a new persistence model if current analytics/template routes
  are sufficient for an initial read-only surface.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
