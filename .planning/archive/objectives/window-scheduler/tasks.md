# Tasks — window-scheduler

## T1: Formalize the canonical scheduler domain contract

### Purpose

Turn the architecture and schema docs into a concrete planning contract for the reusable core scheduler slice.

### Validation

- Confirm all five canonical entities are represented
- Confirm all four canonical rules are captured

### Acceptance Criteria

- [ ] `backend_session`, `availability_state`, `run_policy`, `scheduler_event`, and `scheduler_checkpoint` are explicitly represented
- [ ] The checkpoint-before-switch invariant is explicit
- [ ] Reset estimation source/confidence requirements are explicit

## T2: Define the switching and resume boundaries

### Purpose

Specify what belongs to provider registry, availability tracking, eligibility, switch policy, checkpointing, and resume.

### Validation

- Review boundaries against `16-WINDOW-SCHEDULER-ARCHITECTURE.md`

### Acceptance Criteria

- [ ] Component boundaries are clear and non-overlapping
- [ ] Automatic switch vs pause/escalation decision points are explicit
- [ ] Minimum resume payload is defined

## T3: Queue the first implementation slice

### Purpose

Translate the planning package into the next implementation-ready work items without expanding scope into reports, UI, or provider heuristics.

### Validation

- Follow-on work is incremental and does not depend on chat memory

### Acceptance Criteria

- [ ] The first implementation slice is identified
- [ ] Follow-on items for heuristics/reporting are deferred explicitly
- [ ] The package is handoff-ready for the next session
