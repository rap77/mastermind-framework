# Tasks — mm-harness-exception-update-workflow

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: improve exception update ergonomics without weakening transparency or validation.

## T1: Define exception update workflow contract

### Purpose

Make the smallest safe update-oriented workflow explicit before adding helper tooling.

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

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-update-workflow`

### Acceptance Criteria

- [ ] update workflow contract is explicit
- [ ] implementation touchpoints are explicit
- [ ] remaining tasks are specific enough to execute without improvisation

## T2: Implement the smallest update workflow slice

### Purpose

Add the chosen update-oriented helper flow and connect it to validation.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/` helper command for rendering one existing exception
- exception authoring docs/examples
- validator only if output/usage guidance needs alignment

### Validation Commands

- helper-specific smoke checks for:
  - missing artifact
  - unknown `id`
  - successful render by `id`
  - successful render with narrow overrides
- `python3 .mm-flow/commands/mm/validate-active-objective-exceptions.py`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-update-workflow`

### Acceptance Criteria

- [ ] helper renders an existing entry by `id` without mutating artifacts
- [ ] update workflow reduces manual extraction/copy risk
- [ ] validation remains an explicit required step
- [ ] artifacts remain directly inspectable

## T3: Refresh continuity and record the next gap

### Purpose

Document the new update workflow and record the next strongest exception-related gap.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`
- package docs if usage examples need final refresh

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-update-workflow`

### Acceptance Criteria

- [ ] handoff explains the workflow clearly
- [ ] next exception-related gap is recorded explicitly
- [ ] another model can continue from artifacts alone
