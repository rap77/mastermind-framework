# Tasks — knowledge-ingestion-manual

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
- [ ] The objective is explicitly narrowed to a first slice around the manual
  ingestion operator workflow.
- [ ] Existing architecture constraints are preserved and documented,
  especially “manual first” and “no auto-update pipeline.”

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- manual ingestion command/script surface
- related docs/report artifacts
- focused tests if a new helper is added

### Validation Commands
- Run targeted validation commands for the touched ingestion helper or report path.

### Acceptance Criteria
- [ ] A narrow manual-ingestion operator path exists or is materially advanced.
- [ ] The slice is auditable by another operator/model from artifacts or command output.
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
