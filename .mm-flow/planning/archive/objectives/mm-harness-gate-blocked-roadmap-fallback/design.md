# Design — mm-harness-gate-blocked-roadmap-fallback

## Architecture / Boundaries

This objective refines roadmap output semantics inside:

- `.mm-flow/commands/mm/discover-handler.py`

It keeps existing shared helpers and safety checks intact:

- `objective-gate-status.py`
- gate-aware reranking
- `activate-next-objective` blocking

## Technical Approach

### 1. Detect blocked fallback recommendation

After choosing the roadmap recommendation:

- if the chosen objective is not activation-ready, the recommendation is a
  blocked fallback
- this can only happen once the reranking logic has already failed to find any
  gate-ready dependency-ready candidate

### 2. Expose fallback explicitly

Minimum surfaces:

- `objectives.json` gets a `recommended_blocked_fallback` flag
- roadmap summary reason changes for the all-blocked case
- handoff includes a sentence that all dependency-ready objectives are blocked

### 3. Preserve downstream safety

- activation remains blocked for the fallback recommendation
- the fallback exists to explain state, not to weaken enforcement

## Dependencies

- gate-aware reranking
- shared gate-status inference
- roadmap/handoff materialization

## Validation Strategy

Concrete checks should include:

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-gate-blocked-roadmap-fallback
```

Need tests for at least:

- roadmap flags blocked fallback recommendation
- handoff explains all-blocked state
- activation still blocks

## Important Tradeoffs

- **Explicitness vs verbosity:** the roadmap should explain the blocked state
  without overwhelming normal cases
- **Fallback vs inaction:** a blocked fallback is better than no recommendation,
  but must not be mistaken for a ready objective

## Files / Areas Likely Touched

- `.mm-flow/commands/mm/discover-handler.py`
- `tests/unit/test_mm_discover_workflow.py`
- `.mm-flow/README.md`
