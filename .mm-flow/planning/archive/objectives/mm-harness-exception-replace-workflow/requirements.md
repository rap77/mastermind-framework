# Requirements — mm-harness-exception-replace-workflow

## Problem / Purpose

Exception authoring now supports:

- scaffold-to-stdout for new entries
- render-by-id for existing entries
- explicit validation after editing

The weakest remaining step is replacing the rendered entry back into
`active-objective-exceptions.json` safely and repeatably.

This objective defines the smallest auditable replace-by-id workflow for active
objective exception entries.

## Stakeholders / Users

- **Primary:** maintainers tightening exception authoring ergonomics
- **Secondary:** operators updating one existing exception entry safely
- **Tertiary:** future automation that needs stable replace semantics

## Scope

### In Scope

- define the smallest safe replace-by-id workflow for one exception entry
- preserve direct inspectability of the artifact transition
- keep validation explicit in the replacement workflow

### Out of Scope

- do not redesign runtime semantics
- do not build a general-purpose JSON mutation tool
- do not add broad batch-edit support

## Non-negotiables

- single-active remains the default policy
- exception artifacts must remain legible to another model/operator
- replacement help must stay fail-closed and explicit

## Objective-level Acceptance Criteria

- [ ] replace-by-id workflow contract is explicit
- [ ] implementation touchpoints are specific enough to execute safely
- [ ] follow-up tasks are concrete enough to continue without improvisation
