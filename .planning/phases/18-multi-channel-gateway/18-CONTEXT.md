# Phase 18: Multi-channel Gateway — Brain-Informed Context

> Generated: 2026-04-10T22:55:00Z
> Status: Ready for Planning
> Brain #7 Verdict: APPROVED_WITH_CONDITIONS (3.0/5.0)

---

## What This Is

Phase 18 adds a **Multi-channel Gateway** to MasterMind — unified inbox across WhatsApp Business Cloud API, Instagram Graph API, and Email (aiosmtplib). Users can send/receive messages across all 3 channels from a single interface, with an AI-powered Channel Router that suggests optimal response channels.

This is NEW infrastructure, not an extension of existing features.

---

## Brain Consultation Summary

**Brains Consulted:** #2 UX, #4 Frontend, #5 Backend, #6 QA, #7 Growth/Data

**Brain #7 Verdict:** ✅ APPROVED_WITH_CONDITIONS (3.0/5.0)
- Strong first-order architecture (webhook flow, UI layout, testing)
- Missing second-order analysis (queue backup loops, localStorage quota, DLQ thundering herd)
- 7 must-address conditions before launch

**Key Decisions:**
1. Rust handles webhooks + routing, Python handles AI processing
2. In-memory `tokio::sync::mpsc` queue for MVP (migrate to Redis if >1 crash/week)
3. 3-pane inbox UI (Channels → Thread List → Active Thread)
4. Channel-specific message components (WhatsAppMessage, InstagramMessage, EmailMessage)
5. DLQ with manual retry + exponential backoff (1s → 5s → 30s → DLQ)
6. Idempotency via UNIQUE constraint on `(external_message_id, channel)`

---

## Constraints (Brain #7 Conditions — Blocking)

### 1. Cross-Channel Thread Merge Logic (DEFINED)
**Decision:** Launch with MANUAL merge only.
- Same customer on WhatsApp + Instagram = 2 separate threads (MVP)
- User manually merges threads via UI action
- Measure merge frequency post-launch
- Automate if >20% of users manually merge threads

### 2. Queue Depth Monitoring (REQUIRED)
**Implementation:**
- Expose queue depth metric: `tokio_queue_depth_percent` (0-100)
- Alert at 75% capacity (SRE notification)
- Reject new webhooks at 90% capacity (return 503 Service Unavailable)
- Prometheus metric: `webhook_queue_depth_percent{channel="whatsapp"}"`

### 3. End-to-End Latency SLI (REQUIRED)
**Metric:** Webhook → AI response <30s P95
- NOT just webhook ACK <100ms (that's infrastructure, not user-facing)
- Full flow: webhook received → queued → AI processed → response sent
- Track per-channel: `webhook_e2e_latency_seconds{channel="whatsapp",quantile="p95"}`

### 4. LocalStorage Quota Monitoring (REQUIRED)
**Implementation:**
- Monitor localStorage usage: `JSON.stringify(localStorage).length`
- Alert at 80% quota usage (~4MB for 5MB limit)
- Block persistence at 90% quota usage (notify user to archive)
- Fallback: In-memory only if quota full (warn user on refresh)

### 5. Frontend vs Backend Grouping (DECISION REQUIRED)
**Question:** UX wants "group by agent ownership" — WHERE does this happen?
- **Option A (Frontend O(n)):** Filter in component render → simpler backend, slower UI
- **Option B (Backend O(1)):** Pre-group in query → add `agent_id` column to messages table, indexed
- **Decision:** Option A for MVP (frontend filtering), measure performance, migrate to B if >500ms render time

### 6. DLQ Retry Backoff Strategy (DEFINED)
**Implementation:**
- Retry 1: 1 second delay (transient glitch)
- Retry 2: 5 second delay (provider throttling)
- Retry 3: 30 second delay (provider outage)
- After 3 failures: Move to DLQ (manual inspection + retry)
- Exponential backoff prevents thundering herd

### 7. PostgreSQL UNIQUE Constraint Benchmark (REQUIRED)
**Action:** Run k6 load test BEFORE launch
```bash
k6 run rust_control_plane/tests/k6-webhook-load.js
# Target: 1000 webhooks/sec with UNIQUE constraint
# Success: <5% violation rate (race conditions acceptable)
# Failure: Add Redis for idempotency (SET with NX flag)
```

---

## Architecture Decisions

### Backend (Rust + Python)

**Rust Control Plane (webhook receiver):**
```rust
// Axum handler for /webhooks/{channel}
async fn webhook_receiver(
    Path(channel): Path<String>,
    payload: Json<Value>,
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

**Python FastAPI (AI worker):**
```python
# gRPC consumer from queue
@app.post("/api/webhook-worker/consume")
async def consume_webhook(event: WebhookEvent):
    # 1. Route to Channel Router brain agent
    suggested_channel = channel_router_agent.suggest_channel(event)

    # 2. Generate AI response
    response = await brain_agent.process(event)

    # 3. Send via channel adapter (WhatsApp/Instagram/Email)
    await channel_adapter.send(response, suggested_channel)

    return {"status": "processed", "trace_id": event.trace_id}
```

**DLQ Implementation:**
- PostgreSQL table: `webhook_dlq (id, external_message_id, channel, payload, error, retry_count, created_at)`
- Retry worker: Cron job every 30 seconds
- Query: `SELECT * FROM webhook_dlq WHERE retry_count < 3 ORDER BY created_at ASC LIMIT 100`

### Frontend (Next.js 16 + React 19)

**messageStore (Zustand + Immer + persist):**
```typescript
interface MessageStore {
  messages: Map<string, MessageState>
  drafts: Map<string, MessageDraft>

  // O(1) targeted selector
  useMessage: (id: string) => MessageState | undefined

  // Actions
  addMessage: (message: MessageState) => void
  updateMessageStatus: (id: string, status: MessageStatus) => void
  saveDraft: (channelId: string, draft: MessageDraft) => void
}

export const useMessageStore = create<MessageStore>()(
  immer(),
  persist({
    name: 'mastermind-messages',
    partialize: (state) => ({ drafts: state.drafts }), // Only persist drafts
  })
)
```

**Component Hierarchy:**
```
UnifiedInboxPage (new route: /messaging)
├── ChannelRail (whatsapp | instagram | email)
├── ThreadList (react-virtuoso, 7±2 visible)
│   └── ThreadItem (selected indicator, unread badge, status icon)
├── ThreadDetail (active thread)
│   ├── MessageList (Virtuoso virtualized)
│   │   ├── WhatsAppMessage (green bubble, checkmarks)
│   │   ├── InstagramMessage (gradient border, media grid)
│   │   └── EmailMessage (blue/gray, subject line, thread view)
│   └── MessageComposer (channel-specific UI)
│       ├── WhatsAppComposer (text input, emoji picker)
│       ├── InstagramComposer (media upload, caption)
│       └── EmailComposer (subject, cc/bcc, rich text + DOMPurify)
└── DLQInlineRetry (error threads with "Retry" button)
```

**WebSocket Integration:**
```typescript
// Extend wsDispatcher.ts
wsDispatcher.subscribe('thread_updates', (event) => {
  messageStore.getState().addMessage(event.message)
})

// RAF batching (extend brainStore pattern)
messageStore.subscribe((state, previousState) => {
  state.messages.forEach((msg) => {
    if (!previousState.messages.has(msg.id)) {
      eventQueue.push({ type: 'MESSAGE_ADDED', message: msg })
    }
  })
})
```

---

## Success Criteria (Brain-Validated)

### UX (Brain #2)
- Time-to-First-Response < 5s (user lands → selects thread → composes)
- Error Recovery Time < 10s (DLQ → retry → resubmitted)
- Channel Recognition Accuracy > 95% (identify source without reading)
- Zero Mistake Errors (system prevents invalid sends)
- Keyboard Navigation Usage > 50% (expert users)

### Frontend (Brain #4)
- Message list render time (1000 msgs) < 100ms
- Frame drops during scroll: 0 at 60fps
- Main thread blocking (WS burst 50 msgs/sec) < 16ms per frame
- Email composition preview < 50ms
- Draft persistence < 16ms, non-blocking
- XSS vulnerabilities: 0 (DOMPurify coverage)

### Backend (Brain #5)
- Zero Message Loss (100% processed or in DLQ)
- Webhook ACK latency < 100ms P95
- Effective Traceability (trace_id propagation)
- High Concurrency (2000 connections, no degradation)
- Idempotency Success Rate: 0% duplicates

### QA (Brain #6)
- DORA: Lead Time < 1 hour, Change Failure Rate < 15%
- SLO: 99.9% webhooks acknowledged within 200ms
- MTTR: < 1 hour to recover from routing failure

### Brain #7 (Systems)
- SLI-1: Users respond within 5 minutes
- SLI-2: Queue depth < 50% P95
- SLI-3: End-to-end latency < 30s P95
- SLI-4: LocalStorage quota < 80%
- SLI-5: DLQ recovery rate > 80%
- SLI-6: Cross-channel merge accuracy > 90%

---

## Implementation Gaps (Verified via Grep)

🔴 **Missing for Phase 18:**
- Webhook receiver Rust code (zero files handle WhatsApp/Instagram webhooks)
- MessageStore (no message-specific Zustand store)
- Channel-specific components (no WhatsApp/Instagram/Email components)
- DLQ implementation (no DLQ table, no retry worker)
- Idempotency layer (no UNIQUE constraint on messages table)
- Queue depth monitoring (no Prometheus metric for queue depth)
- LocalStorage quota monitoring (no usage tracking)

✅ **Already Available:**
- react-virtuoso v4.18.3 (package.json)
- RAF batching pattern (brainStore.ts lines 44-66)
- DOMPurify (4 files use sanitization)
- useTransition (CostDashboard.tsx demonstrates)
- Zustand + persist (layoutStore.ts shows pattern)
- gRPC infrastructure (Phase 16)
- Distributed tracing (Phase 16)

---

## Testing Strategy (Brain #6)

| Layer | What | Count | Offline? |
|-------|------|-------|----------|
| Webhook unit tests | Idempotency, deduplication, DLQ | 15-20 | Yes |
| Provider contract tests | WhatsApp/Instagram mocks | 8-12 | Yes |
| Cross-channel routing tests | Channel Router selection | 5-8 | Yes |
| Load tests | 1000 webhooks/sec, p99 < 200ms | 3-5 | No |
| Soak tests | 1-hour endurance | 1-2 | No |
| Integration tests | End-to-end webhook → response | 3-5 | No |

**Run Commands:**
```bash
# Backend (from ROOT per .pre-commit-config.yaml pattern)
cd apps/api && uv run pytest tests/integration/test_webhook_idempotency.py -v
cd apps/api && uv run pytest tests/integration/test_webhook_dlq.py -v

# Load tests (from ROOT)
k6 run rust_control_plane/tests/k6-webhook-load.js
k6 run rust_control_plane/tests/k6-webhook-soak.js

# Full suite
cd apps/api && uv run pytest --cov=mastermind_cli --cov-report=xml
pnpm --prefix apps/web test run
```

---

## Next Steps

1. **Create 7 plans** (18-01 through 18-07) via GSD planner
2. **Execute in waves:**
   - Wave 1: Foundation (18-01 webhook receiver, 18-02 idempotency, 18-03 DLQ)
   - Wave 2: Channel adapters (18-04 WhatsApp, 18-05 Instagram, 18-06 Email)
   - Wave 3: Frontend (18-07 unified inbox UI)
3. **Brain #7 re-evaluation** after each wave

---

**Context complete. Ready for `/mm:execute-phase 18` or manual planning.**
