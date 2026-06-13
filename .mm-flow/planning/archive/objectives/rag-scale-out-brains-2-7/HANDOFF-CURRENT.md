# Handoff — rag-scale-out-brains-2-7

## Current objective
- `rag-scale-out-brains-2-7`

## Decisions already made
- This is not a big-bang rollout across all remaining brains.
- The first coherent scale-out slice is a shared `rag_context` seam for
  **Brains #2, #3, and #7** first.
- The slice should reuse the existing Brain #1 retrieval contract and preserve
  runtime alias compatibility (`brain-02-ux`, `brain-03-ui`, `brain-07-growth`
  vs canonical IDs).
- The separate `run_brain_task` validation-isolation gap stays out of scope for
  this objective unless it directly blocks the first cohort.
- The first cohort seam is now implemented for `brain-02-ux-research`,
  `brain-03-ui-design`, and `brain-07-growth-data` by reusing the existing
  `RAGContextBuilder` contract and the same empty-context guard as Brain #1.
- Runtime short aliases for the cohort (`brain-02-ux`, `brain-03-ui`,
  `brain-07-growth`) continue to work because the coordinator checks canonical
  variants before deciding whether to build RAG context.

## Blockers / risks
- This objective intentionally stops at shared prompt plumbing; it does not yet
  extend the same seam to Brains #4, #5, or #6.
- `run_brain_task` validation remains noisy / hang-prone and should still be
  treated as a separate follow-up unless it blocks a future cohort rollout.

## Exact next recommended task
- Archive this objective and open the next RAG rollout slice only when there is
  a concrete need to extend the seam beyond the first cohort.

## Validation commands
- `/mm:discover-contract-check --objective rag-scale-out-brains-2-7`
- `apps/api/.venv/bin/python -m pytest apps/api/tests/unit/test_stateless_coordinator.py -k "short_brain1_alias or first_scale_out_aliases or alias_context or executes_single_brain or executes_multiple_brains"`

## Current objective
- `rag-scale-out-brains-2-7`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.

## Blockers / risks
- The package is scaffolded from repository evidence and may need refinement for deeper implementation context.
- Historical legacy material may still exist under archive/legacy, but it is not part of the active workflow.

## Exact next recommended task
- Start with `T1` from `tasks.md`.

## Validation commands
- `/mm:discover-contract-check --objective rag-scale-out-brains-2-7`
- Run targeted tests for touched files before handing off again
