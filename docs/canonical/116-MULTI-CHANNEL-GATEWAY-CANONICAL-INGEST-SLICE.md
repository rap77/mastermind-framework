# Multi-Channel Gateway Canonical Ingest Slice

## Índice

1. Estado canónico
2. Propósito
3. Evidencia de partida
4. Decisión central
5. Alcance y no-objetivos
6. Arquitectura del slice
7. Webhook subscription y autenticidad
8. CanonicalInboundEvent v1
9. Persistencia e idempotencia
10. ACK y failure semantics
11. Data handling y seguridad
12. Configuración y rollout
13. Observabilidad
14. Testing contract
15. Integración con superficies existentes
16. Criterios de aceptación
17. Trabajo diferido
18. Estado de implementación
19. Referencias

## 1. Estado canónico

- **Estado de la decisión:** aprobado
- **Estado del diseño:** canonizado
- **Estado de planificación:** MCG0-MCG6 completos; objective activo pendiente de archivo
- **Estado de implementación:** slice canónico implementado y validado; rollout deshabilitado
- **Estado de producción:** no habilitado; retención y protección at-rest siguen bloqueando rollout
- **Objective slug:** `multi-channel-gateway`
- **Primer slice:** `whatsapp-inbound-text-canonical-ingest`

## 2. Propósito

Implementar el primer boundary confiable del Multi-Channel Gateway:

```text
WhatsApp text webhook
  -> subscription/signature verification
  -> canonical normalization
  -> atomic deduplication
  -> durable PostgreSQL persistence
  -> provider ACK
```

El slice demuestra ingest autenticado y durable. No afirma que exista todavía
un inbox, conversación, AI response o outbound delivery end-to-end.

## 3. Evidencia de partida

El repositorio ya contiene:

- `POST /webhooks/:channel` en Rust
- WhatsApp/Instagram/Email parsers
- Python `CanonicalInboundEvent`
- tabla `messages` con unique constraint
- bounded in-memory queue y worker gRPC
- senders outbound por canal
- DLQ/retry scaffolding
- UI shell de unified inbox

Sin embargo, la evidencia actual muestra:

- signature result ignorado y verificación sobre JSON reserializado
- ausencia del GET subscription challenge de Meta
- check-then-insert race en deduplication
- persist-before-enqueue que puede dejar mensajes stranded
- normalizador canónico Python desconectado del ingress Rust
- queue no durable y retry/DLQ parcialmente stubbed
- inbox, WebSocket messaging y composer basados en mocks
- ausencia de tenancy/channel-account authorization y PII lifecycle

Documentos históricos que declaran Phase 18 completa no son evidencia runtime.
El package `.planning/changes/multi-channel-gateway/` es la superficie activa.

## 4. Decisión central

> El primer vertical slice será WhatsApp inbound text solamente. Rust será la
> autoridad de ingress, autenticidad, normalización y persistencia durable. El
> ACK no dependerá de la queue in-memory, gRPC, AI ni outbound send.

La decisión reduce riesgo antes de expandir canales. Instagram y Email deberán
implementar el mismo contract mediante adapters posteriores.

## 5. Alcance y no-objetivos

### Incluye

- GET Meta subscription verification para WhatsApp
- POST signature verification sobre raw request bytes
- payload parsing después de verificar autenticidad
- text-message normalization a schema versionado
- single configured WhatsApp account validation
- atomic insert-or-deduplicate
- durable accepted state en PostgreSQL
- safe metrics/logging y integration tests no-skippable
- feature-gated rollout

### No incluye

- AI-generated responses o automatic replies
- outbound WhatsApp calls
- media/attachments, delivery/read receipts o status events
- Instagram o Email ingress
- unified inbox, threads, identity merge o realtime events
- queue, worker, retry o DLQ redesign
- channel routing intelligence
- multi-account/tenant support
- public/diagnostic message-read API

## 6. Arquitectura del slice

```text
Meta
  -> GET /webhooks/whatsapp
       -> verify mode + verify token
       -> return challenge

Meta
  -> POST /webhooks/whatsapp
       -> RawBodyExtractor
       -> WhatsAppSignatureVerifier
       -> JSON boundary validation
       -> WhatsAppTextAdapter
       -> CanonicalInboundEventV1
       -> InboundEventRepository.insert_or_get()
       -> 200 OK
```

Transitional routing:

- exact GET/POST `/webhooks/whatsapp` routes are always registered before the
  dynamic route and dispatch to `whatsapp_webhook.rs`
- when the feature is disabled, the exact route returns 503 and never falls back
- legacy `POST /webhooks/:channel` remains for Instagram/Email only and must
  reject `channel == whatsapp`
- an integration test proves the exact static route wins over the dynamic route
- canonical WhatsApp path never invokes the current in-memory queue/gRPC worker
- later delivery processing will consume durable accepted records through a
  separately designed dispatcher/outbox

Runtime modules and state:

```text
src/messaging/config.rs
src/messaging/canonical_event.rs
src/messaging/inbound_repository.rs
src/messaging/mod.rs
src/handlers/whatsapp_webhook.rs
```

`WhatsAppIngressState` contains only config, repository and ingest metrics. It
is derived from `AppState` through `FromRef`; it contains no queue, gRPC, AI or
outbound sender reference.

## 7. Webhook subscription y autenticidad

### GET subscription verification

Input query parameters:

- `hub.mode`
- `hub.verify_token`
- `hub.challenge`

Rules:

- require `hub.mode == subscribe`
- compare verify token with `subtle::ConstantTimeEq`
- return `hub.challenge` with 200 only on match
- return 403 on mismatch
- never log tokens or challenge values

Handler contract:

```rust
verify_whatsapp_subscription(
    State<WhatsAppIngressState>,
    Query<MetaVerifyQuery>,
) -> Response
```

### POST payload verification

- extract `axum::body::Bytes`; do not use `Json<Value>` at the boundary
- require `X-Hub-Signature-256` with `sha256=<hex>`
- reject other algorithms, missing prefix, non-hex or decoded length != 32
- compute HMAC-SHA256 over exact bytes using `WHATSAPP_APP_SECRET`
- use `Hmac::<Sha256>::verify_slice` for constant-time MAC verification
- reject missing, malformed or invalid signatures before parsing/persistence
- `WHATSAPP_VERIFY_TOKEN` and `WHATSAPP_APP_SECRET` are distinct secrets
- during boundary-only MCG2, a valid signature returns retryable 503 without
  parsing; only MCG4 may replace it with 200 after durable commit

Handler contract:

```rust
receive_whatsapp_webhook(
    State<WhatsAppIngressState>,
    HeaderMap,
    Bytes,
) -> StatusCode
```

## 8. CanonicalInboundEvent v1

Canonical JSON schema previsto:

```yaml
schema_version: messaging.inbound.v1
event_id: uuid
channel: whatsapp
account_external_id: string
external_message_id: string
direction: inbound
sender_external_id: string
recipient_external_id: string
message_type: text
content_text: string
occurred_at: timestamp
received_at: timestamp
payload_sha256: string
processing_status: accepted
retention_expires_at: timestamp
```

Schema rules:

- JSON Schema draft 2020-12
- all fields above are required
- `additionalProperties: false`
- `schema_version`, `channel`, `direction`, `message_type` and
  `processing_status` use `const`
- IDs are non-empty strings; `event_id` uses `format: uuid`
- timestamps use `format: date-time`
- `content_text` has `minLength: 1`, `maxLength: 4096`
- `payload_sha256` uses `pattern: ^[0-9a-f]{64}$`

Rules:

- `account_external_id` proviene de `metadata.phone_number_id`
- account ID debe coincidir con la cuenta configurada
- `external_message_id` proviene de `messages[0].id`
- `event_id` es UUID v4 interno generado después de autenticidad/clasificación
- `recipient_external_id` usa el configured/matched `phone_number_id`
- `sender_external_id` proviene de `messages[0].from`
- sólo `messages[0].type == text` entra en el slice
- `content_text` vacío o timestamp inválido es malformed (400)
- timestamp Unix de proveedor se normaliza a UTC/RFC 3339
- digest es SHA-256 lowercase de raw bytes y no sustituye signature verification
- no se persiste `metadata` arbitraria ni raw body

El schema compartido vive en:

```text
docs/contracts/messaging/canonical-inbound-event-v1.schema.json
```

Rust es owner runtime. Python conserva conformance mediante shared fixtures; no
existe un segundo contrato canónico.

The schema file is the contract authority. MCG1 introduces a new Python
`CanonicalInboundEventV1` beside the legacy multi-channel model; it does not
silently rename legacy fields. Its idempotency key includes channel, account and
external message ID. Rust introduces a separate v1 struct and adapter.

## 9. Persistencia e idempotencia

Crear `migrations/messaging/001_add_canonical_inbound_events.sql` dentro de un
lineage SQLx dedicado, sin editar migrations históricas aplicadas. El directorio
legacy padre fue ejecutado manualmente, contiene versiones duplicadas y no se
debe reproducir desde el harness de este slice.

Unique identity:

```text
(channel, account_external_id, external_message_id)
```

Repository contract:

```rust
enum InsertOutcome {
    Inserted { event_id: Uuid },
    Duplicate { event_id: Uuid },
}

enum InboundRepositoryError {
    Unavailable,
    SchemaMissing,
    Database,
}

async fn insert_or_get(
    &self,
    event: &CanonicalInboundEventV1,
) -> Result<InsertOutcome, InboundRepositoryError>
```

`InboundEventRepository` owns a cloned `PgPool` and uses dynamic
`sqlx::query_as`, avoiding compile-time database access. The statement uses a
CTE with `INSERT ... ON CONFLICT DO NOTHING RETURNING`, followed by a select of
the existing row in the same SQL statement. No check-then-insert is permitted.

Table `canonical_inbound_events` contains:

- UUID primary key and schema version
- channel/account/external ID unique key
- sender/recipient external IDs
- direction, message type and content text
- occurred/received timestamps
- payload digest, processing status and retention expiry
- created timestamp

All timestamps are `TIMESTAMPTZ`. Handler sets `received_at = Utc::now()` and
computes retention expiry from validated config. Diez requests concurrentes
idénticos producen un record, respuestas idempotentes y cero 500 por unique
violations.

El estado `accepted` es la durable processing boundary. En este slice no se crea
un in-memory queue event. Reiniciar Rust después del ACK no pierde el record.

La migration se aplica por el deployment mechanism existente. Readiness debe
fallar si el feature está enabled y el schema requerido no existe; el runtime no
ejecuta migrations silenciosamente.

## 10. ACK y failure semantics

| Caso | Resultado |
| --- | --- |
| GET token válido | 200 + challenge |
| GET token inválido | 403 |
| POST signature ausente/inválida | 401 |
| text message nuevo persistido | 200 |
| duplicate ya persistido | 200 |
| evento autenticado pero fuera del slice | 200 + safe metric, sin persistencia |
| JSON/envelope inválido | 400 |
| metadata/phone number ID ausente | 400 |
| account ID no permitido | 403 |
| PostgreSQL/schema unavailable | 503 |

No se devuelve 200 antes del commit durable. No se expone en la respuesta si el
evento era nuevo o duplicate; ambos devuelven un body vacío.

Out-of-scope autenticado incluye `statuses` y mensajes con type distinto de
`text`. Envelope sin `messages` ni un evento conocido es malformed (400).

## 11. Data handling y seguridad

Clasificación:

- sender/recipient identifiers: restricted PII
- content text: restricted user content
- app secret, verify token y signature: secret/auth material

Rules:

- no raw webhook body en PostgreSQL
- no sender, recipient, content, raw body, token o signature en logs
- logs permiten internal event ID, channel, outcome enum, latency y safe reason code
- logs prohíben provider external message ID y payload digest además de PII
- persisted content se limita a fields del schema
- `retention_expires_at` es obligatorio
- production enablement requiere `MESSAGING_RETENTION_DAYS` aprobado y mayor a cero
- deletion worker, subject access y application-level encryption quedan fuera
  del slice, pero production readiness debe documentar su owner/next objective
- existing database/infrastructure at-rest protection debe verificarse antes de rollout

## 12. Configuración y rollout

Feature flag:

```text
WHATSAPP_CANONICAL_INGEST_ENABLED=false
```

Cuando está enabled, startup/readiness requiere:

- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_APP_SECRET`
- `WHATSAPP_PHONE_NUMBER_ID`
- `MESSAGING_RETENTION_DAYS`
- required database schema

No existen valores production fallback. Tests usan secretos y account IDs
efímeros.

Configuration owner:

```rust
WhatsAppIngressConfig::from_env() -> Result<Option<Self>>
```

- missing/false flag returns `None`
- true requires all four values, retention > 0 and distinct secrets
- `AppState` stores `Option<WhatsAppIngressState>`
- exact handlers return 503 when state is absent
- `health::ready::readiness_check` verifies config and repository schema when enabled
- Cargo adds `subtle`; SQLx enables `macros` and `migrate` for test migrations

## 13. Observabilidad

Métricas mínimas:

- `whatsapp_ingest_requests_total{outcome}`
- `whatsapp_ingest_persistence_failures_total{reason}`
- `whatsapp_ingest_latency_seconds`

Allowed outcomes: `inserted`, `duplicate`, `unsupported`, `invalid_signature`,
`invalid_payload`, `account_mismatch`, `unavailable`. Allowed persistence reasons:
`pool`, `schema`, `database`. No other dynamic labels are permitted. External
IDs, phone numbers, content and digests are never labels.

## 14. Testing contract

### Unit

- challenge/token decisions
- valid, malformed and invalid signatures over raw bytes
- text payload normalization
- account mismatch and unsupported events
- schema fixture conformance Rust/Python

### PostgreSQL integration

- migration/schema presence
- insert and duplicate behavior
- ten concurrent identical requests produce one row
- transaction failure produces no partial accepted state
- tests fail if test PostgreSQL is unavailable; no silent skip

Test harness contract:

- require explicit dedicated `TEST_DATABASE_URL`
- fail immediately if missing or equal to `DATABASE_URL`
- apply checked-in `migrations/messaging` through `sqlx::migrate!`
- serialize database integration tests and truncate only the canonical table
- CI/local operator must provision a disposable test database

### Endpoint integration

- valid signed request persists then ACKs
- invalid signature never parses/persists
- duplicate returns indistinguishable 200
- database unavailable returns retryable 503
- restart is simulated by dropping state/repository, reconstructing it against
  the same test database and reading the previously ACKed row
- compile-time `WhatsAppIngressState` excludes queue/gRPC/AI/outbound references;
  endpoint tests assert the legacy queue pending count does not change

## 15. Integración con superficies existentes

### Reusar

- Axum/Rust public route and AppState
- HMAC/sha2 dependencies, replacing manual byte equality with MAC verification
- WhatsApp parser knowledge and canonical Python fixtures
- PostgreSQL/sqlx pool
- tracing/metrics infrastructure
- `src/lib.rs` exports the new `messaging` module

### Corregir o aislar

- existing generic handler remains legacy for deferred channels and explicitly
  rejects WhatsApp
- current `messages` table remains historical/legacy ingress storage
- Python `internal.py` raw-payload-to-outbound behavior is not used
- in-memory queue, worker, DLQ and UI shell are not acceptance evidence

## 16. Criterios de aceptación

- exact WhatsApp GET/POST routes implement the security contract
- signature verification uses original bytes and constant-time MAC verification
- only configured-account text events normalize to schema v1
- canonical event persists without raw payload
- concurrent duplicates produce one row and identical 200 responses
- provider ACK happens only after durable commit
- process restart cannot erase accepted records
- queue, gRPC, AI and outbound send are not invoked
- PII/logging/retention rules are tested
- PostgreSQL integration tests cannot silently skip
- active package, execution-state, handoff and canonical docs agree

## 17. Trabajo diferido

Separate follow-up objectives/slices:

- durable dispatcher/outbox and worker recovery
- media and attachment lifecycle
- delivery/read/status event ingestion
- authenticated account/tenant connection model
- conversation/thread aggregate and identity merge
- operator inbox and realtime events
- operator-approved or automatic response policy
- outbound channel authorization
- Instagram adapter
- selected inbound Email provider and verification protocol
- retention deletion and data-subject workflows
- public/diagnostic inbox and message-read APIs
- application-level encryption for restricted message content
- production retention approval and verified database at-rest protection

El cierre de este slice no completa el gateway amplio ni habilita producción.
`WHATSAPP_CANONICAL_INGEST_ENABLED=false` sigue siendo el default. El siguiente
paso operativo es archivar `multi-channel-gateway`; sólo después el comando
dedicado de activación debe seleccionar el siguiente objetivo del roadmap.

## 18. Estado de implementación

### Implementado y probado en el slice canónico

- MCG0: configuración fail-closed, módulo messaging y harness PostgreSQL dedicado.
- MCG1: schema compartido y modelos/fixtures conformes en Python y Rust.
- MCG2: GET/POST exactos, autenticidad sobre raw bytes y aislamiento del route legacy.
- MCG3: migration dedicada y repositorio atómico insert-or-deduplicate.
- MCG4: normalización, persistencia durable y ACK posterior al commit.
- MCG5: concurrencia, restart, fallas, readiness y observabilidad PII-safe.

### Evidencia verificable MCG0-MCG5

| Task | Implementación / test evidence | Resultado verificado |
| --- | --- | --- |
| MCG0 | `rust_control_plane/src/messaging/config.rs`; `rust_control_plane/tests/postgres_harness_test.rs`; `rust_control_plane/tests/support/postgres.rs` | 7/7 config tests passed; 1/1 PostgreSQL harness test passed |
| MCG1 | `docs/contracts/messaging/canonical-inbound-event-v1.schema.json`; `apps/api/tests/test_canonical_events.py`; `rust_control_plane/tests/canonical_event_contract_test.rs` | 20 Python tests + 2 Rust contract tests passed |
| MCG2 | `rust_control_plane/src/handlers/whatsapp_webhook.rs`; `rust_control_plane/tests/whatsapp_webhook_security_test.rs` | 7/7 boundary tests passed; 6/6 active legacy tests passed; 6 legacy tests ignored |
| MCG3 | `rust_control_plane/migrations/messaging/001_add_canonical_inbound_events.sql`; `rust_control_plane/src/messaging/inbound_repository.rs`; `rust_control_plane/tests/inbound_repository_test.rs` | 1/1 focused PostgreSQL repository contract test passed with no skips |
| MCG4 | `rust_control_plane/tests/whatsapp_canonical_ingest_test.rs`; `rust_control_plane/src/messaging/state.rs`; `rust_control_plane/src/health/ready.rs` | 1/1 focused endpoint ingest contract test passed |
| MCG5 | `rust_control_plane/tests/whatsapp_ingest_concurrency_test.rs`; `rust_control_plane/tests/whatsapp_ingest_failure_test.rs`; `rust_control_plane/tests/whatsapp_ingest_observability_test.rs` | 3/3 focused integration tests passed; MCG2-MCG4 regressions 9/9, config 14/14 and readiness 2/2 also passed in the MCG5 durable checkpoint |

Estos resultados prueban implementación y comportamiento del slice con una base
de test dedicada. No prueban production enablement. El flag permanece apagado y
producción requiere aprobación de `MESSAGING_RETENTION_DAYS` y verificación de
protección at-rest antes de cualquier rollout.

### Aún diferido o bloqueado

- Instagram, Email, media/statuses y expansión multi-account/tenant
- outbound, dispatcher/outbox, worker recovery y routing de respuestas
- inbox, conversaciones, realtime y APIs de lectura de mensajes
- deletion worker, subject access y application-level encryption
- aprobación de retención de producción y verificación at-rest

## 19. Referencias

- `https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started`
- `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/create-webhook-endpoint`
- `https://developers.facebook.com/docs/graph-api/webhooks/getting-started/#validating-payloads`
- `https://github.com/fbsamples/whatsapp-api-examples`
- `rust_control_plane/src/handlers/webhook.rs`
- `rust_control_plane/src/channels/whatsapp.rs`
- `rust_control_plane/migrations/003_add_messages_table.sql`
- `apps/api/routers/canonical_events.py`
- `.planning/changes/multi-channel-gateway/`
- `docs/canonical/decision-records/DR-014-WHATSAPP-FIRST-CANONICAL-INGEST.md`

## Key Learnings:

1. Parsers, queues y UI shells no prueban un gateway end-to-end.
2. ACK durable e idempotencia atómica deben preceder multi-channel expansion.
3. Un provider adapter seguro comienza con bytes autenticados, no JSON confiado.
