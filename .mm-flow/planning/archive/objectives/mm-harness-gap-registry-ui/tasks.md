# Tasks — mm-harness-gap-registry-ui

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

## T1: Define and stabilize the slice

### Purpose
Clarify the exact boundary before implementation expands.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- requirements.md
- design.md
- tasks.md
- HANDOFF-CURRENT.md

### Validation Commands
- Review requirements/design/tasks package for consistency.

### Acceptance Criteria
- [ ] The exact boundary of the objective is implemented or tightened.
- [ ] The package explicitly narrows phase 1 to a read-only gap registry panel in the existing UI surface.
- [ ] UI write actions remain out of scope.

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/web/src/app/(protected)/project-state/page.tsx`
- `apps/web/src/components/project-state/ProjectStateDashboard.tsx`
- `apps/web/src/lib/project-state-api.ts`
- focused frontend/backend tests for the chosen data path

### Validation Commands
- Run targeted validation commands for the touched area.

### Acceptance Criteria
- [ ] The UI shows a read-only view of current gap registry entries.
- [ ] Empty-state behavior is explicit when no gaps exist.
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
