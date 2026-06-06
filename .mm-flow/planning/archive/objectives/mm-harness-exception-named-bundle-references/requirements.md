# Requirements — mm-harness-exception-named-bundle-references

## Problem / Purpose

Exception authoring validation now reduces drift, but exceptions and command
bundles still live in separate artifacts with manual cross-file coordination.
Operators still need to know which parent command implies which delegated child
commands.

This objective defines the smallest safe way for exception entries to reference
named command bundles instead of repeating that knowledge manually.

## Stakeholders / Users

- **Primary:** maintainers evolving exception authoring ergonomics
- **Secondary:** operators authoring exception artifacts
- **Tertiary:** future automation that should compose exception entries from reusable command scope definitions

## Scope

### In Scope

- define whether exception entries may reference named command bundles
- preserve current fail-closed runtime semantics
- keep the model explicit enough for another operator/model to inspect from artifacts alone

### Out of Scope

- do not weaken current slug matching or expiration enforcement
- do not add roadmap exception awareness in this objective
- do not build a full exception editor UI

## Non-negotiables

- single-active remains the default policy
- invalid bundle references must fail closed
- another model/operator must be able to resolve a named bundle to effective command scopes from artifacts alone

## Explicit Contract Chosen In T1

- each command bundle entry gets a required stable `name`
- exception entries may use:
  - `commands`
  - `command_bundle_refs`
  - or both
- effective allowed command scopes are:
  - explicit `commands`
  - union parent commands resolved from `command_bundle_refs`
- invalid or unknown bundle refs mean the exception does not match
- validation must surface the effective resolved command scopes to the operator

## Objective-level Acceptance Criteria

- [x] named-bundle reference model is explicit
- [x] runtime/authoring touchpoints are explicit enough to execute safely
- [x] follow-up tasks are specific enough to execute without improvisation
