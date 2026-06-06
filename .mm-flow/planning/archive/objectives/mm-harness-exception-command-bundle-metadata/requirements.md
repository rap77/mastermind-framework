# Requirements — mm-harness-exception-command-bundle-metadata

## Problem / Purpose

Delegated multi-active exception scopes now work at runtime, but the delegation
relationship is still hardcoded in `active-objective-state.py`. Operators can
benefit from simpler artifact authoring, yet another model/operator still cannot
infer the command-bundle relationship directly from planning artifacts.

This objective defines the smallest artifact-visible model for exception command
bundles or delegation relationships.

## Stakeholders / Users

- **Primary:** maintainers evolving exception semantics
- **Secondary:** operators authoring `active-objective-exceptions.json`
- **Tertiary:** future automation that should infer exception scope rules from artifacts, not runtime code alone

## Scope

### In Scope

- define whether command bundles/delegation relationships should become artifact-visible
- choose the smallest safe artifact model
- preserve the current fail-closed runtime semantics unless the metadata is explicit and valid

### Out of Scope

- do not redesign objective slug matching
- do not add roadmap exception awareness in this objective
- do not add machine-checkable expiration unless it becomes inseparable from the chosen model

## Non-negotiables

- single-active remains the default policy
- invalid or missing bundle metadata must degrade safely to current behavior
- another model/operator must be able to explain why one command scope implies another

## Explicit Contract Chosen In T1

- command-bundle relationships live in a separate root artifact:
  - `.mm-flow/planning/active-objective-command-bundles.json`
- phase-1 schema is:
  - `version` (required integer)
  - `bundles` (required list)
  - each bundle has:
    - `parent_command` (required string)
    - `delegated_commands` (required non-empty list of strings)
    - `reason` (required string)
- delegated scope inheritance is allowed only when:
  - the child command is invoked with `--delegated-from <parent>`
  - the bundle artifact explicitly lists that parent -> child relationship
  - the exception entry itself authorizes the `parent_command`
- direct/manual child command invocation does not inherit parent scope

## Objective-level Acceptance Criteria

- [x] artifact-visible bundle/delegation model is explicit
- [x] runtime touchpoints are explicit enough to implement safely
- [x] next tasks are specific enough to execute without improvisation
