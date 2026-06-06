# Design — mm-harness-gate-aware-roadmap-reranking

## Architecture / Boundaries

This objective refines roadmap recommendation logic inside:

- `.mm-flow/commands/mm/discover-handler.py`

It reuses existing helpers instead of inventing a new gate system:

- `objective-gate-status.py`
- downstream activation/discover preflight checks

## Technical Approach

### 1. Define activation-ready set

For roadmap reranking:

- `NO_CANONICAL` -> activation-ready
- `PASSED` -> activation-ready
- `NOT_RUN` -> blocked
- `NEEDS_INPUT` -> blocked
- `FAILED` -> blocked

### 2. Rerank only inside ready-now candidates

Current recommendation already filters to objectives that are:

- `planned` or `missing-but-required`
- `ready_now` from dependency perspective

Phase-1 reranking keeps that filter, then prefers:

1. gate-ready candidates
2. existing deterministic priority/unlock order inside that pool
3. blocked candidates only as fallback when no gate-ready candidate exists

### 3. Preserve visibility and safety nets

- roadmap still shows gate status for blocked candidates
- activation/discover still block if the chosen objective is not gate-ready
- this objective improves recommendation quality, not correctness alone

## Dependencies

- shared gate-status inference
- current objective priority ordering
- roadmap materialization in `discover-handler.py`

## Validation Strategy

Concrete checks should include:

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-gate-aware-roadmap-reranking
```

Need tests for at least:

- roadmap reranks away from a gate-blocked higher-priority candidate
- blocked candidate still exposes gate status in roadmap output
- activation follows the reranked objective

## Important Tradeoffs

- **Actionability vs strict priority:** reranking improves operator experience
  but means raw priority is no longer the only top-level signal
- **Visibility vs suppression:** blocked candidates stay visible to avoid hiding
  important work
- **Fallback behavior:** if every ready candidate is gate-blocked, the roadmap
  may still recommend the top blocked one and rely on downstream guidance

## Files / Areas Likely Touched

- `.mm-flow/commands/mm/discover-handler.py`
- `tests/unit/test_mm_discover_workflow.py`
- `.mm-flow/README.md`
