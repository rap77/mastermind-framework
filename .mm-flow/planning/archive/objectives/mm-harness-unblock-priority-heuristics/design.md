# Design — mm-harness-unblock-priority-heuristics

## Architecture / Boundaries

This objective refines the explanation layer around blocked fallback roadmap
recommendations.

Likely touchpoints:

- `.mm-flow/commands/mm/discover-handler.py`
- roadmap artifacts under `.mm-flow/planning/roadmap/`
- root handoff guidance

## Technical Approach

### 1. Define blocked-queue heuristic explicitly

Candidate heuristic inputs:

1. existing objective priority score
2. number of downstream unlocks
3. gate status severity (`NOT_RUN` vs `NEEDS_INPUT` vs `FAILED`)

Phase-1 should pick a deterministic combination and document it.

### 2. Surface reasoning, not just result

When a blocked fallback is recommended, artifacts should say why that blocked
objective is the one to unblock first, e.g.:

- highest priority among blocked ready candidates
- unlocks the most downstream work
- lowest remediation cost (if modeled later)

### 3. Keep enforcement untouched

- activation remains blocked
- discover remains blocked
- this slice improves operator guidance, not execution permissions

## Dependencies

- blocked fallback roadmap semantics
- existing priority/unlock calculations
- gate status inference

## Validation Strategy

Concrete checks should include:

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-unblock-priority-heuristics
```

Need tests for at least:

- blocked fallback exposes explicit unblock-priority reason
- the chosen blocked candidate remains deterministic
- activation remains blocked

## Important Tradeoffs

- **Clarity vs complexity:** richer unblock heuristics help operators but can
  overcomplicate the roadmap
- **Severity vs strategic value:** the easiest objective to unblock is not
  always the most valuable one

## Files / Areas Likely Touched

- `.mm-flow/commands/mm/discover-handler.py`
- `tests/unit/test_mm_discover_workflow.py`
- `.mm-flow/README.md`
