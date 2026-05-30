# Tasks — window-scheduler

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

## T1: Define and stabilize the slice

### Purpose
Clarify the exact objective boundary before implementation expands. Tighten naming and acceptance criteria.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- `.mm-flow/planning/changes/window-scheduler/requirements.md`
- `.mm-flow/planning/changes/window-scheduler/design.md`
- `.mm-flow/planning/changes/window-scheduler/tasks.md`

### Validation Commands
- Verify all three docs reference "window-scheduler" (not "runtime-window-scheduler" or other aliases)
- Verify design.md lists the 5 minimum viable entities: BackendSession, AvailabilityState, RunPolicy, SchedulerEvent, SchedulerCheckpoint
- Verify design.md states the 4 schema constraints (no switch without checkpoint, no checkpoint without next_step_summary, reset estimations need source+confidence, every run needs policy)
- Verify requirements.md acceptance criteria are specific and measurable

### Acceptance Criteria
- [x] All three docs use the consistent objective name "window-scheduler"
- [x] Design.md explicitly defines the 5 minimum viable entities
- [x] Design.md explicitly states the 4 schema constraints
- [x] Requirements.md has specific, measurable acceptance criteria (not vague statements)

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- Implementation-specific files (to be defined after T1 stabilization)

### Validation Commands
- Run targeted validation commands for the touched area.

### Acceptance Criteria
- [ ] The main user-visible or system-visible behavior exists.
- [ ] Tests or validation commands demonstrate the behavior.

## T3: Close the continuity loop

### Purpose
Refresh handoff and validation context for the next model/session.

### Depends On
T2

### Parallelizable
no

### Files / Areas Likely Touched
- `.mm-flow/planning/changes/window-scheduler/HANDOFF-CURRENT.md`
- `.mm-flow/planning/changes/window-scheduler/tasks.md`
- `.mm-flow/planning/changes/window-scheduler/todo.md`

### Validation Commands
- Refresh handoff and rerun discovery contract check.
- Run: `python3 .claude/commands/mm/discover-contract-check.py --objective window-scheduler`

### Acceptance Criteria
- [ ] Handoff notes are refreshed with next recommended work.
- [ ] Validation commands are documented and pass.
