# Handoff — context-window-management

## Current objective
- `context-window-management`

## Decisions already made
- Per-objective planning artifacts are the source of truth for this objective.
- `execution-state.json` is the durable ledger; `todo.md` and `HANDOFF-CURRENT.md` are projected artifacts.
- Do not restart from historical kickoff notes when durable state already exists.

## Blockers / risks
- This objective previously drifted from implementation progress because the planning surface and harness paths diverged.
- Use `python3 .claude/commands/mm/complete-task-handler.py --resync-objective context-window-management` after repairing objective artifacts.
- Do not manually edit `todo.md`, `HANDOFF-CURRENT.md`, `task-progress.json`, or `execution-state.json`.

## Completed tasks
- [x] T1: Define context budget and fit contracts
- [x] T2: Implement deterministic context packing
- [x] T3: Gate backend switches by context safety
- [x] T4: Validate context-safe continuity

## Exact next recommended task
- `/mm:archive-objective context-window-management`
- After archive: `/mm:activate-next-objective`.

## Validation commands for objective completion
- None — objective currently appears complete.
