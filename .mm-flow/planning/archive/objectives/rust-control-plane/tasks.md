# Tasks — rust-control-plane

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
- [ ] The first slice is explicitly scoped to closing the logout placeholder.
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
- nearby auth tests

### Validation Commands
- `cargo test --manifest-path rust_control_plane/Cargo.toml auth`

### Acceptance Criteria
- [ ] Logout no longer returns `NOT_IMPLEMENTED`.
- [ ] Logout revokes sessions for the authenticated user via the existing auth boundary.
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

## T4: Define the next Rust control-plane slice

### Purpose

Keep the broader `rust-control-plane` objective alive by choosing the next
highest-value slice after auth completion.

### Depends On

T3

### Parallelizable

no

### Files / Areas Likely Touched

- `design.md`
- `tasks.md`
- `todo.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] The next Rust control-plane slice is explicit.
- [ ] The next slice is narrow enough to execute safely.
- [ ] Another model can resume from artifacts alone.

## T5: Implement explicit AI-worker runtime boundary

### Purpose

Replace the current placeholder AI-worker runtime state with an explicit
boundary that another model or operator can understand from code and health
signals.

### Depends On

T4

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/src/main.rs`
- `rust_control_plane/src/queue/worker.rs`
- `rust_control_plane/src/health/ready.rs`
- any small shared Rust type needed for the boundary

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`

### Acceptance Criteria

- [ ] The placeholder `Option<Arc<()>>` no longer exists on the touched runtime path.
- [ ] Disabled AI-worker state is represented explicitly, including reason/context.
- [ ] Readiness or equivalent runtime output no longer pretends `grpc_python` is healthy by default.

## T6: Close continuity for the next Rust slice

### Purpose

Refresh package continuity after the AI-worker boundary slice lands.

### Depends On

T5

### Parallelizable

no

### Files / Areas Likely Touched

- `HANDOFF-CURRENT.md`
- `todo.md`
- root planning handoff if needed

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff states the new Rust boundary clearly.
- [ ] Validation commands are refreshed and pass.

## T7: Define the next Rust control-plane slice

### Purpose

Choose the next narrow Rust slice after the explicit AI-worker boundary lands.

### Depends On

T6

### Parallelizable

no

### Files / Areas Likely Touched

- `requirements.md`
- `design.md`
- `tasks.md`
- `todo.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] The next Rust gap is explicit from artifacts alone.
- [ ] The next slice is narrower than the whole Rust backlog.
- [ ] Another model can resume without chat context.

## T8: Restore the metrics latency validation baseline

### Purpose

Repair the narrow `metrics::latency` mismatch so Rust validation becomes more
truthful without mixing in unrelated failing suites.

### Depends On

T7

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/src/metrics/latency.rs`
- nearby latency tests only

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml metrics::latency`

### Acceptance Criteria

- [ ] `record_e2e_latency` no longer ignores the `channel` dimension.
- [ ] `metrics::latency` tests pass against the actual Prometheus metric shape.
- [ ] The slice stays confined to metrics latency behavior and tests.

## T9: Close continuity for the metrics slice

### Purpose

Refresh objective continuity after the metrics validation slice lands.

### Depends On

T8

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml metrics::latency`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects the restored metrics baseline and remaining Rust gaps.
- [ ] Validation commands are refreshed and pass.

## T10: Define the next Rust control-plane slice

### Purpose

Choose the next narrow Rust slice now that metrics latency and email thread-id
parsing are no longer the blockers.

### Depends On

T9

### Parallelizable

no

### Files / Areas Likely Touched

- `requirements.md`
- `design.md`
- `tasks.md`
- `todo.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] The next Rust gap is explicit from artifacts alone.
- [ ] The next slice is narrower than the whole Rust backlog.
- [ ] Another model can resume without chat context.

## T11: Clarify the DLQ test environment contract

### Purpose

Make `dlq_test` behave predictably by aligning its setup with the intended test
database contract.

### Depends On

T10

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/tests/dlq_test.rs`
- only closely related DLQ test setup helpers if needed

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml --test dlq_test`

### Acceptance Criteria

- [ ] The DLQ integration tests no longer depend on a contradictory setup path.
- [ ] The intended database/test-environment contract is explicit in code.
- [ ] The slice stays confined to DLQ test setup unless a real logic bug is uncovered.

## T12: Close continuity for the DLQ test slice

### Purpose

Refresh objective continuity after the DLQ test-contract slice lands.

### Depends On

T11

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml --test dlq_test`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects the DLQ test contract and any remaining Rust gaps.
- [ ] Validation commands are refreshed and pass.

## T13: Define the next Rust control-plane slice

### Purpose

Choose the next narrow Rust slice now that the current test baseline is green.

### Depends On

T12

### Parallelizable

no

### Files / Areas Likely Touched

- `requirements.md`
- `design.md`
- `tasks.md`
- `todo.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] The next Rust gap is explicit from artifacts alone.
- [ ] The next slice is narrower than full worker/gRPC reactivation.
- [ ] Another model can resume without chat context.

## T14: Restore the typed AI-worker startup seam

### Purpose

Reconnect Rust startup to the existing gRPC client type so runtime state can
distinguish disabled, unavailable, and initialized worker modes honestly.

### Depends On

T13

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/src/state.rs`
- `rust_control_plane/src/main.rs`
- `rust_control_plane/src/queue/worker.rs`
- possibly a small focused startup/runtime test surface

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`

### Acceptance Criteria

- [ ] Runtime state is no longer limited to a single disabled variant.
- [ ] Startup attempts AI-worker client initialization through the typed gRPC client path.
- [ ] Connection failure degrades cleanly without pretending the worker is active.

## T15: Close continuity for the startup seam slice

### Purpose

Refresh objective continuity after the typed AI-worker startup seam lands.

### Depends On

T14

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed
- narrow planning artifacts if a next slice must be made explicit

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects the restored startup seam and the remaining Rust runtime gap.
- [ ] The next narrow Rust slice is explicit enough for another model to resume from artifacts alone.
- [ ] Validation commands are refreshed and pass.

## T16: Retain the initialized AI-worker client in runtime state

### Purpose

Remove the next worker/gRPC placeholder by keeping the successfully initialized
typed client in runtime state for later dispatch slices.

### Depends On

T15

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/src/state.rs`
- `rust_control_plane/src/main.rs`
- `rust_control_plane/src/queue/worker.rs`
- small focused runtime tests only

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`

### Acceptance Criteria

- [ ] `AiWorkerRuntimeMode::Ready` retains the initialized typed client instead of only an address.
- [ ] Startup no longer discards the successfully connected client.
- [ ] The dispatch path still remains fail-closed in this slice.

## T17: Close continuity for the retained-client slice

### Purpose

Refresh objective continuity after the retained-client runtime slice lands.

### Depends On

T16

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed
- narrow planning artifacts if the next slice must be made explicit

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects retained-client runtime state and the next worker/gRPC gap.
- [ ] The next narrow Rust slice is explicit enough for another model to resume from artifacts alone.
- [ ] Validation commands are refreshed and pass.

## T18: Use the retained AI-worker client for first dispatch

### Purpose

Turn retained worker connectivity into a real typed dispatch path without
reopening the whole worker/gRPC backlog.

### Depends On

T17

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/src/queue/worker.rs`
- `rust_control_plane/src/grpc/worker.rs`
- small focused worker tests only

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`

### Acceptance Criteria

- [ ] `send_to_ai_worker()` uses the retained typed client when runtime is `Ready`.
- [ ] Disabled and unavailable modes keep their current explicit behavior.
- [ ] Worker/gRPC dispatch failures no longer masquerade as success.

## T19: Close continuity for the first-dispatch slice

### Purpose

Refresh objective continuity after the first-use typed dispatch slice lands.

### Depends On

T18

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed
- narrow planning artifacts if the next slice must be made explicit

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects the first-dispatch slice and the next remaining worker/gRPC gap.
- [ ] The next narrow Rust slice is explicit enough for another model to resume from artifacts alone.
- [ ] Validation commands are refreshed and pass.

## T20: Fail closed for disabled and unavailable worker runtime modes

### Purpose

Remove the remaining silent-success behavior in degraded worker runtime modes.

### Depends On

T19

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/src/queue/worker.rs`
- small focused worker/runtime tests only

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`

### Acceptance Criteria

- [ ] `Disabled` runtime mode returns an explicit processing error instead of `Ok(())`.
- [ ] `Unavailable` runtime mode returns an explicit processing error instead of `Ok(())`.
- [ ] Existing retry / DLQ behavior absorbs those errors without broad redesign.
- [ ] Webhook processing still remains fail-closed unless explicitly enabled by a later slice.

## T21: Close continuity for the degraded-runtime slice

### Purpose

Refresh objective continuity after degraded runtime modes fail closed.

### Depends On

T20

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed
- narrow planning artifacts if the next slice must be made explicit

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects that degraded runtime modes now fail closed.
- [ ] The next narrow Rust slice is explicit enough for another model to resume from artifacts alone.
- [ ] Validation commands are refreshed and pass.

## T22: Clarify post-dispatch success semantics

### Purpose

Make worker success semantics truthful once the retained AI-worker client
returns a successful response.

### Depends On

T21

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/src/queue/worker.rs`
- focused worker/runtime tests only
- planning artifacts if the contract needs to be narrowed further

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- targeted Rust tests for queue/worker status transitions if added

### Acceptance Criteria

- [ ] Artifacts define what a successful AI-worker response means for message state.
- [ ] Worker status/audit behavior matches that contract in the narrowest possible place.
- [ ] The slice avoids broad retry, DLQ, or schema redesign unless tests prove they are required.

## T23: Close continuity for the post-dispatch semantics slice

### Purpose

Refresh objective continuity after post-dispatch success semantics are made
truthful.

### Depends On

T22

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed
- narrow planning artifacts if the next slice must be made explicit

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml queue::worker`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects the clarified meaning of successful AI-worker dispatch.
- [ ] The next narrow Rust slice is explicit enough for another model to resume from artifacts alone.
- [ ] Validation commands are refreshed and pass.

## T24: Add durable audit surface for successful AI-worker responses

### Purpose

Preserve the minimum useful AI-worker result beyond transient logs.

### Depends On

T23

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/src/queue/worker.rs`
- the narrowest existing audit/event surface that can persist a response summary
- focused worker/runtime tests only

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml queue::worker`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- targeted Rust tests for the chosen audit surface if added

### Acceptance Criteria

- [ ] Artifacts define the minimum durable record that should survive a successful AI-worker response.
- [ ] Worker writes or attaches that record without changing the phase-10 success contract.
- [ ] The slice avoids broad schema or workflow redesign unless tests prove they are required.

## T25: Close continuity for the durable success-audit slice

### Purpose

Refresh objective continuity after successful AI-worker responses gain durable
audit records.

### Depends On

T24

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed
- narrow planning artifacts if the next slice must be made explicit

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml queue::worker`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects the durable success-audit contract.
- [ ] The next narrow Rust slice is explicit enough for another model to resume from artifacts alone.
- [ ] Validation commands are refreshed and pass.

## T26: Add durable audit surface for failed AI-worker responses

### Purpose

Preserve the minimum useful AI-worker failure record alongside the existing
retry/DLQ path.

### Depends On

T25

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/src/queue/worker.rs`
- the narrowest existing audit/event surface that can persist a failure summary
- focused worker/runtime tests only

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml queue::worker`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- targeted Rust tests for the chosen failure-audit surface if added

### Acceptance Criteria

- [ ] Artifacts define the minimum durable record that should survive failed AI-worker processing.
- [ ] Worker writes or attaches that failure record without redesigning retry/DLQ flow.
- [ ] The slice keeps the new success-audit path intact unless tests prove another contract is required.

## T27: Close continuity for the durable failure-audit slice

### Purpose

Refresh objective continuity after failed AI-worker responses gain durable audit
records.

### Depends On

T26

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed
- narrow planning artifacts if the next slice must be made explicit

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml queue::worker`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects the durable failure-audit contract.
- [ ] The next narrow Rust slice is explicit enough for another model to resume from artifacts alone.
- [ ] Validation commands are refreshed and pass.

## T28: Clarify AI-worker audit event taxonomy

### Purpose

Decide whether AI-worker audit records should keep reusing generic
`brain_completed` / `brain_failed` labels or move to a more specific taxonomy.

### Depends On

T27

### Parallelizable

no

### Files / Areas Likely Touched

- planning artifacts first
- `rust_control_plane/src/queue/worker.rs` only if taxonomy changes are justified
- focused worker/audit tests only

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml queue::worker`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- targeted Rust tests for audit event naming if added

### Acceptance Criteria

- [ ] Artifacts explain whether the current event taxonomy is sufficient for AI-worker audit records.
- [ ] Any code change stays narrow and preserves the existing durable audit content.
- [ ] The slice avoids broad event-sourcing redesign unless tests prove it is required.

## T29: Close continuity for the audit-taxonomy slice

### Purpose

Refresh objective continuity after deciding whether AI-worker audit taxonomy
needs to change.

### Depends On

T28

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed
- narrow planning artifacts if the next slice must be made explicit

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml queue::worker`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects the taxonomy decision for AI-worker audit records.
- [ ] The next narrow Rust slice is explicit enough for another model to resume from artifacts alone.
- [ ] Validation commands are refreshed and pass.

## T30: Clarify AI-worker audit query ergonomics

### Purpose

Make AI-worker audit records easier to query by `message_id` or `trace_id`
without broad audit API redesign.

### Depends On

T29

### Parallelizable

no

### Files / Areas Likely Touched

- planning artifacts first
- existing Rust audit surfaces only if a narrow filter is justified
- focused audit/query tests only

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml queue::worker`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- targeted Rust tests for any new audit query helper/filter if added

### Acceptance Criteria

- [ ] Artifacts define the narrowest useful query/filter surface for AI-worker audit records.
- [ ] Any code change reuses existing audit surfaces instead of introducing a broad new subsystem.
- [ ] The slice preserves the current durable audit content and taxonomy decision unless tests prove another contract is required.

## T31: Close continuity for the audit-query slice

### Purpose

Refresh objective continuity after deciding or implementing the narrowest
AI-worker audit query surface.

### Depends On

T30

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed
- narrow planning artifacts if the next slice must be made explicit

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml queue::worker`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects the audit-query decision or implementation.
- [ ] The next narrow Rust slice is explicit enough for another model to resume from artifacts alone.
- [ ] Validation commands are refreshed and pass.

## T32: Decide whether AI-worker needs a dedicated audit convenience surface

### Purpose

Decide whether the new `message_id` / `trace_id` filters are enough, or whether
an AI-worker-specific convenience endpoint/helper is justified.

### Depends On

T31

### Parallelizable

no

### Files / Areas Likely Touched

- planning artifacts first
- existing audit surfaces only if a very narrow convenience layer is justified
- focused audit/query tests only

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml queue::worker`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- targeted Rust tests for any convenience surface if added

### Acceptance Criteria

- [ ] Artifacts explain whether the new filters are sufficient for AI-worker lookup workflows.
- [ ] Any code change stays narrower than a broad new audit API.
- [ ] The slice preserves the current filters, taxonomy, and durable audit content unless tests prove another contract is required.

## T33: Close continuity for the audit-convenience decision slice

### Purpose

Refresh objective continuity after deciding whether AI-worker needs a dedicated
audit convenience surface.

### Depends On

T32

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed
- narrow planning artifacts if the next slice must be made explicit

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml queue::worker`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects the convenience-surface decision.
- [ ] The next narrow Rust slice is explicit enough for another model to resume from artifacts alone.
- [ ] Validation commands are refreshed and pass.

## T34: Decide whether rust-control-plane is ready to close

### Purpose

Determine whether this objective still has a coherent remaining slice or can be
archived in favor of a different system frontier.

### Depends On

T33

### Parallelizable

no

### Files / Areas Likely Touched

- planning artifacts only unless a new slice is clearly justified

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Artifacts clearly state whether a remaining Rust slice still exists.
- [ ] If more work remains, the next slice is narrower than reopening broad worker/gRPC work.
- [ ] If no material slice remains, the objective is ready for archive/transition.

## T15: Close continuity for the startup seam slice

### Purpose

Refresh planning continuity after the typed AI-worker startup seam lands.

### Depends On

T14

### Parallelizable

no

### Files / Areas Likely Touched

- `todo.md`
- `HANDOFF-CURRENT.md`
- root handoff if needed

### Validation Commands

- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective rust-control-plane`

### Acceptance Criteria

- [ ] Handoff reflects the restored startup/runtime seam and the remaining gRPC work.
- [ ] Validation commands are refreshed and pass.
