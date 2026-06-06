# Tasks — mm-harness-multi-active-exception-runtime-recognition

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: preserve single-active defaults unless a valid narrow exception matches.

## T1: Define runtime recognition slice

### Purpose

Make the implementation slice explicit before touching runtime behavior.

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

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-multi-active-exception-runtime-recognition`

### Acceptance Criteria

- [x] parser responsibilities are explicit
- [x] blocking touchpoints are explicit
- [x] test matrix is specific enough to implement without improvisation

## T2: Implement shared exception recognition in discover

### Purpose

Add shared parser/matcher helpers and let `discover --existing --objective <slug>` honor a valid matching exception.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/active-objective-state.py`
- `.mm-flow/commands/mm/discover-handler.py`
- `tests/unit/test_mm_discover_workflow.py`

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`

### Acceptance Criteria

- [x] discover still blocks when no valid exception matches
- [x] discover continues when a valid matching exception exists
- [x] operator output exposes matched exception metadata

## T3: Extend activate-next-objective and refresh continuity

### Purpose

Honor the same recognition path in `activate-next-objective`, validate both entrypoints, and record the next deferred gap.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/activate-next-objective-handler.py`
- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`
- `tests/unit/test_mm_discover_workflow.py`

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-multi-active-exception-runtime-recognition`

### Acceptance Criteria

- [x] activate-next-objective honors the same matching logic
- [x] both entrypoints preserve single-active fallback on mismatch
- [x] handoff records the next remaining exception-related gap explicitly
