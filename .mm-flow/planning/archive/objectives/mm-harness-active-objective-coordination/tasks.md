# Tasks — mm-harness-active-objective-coordination

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints,
  validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: prefer explicit coordination
  policy and deterministic guidance over broad refactors.

## T1: Define active-objective coordination policy

### Purpose

Make the intended single-active vs multi-active policy explicit before changing
behavior.

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `requirements.md`
- `design.md`
- `tasks.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-active-objective-coordination`

### Acceptance Criteria

- [x] the coordination policy is explicit
- [x] the affected entrypoints are explicit
- [x] the remaining tasks are specific enough to execute without improvisation

## T2: Align discover/activation behavior with the coordination policy

### Purpose

Prevent objective creation/activation surfaces from silently diverging when
another active objective already exists.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/discover-handler.py`
- `.mm-flow/commands/mm/activate-next-objective-handler.py`
- tests for active-objective coordination

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`

### Acceptance Criteria

- [x] objective creation/activation surfaces behave consistently
- [x] blocking/warning guidance identifies the conflicting active objective
- [x] tests cover the coordination behavior

## T3: Refresh continuity and record the next harness gap

### Purpose

Update handoff/docs and record what active-objective limitation remains after
this coordination pass.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`
- docs if command behavior changes

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-active-objective-coordination`

### Acceptance Criteria

- [x] handoff/docs explain the coordination behavior clearly
- [x] the next harness gap is recorded explicitly
- [x] final validation passes and another model can continue from artifacts alone
