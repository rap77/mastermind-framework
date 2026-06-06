# Tasks — mm-harness-unblock-priority-heuristics

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints,
  validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: improve blocked-queue guidance
  without weakening execution gates.

## T1: Define unblock-priority contract

### Purpose

Make blocked-queue recommendation logic explicit before changing roadmap output.

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `requirements.md`
- `design.md`
- `tasks.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-unblock-priority-heuristics`

### Acceptance Criteria

- [x] blocked-queue heuristic inputs are explicit
- [x] output surfaces for reasoning are explicit
- [x] remaining tasks are specific enough to execute without improvisation

## T2: Emit explicit unblock-priority reasoning

### Purpose

Tell the operator not only that the queue is blocked, but why one blocked
objective should be unblocked first.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/discover-handler.py`
- `tests/unit/test_mm_discover_workflow.py`

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`

### Acceptance Criteria

- [x] blocked fallback includes explicit unblock-priority reason
- [x] roadmap/handoff expose the reasoning deterministically
- [x] activation remains blocked

## T3: Refresh continuity and record the next harness gap

### Purpose

Document the unblock heuristic and record what remaining ambiguity still exists
after blocked-queue reasoning is explicit.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`
- docs if messaging changes

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-unblock-priority-heuristics`

### Acceptance Criteria

- [x] handoff/docs explain unblock-priority behavior clearly
- [x] the next harness gap is recorded explicitly
- [x] final validation passes and another model can continue from artifacts alone
