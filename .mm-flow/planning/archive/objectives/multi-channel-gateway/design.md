# Design — multi-channel-gateway

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.
- Reuse existing channel senders and the internal gRPC/worker bridge instead of
  inventing a second gateway path.
- Prefer a typed normalization seam for inbound events before queue, retry, or
  UI work expands.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.
- Prefer backend contract clarity over premature infra hardening.
- Prefer an ACL/normalization seam over leaking provider payload schemas into
  the domain.

## Context Notes
- Historical roadmap says Phase 18 was “completed”, but current repo evidence
  shows mostly channel send helpers plus worker routing, not an obviously
  complete inbound normalization/reliability stack.
- Frontend/backends notes already point to a need for a unified internal event
  shape (`message_received` across whatsapp/instagram/email).

## T1 Implementation Direction

### Chosen phase-1 slice
- Define the current objective around **unified inbound event normalization**.
- The implemented T2 slice creates:
  - a typed internal event shape in `apps/api/routers/canonical_events.py`
  - provider-to-internal normalization helpers for WhatsApp, Instagram, and
    Email payload families
  - focused tests proving those payload classes map to one canonical contract
  - gRPC worker logging that now records normalized event identifiers through
    the Python bridge

### Why this slice
- It closes the most dangerous ambiguity first: what the system considers a
  channel message internally.
- It preserves backend authority and keeps later idempotency/DLQ work attached
  to a stable contract.
- It avoids reopening a large UI or provider-integration program before the
  contract is explicit.

### Explicit non-goals for T2
- no full inbox UI
- no Redis queue
- no DLQ implementation
- no full webhook verification workflow
- no cross-channel routing intelligence beyond basic normalization

## Next Likely Follow-up
- The next gap after canonical normalization is **reliability policy attached to
  the contract**, most likely:
  - explicit idempotency/dedup semantics
  - webhook verification at the receiver boundary
  - durable ingest/audit persistence keyed by canonical identifiers
