# Tasks — mm-harness-objective-context-check

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints,
  validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: the new gate must strengthen
  the flow without breaking the existing `discover` lifecycle.

## T1: Define and stabilize the gate contract

### Purpose

Tighten the package so the objective-context-check gate has explicit inputs,
outputs, resolution rules, and deterministic readiness criteria before
implementation begins.

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
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-objective-context-check
```

### Acceptance Criteria

- [x] The gate contract defines exact inputs, outputs, and statuses
- [x] Resolution by slug and path is documented concretely
- [x] Readiness policy for `PASSED|FAILED|NEEDS_INPUT` is explicit
- [x] Remaining tasks are specific enough to execute without improvisation

## T2: Implement the objective-context-check core handler

### Purpose

Add the new core gate that validates objective canonicals plus intake reports
before discovery materializes an execution package.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/objective-context-check-handler.py` *(new)*
- `.mm-flow/commands/mm/objective-context-check.md` *(new)*
- `.mm-flow/README.md`
- tests for readiness decision cases

### Validation Commands

```bash
python3 .mm-flow/commands/mm/objective-context-check-handler.py --help
python3 -m unittest tests.unit.test_mm_discover_workflow
```

### Acceptance Criteria

- [x] The core handler exists and resolves objectives by slug or explicit path
- [x] It validates canonical markdown + intake report together
- [x] It emits structured statuses (`PASSED`, `FAILED`, `NEEDS_INPUT`)
- [x] Tests cover at least one pass/fail/needs-input case

## T3: Wire continuity guidance around the new gate

### Purpose

Document where the new gate fits in the harness lifecycle and refresh the
handoff so future objectives can build on the validated intake pipeline.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/README.md`
- `HANDOFF-CURRENT.md`
- tests/docs if command examples need updates

### Validation Commands

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-objective-context-check
```

### Acceptance Criteria

- [ ] Docs show the new `context-to-canonical -> objective-context-check -> discover` flow explicitly
- [ ] Handoff points to the next harness gap after this gate
- [ ] Final validation passes and another model could continue from artifacts alone
