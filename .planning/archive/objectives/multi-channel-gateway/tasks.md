# Tasks — multi-channel-gateway

## Execution Rules

- Execute in dependency order using TDD.
- Treat provider payloads as untrusted until raw-byte signature verification passes.
- Keep WhatsApp canonical ingest isolated from queue, gRPC, AI and outbound code.
- Never persist raw bodies or log PII/secrets.
- Database integration tests must fail when PostgreSQL is unavailable.
- Use the next available number in `migrations/messaging`; never edit applied migrations.
- Update execution-state, todo and handoff after every task.
- Do not run standalone build commands.

## MCG0: Freeze runtime seams and test infrastructure

### Purpose

Create the messaging module/config boundary and non-skipping PostgreSQL test
harness so later tasks do not invent state ownership or environment behavior.

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/Cargo.toml`
- `rust_control_plane/src/lib.rs`
- `rust_control_plane/src/messaging/config.rs`
- `rust_control_plane/src/messaging/mod.rs`
- `rust_control_plane/tests/support/postgres.rs`

### Validation Commands

- `cd rust_control_plane && cargo test whatsapp_ingress_config`

### Acceptance Criteria

- [x] Disabled config returns `None`; enabled config validates required values, retention and secret distinctness.
- [x] `messaging` module is exported and owns the future ingress types.
- [x] Test DB helper requires a dedicated `TEST_DATABASE_URL`, applies migrations and never skips.
- [x] Cargo includes `subtle` and required SQLx test migration features.

## MCG1: Define the shared canonical inbound contract

### Purpose

Create schema v1 and prove Python/Rust WhatsApp text fixtures represent one
contract before ingress code depends on it.

### Depends On

MCG0

### Parallelizable

no

### Files / Areas Likely Touched

- `docs/contracts/messaging/canonical-inbound-event-v1.schema.json`
- `apps/api/routers/canonical_events.py`
- `apps/api/tests/test_canonical_events.py`
- `rust_control_plane/src/messaging/canonical_event.rs`
- `rust_control_plane/tests/canonical_event_contract_test.rs`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/test_canonical_events.py`
- `cd rust_control_plane && cargo test canonical_event_contract`

### Acceptance Criteria

- [x] Schema v1 contains the approved WhatsApp text fields and forbids arbitrary properties.
- [x] Python and Rust pass the same valid/invalid fixtures.
- [x] New v1 models coexist with the legacy Python multi-channel model without redefining its idempotency semantics.
- [x] Raw provider metadata is not part of the canonical contract.

## MCG2: Implement the secure WhatsApp webhook boundary

### Purpose

Add exact GET subscription and POST raw-byte signature handlers behind the
feature flag, without persistence or downstream calls yet.

### Depends On

MCG1

### Parallelizable

yes, coordinated with MCG3 only through the contract

### Files / Areas Likely Touched

- `rust_control_plane/src/handlers/whatsapp_webhook.rs`
- `rust_control_plane/src/handlers/webhook.rs`
- `rust_control_plane/src/handlers/mod.rs`
- `rust_control_plane/src/main.rs`
- `rust_control_plane/tests/whatsapp_webhook_security_test.rs`

### Validation Commands

- `cd rust_control_plane && cargo test --test whatsapp_webhook_security_test`

### Acceptance Criteria

- [x] GET challenge uses the verify token and returns 403 on mismatch.
- [x] POST uses `Bytes`, accepts only `sha256=<32-byte hex>` and calls `verify_slice`.
- [x] Invalid/missing signatures cannot reach JSON parsing or downstream services.
- [x] Dynamic legacy handler rejects WhatsApp; static route dispatch is proven.

## MCG3: Add atomic canonical persistence

### Purpose

Create the canonical table/repository and prove insert-or-deduplicate behavior,
retention expiry and non-skippable PostgreSQL tests.

### Depends On

MCG1

### Parallelizable

yes, coordinated with MCG2 only through the contract

### Files / Areas Likely Touched

- `rust_control_plane/migrations/messaging/001_add_canonical_inbound_events.sql`
- `rust_control_plane/src/messaging/inbound_repository.rs`
- `rust_control_plane/src/messaging/mod.rs`
- `rust_control_plane/tests/inbound_repository_test.rs`

### Validation Commands

- `cd rust_control_plane && cargo test --test inbound_repository_test -- --test-threads=1`

### Acceptance Criteria

- [x] Unique identity includes channel, account and external message ID.
- [x] Atomic conflict handling returns inserted/duplicate without unique-violation 500s.
- [x] Repository uses the canonical CTE statement and normalized error enum.
- [x] Stored rows exclude raw payload and require retention expiry.
- [x] Test setup fails loudly when PostgreSQL/migrations are unavailable.

## Checkpoint A: Secure contract and storage

- [x] MCG1-MCG3 tests pass.
- [x] Human/security review confirms signature, schema and data-minimization boundaries.
- [x] Feature remains disabled.

## MCG4: Integrate durable WhatsApp canonical ingest

### Purpose

Connect authenticated text normalization to atomic persistence and ACK after
commit while proving all forbidden downstream paths remain untouched.

### Depends On

MCG2, MCG3

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/src/handlers/whatsapp_webhook.rs`
- `rust_control_plane/src/state.rs`
- `rust_control_plane/src/main.rs`
- `rust_control_plane/src/health/ready.rs`
- `rust_control_plane/tests/whatsapp_canonical_ingest_test.rs`

### Validation Commands

- `cd rust_control_plane && cargo test --test whatsapp_canonical_ingest_test -- --test-threads=1`

### Acceptance Criteria

- [x] Valid configured-account text persists before 200 ACK.
- [x] Duplicate returns the same 200 and one durable row.
- [x] Unsupported authenticated events ACK without persistence.
- [x] Missing account metadata returns 400; account mismatch returns 403.
- [x] Handler state has no queue/gRPC/AI/outbound capability and queue count remains unchanged.

## MCG5: Prove concurrency, failure and data-safety behavior

### Purpose

Exercise concurrent duplicates, restart durability, persistence failure,
readiness, metrics and PII-safe observability.

### Depends On

MCG4

### Parallelizable

no

### Files / Areas Likely Touched

- `rust_control_plane/src/metrics/prometheus.rs`
- `rust_control_plane/tests/whatsapp_ingest_concurrency_test.rs`
- `rust_control_plane/tests/whatsapp_ingest_failure_test.rs`
- `rust_control_plane/tests/whatsapp_ingest_observability_test.rs`

### Validation Commands

- `cd rust_control_plane && cargo test --test whatsapp_ingest_concurrency_test --test whatsapp_ingest_failure_test --test whatsapp_ingest_observability_test -- --test-threads=1`

### Acceptance Criteria

- [x] Ten concurrent duplicates produce one row, ten 200s and no 500s.
- [x] Database/schema failure returns 503 and no accepted partial row.
- [x] Restart preserves ACKed records.
- [x] Logs/metrics follow the exact canonical allowlist and fixed label enums.

## Checkpoint B: Vertical slice evidence

- [x] Signed request -> canonical durable record -> ACK passes end-to-end.
- [x] Negative security, failure and concurrency paths pass.
- [x] Feature enablement prerequisites are documented and fail closed.

## MCG6: Reconcile status, handoff and deferred roadmap

### Purpose

Close only the canonical-ingest slice with evidence and preserve explicit next
work without reviving stale Phase 18 completion claims.

### Depends On

MCG5

### Parallelizable

no

### Files / Areas Likely Touched

- `docs/canonical/116-MULTI-CHANNEL-GATEWAY-CANONICAL-INGEST-SLICE.md`
- `.planning/changes/multi-channel-gateway/HANDOFF-CURRENT.md`
- `.planning/changes/multi-channel-gateway/execution-state.json`
- `.planning/changes/multi-channel-gateway/todo.md`
- `.planning/roadmap/objectives.json`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective multi-channel-gateway`
- Review canonical implementation status against linked test evidence.

### Acceptance Criteria

- [x] Only proven canonical ingest behavior is marked complete.
- [x] Deferred dispatcher, channels, inbox and data-lifecycle work remain explicit.
- [x] Planning state and handoff identify archive, then dedicated activation, as the exact next actions.
