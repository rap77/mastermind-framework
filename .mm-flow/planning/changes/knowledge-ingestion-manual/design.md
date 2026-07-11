# Design — knowledge-ingestion-manual

## Architecture / Boundaries
- Follow the existing monorepo split: Python handles manual ingestion previews and source validation.
- New behavior should enter through explicit CLI/service boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice: keep manual ingestion preview deterministic and auditable for distilled FUENTE sources.
- Reuse the existing `rag/manual_ingestion.py` preview helper and `commands/source.py` CLI path.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted CLI and RAG tests for the preview contract.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.

## Context Notes
- The preview path is intentionally manual-first; the objective is to validate the auditable preview contract, not to add automatic DB ingestion.
