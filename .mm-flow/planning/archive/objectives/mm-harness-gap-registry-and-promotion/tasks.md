# Tasks — mm-harness-gap-registry-and-promotion

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
- [ ] The package explicitly narrows phase 1 to a durable gap registry artifact
  plus a narrow helper workflow.
- [ ] Automatic prioritization / auto-objective-creation are explicitly left out
  of scope for this slice.

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `.mm-flow/planning/gaps/gap-registry.json`
- `.mm-flow/commands/mm/` helper(s) for register/list/promote
- focused tests or validation commands for registry behavior

### Validation Commands
- Run targeted validation commands for the touched area.

### Acceptance Criteria
- [ ] The main user-visible or system-visible behavior exists.
- [ ] Tests or validation commands demonstrate the behavior.
- [ ] The harness can persist a newly detected gap in a central artifact.
- [ ] The harness can mark a recorded gap as promoted to an objective without
  creating the objective automatically.

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
