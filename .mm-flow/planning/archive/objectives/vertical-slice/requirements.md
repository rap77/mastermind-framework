# Requirements — vertical-slice

## Problem / Purpose
Vertical Slice

## T1 Boundary Decision
- This objective is **not** a greenfield rebuild of the historical Phase 13
  vertical slice.
- Planning sources already mark Phase 13 as completed; the current gap is
  **contract drift risk** in the surviving vertical-slice surfaces.
- The first coherent slice should focus on the narrowest high-value seam:
  **TypeScript proto parity** for the `DispatchTask` contract used by the
  Next.js → Rust entrypoint.
- The current repository still ships a manual TypeScript shim with an explicit
  TODO to generate from `proto/mastermind/v1/brain_runtime.proto`, which means
  the architecture may be historically validated but still operationally drift-prone.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- Do not reimplement the full Next.js → Rust → gRPC → Python path in this
  slice.
- Do not introduce a new proto generation toolchain if existing local tooling
  is unavailable.
- Do not fold in unrelated Rust control-plane or FastAPI runtime issues.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
