# Design — pgvector-schema-langsmith-foundation-paralelo

## Architecture / Boundaries
- Phase 20 runtime remains untouched: its migration lives under
  `apps/api/mastermind_cli/rag/migrations/`, retrieval under `rag/search.py`, and
  LangSmith hooks stay in the dispatch engine and task runner.
- This objective is a planning-ledger reconciliation. Its only source change is
  the stale Phase 20 state in `.planning/ROADMAP-v3.2.md` if verification passes.

## Technical Approach
1. Run the repository's focused verification report and Phase 20 unit tests.
2. Compare the passing checks with the archived Phase 20 task list.
3. Mark Phase 20 complete in the v3.2 roadmap and record the evidence in the
   objective package.
4. Complete and archive the objective with the existing MM lifecycle commands.

## Dependencies
- Existing Phase 20 implementation and archived completion record.

## Validation Strategy
- `uv run pytest tests/unit/test_rag_foundation_verify.py tests/unit/test_rag_langsmith.py`
- `uv run python -m mastermind_cli.rag.foundation_verify`
- `/mm:discover-contract-check --objective pgvector-schema-langsmith-foundation-paralelo`

## Important Tradeoffs
- Treating an implemented phase as pending causes duplicate work and contradicts
  the historical acceptance record. Reconciliation is the smallest correct slice.
- The focused verifier is marker-based and does not replace a live PostgreSQL or
  LangSmith integration test; those require infrastructure and credentials, which
  are deliberately outside this reconciliation objective.

## Context Notes
- `.planning/archive/legacy/root-tasks/todo.md` marks Phase 20 tasks 20.01–20.25
  complete.
- `apps/api/tests/unit/test_rag_foundation_verify.py` confirms the corresponding
  repository markers remain present.
