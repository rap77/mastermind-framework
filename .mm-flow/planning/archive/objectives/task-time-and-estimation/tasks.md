# Tasks — task-time-and-estimation

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

## T1: Define and stabilize the slice

### Purpose
Clarify the exact objective boundary before implementation expands.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- requirements.md
- design.md
- tasks.md

### Validation Commands
- Review requirements/design/tasks package for consistency.

### Acceptance Criteria
- [ ] The exact boundary of the objective is implemented or tightened.
- [ ] Existing architecture constraints are preserved and documented.
- [ ] The package explicitly states that phase 1 targets estimation coverage
  visibility rather than the full canonical timing model.
- [ ] The likely T2 target is narrowed to one read-only project-state surface.

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/api/mastermind_cli/project_state/services/project_overview.py`
- `apps/api/mastermind_cli/project_state/schemas/overview.py`
- `apps/api/mastermind_cli/api/routes/project_overview.py`
- `apps/api/tests/unit/test_project_overview_service.py`
- `apps/api/tests/api/test_project_time_summary.py`
- `apps/web/src/lib/project-state-api.ts`
- `apps/web/src/components/project-state/ProjectStateDashboard.tsx`
- `apps/web/src/components/project-state/__tests__/ProjectStateDashboard.test.tsx`

### Validation Commands
- Run targeted validation commands for the touched area.

### Acceptance Criteria
- [ ] The main user-visible or system-visible behavior exists.
- [ ] Tests or validation commands demonstrate the behavior.
- [ ] Another operator can tell how much of the current ETA depends on explicit
  estimates versus fallback heuristics.
- [ ] The slice stays read-only and does not introduce a new timing-write path.

## T3: Close the continuity loop

### Purpose
Refresh handoff and validation context for the next model/session.

### Depends On
T2

### Parallelizable
no

### Files / Areas Likely Touched
- HANDOFF-CURRENT.md
- tasks.md
- todo.md

### Validation Commands
- Refresh handoff and rerun discovery contract check.

### Acceptance Criteria
- [ ] Handoff notes are refreshed with next recommended work.
- [ ] Validation commands are documented and pass.
