# Handoff — context-projection

## Current objective
- `context-projection`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.
- The initial slice is the existing task/doctrine projection read model backed by `ProjectOverviewService`.
- The objective stays read-only and backend-authoritative; no new storage layer is introduced in T1.

## Blockers / risks
- The package is scaffolded from repository evidence and may need refinement for deeper implementation context.
- Historical legacy material may still exist under archive/legacy, but it is not part of the active workflow.

## Exact next recommended task
- Archive the `context-projection` objective package.

## Validation commands
- `/mm:discover-contract-check --objective context-projection`
- `cd apps/api && UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m pytest tests/api/test_project_context_projection.py -q`
