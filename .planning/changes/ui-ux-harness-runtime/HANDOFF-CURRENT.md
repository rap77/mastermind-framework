# Handoff — ui-ux-harness-runtime

## Current objective
- `ui-ux-harness-runtime`

## Decisions already made
- Per-objective planning artifacts are the source of truth for this objective.
- `execution-state.json` is the durable ledger; `todo.md` and `HANDOFF-CURRENT.md` are projected artifacts.
- Do not restart from historical kickoff notes when durable state already exists.

## Blockers / risks
- This objective previously drifted from implementation progress because the planning surface and harness paths diverged.
- Use `python3 .claude/commands/mm/complete-task-handler.py --resync-objective ui-ux-harness-runtime` after repairing objective artifacts.
- Do not manually edit `todo.md`, `HANDOFF-CURRENT.md`, `task-progress.json`, or `execution-state.json`.

## Completed tasks
- None yet.

## Exact next recommended task
- `UXH1` from `tasks.md` — depends on None.

## Validation commands for UXH1
- `cd apps/api && uv run pytest -q tests/unit/test_harness_run_executor.py tests/unit/test_multi_harness_models.py`
- `cd apps/api && uv run ruff check mastermind_cli/orchestrator/runtime_contracts/models.py mastermind_cli/mm_flow/harness_run_executor.py tests/unit/test_harness_run_executor.py tests/unit/test_multi_harness_models.py`
