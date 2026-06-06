# Handoff — mm-harness-gate-aware-roadmap-reranking

## Current objective
- `mm-harness-gate-aware-roadmap-reranking`

## Decisions already made
- Roadmap recommendation now prefers objectives that are both dependency-ready
  and gate-ready (`NO_CANONICAL` or `PASSED`).
- Gate-blocked candidates remain visible in roadmap artifacts with their gate
  status; they are not silently hidden.
- Activation/discover blocking still remains as a downstream safety net.

## Blockers / risks
- If every dependency-ready objective is gate-blocked, the roadmap may still
  fall back to the top blocked candidate and rely on downstream guidance.
- Multi-active exception policy is still not formalized beyond the current
  single-active default.

## Exact next recommended task
- Validate/archive this objective package, then decide whether the next harness
  gap is fallback behavior when every candidate is gate-blocked or explicit
  multi-active exception metadata.

## Validation commands
- `/mm:discover-contract-check --objective mm-harness-gate-aware-roadmap-reranking`
- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- Run targeted tests for touched files before handing off again
