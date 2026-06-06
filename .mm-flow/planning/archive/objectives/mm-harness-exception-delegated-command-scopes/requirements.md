# Requirements — mm-harness-exception-delegated-command-scopes

## Problem / Purpose

The harness now supports explicit multi-active exceptions at runtime, but a new
coordination gap appeared: some commands delegate to other commands internally.
Today `activate-next-objective` can honor an exception only if the same artifact
also authorizes the delegated `discover --existing --objective` path.

That is safe, but it leaks internal orchestration details into operator-facing
metadata.

This objective defines the smallest safe model for delegated command scopes.

## Stakeholders / Users

- **Primary:** maintainers evolving harness command orchestration
- **Secondary:** operators authoring exception artifacts
- **Tertiary:** future automation that should not need deep knowledge of internal command delegation

## Scope

### In Scope

- define whether delegated commands should inherit exception scope from a parent command
- define the narrowest artifact/runtime rule that preserves fail-closed behavior
- make operator-facing exception authoring guidance less coupled to handler internals

### Out of Scope

- do not redesign the entire exception artifact schema unless required
- do not weaken exact slug-set matching
- do not implement roadmap exception awareness in this objective

## Non-negotiables

- single-active remains the default when no valid exception matches
- delegated-scope behavior must remain deterministic and fail closed
- another model/operator must be able to tell why one command scope implies another

## Explicit Contract Chosen In T1

- delegated scope inheritance is allowed only for **explicitly marked internal delegation**
- phase-1 parent command:
  - `activate-next-objective`
- phase-1 delegated child command:
  - `discover --existing --objective`
- inheritance applies only when `discover` is invoked with an explicit delegation marker from `activate-next-objective`
- direct/manual `discover --existing --objective` invocations do **not** inherit `activate-next-objective` scope
- if the delegation marker is missing, malformed, or unsupported, runtime falls back to normal command-name matching

## Objective-level Acceptance Criteria

- [x] delegated-scope policy is explicit
- [x] artifact/runtime touchpoints are explicit enough to implement safely
- [x] follow-up implementation tasks are specific enough to execute without improvisation
