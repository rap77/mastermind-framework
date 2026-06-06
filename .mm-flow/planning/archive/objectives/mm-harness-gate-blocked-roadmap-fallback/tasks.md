# Tasks — mm-harness-gate-blocked-roadmap-fallback

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints,
  validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: improve explanation of blocked
  queues without weakening gate enforcement.

## T1: Define blocked-fallback roadmap contract

### Purpose

Make the all-blocked roadmap case explicit before changing output semantics.

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `requirements.md`
- `design.md`
- `tasks.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-gate-blocked-roadmap-fallback`

### Acceptance Criteria

- [x] blocked fallback semantics are explicit
- [x] fallback output surfaces are explicit
- [x] remaining tasks are specific enough to execute without improvisation

## T2: Emit explicit fallback guidance in roadmap outputs

### Purpose

Mark when `recommended_next` is only a blocked fallback because every
dependency-ready candidate is gate-blocked.

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

- [x] roadmap artifacts expose `recommended_blocked_fallback`
- [x] handoff/summary explain the all-blocked state
- [x] tests cover fallback roadmap behavior and blocked activation

## T3: Refresh continuity and record the next harness gap

### Purpose

Document the explicit blocked-fallback behavior and record the next remaining
gap after fallback semantics are covered.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/README.md`
- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-gate-blocked-roadmap-fallback`

### Acceptance Criteria

- [x] docs and handoff describe blocked fallback behavior clearly
- [x] the next harness gap is recorded explicitly
- [x] final validation passes and another model can continue from artifacts alone
