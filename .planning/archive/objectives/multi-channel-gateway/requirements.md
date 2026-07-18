# Requirements — multi-channel-gateway

## Problem / Purpose

MasterMind tiene parsers, senders, ingress Rust, PostgreSQL, una queue in-memory,
worker/DLQ scaffolding y un inbox visual, pero no un gateway multi-channel
productivo demostrado end-to-end.

El primer slice debe establecer una frontera confiable para WhatsApp inbound
text: verificar autenticidad sobre bytes originales, normalizar a un contrato
canónico, deduplicar atómicamente, persistir durablemente y recién entonces ACK.

## Stakeholders / Users

- operadores que conectan la cuenta WhatsApp de MasterMind
- maintainers de Rust ingress, Python contracts y PostgreSQL
- security/reliability reviewers
- futuros adapters de Instagram y Email
- futuros inbox/dispatcher consumers del canonical event

## Scope

- GET WhatsApp subscription challenge
- POST `X-Hub-Signature-256` validation sobre raw bytes
- single configured WhatsApp account validation
- text-message-only canonical normalization
- shared `messaging.inbound.v1` JSON schema
- atomic insert-or-deduplicate en PostgreSQL
- durable `accepted` state antes del ACK
- retention expiry y PII-safe logging/metrics
- feature-gated rollout y readiness preconditions
- unit, contract, PostgreSQL concurrency y endpoint integration tests
- explicit reconciliation of stale Phase 18 completion claims

## Out of Scope

- AI response, automatic reply u operator approval flows
- outbound WhatsApp sending
- media/attachments y delivery/read/status events
- Instagram y Email ingress
- inbox, threads, identity merge y realtime events
- queue/worker/retry/DLQ redesign
- channel routing intelligence
- multi-account o tenant support
- message-read API
- application-level encryption, deletion worker and subject-access implementation
- unrelated Phase 18 cleanup

## Non-negotiables

- Rust is the ingress/runtime authority for this slice.
- Signature verification uses exact request bytes and constant-time MAC verification.
- Verify token and app secret are distinct configuration values.
- JSON parsing and persistence happen only after signature verification.
- ACK happens only after durable commit.
- Deduplication uses `INSERT ... ON CONFLICT`, never check-then-insert.
- Raw webhook body, tokens, signatures and arbitrary metadata are not persisted.
- Sender, recipient and content never appear in logs or metric labels.
- Queue, gRPC, AI and outbound calls are forbidden in the canonical ingest path.
- PostgreSQL integration tests fail when the test database is unavailable; no skip.
- Existing generic routes remain legacy/deferred and cannot satisfy acceptance.
- No build command is required by the planning objective.

## Functional Requirements

- [x] Validate GET `hub.mode`, `hub.verify_token` and `hub.challenge`.
- [x] Validate POST `X-Hub-Signature-256` with `WHATSAPP_APP_SECRET`.
- [x] Parse only authenticated WhatsApp Business Account payloads.
- [x] Accept only text messages for the configured `phone_number_id`.
- [x] Produce a schema-valid `CanonicalInboundEventV1`.
- [x] Persist canonical fields, digest, status and retention expiry without raw body.
- [x] Return indistinguishable 200 responses for inserted and duplicate records.
- [x] Return retryable 503 when durable persistence cannot complete.
- [x] Record safe low-cardinality metrics for outcomes and latency.
- [x] Keep legacy queue/gRPC/outbound call counts at zero for this path.

## Security and Data Requirements

- [x] Feature defaults disabled.
- [x] Enabled feature requires verify token, app secret, account ID and retention days.
- [x] Account ID mismatch returns 403 without persistence.
- [x] Missing/invalid signatures return 401 without parsing/persistence.
- [x] `retention_expires_at` is always present.
- [ ] Production activation records approved retention and at-rest protection.
- [x] No endpoint exposes persisted message content in this slice.

## Objective-level Acceptance Criteria

- [x] Valid signed WhatsApp text creates one durable canonical record.
- [x] Invalid signature creates no record.
- [x] Ten concurrent duplicates create one row and no 500 responses.
- [x] Restart after ACK preserves the accepted record.
- [x] Queue saturation cannot suppress provider retry because the path does not enqueue.
- [x] Unsupported authenticated events ACK safely without claiming ingestion.
- [x] Contract fixtures pass in Rust and Python.
- [x] PostgreSQL tests are non-skippable and prove transaction semantics.
- [x] PII/logging/retention checks pass.
- [x] Package, execution-state, handoff, roadmap and canonical docs agree.
