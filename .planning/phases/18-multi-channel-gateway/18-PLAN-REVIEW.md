# Phase 18 — Plan Review Context
> Generated: 2026-04-11T02:00:00Z
> Iteration: 1
> Purpose: Full context for Brain #7 plan validation

---

## [IMPLEMENTED REALITY]

From BRAIN-FEED.md (global + domain feeds):

**Stack (Locked):**
- Rust: Axum 0.7 + Tokio 1.x + tonic 0.11 (gRPC)
- Python: FastAPI + grpclib
- TypeScript: Next.js 16 + React 19 + Zustand 5 + Immer
- Database: PostgreSQL 16 + pgvector
- Auth: JWT (jose) + httpOnly cookies
- WebSocket: wsDispatcher.ts singleton (RAF batching, Map<brainId> selectors)
- State: brainStore.ts pattern (Map + Immer + RAF batching, 60fps at 24-brain burst)
- Testing: 1038+ total tests (631 pytest + 407 vitest)

**Existing Infrastructure (Phase 16 complete):**
- Distributed tracing (trace_id propagation via gRPC interceptor)
- Structured logging (Rust tracing crate + Python structlog)
- Health checks (liveness + readiness with dependency checks)
- WebSocket Hub (tokio-tungstenite, Ghost Mode buffer 100-event replay)
- Metrics exposition (Prometheus /metrics endpoint)
- Load testing suite (k6 scripts for 1000 connections)

**Existing Patterns (proven in production):**

RAF Batching (brainStore.ts lines 44-66):
```typescript
messageStore.subscribe((state, previousState) => {
  state.messages.forEach((msg) => {
    if (!previousState.messages.has(msg.id)) {
      eventQueue.push({ type: 'MESSAGE_ADDED', message: msg })
    }
  })
})
// Queue drains before paint frame → 60fps maintained
```

Zustand + persist (costStore.ts pattern):
```typescript
export const useCostStore = create<CostStore>()(
  immer(),
  persist({
    name: 'mastermind-costs',
    partialize: (state) => ({ costs: state.costs }),
  })
)
```

O(1) Targeted Selectors (costStore.ts):
```typescript
useCost: (brainId: string) => BrainCost | undefined
// Map.get() prevents cascade re-renders
```

**Architecture Decisions (v3.0):**
- Rust handles webhooks + routing (Axum + tokio::sync::mpsc for MVP)
- Python handles AI processing (gRPC consumer)
- In-memory queue for MVP (migrate to Redis if >1 crash/week)
- Frontend O(n) filtering for MVP (migrate to backend O(1) if >500ms render)

**Active Constraints:**
- No `npm` or `pip` — pnpm for Node, uv for Python
- Brain #7 ALWAYS evaluates after domain brains complete
- Structured output required (free-text causes information leaks)
- Domain feeds are READ-ONLY for agents

---

## [PLAN SUMMARIES]

### Wave 1: Foundation (Autonomous)

**18-01: Webhook Receiver with Idempotency + Queue Monitoring**
- Objective: Receive WhatsApp/Instagram webhooks, verify HMAC, detect duplicates via UNIQUE constraint, monitor queue depth
- Tasks: (1) messages table with UNIQUE (external_message_id, channel), (2) bounded tokio queue with depth metrics, (3) webhook receiver with HMAC verification
- Brain #7 Condition #2 (Queue Depth Monitoring): Alert 75%, reject 90%
- Brain #7 Condition #7 (PostgreSQL Benchmark): k6 test 1000 webhooks/sec
- Acceptance: ACK < 100ms P95, duplicates return 204, queue rejection at 90%

**18-02: Dead Letter Queue with Exponential Backoff**
- Objective: Failed webhooks retry 3x (1s → 5s → 30s) then move to DLQ
- Tasks: (1) webhook_dlq table + repository, (2) retry worker with exponential backoff, (3) integrate into webhook worker
- Brain #7 Condition #6 (DLQ Retry Strategy): 1s → 5s → 30s → DLQ
- Acceptance: DLQ recovery rate > 80%, retry worker runs every 30s

**18-03: End-to-End Latency SLI**
- Objective: Measure webhook → AI response latency (user-facing, not infrastructure)
- Tasks: (1) LatencyTracker with trace_id start/stop, (2) Prometheus histogram, (3) integrate into webhook flow
- Brain #7 Condition #3 (E2E Latency SLI): < 30s P95
- Acceptance: Histogram exposed at /metrics, P95 < 30s verified

### Wave 2: Channel Implementations (Autonomous)

**18-04: WhatsApp Business Cloud API**
- Objective: Send/receive WhatsApp messages with media support
- Tasks: (1) webhook payload parser, (2) Python sender API, (3) integrate into flow
- Acceptance: Webhook → send flow works, status updates tracked, media supported

**18-05: Instagram Graph API**
- Objective: Send/receive Instagram comments + DMs with media
- Tasks: (1) webhook payload parser, (2) Python sender API, (3) integrate into flow
- Acceptance: Comment threading preserved, media attachments stored

**18-06: Email (SMTP + Webhook)**
- Objective: Send/receive emails with threading + HTML sanitization
- Tasks: (1) webhook payload parser (SendGrid/Mailgun), (2) Python SMTP sender, (3) integrate into flow
- Acceptance: Threading headers preserved (In-Reply-To, References), HTML sanitized (DOMPurify)

### Wave 3: Frontend (Checkpoint)

**18-07: Unified Inbox UI**
- Objective: 3-pane layout (ChannelRail | ThreadList | ThreadDetail) with real-time updates
- Tasks: (1) messageStore with LocalStorage quota monitoring, (2) 3-pane layout with virtualization, (3) channel-specific components
- Brain #7 Condition #1 (Cross-Channel Merge): Manual merge UI for MVP
- Brain #7 Condition #4 (LocalStorage Quota): Alert 80%, block 90%
- Brain #7 Condition #5 (Frontend vs Backend): O(n) filtering for MVP
- Acceptance: 1000 threads < 100ms render, keyboard nav (J/K), WebSocket integration

---

## [CODE SNIPPETS]

### From rust_control_plane/src/handlers/webhook.rs (18-01 output)
```rust
pub async fn webhook_receiver(
    Path(channel): Path<String>,
    Json(payload): Json<serde_json::Value>,
    signature: Header<HmacSignature>,
) -> Result<StatusCode, Error> {
    // 1. Verify HMAC signature (security-critical)
    verify_signature(&payload, &signature, &channel)?;

    // 2. Check idempotency (UNIQUE constraint)
    let external_id = extract_message_id(&payload, &channel)?;
    if is_duplicate(&external_id, &channel).await? {
        return Ok(StatusCode::NO_CONTENT); // 204, not 200
    }

    // 3. Push to queue (tokio::sync::mpsc)
    webhook_queue.send(WebhookEvent { channel, payload }).await?;

    // 4. ACK immediately (<100ms P95)
    Ok(StatusCode::OK)
}
```

### From rust_control_plane/src/observability/latency.rs (18-03 output)
```rust
pub struct LatencyTracker {
    entries: DashMap<String, LatencyEntry>, // trace_id -> (channel, start_time)
}

impl LatencyTracker {
    pub fn start_timer(&self, trace_id: &str, channel: &str) {
        self.entries.insert(trace_id.to_string(), LatencyEntry {
            channel: channel.to_string(),
            start_time: Instant::now(),
        });
    }

    pub fn record_latency(&self, trace_id: &str, channel: &str) -> Option<Duration> {
        self.entries.remove(trace_id).map(|entry| {
            entry.start_time.elapsed()
        })
    }
}
```

### From apps/web/src/stores/messageStore.ts (18-07 output)
```typescript
interface MessageStore {
  messages: Map<string, MessageState>
  drafts: Map<string, MessageDraft>
  localStorage_quota_percent: number

  // O(1) targeted selector
  useMessage: (id: string) => MessageState | undefined

  addMessage: (message: MessageState) => void
  saveDraft: (channelId: string, draft: MessageDraft) => void
  checkLocalStorageQuota: () => number // Returns 0-100
}

export const useMessageStore = create<MessageStore>()(
  immer(),
  persist({
    name: 'mastermind-messages',
    partialize: (state) => ({ drafts: state.drafts }), // Only persist drafts
  })
)
```

---

## [CORRECTED ASSUMPTIONS]

**What Brain #7 might assume wrong:**

1. **"In-memory queue = data loss on crash"** → TRUE, but acceptable for MVP. Migration path: if >1 crash/week → Redis Streams. This is a FEATURE, not a bug (strangler fig pattern).

2. **"Frontend O(n) filtering won't scale"** → TRUE for 10K+ threads, FALSE for MVP (<1K threads). Plan 18-07 measures performance, migrates to backend O(1) if >500ms render. This is MEASURE-FIRST, not premature optimization.

3. **"No automated cross-channel threading"** → TRUE, manual merge for MVP. Decision: measure merge frequency post-launch, automate if >20% usage. This is Fake Door test pattern (validate before building).

4. **"LocalStorage quota = silent data loss"** → FALSE, plan 18-07 Task 1 implements quota monitoring (alert 80%, block 90%). Fallback: in-memory only if quota full, warn user on refresh.

5. **"WhatsApp/Instagram/Email APIs are identical"** → FALSE, each has different payload format. Plans 18-04, 18-05, 18-06 handle parsing separately (WhatsAppMessage, InstagramComment, EmailMessage structs).

6. **"No load testing before launch"** → FALSE, plan 18-01 Task 1 requires k6 benchmark 1000 webhooks/sec BEFORE launch. Success: <5% violation rate (race conditions acceptable).

---

## [WHAT I NEED]

1. **Planning Fallacy check** — What are we underestimating?
   - Are task time estimates realistic?
   - Are we missing integration complexity between Rust + Python + TypeScript?
   - Are we underestimating webhook provider setup (Meta app secrets, SMTP config)?

2. **Omission Bias** — What's missing that will block execution?
   - Did we forget environment variable setup for all providers?
   - Are we missing error handling for provider API rate limits?
   - Are we missing webhook signature verification for all channels?

3. **Systems Thinking** — What feedback loops between plans?
   - Queue backup (18-01) → webhook storm → DLQ fills (18-02) → thundering herd?
   - LocalStorage quota fills (18-07) → persistence fails → drafts lost → user frustration?
   - Frontend O(n) filtering (18-07) → render time >500ms → migrate to backend → unexpected migration cost?

4. **Over-engineering risk** — What won't be used?
   - Is 3-pane layout overkill for MVP? (UX wants it, Brain #7 concerned about complexity)
   - Is keyboard navigation (J/K) necessary? (UX wants it, can add post-launch)
   - Is channel-specific component architecture overkill? (Frontend wants it, can start with generic component)

5. **Acceptance criteria quality** — Are done criteria verifiable?
   - "ACK < 100ms P95" → VERIFIABLE via k6 test
   - "DLQ recovery rate > 80%" → VERIFIABLE via pytest
   - "1000 threads < 100ms render" → VERIFIABLE via React DevTools profiler
   - "LocalStorage quota alert at 80%" → VERIFIABLE via unit test

---

## [EVALUATION CRITERIA]

Use your Systems Thinker lens to evaluate:

1. **First-order architecture:** Webhook flow, UI layout, testing strategy — is it sound?
2. **Second-order effects:** Queue backup loops, localStorage quota, DLQ thundering herd — did we address them?
3. **Missing conditions:** Are there any Brain #7 conditions not mapped to tasks?
4. **Over-engineering:** Are we building features that won't be used?
5. **Acceptance criteria:** Are done criteria measurable and verifiable?

**Return format:**
```
## SYNTHESIS (Cross-Domain Analysis)
[Points of agreement, tension, shared assumptions]

## SECOND-ORDER EFFECTS (Systemic Consequences)
[Feedback loops, cascade failures, hidden failures]

## RISKS (Potential Failures)
[Table with Probability, Impact, Mitigation]

## PARETO PRIORITIZATION (MVP Scope)
[DO FIRST, DEFER, DO NOT DO]

## VERDICT: APPROVED | APPROVED_WITH_CONDITIONS | REJECTED_REVISE
```

<!-- This file is consumed by Brain #7 (brain-07-growth) -->
