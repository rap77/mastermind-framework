# Design — multi-channel-gateway

## Architecture / Boundaries

```text
GET /webhooks/whatsapp
  -> SubscriptionVerifier
  -> challenge response

POST /webhooks/whatsapp
  -> raw bytes
  -> SignatureVerifier
  -> WhatsAppTextAdapter
  -> CanonicalInboundEventV1
  -> InboundEventRepository.insert_or_get
  -> durable commit
  -> 200 ACK
```

- Rust owns ingress, signature verification, normalization and persistence.
- PostgreSQL owns canonical accepted state and idempotency.
- Shared JSON schema owns cross-language contract shape.
- Python is a contract-conformance consumer, not runtime ingress authority.
- Existing queue/gRPC/AI/outbound path is outside this slice.
- Existing UI has no role in acceptance.

## Technical Approach

### Shared contract

Create `docs/contracts/messaging/canonical-inbound-event-v1.schema.json`. Align
new Python/Rust v1 models against shared WhatsApp fixtures while retaining the
legacy Python model for other channels. The schema file is authoritative, uses
JSON Schema 2020-12, requires every canonical field, sets
`additionalProperties: false`, and fixes channel=`whatsapp`,
direction=`inbound`, type=`text`.

Runtime module layout:

```text
rust_control_plane/src/messaging/config.rs
rust_control_plane/src/messaging/canonical_event.rs
rust_control_plane/src/messaging/inbound_repository.rs
rust_control_plane/src/messaging/mod.rs
rust_control_plane/src/handlers/whatsapp_webhook.rs
```

`src/lib.rs` exports `messaging`. `CanonicalInboundEventV1` owns schema fields;
the existing channel `MessagePayload` is only provider-parser input.

### Preflight configuration and test harness

`WhatsAppIngressConfig::from_env() -> Result<Option<Self>>` owns feature/config
validation. `None` means disabled. Enabled configuration requires all four
values, retention > 0 and distinct verify/app secrets.

`WhatsAppIngressState` contains only config, repository and metrics, and is
derived from `AppState` using `FromRef`. Its type cannot access queue, gRPC, AI
or outbound senders.

Cargo adds `subtle` for token comparison and enables SQLx `macros`/`migrate` for
the integration-test migration harness.

The harness uses `migrations/messaging` as a dedicated SQLx lineage. The parent
legacy directory was historically run with manual `psql`, contains duplicate
version `003`, and includes seed data that this slice must not replay. Messaging
migrations start at `001` and are shared by tests and rollout operations.

### Secure boundary

Always register exact GET/POST WhatsApp routes before the dynamic route. GET
uses `Query<MetaVerifyQuery>` and constant-time token comparison. POST accepts
`HeaderMap` plus `axum::body::Bytes`, requires exact `sha256=<64 hex>` and calls
`Hmac::<Sha256>::verify_slice` before JSON parsing.

Disabled exact handlers return 503. The generic `/:channel` handler remains for
Instagram/Email and explicitly rejects WhatsApp. A routing test proves the
static path never falls through to legacy behavior.

MCG2 does not ACK authenticated POSTs: after successful raw-byte verification it
returns retryable 503 without parsing. MCG4 replaces that temporary response only
after normalization and durable insert-or-deduplicate are connected.

### Account scope

This slice supports one configured `WHATSAPP_PHONE_NUMBER_ID`. The payload
`metadata.phone_number_id` must match. Multi-account and tenant routing are
deferred instead of pretending generic JWT auth solves channel ownership.

Missing metadata/account ID is malformed (400); a present non-matching ID is
forbidden (403). Signature verification and JSON parsing happen before account
classification; persistence happens afterward.

The matched phone-number ID becomes both `account_external_id` and the canonical
recipient handle. Sender and external message ID come from the first text
message. Empty text or invalid provider timestamp is malformed. Handler creates
UUID v4 event ID, UTC receive time, lowercase raw-body SHA-256 and retention
expiry.

### Persistence

Add `migrations/messaging/001_add_canonical_inbound_events.sql`. Do not edit the
legacy parent migrations or any applied messaging migration.

Store only canonical fields, `payload_sha256`, `processing_status=accepted` and
`retention_expires_at`. Do not persist raw body or arbitrary provider metadata.

Unique key:

```text
(channel, account_external_id, external_message_id)
```

`InboundEventRepository` owns a cloned `PgPool`. It uses dynamic
`sqlx::query_as` and one CTE statement combining `INSERT ... ON CONFLICT DO
NOTHING RETURNING` with selection of the existing row. It returns:

```rust
InsertOutcome::Inserted { event_id }
InsertOutcome::Duplicate { event_id }
```

Repository errors normalize to `Unavailable`, `SchemaMissing` or `Database`,
all mapped to HTTP 503 at the boundary.

The new table is `canonical_inbound_events`. All timestamps are `TIMESTAMPTZ`.
Handler sets received time and retention expiry from validated config.

### ACK boundary

ACK 200 only after commit. Duplicate also returns 200. Persistence/schema
failure returns 503. Known authenticated out-of-scope events return 200 with a
safe metric so Meta does not retry forever.

Known out-of-scope: `statuses` and message types other than `text`. Missing
messages/statuses or required text fields is malformed (400). New and duplicate
responses are empty 200 responses.

No queue event is emitted. `accepted` records are the durable boundary for a
future dispatcher/outbox objective.

### Data handling

Required configuration when enabled:

- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_APP_SECRET`
- `WHATSAPP_PHONE_NUMBER_ID`
- `MESSAGING_RETENTION_DAYS` greater than zero

Logs allow internal event ID, channel, outcome enum, safe reason and latency.
Provider IDs, digest, phone numbers, content, raw bytes, signature and secrets
are forbidden. Production enablement requires an approved retention value and
verified database at-rest protection.

### Migration/readiness

Runtime does not auto-apply migrations. When the feature is enabled, readiness
checks required schema/configuration and fails closed if missing.
`health::ready::readiness_check` owns this predicate.

## Dependencies

- existing Axum router/AppState and PostgreSQL pool
- existing WhatsApp parser knowledge
- existing Python canonical event fixtures
- HMAC/SHA-256 dependencies already present in Rust
- new `subtle` dependency and SQLx `macros`/`migrate` test features
- `docs/canonical/116-MULTI-CHANNEL-GATEWAY-CANONICAL-INGEST-SLICE.md`
- `docs/canonical/decision-records/DR-014-WHATSAPP-FIRST-CANONICAL-INGEST.md`

No roadmap objective dependency is required. Security constraints are embedded
in this slice while the broader assurance plane remains future work.

## Validation Strategy

### Contract

- Python and Rust validate the same valid/invalid fixtures against schema v1.
- Schema changes require version change or backward-compatible addition.

### Unit

- GET challenge/token decisions
- raw-byte HMAC valid/invalid/malformed cases
- payload/account/text normalization
- unsupported event classification

### PostgreSQL

- migration/schema test
- insert/duplicate/concurrent duplicate tests
- transaction failure and persistence-unavailable behavior
- missing test database is a failure, not a skipped pass

Tests require a dedicated `TEST_DATABASE_URL`, reject a missing value or one
equal to `DATABASE_URL`, apply checked-in migrations with `sqlx::migrate!`, run
serialized and truncate only the canonical table.

### Endpoint

- signed text persists then ACKs
- invalid signature never parses/persists
- duplicate returns the same 200 response
- restart reconstructs state/repository against the same DB and reads the ACKed row
- compile-time ingress state excludes queue/gRPC/AI/outbound references
- legacy queue pending count remains unchanged

### Commands

- `cd apps/api && uv run pytest -q tests/test_canonical_events.py`
- `cd rust_control_plane && cargo test canonical_event_contract`
- `cd rust_control_plane && cargo test --test whatsapp_webhook_security_test`
- `cd rust_control_plane && cargo test --test whatsapp_canonical_ingest_test -- --test-threads=1`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective multi-channel-gateway`

## Important Tradeoffs

- WhatsApp-first delays breadth but proves one secure adapter contract.
- No queue means no asynchronous processing yet, but accepted events cannot be stranded by queue saturation.
- No raw payload limits forensic replay but materially reduces PII exposure.
- Single-account scope is honest and safe; fake multi-tenancy would be worse.
- Feature-gated rollout preserves current routes while the new path is verified.

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Meta contract drift | high | versioned fixtures and source review at activation |
| signature bypass | critical | raw bytes, strict header/parser and constant-time MAC |
| duplicate race | high | database conflict handling in one statement |
| ACK before durability | critical | commit-before-response integration test |
| PII leakage | critical | no raw storage, safe logs, retention expiry |
| migration absent | high | feature readiness fails closed |
| legacy route mistaken as complete | high | exact route and explicit deferred status |

## Context Notes

- Historical Phase 18 completion artifacts are stale and cannot close this objective.
- `multi-channel-gateway` remains the sole active/recommended objective.
- Current package replaces generic T1-T3 scaffolding with implementation tasks.
- Instagram, Email, inbox, realtime and outbound remain explicitly deferred.
