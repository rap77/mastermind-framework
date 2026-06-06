# Tasks — mm-harness-exception-authoring-drift-reduction

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: improve authoring consistency without weakening fail-closed exception behavior.

## T1: Define drift-reduction contract

### Purpose

Make the smallest safe drift-reduction strategy explicit before changing tooling or artifacts.

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

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-authoring-drift-reduction`

### Acceptance Criteria

- [x] drift-reduction strategy is explicit
- [x] implementation touchpoints are explicit
- [x] remaining tasks are specific enough to execute without improvisation

## T2: Implement the smallest drift-reduction slice

### Purpose

Apply the chosen strategy to reduce exception authoring inconsistencies.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/validate-active-objective-exceptions.py`
- `.mm-flow/planning/active-objective-exceptions.json`
- `.mm-flow/planning/active-objective-command-bundles.json`
- authoring docs/examples

### Validation Commands

- `python3 .mm-flow/commands/mm/validate-active-objective-exceptions.py`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-authoring-drift-reduction`

### Acceptance Criteria

- [x] chosen drift source is reduced deterministically
- [x] current runtime semantics remain intact
- [x] another operator can author exceptions more safely

## T3: Refresh continuity and record the next gap

### Purpose

Document the new authoring rule and record the next strongest exception-related gap.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`
- docs/examples if messaging changes

### Validation Commands

- `python3 .mm-flow/commands/mm/validate-active-objective-exceptions.py`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-authoring-drift-reduction`

### Acceptance Criteria

- [x] handoff explains the drift-reduction rule clearly
- [x] next exception-related gap is recorded explicitly
- [x] another model can continue from artifacts alone
