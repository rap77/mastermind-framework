# Design — rag-scale-out-brains-2-7

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.
- Reuse the existing `RAGContextBuilder` and Brain #1 retrieval contract.
- Generalize only the prompt-plumbing seam:
  - selected brain functions accept optional `rag_context: str = ""`
  - `StatelessCoordinator._execute_brain()` decides whether the current brain
    is in the first RAG-enabled cohort and, if so, builds retrieval context
    before the LLM query
  - the empty-context guard remains unchanged (`""` means no block appended)
- Preserve alias compatibility introduced in `rag-pilot-brain-1-only`; the
  shared seam should work with runtime short IDs and canonical IDs.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.
- Prefer one shared activation seam for a small cohort over six per-brain ad
  hoc implementations.
- Prefer brains with existing prompt-driven patterns first, instead of forcing
  RAG into every remaining brain at once.

## Context Notes
- A follow-up gap exists outside this objective: `run_brain_task` validation is
  still noisy / hang-prone. That should stay separate unless it blocks the
  first-cohort runtime proof.
