# Design — knowledge-ingestion-manual

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.
- Follow the documented product constraint: manual ingestion first, automation
  later only if manual ingestion becomes the bottleneck.
- Prefer a script or explicit CLI/operator path over background automation.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.
- For the first slice, prioritize deterministic operator validation (help
  output, dry-run/reporting, or explicit artifact generation) over speculative
  retrieval benchmarking.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.
- Prefer transparent/manual ingestion over hidden automation in Phase 1.

## Context Notes
- Historical evidence repeatedly says:
  - v3.2 should use manual ingestion, not file watching / auto-update
  - BRAIN-FEED files are noisy and should not be treated as the same source
    class as expert/domain knowledge
  - the first safe operator workflow is narrower than “full RAG ingestion for
    everything”

## Phase 1 Slice

### Goal
Define and, if possible in T2, implement the narrowest manual ingestion
workflow that an operator can run intentionally and audit afterward.

### Likely Touchpoints
- an existing Python command/script surface under `apps/api/mastermind_cli`
- docs or reports that summarize what would be ingested
- focused Python tests if a new operator helper is added

### T2 Implementation Chosen
- Add a manual preview helper in `apps/api/mastermind_cli/rag/manual_ingestion.py`
  that:
  - reads one distilled `FUENTE-*` markdown file
  - extracts only `## Conocimiento Destilado`
  - emits deterministic `domain_knowledge` chunk previews with `chunk_hash`
- Expose that helper via the existing CLI surface:
  - `mastermind source ingest-preview <SOURCE_ID> [--output ...]`
- Keep Phase 1 read-only:
  - preview/report only
  - no embeddings
  - no DB inserts
  - no background sync

### Explicit Non-Goals
- no auto-update pipeline
- no watcher-based sync
- no broad “ingest every possible source type” design in the first slice
