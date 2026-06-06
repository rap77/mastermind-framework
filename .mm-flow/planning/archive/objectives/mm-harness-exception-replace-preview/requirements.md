# Requirements — mm-harness-exception-replace-preview

## Problem / Purpose

Exception authoring now supports:

- scaffold-to-stdout for new entries
- render-by-id for existing entries
- replace-by-id from an explicit JSON file
- explicit validation after replacement

The strongest remaining ergonomics gap is lack of a narrow preview/diff step
before the replace helper writes the artifact.

This objective defines the smallest auditable preview workflow for exception
replacement operations.

## Stakeholders / Users

- **Primary:** maintainers improving exception-authoring safety
- **Secondary:** operators who want confidence before a replace-by-id write
- **Tertiary:** future automation that may want a dry-run surface

## Scope

### In Scope

- define the smallest safe preview/diff workflow for one replace-by-id action
- preserve explicit replacement payload visibility
- keep validation explicit and separate from preview

### Out of Scope

- do not redesign runtime exception semantics
- do not build a full artifact diff engine
- do not add generic batch preview support

## Non-negotiables

- replacement preview must remain narrow and deterministic
- artifacts must stay inspectable by another model/operator
- preview must not silently mutate the exception artifact

## Objective-level Acceptance Criteria

- [ ] preview workflow contract is explicit
- [ ] implementation touchpoints are specific enough to execute safely
- [ ] follow-up tasks are concrete enough to continue without improvisation
