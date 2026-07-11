# Design — multi-channel-gateway

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- The slice stays backend-authoritative and should extend the canonical inbound contract rather than introducing a new gateway path.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that adds reliability semantics to the existing canonical inbound contract.
- Reuse the existing `project_state` incremental domain, `canonical_events.py`, and MM command infrastructure where possible.
- Keep the slice read-only / contract-first; do not add a new queue or storage layer in T1.

## Dependencies
- Depends on `project-state-mvp`
- Depends on the existing canonical inbound event model already present in `apps/api/routers/canonical_events.py`

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.

## Context Notes
- Existing API coverage already includes canonical inbound event normalization tests; the follow-up should attach idempotency / verification behavior to that contract.
