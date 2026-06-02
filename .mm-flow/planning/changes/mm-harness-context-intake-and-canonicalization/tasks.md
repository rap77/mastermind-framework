# Tasks — mm-harness-context-intake-and-canonicalization

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints,
  validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: improve the intake contract
  without breaking the existing `discover -> complete-task` lifecycle.

## T1: Define and stabilize the intake slice

### Purpose

Tighten the package so the intake/canonicalization objective has an execution-
ready scope, explicit contracts, and concrete downstream intent.

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
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-context-intake-and-canonicalization
```

### Acceptance Criteria

- [x] The package defines the structured intake/output contract explicitly
- [x] The relationship to the planned `objective-context-check` gate is concrete
- [x] Remaining tasks are specific enough to execute without improvisation
- [x] Validation commands are concrete enough for another model to run

## T2: Implement structured intake and report output

### Purpose

Strengthen `context-to-canonical` so it can produce a standardized canonical
document plus a machine-readable report describing evidence, assumptions, gaps,
and confidence.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/context-to-canonical-handler.py`
- `.mm-flow/commands/mm/context-to-canonical.md`
- `.mm-flow/assets/canonical/**` (only if templates need alignment)
- tests for canonical/report generation

### Validation Commands

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 .mm-flow/commands/mm/context-to-canonical-handler.py --help
python3 .mm-flow/commands/mm/context-to-canonical-handler.py --type objective --name "Add OAuth login" --payload-only
```

### Acceptance Criteria

- [x] `context-to-canonical` has a structured intake contract for objective work
- [x] Canonical generation emits a machine-readable report alongside markdown
- [x] The report distinguishes repo evidence, assumptions, gaps, and confidence
- [x] Validation proves the neutral/core path works without Claude-specific UX

## T3: Add interview fallback and continuity guidance

### Purpose

Add structured fallback behavior for insufficient-context cases and refresh the
handoff so the next harness objective can implement `objective-context-check`
against the new intake contract.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/context-to-canonical-handler.py`
- `.mm-flow/commands/mm/context-to-canonical.md`
- `.mm-flow/README.md`
- `HANDOFF-CURRENT.md`
- tests for fallback/report behavior

### Validation Commands

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-context-intake-and-canonicalization
```

### Acceptance Criteria

- [ ] There is a structured interview/fallback path for insufficient-context cases
- [ ] Docs explain how shell/Codex/Claude can use the improved intake layer
- [ ] Handoff points clearly to the next harness objective around `objective-context-check`
- [ ] Final validation passes with the tightened package and updated docs
