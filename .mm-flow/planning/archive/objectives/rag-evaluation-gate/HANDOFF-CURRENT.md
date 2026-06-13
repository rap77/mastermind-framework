# Handoff — rag-evaluation-gate

## Current objective
- `rag-evaluation-gate`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.
- Brain #1 RAG pilot seams and a baseline helper already exist locally.
- This objective is narrowed to an **offline Recall@5 evaluation** slice first,
  not the entire Phase 21.5 gate at once.
- The delivered slice adds:
  - `apps/api/mastermind_cli/rag/recall_eval.py`
  - `apps/api/tests/rag/fixtures/brain1_recall_pairs.json`
  - focused unit tests for pass/fail Recall@5 behavior
- Another operator/model can now run a stable offline Recall@5 check for Brain
  #1 `domain_knowledge` and get a JSON pass/fail report.

## Blockers / risks
- The roadmap's full gate includes live A/B quality deltas, latency, and
  contamination signals that are broader than this first slice.
- The next meaningful gap is no longer deterministic retrieval eval; it is the
  broader OEC/latency/contamination gate that needs runtime evidence.

## Exact next recommended task
- Run archive-safe validation, then archive this slice and open the next
  evaluation-gate follow-up only if the broader runtime gate still needs a
  dedicated package.

## Validation commands
- `/mm:discover-contract-check --objective rag-evaluation-gate`
- `apps/api/.venv/bin/python -m pytest apps/api/tests/rag/test_recall_eval.py`
- `apps/api/.venv/bin/python -m mastermind_cli.rag.recall_eval --help`
