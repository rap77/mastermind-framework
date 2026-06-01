# Tasks — project-state-mvp

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

## PS1: Realtime events for project_state

### Purpose
Add explicit realtime signaling so the dashboard can observe project_state changes without relying only on periodic refresh.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- apps/api/mastermind_cli/api/routes/project_overview.py
- apps/api/mastermind_cli/project_state/services/project_overview.py
- apps/web/src/components/project-state/ProjectStateLiveShell.tsx

### Validation Commands
- cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_activity_feed.py tests/api/test_project_runs.py
- cd apps/web && pnpm exec tsc --noEmit

### Acceptance Criteria
- [ ] Backend emits project_state-relevant realtime events through an explicit contract.
- [ ] `/project-state` can subscribe or refresh from realtime signals without degrading current functionality.
- [ ] Validation commands for API/web changes are documented and pass.

## PS2: Richer write-side operations

### Purpose
Expand the dashboard from passive observability to more operational project-state actions.

### Depends On
PS1

### Parallelizable
no

### Files / Areas Likely Touched
- apps/api/mastermind_cli/api/routes/project_overview.py
- apps/web/src/app/actions/project-state.ts
- apps/web/src/components/project-state/ProjectStateWritePanel.tsx

### Validation Commands
- cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_write_side.py
- cd apps/web && pnpm exec eslint src/app/actions/project-state.ts src/components/project-state/ProjectStateWritePanel.tsx

### Acceptance Criteria
- [ ] At least one additional write-side action exists (task status, notes, or handoff).
- [ ] The action respects backend authority and is visible in the dashboard.
- [ ] Tests or targeted validation cover the new action.

## PS3: Replace transitional audit gap

### Purpose
Remove the temporary audit skip and replace it with project_state-native activity/audit logging.

### Depends On
PS1, PS2

### Parallelizable
no

### Files / Areas Likely Touched
- apps/api/mastermind_cli/api/app.py
- apps/api/mastermind_cli/project_state/repositories
- apps/api/mastermind_cli/project_state/services/project_overview.py

### Validation Commands
- cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_write_side.py tests/api/test_project_activity_feed.py

### Acceptance Criteria
- [ ] `/api/projects` write-side routes are no longer hidden behind a transitional audit skip.
- [ ] project_state-native activity/audit events capture the key write-side actions.
- [ ] The change is validated without regressing existing project_state flows.
