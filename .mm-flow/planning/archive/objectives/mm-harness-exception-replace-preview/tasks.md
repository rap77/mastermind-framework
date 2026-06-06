# Tasks — mm-harness-exception-replace-preview

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints,
  validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: improve preview confidence
  without weakening the narrow replacement workflow.

## T1: Define replace preview workflow contract

### Purpose

Choose the smallest auditable preview workflow before adding helper changes.

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

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-replace-preview`

### Acceptance Criteria

- [ ] preview workflow contract is explicit
- [ ] implementation touchpoints are explicit
- [ ] remaining tasks are specific enough to execute without improvisation

## T2: Implement the smallest preview workflow slice

### Purpose

Add the chosen preview surface for replace-by-id without weakening replacement
or validation semantics.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- helper command(s) under `.mm-flow/commands/mm/`
- `replace-active-objective-exception.py`
- docs/examples if usage guidance changes

### Validation Commands

- helper-specific smoke checks for:
  - `--dry-run` with missing artifact
  - `--dry-run` with unknown `id`
  - `--dry-run` with invalid replacement object
  - `--dry-run` success without mutating the artifact
  - normal write path still succeeds unchanged
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-replace-preview`

### Acceptance Criteria

- [ ] preview flow makes pending replacement clearer before write
- [ ] preview does not mutate the artifact
- [ ] replacement and validation workflows remain explicit
- [ ] normal non-preview replace behavior remains unchanged

## T3: Refresh continuity and record the next gap

### Purpose

Document the preview workflow and record the next strongest exception-authoring
gap.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-replace-preview`

### Acceptance Criteria

- [ ] handoff explains the workflow clearly
- [ ] next exception-related gap is recorded explicitly
- [ ] another model can continue from artifacts alone
