# Tasks — mm-harness-gap-objective-lifecycle-sync

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
- [ ] The package explicitly narrows phase 1 to helper-driven lifecycle sync.
- [ ] Auto-creation and archive hooks are explicitly out of scope.

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `.mm-flow/commands/mm/gap-registry.py`
- `tests/unit/test_mm_gap_registry.py`
- `.mm-flow/planning/gaps/gap-registry.json`

### Validation Commands
- Run targeted validation commands for the touched area.

### Acceptance Criteria
- [ ] The helper can synchronize a gap entry from open/deferred to promoted or resolved using exact objective artifact presence.
- [ ] Tests or validation commands demonstrate the behavior.
- [ ] The slice stays helper-driven and deterministic.

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
