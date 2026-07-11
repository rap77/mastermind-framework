# Tasks — context-projection

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
- Review `requirements.md`, `design.md`, and `tasks.md` together for consistency with the canonical context-projection docs and the existing API slice.
- Confirm the objective stays read-only and backend-authoritative.

### Acceptance Criteria
- [ ] The objective is narrowed to the task/doctrine projection slice backed by project-state read models.
- [ ] Existing architecture constraints are preserved and documented.

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- implementation-specific files

### Validation Commands
- Run targeted validation commands for the touched area.

### Acceptance Criteria
- [x] The main user-visible or system-visible behavior exists.
- [x] Tests or validation commands demonstrate the behavior.

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
