# Requirements — mm-harness-exception-authoring-workflow

## Problem / Purpose

Exception authoring is now much safer thanks to validation, named bundle refs,
and machine-checkable expiration. But operators still edit raw JSON artifacts by
hand to create or update an exception entry.

This objective defines the smallest safe authoring workflow for creating/updating
active-objective exceptions without weakening transparency.

## Stakeholders / Users

- **Primary:** maintainers evolving exception authoring ergonomics
- **Secondary:** operators who need to add or update exceptions safely
- **Tertiary:** future automation that may want a stable authoring entrypoint instead of raw file edits

## Scope

### In Scope

- define the smallest safe workflow for creating/updating exception entries
- preserve artifact visibility and fail-closed runtime semantics
- reduce manual JSON editing without hiding the effective machine policy

### Out of Scope

- do not redesign runtime matching semantics
- do not add roadmap exception awareness in this objective
- do not build a UI or external service

## Non-negotiables

- single-active remains the default policy
- the resulting artifacts must remain directly inspectable by another model/operator
- authoring help must not bypass validation or runtime safety

## Explicit Contract Chosen In T1

- phase-1 authoring workflow is **scaffold + validate**, not in-place mutation
- a helper command will generate one exception-entry JSON skeleton to stdout
- operator flow becomes:
  1. run scaffold helper with explicit args
  2. paste entry into `active-objective-exceptions.json`
  3. run `validate-active-objective-exceptions.py`
- updates use the same flow by regenerating a corrected entry and replacing the old one manually

## Objective-level Acceptance Criteria

- [x] authoring workflow contract is explicit
- [x] implementation touchpoints are explicit enough to execute safely
- [x] follow-up tasks are specific enough to execute without improvisation
