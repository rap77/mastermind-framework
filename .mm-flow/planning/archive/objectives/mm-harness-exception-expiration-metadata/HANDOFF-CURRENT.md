# Handoff — mm-harness-exception-expiration-metadata

## Current objective
- `mm-harness-exception-expiration-metadata`

## Decisions already made
- Exception slug matching and command-bundle metadata are implemented and archived.
- `expires_when` remains human-readable guidance, but runtime now requires machine-checkable `expires_at_utc`.
- Exceptions match only when `expires_at_utc` parses successfully and is still in the future.
- Missing, malformed, or expired timestamps now fail closed.

## Blockers / risks
- Timestamp-only expiry is deterministic, but less expressive than state-based expiry.
- Existing exception authoring now has two expiration fields to keep aligned (`expires_when` and `expires_at_utc`).

## Deferred follow-up gaps
- Reduce authoring drift between human `expires_when` and machine `expires_at_utc`.
- Decide whether exceptions should support named duration helpers or templates without losing determinism.
- Revisit roadmap exception awareness now that slug, bundle, and expiration semantics are artifact-visible.

## Exact next recommended task
- All objective tasks are complete; run `/mm:archive-objective mm-harness-exception-expiration-metadata` and open the next exception-related follow-up objective.

## Validation commands
- `/mm:discover-contract-check --objective mm-harness-exception-expiration-metadata`
- `python3 -m unittest tests.unit.test_mm_discover_workflow`
