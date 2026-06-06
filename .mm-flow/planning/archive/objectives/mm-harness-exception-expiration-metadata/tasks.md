# Tasks — mm-harness-exception-expiration-metadata

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: preserve fail-closed exception behavior while making expiration machine-checkable.

## T1: Define expiration metadata contract

### Purpose

Make the expiration model explicit before changing runtime behavior.

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

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-expiration-metadata`

### Acceptance Criteria

- [x] machine-checkable expiration contract is explicit
- [x] runtime ownership/touchpoints are explicit
- [x] remaining tasks are specific enough to execute without improvisation

## T2: Implement expiration-aware exception matching

### Purpose

Apply the chosen expiration model in shared exception helpers and tests.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/active-objective-state.py`
- `.mm-flow/planning/active-objective-exceptions.json`
- `tests/unit/test_mm_discover_workflow.py`

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`

### Acceptance Criteria

- [x] expired exceptions no longer match
- [x] invalid/missing machine expiration metadata fails closed
- [x] tests prove active, expired, and invalid expiration paths

## T3: Refresh continuity and record the next gap

### Purpose

Document the expiration rule and record what exception-related gap remains next.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-expiration-metadata`

### Acceptance Criteria

- [x] handoff explains the expiration rule clearly
- [x] next exception-related gap is recorded explicitly
- [x] another model can continue from artifacts alone
