# Tasks — rust-control-plane-hardening

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
- [ ] The first hardening slice is explicitly scoped to the refresh-token flow.
- [ ] Existing architecture constraints are preserved and documented.

## T2: Implement the smallest coherent deliverable

### Purpose
Land the core behavior that proves the objective is advancing.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `rust_control_plane/src/handlers/auth.rs`
- `rust_control_plane/src/auth/rotation.rs`
- Rust auth tests near the touched modules

### Validation Commands
- `cargo test --manifest-path rust_control_plane/Cargo.toml auth`

### Acceptance Criteria
- [ ] Refresh-token lookup no longer depends on re-hashing bcrypt for equality.
- [ ] Rotation uses the matched stored session/hash path.
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
