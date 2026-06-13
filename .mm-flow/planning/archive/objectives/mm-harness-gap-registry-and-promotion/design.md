# Design — mm-harness-gap-registry-and-promotion

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.
- Reuse the existing MM command/helper pattern and keep the first slice
  file-backed, explicit, and fail-closed.
- Introduce a durable artifact such as:
  - `.mm-flow/planning/gaps/gap-registry.json`
- Gap entries should carry only the minimum phase-1 metadata needed to avoid
  losing context:
  - `id`
  - `title`
  - `status` (`open`, `deferred`, `promoted`, `closed`)
  - `detected_from`
  - `objective_slug`
  - `evidence`
  - `impact`
  - `urgency`
  - `suggested_followup`
  - `promotion_readiness`
  - `promoted_objective_slug` (optional)
- Add a narrow helper surface that can:
  - register a new gap
  - list open gaps
  - mark a gap as promoted to an explicit objective slug
- Prefer append/update semantics that are deterministic and artifact-visible
  over hidden in-memory orchestration.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.
- Prefer explicit operator/model promotion over automatic promotion in phase 1.
- Prefer one durable artifact over scattering follow-up gaps across many handoff
  files without a central index.

## Context Notes
- The harness already records “next gaps” and deferred follow-ups in many
  archived objectives; the missing layer is a central, operable registry.
