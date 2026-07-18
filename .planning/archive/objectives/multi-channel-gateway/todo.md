# Todo — multi-channel-gateway

## Execution Checklist

- [x] MCG0: Freeze runtime seams and test infrastructure
  - [x] MCG0.1: Add messaging module and validated config owner
  - [x] MCG0.2: Add dedicated non-skipping PostgreSQL test helper
  - [x] MCG0.3: Validate disabled/enabled/failing config cases
  - depends_on: None
  - validation: `cd rust_control_plane && cargo test whatsapp_ingress_config`

- [x] MCG1: Define the shared canonical inbound contract
  - [x] MCG1.1: Write shared valid/invalid WhatsApp text fixtures
  - [x] MCG1.2: Add schema v1 and align Python/Rust models
  - [x] MCG1.3: Run cross-language contract validation
  - depends_on: MCG0
  - validation: `cd apps/api && uv run pytest -q tests/test_canonical_events.py` | `cd rust_control_plane && cargo test canonical_event_contract`

- [x] MCG2: Implement the secure WhatsApp webhook boundary
  - [x] MCG2.1: Write GET challenge and raw-byte signature tests
  - [x] MCG2.2: Add exact feature-gated GET/POST handlers
  - [x] MCG2.3: Validate invalid requests cannot cross the boundary
  - depends_on: MCG1
  - validation: `cd rust_control_plane && cargo test --test whatsapp_webhook_security_test`

- [x] MCG3: Add atomic canonical persistence
  - [x] MCG3.1: Write schema, concurrency and missing-database tests
  - [x] MCG3.2: Add messaging migration 001 and insert-or-get repository
  - [x] MCG3.3: Validate data minimization and retention expiry
  - depends_on: MCG1
  - validation: `cd rust_control_plane && cargo test --test inbound_repository_test -- --test-threads=1`

- [x] MCG4: Integrate durable WhatsApp canonical ingest
  - [x] MCG4.1: Write endpoint happy/duplicate/unsupported tests
  - [x] MCG4.2: Connect verification, adapter and repository
  - [x] MCG4.3: Assert queue/gRPC/AI/outbound remain untouched
  - depends_on: MCG2, MCG3
  - validation: `cd rust_control_plane && cargo test --test whatsapp_canonical_ingest_test -- --test-threads=1`

- [x] MCG5: Prove concurrency, failure and data-safety behavior
  - [x] MCG5.1: Add ten-request concurrency and restart tests
  - [x] MCG5.2: Add persistence/readiness failure tests
  - [x] MCG5.3: Validate safe metrics and PII-free logs
  - depends_on: MCG4
  - validation: `cd rust_control_plane && cargo test --test whatsapp_ingest_concurrency_test --test whatsapp_ingest_failure_test --test whatsapp_ingest_observability_test -- --test-threads=1`

- [x] MCG6: Reconcile status, handoff and deferred roadmap
  - [x] MCG6.1: Link implementation evidence and update canonical status
  - [x] MCG6.2: Preserve deferred work and next slice
  - [x] MCG6.3: Run discovery contract check
  - depends_on: MCG5
  - validation: `python3 .mm-flow/commands/mm/discover-contract-check.py --objective multi-channel-gateway` | Review canonical implementation status against linked test evidence.
