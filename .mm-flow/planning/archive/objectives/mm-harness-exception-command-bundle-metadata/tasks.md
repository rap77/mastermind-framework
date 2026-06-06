# Tasks — mm-harness-exception-command-bundle-metadata

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: preserve fail-closed delegated-scope behavior while making command relationships more artifact-visible.

## T1: Define command-bundle metadata contract

### Purpose

Make the bundle/delegation model explicit before changing runtime behavior.

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

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-command-bundle-metadata`

### Acceptance Criteria

- [x] artifact-visible bundle model is explicit
- [x] runtime ownership/touchpoints are explicit
- [x] remaining tasks are specific enough to execute without improvisation

## T2: Implement bundle-aware exception matching

### Purpose

Apply the chosen bundle/delegation model in shared exception helpers and tests.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/active-objective-state.py`
- `.mm-flow/commands/mm/activate-next-objective-handler.py`
- `.mm-flow/commands/mm/discover-handler.py`
- `.mm-flow/planning/active-objective-command-bundles.json`
- `tests/unit/test_mm_discover_workflow.py`

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`

### Acceptance Criteria

- [x] command-bundle matching is deterministic
- [x] runtime remains fail closed on invalid/missing metadata
- [x] tests prove bundle-aware and non-matching paths

## T3: Refresh continuity and record the next gap

### Purpose

Document the command-bundle rule and record what exception-related gap remains next.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-command-bundle-metadata`

### Acceptance Criteria

- [x] handoff explains the command-bundle rule clearly
- [x] next exception-related gap is recorded explicitly
- [x] another model can continue from artifacts alone
