# Requirements — mm-harness-exception-authoring-drift-reduction

## Problem / Purpose

Active-objective exceptions now have artifact-visible slug sets, command bundles,
and machine-checkable expiration. But authoring still requires operators to keep
human and machine fields aligned manually, especially `expires_when` and
`expires_at_utc`.

This objective defines the smallest safe way to reduce exception authoring drift.

## Stakeholders / Users

- **Primary:** maintainers evolving exception authoring ergonomics
- **Secondary:** operators writing exception artifacts by hand
- **Tertiary:** future automation that should generate or validate exception artifacts consistently

## Scope

### In Scope

- define the smallest safe strategy to reduce drift between human and machine exception metadata
- preserve fail-closed runtime behavior
- keep the model explainable to another model/operator from artifacts alone

### Out of Scope

- do not weaken current slug matching, bundle matching, or expiration enforcement
- do not add roadmap exception awareness in this objective
- do not build a full interactive exception editor

## Non-negotiables

- single-active remains the default policy
- runtime stays fail closed on invalid exception metadata
- any ergonomics improvement must not hide the effective machine policy

## Explicit Contract Chosen In T1

- phase-1 drift reduction is **validation-first**, not generation-first
- `expires_when` remains human-readable, but must start with the exact machine expiry:
  - `Expires at <expires_at_utc> — ...`
- a dedicated validation helper should fail when:
  - `expires_at_utc` is missing or invalid
  - `expires_when` is missing
  - `expires_when` does not start with `Expires at <expires_at_utc>`
- the helper should also validate that any delegated command bundle artifact is structurally sound

## Objective-level Acceptance Criteria

- [x] drift-reduction strategy is explicit
- [x] implementation touchpoints are explicit enough to execute safely
- [x] follow-up tasks are specific enough to execute without improvisation
