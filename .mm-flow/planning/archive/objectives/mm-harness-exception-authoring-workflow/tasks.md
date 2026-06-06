# Tasks — mm-harness-exception-authoring-workflow

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: improve exception authoring workflow without weakening validation or runtime safety.

## T1: Define exception authoring workflow contract

### Purpose

Make the smallest safe authoring workflow explicit before adding helper tooling.

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `requirements.md`
- `design.md`
- `tasks.md`
- `todo.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-authoring-workflow`

### Acceptance Criteria

- [x] authoring workflow contract is explicit
- [x] implementation touchpoints are explicit
- [x] remaining tasks are specific enough to execute without improvisation

## T2: Implement the smallest authoring workflow slice

### Purpose

Add the chosen helper/template flow and connect it to validation.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/scaffold-active-objective-exception.py`
- exception authoring docs/examples
- `.mm-flow/commands/mm/validate-active-objective-exceptions.py`

### Validation Commands

- `python3 .mm-flow/commands/mm/scaffold-active-objective-exception.py --help`
- `python3 .mm-flow/commands/mm/scaffold-active-objective-exception.py ...`
- `python3 .mm-flow/commands/mm/validate-active-objective-exceptions.py`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-authoring-workflow`

### Acceptance Criteria

- [x] new authoring workflow reduces raw JSON editing risk
- [x] validation remains part of the workflow
- [x] artifacts remain directly inspectable

## T3: Refresh continuity and record the next gap

### Purpose

Document the new authoring workflow and record the next strongest exception-related gap.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`
- docs/examples if messaging changes

### Validation Commands

- `python3 .mm-flow/commands/mm/scaffold-active-objective-exception.py --help`
- `python3 .mm-flow/commands/mm/validate-active-objective-exceptions.py`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-authoring-workflow`

### Acceptance Criteria

- [x] handoff explains the workflow clearly
- [x] next exception-related gap is recorded explicitly
- [x] another model can continue from artifacts alone
