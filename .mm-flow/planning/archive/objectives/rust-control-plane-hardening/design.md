# Design — rust-control-plane-hardening

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance
  criteria.
- Reuse the existing control-plane auth boundaries instead of redesigning the
  token model in phase 1.

### Chosen phase-1 slice

Phase 1 hardens **only the refresh-token lookup and rotation path** in
`rust_control_plane`.

Current defect observed in `src/handlers/auth.rs`:

- the refresh handler bcrypt-hashes the presented refresh token
- then tries to query `sessions.refresh_token_hash = $1`

That is not correct because bcrypt hashes are salted; hashing the same refresh
token twice does not produce the same value.

### Phase-1 approach

The smallest safe fix is:

1. query active, non-expired refresh-token sessions
2. verify the presented token against stored bcrypt hashes with
   `bcrypt::verify`
3. identify the matching session deterministically
4. rotate from the matched stored hash, not from a newly generated hash

This keeps the external contract stable while restoring correctness.

### Implemented phase-1 behavior

The refresh flow now:

1. loads active, non-expired sessions
2. verifies the presented refresh token against stored bcrypt hashes with
   `bcrypt::verify`
3. identifies the matching stored session
4. rotates using the matched stored hash instead of a newly re-hashed value

This restores correctness without changing the external request/response
contract for refresh.

## Dependencies
- Depends on `backend-service-boundary-for-agents`

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.
- Prefer restoring refresh correctness now over solving all auth placeholders at
  once.

## Context Notes
- Worker/gRPC, migration hygiene, and logout placeholder remain valid follow-up
  gaps, but they stay out of scope for this first hardening slice.
