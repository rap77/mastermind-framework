# Tasks — rag-pilot-brain-1-only

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
- [ ] The package explicitly states that phase 1 targets Brain #1 runtime ID
  alignment, not a greenfield RAG pilot.
- [ ] The likely T2 target is narrowed to the normal runtime path
  (`task_runner`/`StatelessCoordinator`) rather than isolated helper tests.

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/api/mastermind_cli/orchestrator/stateless_coordinator.py`
- `apps/api/mastermind_cli/api/services/task_runner.py`
- potentially narrow ID-compatibility helpers/tests only
- focused tests around Brain #1 runtime execution and `rag_enabled`

### Validation Commands
- Run targeted validation commands for the touched area.

### Acceptance Criteria
- [ ] The main user-visible or system-visible behavior exists.
- [ ] Tests or validation commands demonstrate the behavior.
- [ ] A normal Brain #1 runtime execution path actually activates RAG when a
  DB connection is available.
- [ ] `rag_enabled` metadata reflects the aligned runtime path.

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
