# Phase 18 — Domain Brain Outputs
> Generated: 2026-04-10T22:45:00Z
> Status: complete

## Brain #2 — UX Research

### Executive Summary

Comprehensive UX analysis for Phase 18's multi-channel unified inbox (WhatsApp + Instagram + Email). Grounded in Norman, Nielsen, and Hall's principles, with specific focus on **expert efficiency** and **cognitive load reduction**.

### 1. Five Core UX Principles

1. **Recognition Over Recall (Jakob's Law)**: Channel affordances must be instantly recognizable via color-coded signifiers (WhatsApp green, Instagram gradient, Email blue/gray) — visual recognition in <100ms.

2. **Chunking Over Filtering (Miller's Law)**: 7±2 threads visible per view to respect working memory limits. Group by "agent ownership" NOT just channel — this is an orchestration platform, not a community manager tool.

3. **Natural Mapping for Status (Norman)**: Webhook status colors are universal mappings (Red = DLQ/error, Yellow = retrying, Green = delivered). No legend needed — the affordance IS the mapping.

4. **Progressive Disclosure (Hick's Law)**: Show only relevant tools per channel in composition panel (WhatsApp Quick Replies vs Email Subject field). Irrelevant options increase decision time logarithmically.

5. **Error Recovery First-Class (Nielsen H3)**: DLQ items need "Retry" button inline — not hidden in separate error screen. Recovery in ≤2 actions: click thread → click retry.

### 2. Three-Pane Inbox Layout (APPROVED)

Aligned with Slack/Discord patterns per Jakob's Law:

```
┌─────────────────────────────────────────────────────────────┐
│ Channels (WA│IG│Email)  │  Thread List (7±2 visible)  │  Active Thread  │
│ [Unread: 12] [3] [5]   │  ◉ Customer A (WA)        │  [Message bubbles] │
│                        │  ○ Customer B (IG)        │  [Agent status]    │
│ [Filter: All]          │  ○ Support Ticket #123    │  [Compose box]     │
│ [Requires Manual: 3]   │  [DLQ: 2 errors]         │                    │
└─────────────────────────────────────────────────────────────┘
```

### 3. Keyboard-First Navigation (APPROVED)

- `J/K` to navigate threads (Vim/IDE pattern — Jakob's Law for expert users)
- `Enter` to focus thread detail
- `Esc` to return to thread list

### 4. Five Anti-Patterns to Avoid

1. **"Unified" Means "Identical"** — WRONG: Treat all channels the same. RIGHT: Respect channel constraints with progressive disclosure.
2. **Hidden Status Information** — WRONG: Status icons only on hover. RIGHT: Status column always visible.
3. **Filter-Only Navigation** — WRONG: 10+ filter options (Hick's Law violation). RIGHT: Smart chunks: "All", "Manual", "AI", "DLQ" (max 4 options).
4. **No Keyboard Navigation** — WRONG: Mouse-only thread navigation. RIGHT: `J/K/Enter/Esc` (Vim/IDE standard).
5. **Error Recovery Buried** — WRONG: DLQ items in separate screen. RIGHT: DLQ badge + inline "Retry" button.

### 5. Success Criteria (Measurable)

1. **Time-to-First-Response < 5s** (user lands → selects thread → starts composing)
2. **Error Recovery Time < 10s** (DLQ detected → retry initiated → resubmitted)
3. **Channel Recognition Accuracy > 95%** (identify source without reading text)
4. **Zero Mistake Errors** (system prevents invalid sends)
5. **Keyboard Navigation Usage > 50%** (expert users with >10 sessions)

### P0 Recommendations (Blocking for Phase 18):

1. **Create `UnifiedInbox` component** — 3-pane layout (Channel Rail → Thread List → Thread Detail)
2. **WebSocket `thread_updates` channel** — extend existing `wsStore.ts`
3. **`ComposePanel` with channel validation** — character limits, channel-specific tools
4. **DLQ retry inline** — NOT separate error screen

---

## Brain #4 — Frontend Architecture

### 1. Principles (React/Next.js Performance for Real-Time Messaging)

**RAF Batching > Direct Updates**
- Queue incoming WS messages, drain before paint (16ms budget)
- Extend existing brainStore pattern — NO separate RAF loop
- Target: 60fps sustained during 3-channel burst (50 msgs/sec)

**O(1) Selectors > O(n) Filters**
- `useMessage(id)` targeted selector — prevents cascade re-renders
- Map<messageId, MessageState> structure — O(1) lookup
- Filter in store selector, NOT component (inline filter = O(n) on every render)

**Viewport Rendering > Full Render**
- react-virtuoso for 1000+ messages (only render visible rows)
- Append-only updates (new messages prepend, Virtuoso handles scroll anchoring)
- Intersection Observer for infinite scroll (NOT onScroll listeners)

**Main Thread Free > Blocking Operations**
- Web Worker for Email HTML parsing (>16ms operations)
- useTransition for non-critical updates (typing indicators, read receipts)
- INP (Interaction to Next Paint) < 100ms target

### 2. Patterns

**Message List Virtualization**
- react-virtuoso (already verified in package.json v4.18.3)
- LiveLogPanel.tsx demonstrates Virtuoso + WS integration pattern
- Targeted selector: `useMessage(id)` for O(1) lookups

**Channel-Specific Message Components**
- Type-safe discriminated union for channel types
- Compound components pattern: MessageContainer wrapper + channel-specific body
- WhatsAppMessage, InstagramMessage, EmailMessage components

**WebSocket Message Handling**
- Web Worker for heavy processing (Email HTML > 16ms parse time)
- useTransition for non-critical updates (typing indicators, read receipts)
- Deduplication: Stability Keys via Map<messageId, MessageState>

### 3. Anti-Patterns

❌ Server State Duplication — Copy TanStack Query data to local useState
❌ Incorrect Animation Properties — Animate width/height/top (reflows)
❌ Uncleared WS Subscriptions — Memory leak after 30+ minutes
❌ Synchronous Heavy Processing — Parse 50MB Email HTML on main thread
❌ Multiple RAF Loops — Frame budget fragmentation
❌ Inline Message Filtering — O(n) on every render
❌ Full Message List Render — Main thread freeze

### 4. Success Criteria

| Metric | Target |
|--------|--------|
| Message list render time (1000 msgs) | < 100ms |
| Frame drops during scroll | 0 at 60fps |
| Main thread blocking (WS burst: 50 msgs/sec) | < 16ms per frame |
| Email composition preview | < 50ms |
| Draft persistence (keypress → localStorage) | < 16ms, non-blocking |
| XSS vulnerabilities | 0 (DOMPurify coverage) |

### 5. Recommendations

**messageStore Structure (Zustand + Immer + persist)**
```typescript
interface MessageState {
  id: string
  channel: 'whatsapp' | 'instagram' | 'email'
  content: string
  timestamp: number
  status: 'sending' | 'sent' | 'delivered' | 'read' | 'failed'
  senderId: string
  metadata: Record<string, unknown>
}

interface MessageStore {
  messages: Map<string, MessageState>
  drafts: Map<string, MessageDraft>
  addMessage: (message: MessageState) => void
  updateMessageStatus: (id: string, status: MessageState['status']) => void
  saveDraft: (channelId: string, draft: Omit<MessageDraft, 'updatedAt'>) => void
  clearDraft: (channelId: string) => void
}
```

**Component Hierarchy**
```
UnifiedInboxPage
├── ChannelTabs (whatsapp | instagram | email)
├── MessageList (Virtuoso virtualized)
│   ├── WhatsAppMessage
│   ├── InstagramMessage
│   └── EmailMessage
└── MessageComposer (per-channel UI)
```

### Implementation Gaps

🔴 **Missing for Phase 18:**
- Web Worker usage (Zero files use Worker pattern)
- Intersection Observer (Zero files use this API)
- MessageStore (No message-specific store exists)
- Channel-specific components (No WhatsApp/Instagram/Email components)

✅ **Already Available:**
- react-virtuoso v4.18.3 in package.json
- RAF batching pattern (brainStore.ts)
- DOMPurify (4 files use sanitization)
- useTransition (CostDashboard.tsx)
- Zustand + persist (layoutStore.ts)

---

## Brain #5 — Backend Architecture

### 1. Principles (Backend Architecture for Webhook Reliability)

**Design for Failure**
Assume external services (WhatsApp, Instagram) or internal processors (Python AI) will fail. Systems must incorporate **retries with exponential backoff** and **graceful fallbacks**.

**Stateless Gateway**
The Rust-based webhook receivers should remain **stateless**. By moving state to a shared store (PostgreSQL for MVP, Redis for scale), the system can scale horizontally.

**Separation of Concerns (Clean Architecture)**
External channel details (API formats, webhooks) must be separated from **high-level business logic** (AI processing) using the Dependency Rule.

**Fail Fast**
Webhook receivers should validate requests immediately and return a **200 OK** or a clear **4xx error** if the payload is malformed.

### 2. Patterns

**Anti-Corruption Layer (ACL)**
Implement an ACL in the Rust Control Plane to translate incoming payloads from WhatsApp or Instagram into a **unified internal event format** (Protobuf). Extend `mastermind.events.v1` for multi-channel events.

**Idempotency Keys**
Use the unique message IDs provided by WhatsApp/Instagram as **idempotency keys** in PostgreSQL (UNIQUE constraint) or Redis (SET with NX flag).

**Message Queue (Decoupling)**
Use a message queue to decouple the high-volume Rust receivers from the slower Python AI processing.
- **MVP:** In-memory `tokio::sync::mpsc` bounded channels (proven in Phase 16)
- **Scale:** Redis Streams for durability

**Dead Letter Queue (DLQ)**
Messages that fail after a maximum number of retries must be moved to a DLQ. This prevents a "poison pill" message from blocking the main queue.

**Circuit Breaker**
If the Python AI backend or an external channel API is down, a circuit breaker should "open" to prevent the system from wasting resources on doomed requests.

### 3. Anti-Patterns

❌ Blocking the Event Loop — Heavy AI processing in Rust receiver
❌ Tight Coupling with External APIs — Internal DB matches external schema
❌ Swallowing Errors — Silent data loss
❌ Lack of Idempotency — Duplicate responses
❌ Synchronous Inter-service Communication — Rust waits for gRPC response

### 4. Success Criteria

**Zero Message Loss**
100% of received webhooks are either successfully processed or safely stored in the **DLQ**.

**Low Receiver Latency**
Webhook ACKs (HTTP 200) should be returned in **<100ms P95**.

**Effective Traceability**
Successful **trace_id propagation** across the Rust receiver, queue, and Python processor.

**High Concurrency**
The Rust Control Plane handles up to **2,000 concurrent connections** without event loop degradation.

**Idempotency Success Rate**
0% duplicate entries in the database for the same external `message_id`.

### 5. Recommendations

**Rust as the High-Performance Gatekeeper**
Use Axum to handle the **WhatsApp/Instagram webhook verification** (HMAC signatures, Hub challenges). Validate the payload and immediately push it to a queue.

**Queue Architecture Decision**
- **MVP:** In-memory `tokio::sync::mpsc` bounded channels (proven in ws/hub.rs)
- **Scale:** Redis Streams for durability
- **Verdict:** Start simple, migrate when needed

**Idempotency Implementation**
- **MVP:** PostgreSQL UNIQUE index on `(external_message_id, channel)`
- **Scale:** Redis SET with NX flag
- **Pattern:** Check idempotency key BEFORE queuing

**Python AI Worker Pattern**
Implement the Python FastAPI backend as a **consumer of the queue** via gRPC. Reuse existing gRPC infrastructure from Phase 16.

**Webhook Verification (Security MUST)**
WhatsApp/Instagram webhooks require HMAC signature verification. Extract signature from headers, compute HMAC, compare using constant-time comparison.

### Critical Gaps

1. **No message queue infrastructure** — `tokio::sync::mpsc` exists but NO persistent queue
2. **No DLQ implementation** — failed webhooks will block or be lost
3. **No idempotency layer** — duplicate webhooks WILL cause duplicate processing
4. **No ACL implementation** — external API schemas will leak into domain
5. **No circuit breaker** — cascading failures when external APIs go down
6. **No webhook verification** — security vulnerability
7. **No rate limiting** — WhatsApp API has strict limits

---

## Brain #6 — QA/DevOps

### 1. Principles (QA Philosophy for Webhook Reliability)

**Jez Humble (Continuous Delivery):** The webhook gateway must be a first-class citizen of the deployment pipeline. Every change to routing logic or retry policy is automatically validated before deployment.

**Charity Majors (Observability-Driven Development):** Shift from "is it up?" to "what is it doing?" Webhook reliability depends on querying **high-cardinality data** (specific `trace_id`, `channel_id`, `provider_response_code`).

**Michael Feathers (Working Effectively with Legacy Code):** Even new gateway code gets the legacy system rigor. Use **seams** to isolate external provider dependencies.

### 2. Patterns

**Webhook Testing (Idempotency & Deduplication)**
- Use seams to inject unique `transaction_id` into incoming webhook headers
- Send exact same payload twice. Success = `200 OK` or `204 No Content` on second call
- Extend `/home/rpadron/proy/mastermind/rust_control_plane/tests/k6-websocket-load.js` → `k6-webhook-load.js`

**DLQ Testing (Retry Logic)**
- Mock transient `503 Service Unavailable` from backend using "Chaos" pattern
- Message transitions to DLQ → trigger "Retry Worker" → verify message re-queued

**Load Testing for Throughput (k6)**
- **Target:** 1000+ webhooks/second with **p99 latency < 200ms**
- **Soak Testing:** 1-hour endurance test at peak load

**Monitoring Patterns**
- **SLO-Based Alerting:** Alert on **Error Budget burn rate**
- **High-Cardinality Logs:** Every event includes `provider_response_code`, `payload_size_bytes`, `trace_id`
- **Prometheus Metrics:** `webhook_received_total`, `webhook_dlq_total`, `webhook_processing_duration_seconds`

### 3. Anti-Patterns

| Anti-pattern | Why It Fails |
|-------------|--------------|
| **Silent Drop** | Returning `200 OK` before message is safely persisted |
| **Flaky Mocks** | Generic API mocks that don't replicate specific timeout/rate-limiting behaviors |
| **Average-Driven Monitoring** | Dashboards showing "99% success" hide total failure of specific channel |
| **Manual DLQ Management** | Treating DLQ as manual "to-do list" instead of automated recovery |

### 4. Success Criteria

**DORA Performance Metrics:**
- Lead Time for Changes < 1 hour (Elite status)
- Change Failure Rate < 15% for Phase 18 deliverables

**Reliability SLOs:**
- 99.9% of webhooks successfully acknowledged and queued within **200ms (p99)**
- Zero dropped messages (DLQ captures all failures)

**MTTR (Mean Time to Restore):**
- < 1 hour to recover or rollback from routing failure

### 5. Recommendations

**Test Layer Strategy**

| Layer | What | Tool | Count Target |
|-------|------|------|-------------|
| Webhook unit tests | Idempotency, deduplication, DLQ transitions | pytest | 15-20 |
| Provider contract tests | WhatsApp/Instagram API mock contracts | pytest + respx | 8-12 |
| Cross-channel routing tests | Channel Router brain agent selection | pytest | 5-8 |
| Load tests (k6) | 1000 webhooks/second, p99 < 200ms | k6 | 3-5 scripts |
| Soak tests | 1-hour endurance for memory leaks | k6 | 1-2 scripts |
| Integration tests | End-to-end webhook → agent → response | Docker Compose + pytest | 3-5 |

**Run Commands**
```bash
# Backend webhook tests
cd apps/api && uv run pytest tests/integration/test_webhook_idempotency.py -v
cd apps/api && uv run pytest tests/integration/test_webhook_dlq.py -v
cd apps/api && uv run pytest tests/integration/test_cross_channel_routing.py -v

# Load tests
k6 run rust_control_plane/tests/k6-webhook-load.js
k6 run rust_control_plane/tests/k6-webhook-soak.js
```

**Regression Impact**
- **Current baseline:** 682 backend + 575 frontend = 1,257 total tests
- **Phase 18 adds:** ~50 new tests
- **No breaking changes** to existing test suite

---

## Dispatch Meta

| Property | Value |
|----------|-------|
| Total brains dispatched | 4 |
| Brains consulted | #2 UX, #4 Frontend, #5 Backend, #6 QA |
| All returned successfully | yes |
| Outputs written to | `.planning/BRAIN-FEED-0{2,4,5,6}-*.md` |
