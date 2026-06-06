# Tasks — mm-harness-lifecycle-gate-integration

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints,
  validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: integrate the gate incrementally
  without breaking existing objective execution.

## T1: Define and stabilize the lifecycle integration contract

### Purpose

Tighten the package so the lifecycle integration work has explicit enforcement
scope, gate-status rules, and concrete touchpoints before code changes begin.

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `requirements.md`
- `design.md`
- `tasks.md`

### Validation Commands

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-lifecycle-gate-integration
```

### Acceptance Criteria

- [x] The integration surfaces are explicit
- [x] The initial enforcement policy is explicit
- [x] Gate-status inference strategy is explicit
- [x] Remaining tasks are specific enough to execute without improvisation

## T2: Integrate gate awareness into lifecycle guidance

### Purpose

Make the lifecycle aware of `objective-context-check` so the user/model gets the
right next-step guidance instead of bypassing the gate silently.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/discover-handler.py`
- `.mm-flow/commands/mm/context-to-canonical-handler.py` and/or docs
- `.mm-flow/README.md`
- tests for lifecycle guidance

### Validation Commands

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 .mm-flow/commands/mm/discover-handler.py --roadmap --existing
```

### Acceptance Criteria

- [x] lifecycle messaging points to `objective-context-check` where appropriate
- [x] at least one relevant path warns or blocks when the gate is unsatisfied
- [x] guidance distinguishes `PASSED|FAILED|NEEDS_INPUT|not-yet-run`
- [x] tests cover the new lifecycle guidance

## T3: Close continuity and document the integration boundary

### Purpose

Refresh handoff/docs with the integrated lifecycle and record the next harness
gap after this enforcement phase.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/README.md`
- `HANDOFF-CURRENT.md`
- tests/docs if command recommendations change

### Validation Commands

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-lifecycle-gate-integration
```

### Acceptance Criteria

- [x] docs and handoff describe the integrated lifecycle clearly
- [x] the next harness objective/gap is recorded explicitly
- [x] final validation passes and another model can continue from artifacts alone
