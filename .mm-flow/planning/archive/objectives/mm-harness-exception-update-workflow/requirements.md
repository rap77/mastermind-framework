# Requirements — mm-harness-exception-update-workflow

## Problem / Purpose

Creating new exception entries is safer now via scaffold-to-stdout plus
validation. But updating an existing exception entry still requires manual
copy/replace work in raw JSON.

This objective defines the smallest safe update-oriented workflow for existing
active-objective exception entries.

## Stakeholders / Users

- **Primary:** maintainers evolving exception authoring ergonomics
- **Secondary:** operators who need to edit existing exceptions safely
- **Tertiary:** future automation that may want stable update semantics without opaque mutation

## Scope

### In Scope

- define the smallest safe workflow for updating existing exception entries
- preserve artifact inspectability and fail-closed runtime semantics
- reduce manual copy/replace risk compared with the current scaffold-only flow

### Out of Scope

- do not redesign runtime matching semantics
- do not add roadmap exception awareness in this objective
- do not build a general-purpose JSON editor

## Non-negotiables

- single-active remains the default policy
- updated artifacts must remain directly inspectable by another model/operator
- any update help must keep validation explicit in the workflow

## Objective-level Acceptance Criteria

- [ ] update workflow contract is explicit
- [ ] implementation touchpoints are explicit enough to execute safely
- [ ] follow-up tasks are specific enough to execute without improvisation
