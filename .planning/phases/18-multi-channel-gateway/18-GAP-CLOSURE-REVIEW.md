# Phase 18 — Gap Closure Review Context
> Generated: 2026-04-11T16:00:00Z
> Iteration: 1
> Purpose: Brain #7 validation for gap closure plans (18-08, 18-09, 18-10)

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

**Phase 18 Current Status (from VERIFICATION.md):**
- 20/30 truths verified (67%)
- 4 critical BLOCKERS preventing core functionality
- 9 feature gaps (success criteria not met)
- 3 waves of gap closure planned: 18-08 (infrastructure), 18-09 (integration), 18-10 (features)

---

## [CODE REALITY — What Actually Exists]

### rust_control_plane/src/queue/mod.rs (Lines 48-102)
```rust
/// Get current queue depth as percentage (0-100)
pub fn queue_depth_percent(&self) -> f64 {
    // Note: tokio::sync::mpsc::Sender doesn't provide remaining() method
    // We'll approximate by using capacity() - semaphore_permits()
    // For now, return 0 as a placeholder
    // TODO: Implement proper queue depth tracking
    if self.capacity == 0 {
        return 0.0;
    }
    0.0 // Placeholder - needs implementation
}

/// Get approximate current length
pub fn len(&self) -> usize {
    // Note: tokio::sync::mpsc::Sender doesn't provide remaining() method
    // TODO: Implement proper queue length tracking
    0 // Placeholder - needs implementation
}

/// Check if queue is empty
pub fn is_empty(&self) -> bool {
    // Note: tokio::sync::mpsc::Sender doesn't provide is_empty() method
    // TODO: Implement proper queue empty tracking
    true // Placeholder - assumes empty
}
```
**Issue:** All three methods are stubbed. Queue depth monitoring doesn't work. 90% rejection never triggers.

### rust_control_plane/src/main.rs (Lines 76-99)
```rust
let app = Router::new()
    // Metrics endpoint (public)
    .route("/metrics", get(metrics::metrics_endpoint))
    // Ghost Mode replay endpoint (public)
    .route("/api/ghost/replay", get(ghost_replay_handler))
    // WebSocket endpoint (public)
    .route("/ws", get(websocket::websocket_handler))
    // Kubernetes-style health probes (public)
    .route("/health/live", get(health::live::liveness_probe))
    .route("/health/ready", get(health::ready::readiness_check))
    // Auth routes (public)
    .route("/api/auth/login", post(handlers::auth::login))
    .route("/api/auth/refresh", post(handlers::auth::refresh))
    // Protected auth routes (require authentication)
    .route("/api/auth/logout", post(handlers::auth::logout))
    // Audit log routes (protected, admin-only)
    .route("/api/audit/activity", get(handlers::audit::get_activity_log))
    .route("/api/audit/brain/:brain_id", get(handlers::audit::get_brain_timeline))
    .layer(middleware::from_fn_with_state(
        state.clone(),
        auth_middleware,
    ))
    .layer(middleware::from_fn(inject_trace_middleware))
    .with_state(state);
```
**Issue:** NO `/webhooks/:channel` route registered. Handler exists in `handlers/webhook.rs` but route missing.

### rust_control_plane/src/queue/worker.rs (Lines 159-162)
```rust
// TODO: Send to Python AI worker via gRPC
// For now, simulate success/failure
self.send_to_ai_worker(event).await?;
```
**Issue:** `send_to_ai_worker()` is stub (logs only, no actual gRPC call). End-to-end flow broken at AI processing.

### rust_control_plane/src/handlers/webhook.rs (Lines 99-120)
```rust
/// Check if webhook is duplicate via UNIQUE constraint
async fn is_duplicate(db: &PgPool, external_id: &str, channel: &str) -> anyhow::Result<bool> {
    let result = sqlx::query_scalar::<_, i64>(
        "SELECT COUNT(*) FROM messages WHERE external_message_id = $1 AND channel = $2"
    )
    .bind(external_id)
    .bind(channel)
    .fetch_one(db)
    .await?;

    Ok(result > 0)
}
```
**Issue:** sqlx macros require DATABASE_URL or offline mode. 16 compilation errors without DATABASE_URL.

---

## [GAP CLOSURE PLANS]

### Wave 1: Plan 18-08 — Critical Infrastructure Fixes
**Objective:** Fix 3 BLOCKERS preventing core functionality
**Autonomous:** true

**Tasks:**
1. Implement actual queue depth tracking using semaphore permits
2. Fix metrics updater to use valid queue depth calculation
3. Register webhook route in main.rs with WebhookState
4. Generate SQLX offline cache for compilation without DATABASE_URL

**Must-Have Truths:**
- Queue depth is monitored via Prometheus metric (real values, not 0.0)
- Webhooks are rejected at 90% queue capacity (503 response)
- POST /webhooks/{channel} endpoint is accessible
- Rust compilation succeeds without DATABASE_URL
- All tests pass (cargo test)

### Wave 2: Plan 18-09 — gRPC Integration
**Objective:** Complete webhook → queue → AI → channel send flow
**Autonomous:** true
**Depends on:** 18-08

**Tasks:**
1. Create Protobuf contract for Rust ↔ Python gRPC
2. Implement gRPC client in Rust worker (replace stub)
3. Implement Python gRPC server for webhook processing
4. Add delivery status tracking table

**Must-Have Truths:**
- AI processing via gRPC call to Python worker (not stub)
- E2E latency SLI includes actual AI processing time
- WhatsApp/Instagram/Email messages sent via respective APIs
- Message status updates (sent, delivered, read) tracked

### Wave 3: Plan 18-10 — Feature Gaps
**Objective:** Complete remaining feature gaps
**Autonomous:** false (requires human verification)
**Depends on:** 18-08, 18-09

**Tasks:**
1. Add DLQ API endpoints for manual retry
2. Add nh3 sanitization for HTML emails (backend)
3. Add DOMPurify sanitization (frontend)
4. Implement thread merge UI
5. Create Channel Router brain agent stub
6. Verify email threading + media handling stubs
7. Add performance test for 1000 message render

**Must-Have Truths:**
- Manual retry UI allows resubmitting failed webhooks
- HTML email sanitization prevents XSS
- Manual thread merge UI works
- Channel Router agent selects optimal channel
- Message list render time < 100ms

---

## [CORRECTED ASSUMPTIONS]

**What Brain #7 might assume wrong:**

1. **"Queue depth tracking is trivial"** → FALSE. tokio::sync::mpsc::Sender doesn't provide len() method. Plan 18-08 Task 1 uses Semaphore permits for accurate tracking. This is CORRECT approach.

2. **"gRPC bridge is over-engineering"** → FALSE. Rust ↔ Python gRPC enables proper separation of concerns (Rust for webhooks/queue, Python for AI). This is INTENTIONAL architecture for v3.0.

3. **"SQLX offline mode is optional"** → FALSE. CI/CD can't require DATABASE_URL. Plan 18-08 Task 4 generates sqlx-data.json for compilation. This is REQUIRED.

4. **"Channel Router must be sophisticated"** → FALSE. Plan 18-10 Task 5 creates stub for MVP (return original channel with 50% confidence). Sophisticated routing deferred based on metrics.

5. **"Media handling must be complete"** → FALSE. Plan 18-10 Task 6 implements stubs with TODOs. Full media processing deferred post-launch.

---

## [WHAT I NEED FROM BRAIN #7]

### 1. Planning Fallacy Check
**Are task time estimates realistic?**
- Plan 18-08 Task 1 (Semaphore queue depth): Is 1-2 hours realistic? Have we underestimated tokio::sync::Semaphore complexity?
- Plan 18-09 Task 3 (Python gRPC server): Is 2-3 hours realistic? Have we underestimated grpclib integration?
- Plan 18-10 Task 4 (Thread merge UI): Is 2-3 hours realistic? Have we underestimated React state management complexity?

### 2. Omission Bias
**What's missing that will block execution?**
- Did we forget environment variable setup for gRPC (PYTHON_GRPC_PORT)?
- Are we missing error handling for gRPC connection failures?
- Did we forget to run migrations for delivery_status table?
- Are we missing webhook provider setup (Meta app secrets, SMTP config)?

### 3. Systems Thinking
**What feedback loops between plans?**
- Plan 18-08 fixes queue depth → enables Plan 18-09 gRPC integration
- Plan 18-09 gRPC bridge → enables Plan 18-10 DLQ retry (actual failures to retry)
- Plan 18-10 thread merge → depends on Plan 18-09 delivery status (need sent status to merge)
- Plan 18-08 SQLX fix → unblocks ALL plans (compilation blocking everything)

**Cascade failures:**
- If Plan 18-08 Task 1 (queue depth) fails → Plan 18-09 can't test 90% rejection
- If Plan 18-09 Task 2 (gRPC client) fails → Plan 18-10 can't test DLQ retry (no real failures)
- If Plan 18-08 Task 4 (SQLX) fails → NO plans can execute (compilation blocker)

### 4. Over-Engineering Risk
**What won't be used?**
- Is delivery status tracking overkill for MVP? (Plan 18-09 Task 4)
- Is Channel Router agent necessary? (Plan 18-10 Task 5) — Success criteria mentions "new brain agent" but is it MVP-blocking?
- Is thread merge UI overkill? (Plan 18-10 Task 4) — Can we defer post-launch?

### 5. Acceptance Criteria Quality
**Are done criteria verifiable?**
- "Queue depth returns real values 0-100" → VERIFIABLE via /metrics endpoint
- "Webhook route accessible" → VERIFIABLE via curl
- "cargo build succeeds without DATABASE_URL" → VERIFIABLE via unset DATABASE_URL && cargo build
- "gRPC client calls Python worker" → VERIFIABLE via integration test
- "Thread merge UI works" → VERIFIABLE via manual UI test
- "Performance test <100ms" → VERIFIABLE via vitest

---

## [EVALUATION CRITERIA]

Use your Systems Thinker lens to evaluate:

1. **First-order architecture:** Semaphore-based queue depth, gRPC bridge, delivery status — is it sound?
2. **Second-order effects:** Queue backup → gRPC timeout → DLQ fills — did we address this?
3. **Missing conditions:** Are there any Brain #7 conditions not mapped to tasks?
4. **Over-engineering:** Are we building features that won't be used (Channel Router, delivery status)?
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

---

<!-- This file is consumed by Brain #7 (brain-07-growth) -->
