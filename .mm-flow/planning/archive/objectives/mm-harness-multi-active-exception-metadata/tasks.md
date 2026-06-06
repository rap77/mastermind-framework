# Tasks — mm-harness-multi-active-exception-metadata

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints,
  validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: preserve single-active defaults while designing explicit exceptions.

## T1: Define multi-active exception contract

### Purpose

Make the exception model explicit before changing any handler behavior.

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `requirements.md`
- `design.md`
- `tasks.md`
- `todo.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-multi-active-exception-metadata`

### Acceptance Criteria

- [x] exception metadata shape is explicit
- [x] default single-active behavior remains explicit
- [x] remaining tasks are specific enough to execute without improvisation

## T2: Define enforcement/recognition touchpoints

### Purpose

Turn the contract into an implementation map for the smallest safe handler
changes.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/active-objective-state.py`
- `.mm-flow/commands/mm/discover-handler.py`
- `.mm-flow/commands/mm/activate-next-objective-handler.py`
- `.mm-flow/README.md`
- `tests/unit/test_mm_discover_workflow.py`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-multi-active-exception-metadata`

### Acceptance Criteria

- [x] discover/activate touchpoints are explicit
- [x] helper ownership for parsing exception metadata is explicit
- [x] operator-visible explanation path is explicit
- [x] implementation can proceed without improvisation

## T3: Refresh continuity and record the next harness gap

### Purpose

Document the exception model and record what still remains after touchpoints are
explicit.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`
- objective completion notes if messaging changes

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-multi-active-exception-metadata`

### Acceptance Criteria

- [x] handoff explains the exception model clearly
- [x] the next harness gap after touchpoint definition is recorded explicitly
- [x] final validation passes and another model can continue from artifacts alone
