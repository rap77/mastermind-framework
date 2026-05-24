# Project State Handoff — 2026-05-24

## Goal
Continue the MasterMind `project_state` MVP thin slice across API + web without losing architectural coherence.

## Current status
Implemented and working:

### Backend (`apps/api`)
Read-side endpoints already available:
- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `GET /api/projects/{project_id}/overview`
- `GET /api/projects/{project_id}/tasks`
- `GET /api/projects/{project_id}/tasks/{task_id}`
- `GET /api/projects/{project_id}/tasks/{task_id}/dependencies`
- `GET /api/projects/{project_id}/tasks/{task_id}/context-projection`
- `GET /api/projects/{project_id}/tasks/{task_id}/doctrine-projection`
- `GET /api/projects/{project_id}/runs/active`
- `GET /api/projects/{project_id}/runs/{run_id}`
- `GET /api/projects/{project_id}/checkpoints/latest`
- `GET /api/projects/{project_id}/costs/summary`
- `GET /api/projects/{project_id}/token-usage`
- `GET /api/projects/{project_id}/time-summary`
- `GET /api/projects/{project_id}/activity`
- `GET /api/projects/{project_id}/decisions`
- `GET /api/projects/{project_id}/decisions/{decision_id}`

Write-side minimum already available:
- `POST /api/projects/{project_id}/tasks/{task_id}/checkpoints`
- `POST /api/projects/{project_id}/decisions`

Important backend files:
- `apps/api/mastermind_cli/api/routes/project_overview.py`
- `apps/api/mastermind_cli/project_state/services/project_overview.py`
- `apps/api/mastermind_cli/project_state/schemas/overview.py`
- `apps/api/mastermind_cli/project_state/repositories/*`
- `apps/api/mastermind_cli/project_state/models/*`

### Web (`apps/web`)
Protected page implemented:
- `/project-state`

Main UI files:
- `apps/web/src/app/(protected)/project-state/page.tsx`
- `apps/web/src/components/project-state/ProjectStateDashboard.tsx`
- `apps/web/src/components/project-state/ProjectStateLiveShell.tsx`
- `apps/web/src/components/project-state/TaskGraphPanel.tsx`
- `apps/web/src/components/project-state/ProjectStateWritePanel.tsx`
- `apps/web/src/app/actions/project-state.ts`
- `apps/web/src/lib/project-state-api.ts`

Current UI capabilities:
- project list
- task list
- task graph visualization
- overview
- ETA / time summary
- active runs
- latest checkpoint / latest decision
- cost telemetry + raw token usage
- activity feed
- context projection
- doctrine projection
- live refresh shell
- write-side forms to create checkpoints and decisions

## Key implementation decisions
1. `project_state` is incremental and coexists with legacy state code for now.
2. PostgreSQL is the architectural target; do not expand the old sqlite/aiosqlite path.
3. For now, `project_state` write-side uses a pragmatic boundary in audit middleware:
   - request body is buffered + replayed
   - legacy audit write is skipped for `/api/projects` POST flows
4. Harness direction is model/provider agnostic.
5. Rust source of truth is `rust_control_plane`; `apps/control-plane` was removed.

## Important gotchas
### 1. FastAPI audit middleware bug was fixed
File:
- `apps/api/mastermind_cli/api/app.py`

Problem:
- middleware consumed POST body and handlers hung

Fix:
- buffer and replay body through custom `receive()`

### 2. Transitional audit boundary
For `/api/projects` write-side routes, legacy audit persistence is currently skipped.
This should later become project_state-native event logging.

### 3. React form reset
`ProjectStateWritePanel` uses a keyed child component strategy instead of calling `setState` synchronously inside `useEffect`.

## Validation status
Already validated recently:
- backend thin-slice tests green
- write-side targeted tests green
- web ESLint green
- web TypeScript green

Useful commands:

### Backend tests
```bash
cd apps/api
. .venv/bin/activate
pytest -q tests/unit/test_project_overview_service.py tests/api/test_project_overview.py tests/api/test_project_state_detail.py tests/api/test_project_cost_summary.py tests/api/test_project_activity_feed.py tests/api/test_project_decisions.py tests/api/test_project_context_projection.py tests/api/test_project_doctrine_projection.py tests/api/test_projects_list_detail.py tests/api/test_project_runs.py tests/api/test_project_tasks_graph.py tests/api/test_project_token_usage.py tests/api/test_project_time_summary.py tests/api/test_project_write_side.py
```

### Web validation
```bash
cd apps/web
pnpm exec eslint src/app/actions/project-state.ts src/components/project-state/ProjectStateDashboard.tsx src/components/project-state/ProjectStateWritePanel.tsx src/app/'(protected)'/project-state/page.tsx src/lib/project-state-api.ts
pnpm exec tsc --noEmit
```

## Best next steps
Recommended order:
1. Add real-time project_state WebSocket events
2. Add filters/search/task board views in `/project-state`
3. Add more write-side actions:
   - update task status
   - create task notes
   - record handoffs
4. Replace transitional `/api/projects` audit skip with proper project_state-native event/audit logging
5. Continue Python-vs-Rust hardening later without blocking MVP progress

## If another model takes over
Ask it to:
1. read this file first
2. inspect `apps/api/mastermind_cli/project_state/`
3. inspect `apps/web/src/components/project-state/`
4. preserve the current incremental thin-slice approach
5. avoid reintroducing direct DB access from models; backend services remain the authority

## Suggested resume prompt
```text
Read `.planning/HANDOFF-PROJECT-STATE-2026-05-24.md` first, then continue implementing the Project State MVP from the current thin slice. Preserve the existing architecture: backend authority, project_state incremental domain, model-agnostic harness direction, and the existing /project-state UI.
```
