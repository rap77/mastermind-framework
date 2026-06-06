# Requirements — mm-harness-exception-expiration-metadata

## Problem / Purpose

Multi-active exceptions are now artifact-visible for both objective slug sets and
command bundles, but expiration is still plain-language text in `expires_when`.
That leaves stale exceptions dependent on operator cleanup and weakens
artifact-only reasoning.

This objective defines the smallest machine-checkable expiration model.

## Stakeholders / Users

- **Primary:** maintainers evolving exception lifecycle safety
- **Secondary:** operators authoring exception artifacts
- **Tertiary:** future automation that should detect stale exceptions deterministically

## Scope

### In Scope

- define a machine-checkable expiration model for active-objective exceptions
- preserve existing fail-closed behavior when expiration metadata is missing or invalid
- keep the model small enough to adopt without redesigning all exception artifacts

### Out of Scope

- do not redesign slug matching or command-bundle matching
- do not add roadmap exception awareness in this objective
- do not build a full scheduling system or background cleanup job

## Non-negotiables

- single-active remains the default policy
- invalid expiration metadata must fail closed
- another model/operator must be able to tell whether an exception is still active from artifacts alone

## Explicit Contract Chosen In T1

- each exception entry keeps human-readable `expires_when`
- each exception entry now also requires machine-checkable:
  - `expires_at_utc`
- `expires_at_utc` must be an ISO-8601 UTC timestamp using `Z`, for example:
  - `2026-12-31T23:59:59Z`
- runtime matches an exception only when:
  - `expires_at_utc` parses successfully
  - current UTC time is strictly before that timestamp
- missing, malformed, or already-expired `expires_at_utc` means the exception does not match

## Objective-level Acceptance Criteria

- [x] machine-checkable expiration contract is explicit
- [x] runtime touchpoints are explicit enough to implement safely
- [x] follow-up tasks are specific enough to execute without improvisation
