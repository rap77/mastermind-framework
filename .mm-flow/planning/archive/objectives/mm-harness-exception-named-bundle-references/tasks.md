# Tasks — mm-harness-exception-named-bundle-references

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: reduce cross-file authoring drift without weakening fail-closed exception behavior.

## T1: Define named bundle reference contract

### Purpose

Make the named-bundle reference model explicit before changing runtime or validation.

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

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-named-bundle-references`

### Acceptance Criteria

- [x] named-bundle model is explicit
- [x] runtime/validation touchpoints are explicit
- [x] remaining tasks are specific enough to execute without improvisation

## T2: Implement named bundle reference support

### Purpose

Apply the chosen named-bundle model in validation/runtime helpers and examples.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/active-objective-state.py`
- `.mm-flow/commands/mm/validate-active-objective-exceptions.py`
- `.mm-flow/planning/active-objective-command-bundles.json`
- `.mm-flow/planning/active-objective-exceptions.json`
- `tests/unit/test_mm_discover_workflow.py`

### Validation Commands

- `python3 .mm-flow/commands/mm/validate-active-objective-exceptions.py`
- `python3 -m unittest tests.unit.test_mm_discover_workflow`

### Acceptance Criteria

- [x] named bundle references resolve deterministically
- [x] invalid bundle references fail closed
- [x] validation exposes effective command scopes clearly

## T3: Refresh continuity and record the next gap

### Purpose

Document the named-bundle rule and record the next exception-related gap.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/validate-active-objective-exceptions.py`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-named-bundle-references`

### Acceptance Criteria

- [x] handoff explains the named-bundle rule clearly
- [x] next exception-related gap is recorded explicitly
- [x] another model can continue from artifacts alone
