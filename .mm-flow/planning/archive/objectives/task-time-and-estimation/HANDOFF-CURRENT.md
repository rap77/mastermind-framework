# Handoff — task-time-and-estimation

## Current objective
- `task-time-and-estimation`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.
- Existing heuristic ETA plumbing already exists in backend + API + `/project-state`.
- This objective is narrowed to a **read-only estimation coverage** slice, not
  the full canonical task-time event model.
- The delivered slice explains ETA confidence by exposing how much of the
  current estimate still relies on fallback heuristics.
- The time summary now includes explicit-vs-fallback estimate counts, and
  `/project-state` renders an estimate coverage panel from that read-side data.

## Blockers / risks
- The canonical document describes a broader future model than the current
  implementation can support.
- The next meaningful gap is no longer ETA legibility; it is whether to add
  actual-vs-estimated feedback loops or drill-down on missing task estimates.

## Exact next recommended task
- Run archive-safe validation, then archive the objective if the broader
  follow-up should live as a separate future objective.

## Validation commands
- `/mm:discover-contract-check --objective task-time-and-estimation`
- `apps/api/.venv/bin/python -m pytest apps/api/tests/unit/test_project_overview_service.py -k time_summary`
- `apps/api/.venv/bin/python -m pytest apps/api/tests/api/test_project_time_summary.py`
- `pnpm --dir apps/web test:run src/components/project-state/__tests__/ProjectStateDashboard.test.tsx`
