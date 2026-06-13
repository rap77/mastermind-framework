# Design — vertical-slice

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.
- Reframe this objective as a **foundation verification / drift reduction**
  slice around the already-shipped Phase 13 architecture.
- Treat `proto/mastermind/v1/brain_runtime.proto` as the source of truth and
  the manual TypeScript shim in `apps/web/src/proto/brain_runtime.ts` as the
  likely drift surface.
- Prefer a narrow verification or parity-enforcement surface over introducing
  a full proto codegen toolchain in this slice.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.
- Prefer contract-drift reduction over re-running the whole historical phase.
- Prefer a local parity check / guardrail over adding new infra dependencies.

## Context Notes
- `.planning/ROADMAP.md` and `.planning/SOURCE-OF-TRUTH.md` already mark
  Vertical Slice as complete; the remaining value is making the surviving
  contract surfaces less brittle.
