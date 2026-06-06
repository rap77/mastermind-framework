# Tasks — mm-harness-exception-replace-workflow

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints,
  validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: improve replacement ergonomics
  without weakening inspectability or validation.

## T1: Define replace-by-id workflow contract

### Purpose

Choose the smallest auditable replacement workflow before adding any mutation
helper.

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

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-replace-workflow`

### Acceptance Criteria

- [ ] replace-by-id workflow contract is explicit
- [ ] implementation touchpoints are explicit
- [ ] remaining tasks are specific enough to execute without improvisation

## T2: Implement the smallest replace workflow slice

### Purpose

Add the chosen replace-by-id helper flow without weakening validation or
inspectability.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- helper command(s) under `.mm-flow/commands/mm/`
- exception authoring docs/examples
- validator only if output/usage guidance needs alignment

### Validation Commands

- helper-specific smoke checks for:
  - missing artifact
  - missing replacement file
  - unknown `id`
  - duplicate `id`
  - replacement object `id` mismatch
  - successful replace-by-id
- `python3 .mm-flow/commands/mm/validate-active-objective-exceptions.py`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-replace-workflow`

### Acceptance Criteria

- [ ] replace helper replaces exactly one entry by `id`
- [ ] replace helper reduces manual replace risk
- [ ] validation remains an explicit required step
- [ ] artifact transition remains inspectable

## T3: Refresh continuity and record the next gap

### Purpose

Document the replace workflow and record the next strongest exception-authoring
gap.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-replace-workflow`

### Acceptance Criteria

- [ ] handoff explains the workflow clearly
- [ ] next exception-related gap is recorded explicitly
- [ ] another model can continue from artifacts alone
