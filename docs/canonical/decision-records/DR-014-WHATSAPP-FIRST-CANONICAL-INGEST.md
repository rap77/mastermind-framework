# DR-014 — WhatsApp-First Canonical Ingest

## 1. Decision Metadata

- **Decision ID:** DR-014
- **Date:** 2026-07-14
- **Status:** Approved
- **Related project:** MasterMind
- **Related capability:** Multi-Channel Gateway
- **Related objective:** `multi-channel-gateway`

## 2. Problem Statement

Phase 18 artifacts claim completion, but current runtime evidence shows isolated
parsers/senders, insecure webhook verification, racy deduplication, non-durable
queueing and mock inbox behavior. Expanding three channels simultaneously would
compound unknowns before one trustworthy ingress path exists.

## 3. Options Considered

### Option A — Complete all three channels and inbox together

- **Benefits:** broad visible feature
- **Risks:** mixes provider auth, identity, conversations, realtime, outbound and UI
- **Rejected:** too many unproven boundaries in one slice

### Option B — Build durable queue/DLQ infrastructure first

- **Benefits:** strong asynchronous foundation
- **Risks:** still consumes unauthenticated/non-canonical events and delays proof
- **Rejected:** reliability after an unsafe boundary is the wrong order

### Option C — WhatsApp text canonical ingest first

- **Benefits:** strongest existing evidence, bounded provider contract, proves auth,
  normalization, atomic dedup and durable ACK
- **Risks:** no user-facing inbox or outbound behavior yet
- **Selected:** closes the highest-risk boundary with the smallest vertical slice

## 4. Final Decision

Implement WhatsApp inbound text as the first canonical ingest adapter. Rust owns
raw-byte signature verification, canonical normalization and PostgreSQL
insert-or-deduplicate. ACK occurs after durable commit. Queue, gRPC, AI, outbound,
other channels and message-read APIs remain outside the slice.

Use one configured WhatsApp account and a feature flag until security,
PostgreSQL and retention preconditions pass.

Use `rust_control_plane/migrations/messaging` as the SQLx-managed lineage for
this domain. Do not replay the legacy parent directory, which was designed for
manual `psql`, contains duplicate versions and includes obsolete seed data.

## 5. Consequences

- existing generic ingress remains legacy for deferred channels
- Python canonical models become conformance consumers, not runtime authority
- raw payloads are not persisted by the new path
- a future durable dispatcher consumes accepted records
- inbox and outbound cannot claim completion from this slice
- Instagram and Email must satisfy the same adapter contract later
- messaging tests and rollout operations share one clean migration lineage

## 6. Reversal Conditions

Review if:

- Meta changes subscription/signature contracts materially
- one-account scope cannot represent the intended deployment
- legal/security policy requires raw payload retention or application encryption
- Rust is removed as the operational ingress boundary

## 7. Links / Artifacts

- `docs/canonical/116-MULTI-CHANNEL-GATEWAY-CANONICAL-INGEST-SLICE.md`
- `.planning/changes/multi-channel-gateway/`
- `rust_control_plane/src/handlers/webhook.rs`
- `apps/api/routers/canonical_events.py`

## Key Learnings:

1. Secure one provider boundary before generalizing adapters.
2. Durable ACK must not depend on an in-memory queue.
3. Historical completion claims require current executable evidence.
