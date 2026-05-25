# Todo — project-state-mvp

## Execution Checklist

- [x] PS1: Realtime events for project_state
⏱️ **Estimate**: N/A | **Actual**: in progress | **Deviation**: — | **Progress**: 0/0 (0%)
📊 **Avg/subtask**: — | **ETA**: in progress

  - [x] PS1.1: Review requirements and design context for PS1
  - [x] PS1.2: Implement PS1 end-to-end
  - [x] PS1.3: Run validation for PS1
  - depends_on: none
  - validation: cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_activity_feed.py tests/api/test_project_runs.py | cd apps/web && pnpm exec tsc --noEmit

- [x] PS2: Richer write-side operations
⏱️ **Estimate**: N/A | **Actual**: 15.8m | **Deviation**: N/A | **Progress**: 3/3 (100%)
📊 **Avg/subtask**: 5.3m | **ETA**: 15.8m

  - [x] PS2.1: Review requirements and design context for PS2
  - [x] PS2.2: Implement PS2 end-to-end
  - [x] PS2.3: Run validation for PS2
  - depends_on: PS1
  - validation: cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_write_side.py | cd apps/web && pnpm exec eslint src/app/actions/project-state.ts src/components/project-state/ProjectStateWritePanel.tsx

- [x] PS3: Replace transitional audit gap
⏱️ **Estimate**: N/A | **Actual**: 4.5h | **Deviation**: N/A | **Progress**: 3/3 (100%)
📊 **Avg/subtask**: 1.5h | **ETA**: 4.5h

  - [x] PS3.1: Review requirements and design context for PS3
  - [x] PS3.2: Implement PS3 end-to-end
  - [x] PS3.3: Run validation for PS3
  - depends_on: PS1, PS2
  - validation: cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_write_side.py tests/api/test_project_activity_feed.py
