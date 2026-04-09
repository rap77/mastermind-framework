# Phase 16 — Brain #7 Evaluation
> Generated: 2026-04-07T11:15:54Z
> Status: APPROVED_WITH_CONDITIONS
> Global Rating: 72/100

---

## Planning Fallacy Analysis

**Optimistic Estimates Detected:**

1. **Rust async learning curve underestimated** — Plan assumes ~2-3 hours for OBS-01 (structured logging), but `tracing-opentelemetry` integration with Tokio typically reveals edge cases (span lifecycle, async context propagation) that **double the estimated time**. Reference Class Forecasting suggests adding 40-50% buffer for first-time Rust async tracing integration.

2. **tokio-tungstenite edge cases** — Plan 16-04 assumes straightforward WebSocket implementation, but connection lifecycle under load (handshake timeouts, backpressure handling, partial message framing) typically adds **50% more time** than estimated.

3. **Ghost Mode replay complexity** — Plan 16-05 assumes in-memory ring buffer is trivial, but doesn't account for: concurrent replay requests (thundering herd), serialization overhead, or memory fragmentation under churn. This is a **hidden 2-3x multiplier**.

**Substitution Bias Detected:**
The team answered "Which observability stack is technically superior?" instead of "Can we guarantee stability with this stack under failure conditions?"

---

## Omission Bias Analysis

**Critical Missing Components:**

1. **Thundering Herd Mitigation** — When 1000 WebSocket clients reconnect simultaneously, all will request Ghost Mode replay at once. **No strategy exists** to prevent PostgreSQL connection pool exhaustion or replay endpoint collapse. This is a **production-killer gap**.

2. **Capacity Planning Model** — Both brains assume 1000 connections is sufficient without: growth rate projection, connection churn model, or memory-per-connection baseline.

3. **Alerting Thresholds** — Brain #6 proposed Prometheus metrics, but **no alert rules** defined (e.g., "error rate > 5% for 5 minutes = page on-call"). Metrics without alerts are vanity metrics.

4. **gRPC Backpressure Strategy** — Plan 16-02 assumes gRPC interceptor just "works," but no strategy for: what happens when Python async queue is full? Do we drop events? Block?

5. **Event Ordering Guarantees** — Neither brain addressed: what if gRPC delivers events out-of-order? Frontend displays wrong sequence → user confusion.

---

## Systems Thinking Analysis

**Feedback Loop Risks:**

1. **Ghost Mode Replay Loop** (A → B → C → A):
   - Ghost Mode replay queries PostgreSQL (A)
   - Slow replay queries hold connection pool (B)
   - WebSocket Hub starves for database connections (C)
   - New WebSocket connections timeout (A)

2. **Memory Growth Loop** (Unbounded → OOM → Cascade):
   - Unbounded WebSocket connections
   - Memory per connection grows under load
   - Rust Control Plane OOM crashes
   - Python agents orphaned

3. **MTTR Explosion Loop** (trace_id missing → debugging hell):
   - trace_id not propagated
   - Cross-service debugging requires manual log correlation
   - MTTR explodes from 15min → 2hrs
   - On-call burnout → reduced development velocity

**Cascade Failure Modes:**

- **If PostgreSQL is slow during Ghost Mode replay:**
  1. WebSocket Hub blocks on replay queries
  2. New connections timeout (backpressure not handled)
  3. Existing connections starve
  4. Total system freeze

- **If /metrics endpoint scraped too frequently:**
  1. Prometheus overhead
  2. HTTP handlers degraded
  3. False positive "system degraded" alerts
  4. Alert fatigue → real alerts ignored

---

## Over-engineering Analysis

**What Can Be Simplified or Deferred:**

1. **gRPC Bi-directional Streaming** — START with unary RPCs. Bi-directional streaming adds complexity without validating it's a bottleneck first.

2. **Prometheus Dashboards** — Dashboards are visualization; they don't prevent incidents. Focus on: structured logging + alert thresholds first.

3. **Centralized Logging** — ELK/Loki aggregation is **deferred**. Stdout JSON logs + container log driver is sufficient for Phase 16.

4. **Circuit Breaker** — `tokio-circuit-breaker` is proposed but no clear failure threshold defined. Start with timeouts + retries (simpler).

**What's Essential (Do NOT Cut):**
- Structured logging with trace_id (non-negotiable)
- Bounded WebSocket channels (non-negotiable)
- max_connections ceiling (non-negotiable)
- In-memory Ghost Mode buffer (non-negotiable)
- Health check separation (liveness vs readiness)

---

## Acceptance Criteria Audit

| Vague Criterion | Specific SLI | Business Justification |
|-----------------|--------------|------------------------|
| "Ghost Mode works" | **P95 replay latency < 500ms for last 100 events** | Prevents user frustration during reconnection |
| "WebSocket Hub is stable" | **Memory per connection < 50KB; total Hub < 100MB at 1000 connections** | Prevents OOM crashes |
| "Distributed tracing works" | **100% of cross-service gRPC requests carry trace_id** | Debugging cross-service issues; MTTR < 15min |
| "System handles load" | **Connections beyond max_connections (2000) receive HTTP 429** | Prevents OOM; graceful degradation |
| "Monitoring is ready" | **Critical alerts fire < 5 min from failure start** | Reduces MTTR |

---

## Verdict

**APPROVED_WITH_CONDITIONS**

**Global Rating: 72/100**

**Conditions (MUST address before execution):**

1. **Fix Ghost Mode Replay Thundering Herd** — Implement request throttling (max 10 concurrent replays) or replay caching (TTL 60s) to prevent PostgreSQL pool exhaustion. **Without this, production restart = guaranteed outage.**

2. **Add max_connections Enforcement** — MUST use bounded channels (256 buffer) + max_connections = 2000 constant as specified in 16-CONTEXT.md Condition #2 and #3. This is non-negotiable for OOM prevention.

3. **Defer gRPC Bi-directional Streaming** — Start with unary RPCs (Condition #5 from 16-CONTEXT.md). Add bi-directional streaming **only after metrics** prove unary is a bottleneck.

4. **Add Specific SLIs** — Convert all "works" criteria to measurable SLIs:
   - Ghost Mode replay: P95 < 500ms
   - Memory per connection: < 50KB
   - trace_id propagation: 100%
   - Connection rejection: HTTP 429 beyond 2000
   - Alert latency: < 5 min

5. **Define Alert Thresholds** — Before writing metrics code, define: what error rate triggers alert? What latency threshold? What memory watermark?

6. **Add Task Time Buffers** — Increase OBS-01 estimate by 50% (Rust async tracing learning curve) and 16-04 by 40% (tokio-tungstenite edge cases).

---

## Evidence Citations

- **Brain #5 output** (line 45-52): Proposed UnboundedSender for WebSocket — **CONTRADICTS** 16-CONTEXT.md Condition #2
- **Brain #5 output** (line 88-95): Proposed gRPC bi-directional streaming from start — **CONTRADICTS** 16-CONTEXT.md Condition #5
- **Brain #6 output** (line 108-131): Proposed Prometheus metrics but **no alert thresholds defined**

---

## What Domain Brains Did Well

- Brain #5: Type-safe contracts (TraceMetadata, Protobuf)
- Brain #6: Health check separation (liveness vs readiness)
- Both: PostgreSQL-first for Ghost Mode (correct defer decision)
- Both: Load testing requirement

---

## Next Steps

1. Address Conditions #1-#6 above (non-negotiable)
2. Re-submit plan with conditions addressed
3. Execute with **pre-mortem analysis** before writing code

**Final Warning:** This plan will fail in production without Condition #1 (thundering herd mitigation) and Condition #2 (bounded channels).
