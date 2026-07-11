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
- Review requirements/design/tasks package for consistency with the canonical inbound event contract.
- Confirm the objective is narrowed to reliability semantics on the existing contract, not a full gateway rebuild.

### Acceptance Criteria
- [x] The exact boundary of the objective is implemented or tightened.
- [x] Existing architecture constraints are preserved and documented.
- [x] The package explicitly narrows to canonical inbound idempotency / verification follow-up work.

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/api/routers/canonical_events.py`
- `apps/api/routers/internal.py`
- `apps/api/tests/test_canonical_events.py`

### Validation Commands
- Run targeted validation commands for the touched area.

### Acceptance Criteria
- [ ] The main user-visible or system-visible behavior exists.
- [ ] Tests or validation commands demonstrate the behavior.
- [ ] Reliability semantics are attached to the canonical inbound contract without widening scope.

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
