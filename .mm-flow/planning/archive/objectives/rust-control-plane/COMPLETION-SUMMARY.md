# Completion Summary — rust-control-plane

- Archived at: 2026-06-05T23:04:49
- Completion basis: todo.md shows all checklist items completed
- Source moved from: /home/rpadron/proy/mastermind/.mm-flow/planning/changes/rust-control-plane

## Handoff Snapshot
# Handoff — rust-control-plane

## Current objective
- `rust-control-plane`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.
- Phase 1 is explicitly scoped to closing the Rust `logout` placeholder.
- `/api/auth/logout` now revokes all refresh-token sessions for the authenticated user.
- Auth middleware extensions are now reused consistently for logout.
- The next slice is to make AI-worker unavailability explicit in runtime state before re-enabling full gRPC processing.
- The runtime now carries explicit AI-worker disabled state instead of `Option<Arc<()>>`.
- Readiness no longer treats `grpc_python` as healthy by default when the worker boundary is disabled.
- The `metrics::latency` baseline repair is complete.
- Email thread-id parsing now normalizes RFC angle-bracket references correctly.
- The DLQ integration-test environment contract is now explicit and predictable.
- The full Rust test suite now passes in the current environment.
- The next chosen slice is the typed AI-worker startup/runtime seam, not full webhook gRPC dispatch.
- The typed AI-worker startup/runtime seam is now restored with explicit `disabled` / `unavailable` / `ready` runtime modes.
- Startup now attempts typed gRPC client initialization through `AiWorkerClient::new(...)` and degrades cleanly to `unavailable` on connection failure.
- `Ready` runtime state now retains the initialized typed `AiWorkerClient` instead of only address metadata.
- `Ready` runtime mode now performs the first real typed dispatch path through the retained client.
- `Disabled` and `Unavailable` runtime modes now fail closed instead of returning `Ok(())`.
- A successful `Ready` dispatch now means AI-worker processing completed; it no longer records provider delivery status `sent` at that point.
- Successful AI-worker responses now append an idempotent immutable `activity_log` record with `message_id`, `trace_id`, `channel`, and `ai_response`.
- Failed AI-worker processing now also appends immutable `activity_log` records with `message_id`, `trace_id`, `channel`, `error`, `retry_count`, and `terminal`.
- AI-worker audit records intentionally keep the generic `brain_completed` / `brain_failed` labels for now, scoped by `brain_id = ai_worker`.
- Existing audit queries now support `message_id` and `trace_id` filters for AI-worker records without adding a new audit subsystem.
- The new `message_id` / `trace_id` filters are sufficient for the known AI-worker lookup workflow; no dedicated convenience surface is justified right now.
- This objective is now ready to close; no further narrow slice remains inside the current `rust-control-plane` package.
- Broader follow-up Rust work such as full worker/gRPC reactivation or migration hygiene should start as new objectives instead of extending this package further.

## Blockers / risks
- Full worker/gRPC reactivation is still materially larger than the slices closed so far and should be replanned separately.
- Migration hygiene still exists, but is a lower-priority follow-up rather than unfinished work inside this package.

## Exact next recommended task
- Run `/mm:archive-objective rust-control-plane`.

## Validation commands
- `/mm:discover-contract-check --objective rust-control-plane`
- `cargo test --manifest-path rust_control_plane/Cargo.toml ai_worker_runtime`
- `cargo test --manifest-path rust_control_plane/Cargo.toml grpc::worker`
