# Tasks — context-window-management

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
- HANDOFF-CURRENT.md

### Validation Commands
- Review requirements/design/tasks package for consistency.

### Acceptance Criteria
- [ ] The exact boundary of the objective is implemented or tightened.
- [ ] Existing architecture constraints are preserved and documented.
- [ ] The package explicitly narrows phase 1 to capability metadata plus a pure
  fit evaluator.
- [ ] Switching, compression execution, and UI are explicitly left out of
  scope for this slice.

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/api/mastermind_cli/window_scheduler/models/backend_session.py`
- `apps/api/mastermind_cli/window_scheduler/` helper module(s)
- focused Python tests for capability / fit-state evaluation

### Validation Commands
- Run targeted validation commands for the touched area.

### Acceptance Criteria
- [ ] The main user-visible or system-visible behavior exists.
- [ ] Tests or validation commands demonstrate the behavior.
- [ ] The backend inventory can represent context capability metadata.
- [ ] A pure helper can classify fit states using the canonical four-state
  model.

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
