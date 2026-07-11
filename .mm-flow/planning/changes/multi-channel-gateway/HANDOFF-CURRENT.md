# Handoff — multi-channel-gateway

## Current objective
- `multi-channel-gateway`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.
- The follow-up slice is reliability semantics attached to the canonical inbound event contract, not a full gateway rebuild.
- The canonical inbound contract already lives in `apps/api/routers/canonical_events.py` and its test coverage is the reference boundary.

## Blockers / risks
- The package is narrow and should stay read-only / contract-first.
- Historical legacy material may still exist under archive/legacy, but it is not part of the active workflow.

## Exact next recommended task
- Start with `T3` from `tasks.md`: refresh handoff and archive the objective package when ready.

## Validation commands
- `/mm:discover-contract-check --objective multi-channel-gateway`
- Run targeted tests for touched files before handing off again
