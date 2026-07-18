# Handoff — adaptive-onboarding-harness-runtime

## Current objective
- `adaptive-onboarding-harness-runtime`

## Decisions already made
- Per-objective planning artifacts are the source of truth for this objective.
- `execution-state.json` is the durable ledger; `todo.md` and `HANDOFF-CURRENT.md` are projected artifacts.
- Do not restart from historical kickoff notes when durable state already exists.

## Blockers / risks
- This objective previously drifted from implementation progress because the planning surface and harness paths diverged.
- Use `python3 .claude/commands/mm/complete-task-handler.py --resync-objective adaptive-onboarding-harness-runtime` after repairing objective artifacts.
- Do not manually edit `todo.md`, `HANDOFF-CURRENT.md`, `task-progress.json`, or `execution-state.json`.

## Completed tasks
- None yet.

## Exact next recommended task
- `AOH1` from `tasks.md` — depends on domain-security-assurance-plane, harness-stage-execution-runtime.

## Validation commands for AOH1
- `cd apps/api && uv run pytest -q tests/unit/test_onboarding_classifier.py`
