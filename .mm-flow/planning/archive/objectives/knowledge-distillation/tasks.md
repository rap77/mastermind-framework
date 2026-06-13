# Tasks — knowledge-distillation

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
- [ ] The objective is explicitly narrowed to a first slice that surfaces
  existing knowledge-distillation analytics/templates in a current UI surface.
- [ ] Existing architecture constraints are preserved and documented, including
  “reuse current analytics routes” and “avoid rebuilding Phase 14 backend work.”

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- frontend fetch helpers for analytics/template routes
- one current operator-facing UI surface
- focused frontend/API tests

### Validation Commands
- Run targeted validation commands for the touched web/API area.

### Acceptance Criteria
- [ ] A current UI surface exposes read-only knowledge-distillation signals.
- [ ] The slice reuses the existing backend analytics/template surfaces where
  possible.
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
