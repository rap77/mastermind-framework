# Tasks — multi-channel-gateway

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
- [ ] The package explicitly says this objective is narrowing the **remaining**
  multi-channel gap, not redoing all of historical Phase 18.
- [ ] The likely first implementation slice is stated as unified inbound event
  normalization / canonical contract.

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- channel normalization / event-contract files
- worker or router adapter seam
- focused tests for canonical payload mapping

### Validation Commands
- Run targeted validation commands for the touched area.

### Acceptance Criteria
- [ ] A narrow, backend-authoritative multi-channel behavior exists.
- [ ] Another operator/model can infer the canonical event contract from code
  and tests.
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
