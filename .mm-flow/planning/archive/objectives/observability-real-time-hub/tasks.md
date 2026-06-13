# Tasks — observability-real-time-hub

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
- [ ] The objective is explicitly narrowed to a first slice that exposes live
  brain-event visibility inside `/project-state`.
- [ ] Existing architecture constraints are preserved and documented, including
  “reuse current `/ws/events` + `BrainStatusFeed`” and “do not replace SSE.”

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/web/src/components/project-state/ProjectStateDashboard.tsx`
- `apps/web/src/components/project-state/ProjectStateLiveShell.tsx`
- `apps/web/src/components/ws/BrainStatusFeed.tsx`
- `apps/web/src/components/ws/__tests__/BrainStatusFeed.test.tsx`
- new focused `/project-state` frontend test if needed

### Validation Commands
- `pnpm --dir apps/web test:run src/components/ws/__tests__/BrainStatusFeed.test.tsx`
- Run a focused frontend test for the touched `/project-state` surface if a new
  test file is added.

### Acceptance Criteria
- [ ] `/project-state` exposes a read-only real-time brain-event surface.
- [ ] The new panel reuses existing `BrainStatusFeed` behavior instead of
  inventing a second event-feed abstraction.
- [ ] Tests or validation commands demonstrate the behavior.

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
