# Tasks — mm-harness-roadmap-activation-gate-awareness

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints,
  validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: extend gate awareness without
  rewriting roadmap ranking or duplicating gate logic.

## T1: Define queue-level gate-awareness contract

### Purpose

Make the roadmap/activation boundary explicit before changing behavior.

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `requirements.md`
- `design.md`
- `tasks.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-roadmap-activation-gate-awareness`

### Acceptance Criteria

- [x] queue/activation integration surfaces are explicit
- [x] initial warning/blocking policy is explicit
- [x] reuse of existing gate inference is explicit
- [x] remaining tasks are specific enough to execute without improvisation

## T2: Add gate-aware activation preflight and queue guidance

### Purpose

Prevent activation from failing late or opaquely when the recommended objective
has an unsatisfied canonical gate.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/activate-next-objective-handler.py`
- `.mm-flow/commands/mm/discover-handler.py`
- tests for roadmap/activation behavior

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- `python3 .mm-flow/commands/mm/activate-next-objective-handler.py --quick`

### Acceptance Criteria

- [x] activation preflight surfaces gate-aware status before delegating
- [x] at least one queue/roadmap-facing artifact exposes gate-aware guidance
- [x] guidance distinguishes `PASSED|FAILED|NEEDS_INPUT|NOT_RUN` or equivalent
- [x] tests cover the new activation/queue behavior

## T3: Close continuity and record the next harness gap

### Purpose

Refresh docs/handoff with the queue-aware lifecycle and record the next
remaining enforcement gap after activation surfaces are covered.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/README.md`
- `HANDOFF-CURRENT.md`
- tests/docs if command recommendations change

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-roadmap-activation-gate-awareness`

### Acceptance Criteria

- [x] docs and handoff describe the queue-aware lifecycle clearly
- [x] the next harness objective/gap is recorded explicitly
- [x] final validation passes and another model can continue from artifacts alone
