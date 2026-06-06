# Requirements — mm-harness-multi-active-exception-runtime-recognition

## Problem / Purpose

The harness now has a documented phase-1 contract for intentional multi-active
exceptions, but runtime coordination still ignores it. `discover --existing
--objective <slug>` and `activate-next-objective` continue to behave as strict
single-active entrypoints even when an explicit exception artifact should allow
coexistence.

This objective implements the smallest safe runtime recognition path.

## Stakeholders / Users

- **Primary:** maintainers evolving advanced harness workflows
- **Secondary:** operators intentionally coordinating a narrow pair/set of objectives
- **Tertiary:** future automation that must distinguish default blocking from approved exceptions

## Scope

### In Scope

- parse `.mm-flow/planning/active-objective-exceptions.json` deterministically
- centralize exception interpretation in `active-objective-state.py`
- let `discover --existing --objective <slug>` honor an exact-match exception
- let `activate-next-objective` honor an exact-match exception
- emit operator-visible explanation when an exception is used

### Out of Scope

- do not broaden exception semantics beyond exact slug-set matching
- do not make roadmap recommendation logic exception-aware yet
- do not add machine-checkable expiration in this objective

## Non-negotiables

- single-active remains the default when no valid exception matches
- invalid or partial exception metadata must degrade safely to current blocking behavior
- commands may honor only exceptions that explicitly list them in `commands`
- operator output must make the matched exception visible

## Objective-level Acceptance Criteria

- [x] shared exception parser/recognizer exists in `active-objective-state.py`
- [x] `discover --existing --objective <slug>` honors valid matching exceptions
- [x] `activate-next-objective` honors valid matching exceptions
- [x] tests prove both matching and non-matching paths
