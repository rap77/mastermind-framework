# Handoff — memory-graph-recall-v1

## Current objective
- `memory-graph-recall-v1`

## Decisions already made
- Per-objective planning artifacts are the source of truth for this objective.
- `execution-state.json` is the durable ledger; `todo.md` and `HANDOFF-CURRENT.md` are projected artifacts.
- Do not restart from historical kickoff notes when durable state already exists.

## Blockers / risks
- This objective previously drifted from implementation progress because the planning surface and harness paths diverged.
- Use `python3 .claude/commands/mm/complete-task-handler.py --resync-objective memory-graph-recall-v1` after repairing objective artifacts.
- Do not manually edit `todo.md`, `HANDOFF-CURRENT.md`, `task-progress.json`, or `execution-state.json`.

## Completed tasks
- [x] GR1: Define graph recall seam
- [x] GR2: Add minimal relational expansion
- [x] GR3: Close graph recall v1

## Exact next recommended task
- Archive the `memory-graph-recall-v1` objective package.

## Validation commands for GR1
- `cd apps/api && UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m pytest -q tests/unit -k 'memory and graph'`
- `cd apps/api && UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m pytest -q tests/unit -k 'graph_recall or memory_graph'`
- `cd apps/api && UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m pytest tests/unit/test_memory_eval_harness.py tests/unit/test_memory_layer_postgres_store.py -q`
