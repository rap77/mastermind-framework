# Handoff — pgvector-schema-langsmith-foundation-paralelo

## Current objective
- `pgvector-schema-langsmith-foundation-paralelo`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.
- This objective is now explicitly narrowed to a **foundation verification**
  slice, not a greenfield pgvector or LangSmith build.
- Repo evidence already shows both halves exist in some form:
  RAG/pgvector groundwork and LangSmith fail-soft hooks.
- The implementation slice is a read-only verification helper that emits a
  stable JSON report another operator/model can run without rediscovering the
  code paths manually.

## Blockers / risks
- The broad objective title can invite redundant implementation if we forget the
  existing RAG and LangSmith code already present in the repo.
- Verification evidence remains distributed in code, so the helper must stay
  aligned with the current migration/search/tracing seams rather than drift
  into a second source of truth.

## Exact next recommended task
- Run archive-safe validation, then archive the objective if no new drift is
  discovered.

## Validation commands
- `/mm:discover-contract-check --objective pgvector-schema-langsmith-foundation-paralelo`
- `apps/api/.venv/bin/python -m pytest apps/api/tests/unit/test_rag_foundation_verify.py`
- `apps/api/.venv/bin/python -m mastermind_cli.rag.foundation_verify`
