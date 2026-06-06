# Tasks — mm-harness-exception-delegated-command-scopes

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: preserve fail-closed exception behavior while reducing operator-facing ambiguity.

## T1: Define delegated command-scope contract

### Purpose

Make the delegated-scope rule explicit before changing runtime behavior.

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

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-delegated-command-scopes`

### Acceptance Criteria

- [x] delegated-scope policy is explicit
- [x] implementation touchpoints are explicit
- [x] remaining tasks are specific enough to execute without improvisation

## T2: Implement delegated-scope handling

### Purpose

Apply the chosen delegated-scope rule in shared helpers/runtime entrypoints.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/active-objective-state.py`
- `.mm-flow/commands/mm/activate-next-objective-handler.py`
- `.mm-flow/commands/mm/discover-handler.py`
- `tests/unit/test_mm_discover_workflow.py`

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`

### Acceptance Criteria

- [x] delegated command-scope behavior is deterministic
- [x] runtime remains fail closed on mismatch/invalid metadata
- [x] tests prove both inherited/aliased and non-matching paths

## T3: Refresh continuity and record the next gap

### Purpose

Document the delegated-scope rule and capture what exception-related gap remains next.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-delegated-command-scopes`

### Acceptance Criteria

- [x] handoff explains the delegated-scope rule clearly
- [x] next exception-related gap is recorded explicitly
- [x] another model can continue from artifacts alone
