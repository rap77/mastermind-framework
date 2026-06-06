# Design — rust-control-plane

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance
  criteria.
- Prefer making disabled runtime boundaries explicit before re-enabling a large
  subsystem.

### Completed phase-1 slice

Phase 1 closed the Rust `logout` placeholder in `rust_control_plane`.

Current state:

- `/api/auth/logout` is routed through auth middleware
- authenticated user context is already injected into request extensions
- `revoke_all_tokens(pool, user_id)` already exists
- the handler still returns `501 NOT_IMPLEMENTED`

### Phase-1 approach

The smallest safe fix is:

1. extract `AuthenticatedRequest` from request extensions
2. call `revoke_all_tokens` for the authenticated user
3. return a normal success status instead of `NOT_IMPLEMENTED`

This keeps the boundary narrow and finishes an auth path that is already mostly
built.

### Chosen phase-2 slice

Phase 2 clarifies the AI worker boundary without pretending gRPC integration is
already healthy.

Current state:

- `main.rs` comments out real gRPC client initialization
- runtime state falls back to `Option<Arc<()>>`
- queue processing logs that AI processing is disabled, but the type system does
  not explain why
- readiness currently reports `grpc_python` as healthy by default

### Phase-2 approach

The smallest safe fix is:

1. replace `Option<Arc<()>>` with an explicit AI-worker runtime mode
2. carry a machine-readable disabled reason through startup and queue worker
3. surface that disabled/degraded state through the existing readiness path
4. keep actual webhook gRPC processing disabled until a later slice

This narrows the boundary ambiguity without opening the larger worker/gRPC
reactivation front.

### Chosen phase-3 slice

Phase 3 restores the Rust metrics latency test baseline without mixing in other
failing suites.

Current state:

- `metrics::latency` defines `WEBHOOK_E2E_LATENCY_SECONDS` as a plain
  `Histogram`
- `record_e2e_latency(channel, duration)` ignores the `channel` argument
- the tests expect per-channel labels and a gatherable metric family shape that
  the current implementation does not provide
- the full Rust test run is red partly because of these mismatches

### Phase-3 approach

The smallest safe fix is:

1. make the latency metric shape match the intended `channel` dimension
2. update `record_e2e_latency` to record through that labeled metric
3. keep the slice limited to `metrics::latency` and its tests
4. leave `channels::email` failures for a later slice

This improves validation trust without reopening unrelated runtime boundaries.

### Completed phase-4 slice

Phase 4 normalized email thread-id extraction so RFC angle-bracketed message
references now match the expectations of the Rust email parser tests.

### Chosen phase-5 slice

Phase 5 clarifies why `dlq_test` still fails under the current environment and
makes that contract explicit in code or test setup.

Current state:

- full `cargo test --manifest-path rust_control_plane/Cargo.toml` no longer
  fails in `metrics::latency` or `channels::email`
- the remaining failures are all in `rust_control_plane/tests/dlq_test.rs`
- those tests use `#[sqlx::test]` but still perform a manual `PgPool::connect`
  against a local test database URL
- in the current sandbox that connection fails with `PermissionDenied`

### Phase-5 approach

The smallest safe fix is:

1. define the intended contract for DLQ integration tests clearly
2. remove contradictory setup paths if the sqlx harness should own the database
3. keep the slice focused on test portability and truthful validation
4. avoid mixing in runtime DLQ behavior changes unless tests prove they are needed

This keeps the next Rust slice about validation trust, not feature expansion.

### Completed phase-5 slice

Phase 5 removed the contradictory DLQ integration-test setup and made the test
environment contract explicit: use `TEST_DATABASE_URL` or `DATABASE_URL` when
available, otherwise skip predictably.

### Chosen phase-6 slice

Phase 6 returns to the larger Rust runtime theme, but still as a narrow slice:
make worker/gRPC reactivation explicit enough that another model can implement
it incrementally instead of leaving it as commented-out placeholders.

Current state:

- the full Rust test suite now passes in the current environment
- the active runtime still carries an explicit disabled AI-worker mode
- `main.rs` still comments out real gRPC client initialization
- `queue/worker.rs` still never attempts real worker processing

### Phase-6 approach

The smallest safe next step is:

1. define the first reactivation slice explicitly from artifacts
2. keep it narrower than “turn gRPC fully on”
3. prefer one honest runtime seam over several TODO placeholders

This keeps the next slice execution-ready without reopening the whole control
plane at once.

### Refined phase-6 slice

The first honest reactivation step is not “turn webhook gRPC fully on.” It is
to restore a typed startup/runtime seam for the AI worker client.

Current state:

- `rust_control_plane::grpc::AiWorkerClient` compiles and has its own client
  wrapper
- `state::AiWorkerRuntimeMode` only supports `Disabled`
- `main.rs` still comments out real client initialization even though `lib.rs`
  exports `grpc` and `mastermind`
- `queue/worker.rs` can only log the disabled state, not distinguish disabled
  from startup connection failure or successful initialization

### Phase-6 approach

The smallest safe implementation slice should:

1. add explicit runtime variants beyond `Disabled`
2. restore AI worker startup initialization through the library gRPC client
3. preserve fail-closed behavior when connection fails
4. keep actual webhook dispatch through the client out of scope for now

This gives the system an honest startup/runtime contract before any processing
path is switched over.

### Completed phase-6 slice

Phase 6 restored the typed AI-worker startup seam:

- `main.rs` now attempts `AiWorkerClient::new(...)`
- runtime mode now distinguishes `Disabled`, `Unavailable`, and `Ready`
- queue processing still stays fail-closed even when startup connectivity is
  available

### Chosen phase-7 slice

Phase 7 should make the successful startup seam usable by later slices without
turning dispatch on yet.

Current state:

- startup now proves connectivity through the typed gRPC client path
- `AiWorkerRuntimeMode::Ready` only retains the worker address, not the client
  handle
- later slices would need to reconnect or redesign runtime state before they
  can enable dispatch incrementally
- queue/worker logic still has no typed path to obtain a ready client even when
  startup succeeded

### Phase-7 approach

The smallest safe next step is:

1. retain the initialized AI-worker client in the ready runtime state
2. keep disabled/unavailable behavior unchanged
3. expose only the narrow accessors needed for future dispatch slices
4. keep real webhook dispatch through the client out of scope for now

This preserves slice discipline while removing the next blocking placeholder in
the worker/gRPC path.

### Completed phase-7 slice

Phase 7 now retains the initialized `AiWorkerClient` inside
`AiWorkerRuntimeMode::Ready` instead of discarding it after startup.

Current state:

- startup connects through `AiWorkerClient::new(...)`
- successful initialization is preserved in runtime state
- queue worker can now distinguish a retained ready client from unavailable or
  disabled modes
- dispatch itself is still intentionally fail-closed

### Chosen phase-8 slice

Phase 8 should make the retained client usable by the queue worker without
opening the full worker/gRPC surface all at once.

Current state:

- the client is now retained in `Ready`
- `send_to_ai_worker()` still only logs and returns `Ok(())`
- the next narrow value is to switch that method from “retained but unused” to
  a first explicit typed dispatch path
- this still needs a clear guard so failures degrade through the existing retry
  / DLQ flow instead of pretending success

### Phase-8 approach

The smallest safe next step is:

1. use the retained client inside `send_to_ai_worker()`
2. keep disabled/unavailable behavior unchanged
3. let typed dispatch failures surface as normal worker errors
4. avoid broad readiness or retry redesign in the same slice

This turns retained connectivity into a real but still narrow worker/gRPC
execution seam.

### Completed phase-8 slice

Phase 8 now routes `send_to_ai_worker()` through the retained typed client when
runtime mode is `Ready`.

Current state:

- `Ready` no longer logs fake success; it attempts real typed gRPC dispatch
- worker/gRPC call failures now surface through the existing retry / DLQ path
- `Disabled` and `Unavailable` still return `Ok(())` after explicit warning
  logs

### Chosen phase-9 slice

Phase 9 should remove the remaining silent-success behavior in degraded modes.

Current state:

- `Ready` now fails honestly when gRPC dispatch fails
- `Disabled` and `Unavailable` still let the worker continue as though the
  webhook were processed successfully
- this means degraded runtime modes can still mark messages completed even when
  no AI processing happened
- the next narrow value is to make those degraded runtime modes fail closed too

### Phase-9 approach

The smallest safe next step is:

1. keep `Ready` dispatch behavior as-is
2. change `Disabled` and `Unavailable` branches to return explicit errors
3. let existing retry / DLQ behavior handle those failures
4. avoid mixing in broader delivery-status or response-persistence redesign

This removes the last major “successful without processing” path from the
current worker/gRPC seam.

### Completed phase-9 slice

Phase 9 now fails closed for degraded worker runtime modes instead of
pretending webhook processing succeeded.

Current state:

- `Disabled` returns an explicit processing error with the configured reason
- `Unavailable` returns an explicit processing error with connection context
- existing retry / DLQ behavior absorbs those errors without broad redesign
- `Ready` still treats a successful gRPC response as immediate worker success

### Chosen phase-10 slice

Phase 10 should make post-dispatch success semantics more truthful and
auditable.

Current state:

- a successful `Ready` dispatch only logs `ai_response`
- the worker immediately records delivery status `sent`
- the worker immediately marks the message `completed`
- another model/operator cannot infer from artifacts whether that means
  “AI worker accepted the webhook”, “an outbound provider send happened”, or
  both

### Phase-10 approach

The smallest safe next step is:

1. define the intended success contract after a successful AI-worker response
2. make status/audit behavior match that contract in the narrowest place
3. keep degraded-mode and retry/DLQ behavior unchanged
4. avoid broad schema or queue redesign in the same slice

This keeps the next Rust slice focused on truthful semantics instead of adding
more worker/gRPC surface area.

### Completed phase-10 slice

Phase 10 now makes post-dispatch success semantics explicit in the worker.

Current state:

- a successful AI-worker response marks message processing `completed`
- it no longer records provider delivery status `sent` at that point
- the contract is now explicit in code: AI-worker success is processing
  completion, not provider delivery confirmation
- `ai_response` still only appears in logs

### Chosen phase-11 slice

Phase 11 should make AI-worker results more durable and auditable than a log
line alone.

Current state:

- the worker now uses truthful success semantics for message and delivery state
- successful `ai_response` content is still only emitted through tracing logs
- another model/operator cannot inspect later what the AI worker returned for a
  completed message unless logs were preserved externally

### Phase-11 approach

The smallest safe next step is:

1. define the narrowest durable audit surface for successful AI-worker results
2. persist or attach only the minimum useful response summary
3. keep message-state semantics from phase 10 unchanged
4. avoid broad schema, queue, or provider-delivery redesign in the same slice

This keeps the next Rust slice about auditability, not a larger workflow
reactivation.

### Completed phase-11 slice

Phase 11 now writes a durable audit record for successful AI-worker responses.

Current state:

- successful AI-worker responses append an immutable `activity_log` record
- the record is idempotent per `message_id`
- the payload captures the minimum useful fields: `message_id`, `trace_id`,
  `channel`, and `ai_response`
- message-state semantics from phase 10 remain unchanged

### Chosen phase-12 slice

Phase 12 should make AI-worker audit trails symmetrical across success and
failure.

Current state:

- successful AI-worker responses now have a durable audit record
- failed AI-worker processing still relies on retry/DLQ state plus transient
  logs
- another model/operator cannot query one audit surface and compare successful
  versus failed worker outcomes for the same boundary

### Phase-12 approach

The smallest safe next step is:

1. define the minimum durable failure audit record for AI-worker processing
2. attach it in the narrowest failure path that already owns retry/DLQ handling
3. keep phase-10 message semantics and phase-11 success audit behavior
   unchanged
4. avoid broad DLQ redesign or new event-taxonomy work in the same slice

This keeps the next Rust slice about audit symmetry, not a larger worker
workflow rewrite.

### Completed phase-12 slice

Phase 12 now writes durable failure audit records for AI-worker processing.

Current state:

- failed AI-worker processing appends immutable `activity_log` records
- the payload captures the minimum useful fields: `message_id`, `trace_id`,
  `channel`, `error`, `retry_count`, and `terminal`
- retry/DLQ behavior remains unchanged
- successful and failed worker outcomes are now both queryable through the same
  audit surface

### Chosen phase-13 slice

Phase 13 should decide whether the reused `brain_completed` / `brain_failed`
event taxonomy is precise enough for AI-worker audit records.

Current state:

- success and failure audit records now exist on the same surface
- they currently reuse generic event labels with `brain_id = ai_worker`
- another model/operator can query them, but the taxonomy may still be too
  broad if later worker events need to be distinguished from other brain-style
  records

### Completed phase-13 slice

Phase 13 keeps the current generic taxonomy for AI-worker audit records.

Current state:

- `brain_id = ai_worker` already scopes these records clearly
- `brain_completed` / `brain_failed` preserve compatibility with existing audit
  queries and indexes
- introducing a new event taxonomy now would add churn without materially
  improving the current resume/debug workflow

### Chosen phase-14 slice

Phase 14 should make AI-worker audit records easier to query from existing
surfaces.

Current state:

- success and failure audit records now exist durably
- the taxonomy is intentionally unchanged for now
- another model/operator still has to know the right generic audit filters to
  find records for a given `message_id` or `trace_id`

### Phase-14 approach

The smallest safe next step is:

1. define the narrowest useful query/filter surface for AI-worker audit records
2. prefer existing audit endpoints or store queries over a new subsystem
3. keep taxonomy and durable record content unchanged
4. avoid broad audit-schema or API redesign in the same slice

This keeps the next Rust slice about query ergonomics, not a new worker
integration jump.

### Completed phase-14 slice

Phase 14 adds narrow audit-query ergonomics on top of the existing surfaces.

Current state:

- `ActivityLogQuery` now supports `message_id` and `trace_id`
- `EventStore::read_events()` can filter by those payload fields
- existing audit surfaces are reused; no new subsystem or taxonomy was added

### Chosen phase-15 slice

Phase 15 should decide whether those new filters are sufficient or whether a
smaller AI-worker-specific convenience surface is justified.

Current state:

- another model/operator can now find AI-worker audit records through existing
  activity-log filters
- this may already be enough for resume/debug workflows
- the remaining question is whether the workflow still feels too indirect to
  justify a narrower convenience surface later

### Phase-15 approach

The smallest safe next step is:

1. evaluate whether the new `message_id` / `trace_id` filters already satisfy
   the concrete AI-worker lookup workflow
2. prefer documenting “no new surface needed” over adding another endpoint
3. keep the current filters, taxonomy, and durable audit records unchanged
4. avoid broad audit API growth in the same slice

This keeps the next Rust slice about deciding sufficiency, not adding more
surface area by default.

### Completed phase-15 slice

Phase 15 keeps the existing audit filters as the right convenience level for
now.

Current state:

- `brain_id=ai_worker` plus optional `message_id` / `trace_id` is sufficient
  for the known resume/debug workflow
- a dedicated AI-worker convenience surface would duplicate existing audit
  capability without unlocking a new concrete operator workflow
- the smallest honest next step is to decide whether the Rust control-plane
  objective still has a material remaining gap

### Chosen phase-16 slice

Phase 16 should determine whether `rust-control-plane` still has a coherent
remaining slice or is ready to close.

Current state:

- the objective already closed the original auth placeholder, runtime truth,
  first typed dispatch, degraded fail-closed behavior, and AI-worker auditability
- the remaining broad ideas (`full worker/gRPC reactivation`, `migration hygiene`)
  are no longer narrow follow-ups of the current slice sequence
- keeping them inside this objective would reopen a much larger frontier than
  the package has been using

### Phase-16 approach

The smallest safe next step is:

1. decide whether any remaining Rust work is still coherent with this package
2. if not, declare the objective ready to close and push broader follow-up work
   into a new objective later
3. avoid reopening broad worker/gRPC reactivation inside this package

This keeps the package honest: close the finished hardening/audit sequence and
start any larger frontier as a new objective.

### Completed phase-16 slice

Phase 16 concludes that `rust-control-plane` is ready to close.

Current state:

- no material narrow slice remains inside the current hardening/audit sequence
- broader worker/gRPC reactivation is still real, but it should be a separate
  future objective rather than another tail slice here
- migration hygiene also remains a lower-priority follow-up, not a reason to
  keep this package open

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.
- Prefer explicit degraded-state handling now over pretending the worker/gRPC
  path is already integrated.

## Context Notes
- Full-suite Rust validation now passes in the current environment after the
  DLQ test-contract fix.
- The next narrow Rust gap is no longer degraded-mode error handling,
  post-dispatch success semantics, durable success auditability, or durable
  failure auditability, AI-worker audit taxonomy, audit-query filtering, or
  audit convenience sufficiency; this package is ready to close and any broader
  Rust frontier should start as a new objective.
