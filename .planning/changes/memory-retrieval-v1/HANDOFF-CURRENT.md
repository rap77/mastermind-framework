# Handoff — memory-retrieval-v1

## Current objective
- `memory-retrieval-v1`

## Decisions already made
- Per-objective planning artifacts are the source of truth for this objective.
- `execution-state.json` is the durable ledger; `todo.md` and `HANDOFF-CURRENT.md` are projected artifacts.
- Do not restart from historical kickoff notes when durable state already exists.

## Blockers / risks
- This objective previously drifted from implementation progress because the planning surface and harness paths diverged.
- Use `python3 .claude/commands/mm/complete-task-handler.py --resync-objective memory-retrieval-v1` after repairing objective artifacts.
- Do not manually edit `todo.md`, `HANDOFF-CURRENT.md`, `task-progress.json`, or `execution-state.json`.

## Completed tasks
- None yet.

## Exact next recommended task
- `MR1` from `tasks.md` — depends on none.

## Validation commands for MR1
- Validation commands not declared yet.
