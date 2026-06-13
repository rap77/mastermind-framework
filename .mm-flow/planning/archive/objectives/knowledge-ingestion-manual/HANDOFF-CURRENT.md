# Handoff — knowledge-ingestion-manual

## Current objective
- `knowledge-ingestion-manual`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.
- Historical roadmap/research evidence already constrains this objective to a
  **manual ingestion** phase, not an auto-update pipeline.
- The first slice should focus on the operator workflow and auditability of
  manual ingestion rather than reopening broad RAG automation.
- Source-class boundaries matter: expert/domain knowledge and project memory
  should not be treated as the same ingestion target by default.
- The Phase 1 operator surface is now:
  - `mastermind source ingest-preview <SOURCE_ID> [--output report.json]`
- The first slice is intentionally read-only:
  - deterministic chunk preview
  - chunk hashes
  - no embeddings
  - no DB writes

## Blockers / risks
- The biggest risk is overbuilding automation before proving the manual
  ingestion workflow is coherent and operable.
- Real source corpora do not always use exact `FUENTE-XXX.md` filenames, so
  source lookup must stay tolerant of suffixes and unrelated invalid YAML.

## Exact next recommended task
- Archive this objective or open the next ingestion slice only if a true write
  path is now justified.

## Validation commands
- `/mm:discover-contract-check --objective knowledge-ingestion-manual`
- `apps/api/.venv/bin/python -m pytest apps/api/tests/cli/test_source_ingestion.py`
- `apps/api/.venv/bin/python -m mastermind_cli.main source ingest-preview FUENTE-805 --output /tmp/fuente-805-preview.json`
