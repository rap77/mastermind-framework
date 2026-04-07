# Phase 16 — Domain Brain Outputs
> Generated: 2026-04-07T07:00:00Z
> Status: complete

## Brain #5 — Backend Architecture

### [IMPLEMENTED REALITY]

**Stack:** Python 3.14 + uv | FastAPI + Pydantic v2 strict mode | SQLAlchemy 2.x async driver
**Concurrency:** asyncio.TaskGroup for concurrent brain queries — no Celery
**Auth:** JWT httpOnly cookies | proxy.ts (Next.js) + Server Components + FastAPI dependency (dual-layer)
**Test suite:** 620/620 backend passing — zero failures tolerated
**Package manager:** uv only — never pip, poetry, conda

**Rust Control Plane (Phase 15 COMPLETE):**
- Axum 0.7 + Tokio 1.x operational
- PostgreSQL 16 + pgvector with connection pooling (max 20, 5s timeout)
- JWT auth + RBAC middleware implemented
- Event sourcing with immutable activity_log
- gRPC client (tonic 0.11) for Python communication
- Health endpoint: `/health` returns service status
- **tracing 0.1 + tracing-subscriber 0.3 already in Cargo.toml** (✅ verified)

### Backend Architecture Recommendations

#### 1. Logging Architecture — Distributed Tracing

**Type Contract:**
```rust
pub struct TraceMetadata {
    pub trace_id: Uuid,
    pub request_id: Uuid,
    pub user_id: Option<Uuid>,
}
```

**Async Pattern:** `tracing::span!` in Rust → gRPC metadata → Python `structlog` with `trace_id`

**Stack:** `tracing` crate already in Cargo.toml. Add `tracing-opentelemetry` for OpenTelemetry integration.

#### 2. WebSocket Hub Design — Registry Pattern

**Type Contract:**
```rust
pub struct WebSocketHub {
    connections: Arc<DashMap<UserId, mpsc::UnboundedSender<ClientMessage>>>,
    global_events: broadcast::Sender<SystemEvent>,
    ghost_buffer: Arc<Mutex<VecDeque<StoredEvent>>>,
}
```

**Async Pattern:** tokio-tungstenite for WebSocket, Registry Pattern with DashMap for O(1) lookup

**Stack:** Add `tokio-tungstenite = "0.21"`, `dashmap = "5.5"`

#### 3. Ghost Mode Buffer — PostgreSQL-First

**Type Contract:**
```python
class GhostModeEvent(BaseModel):
    model_config = ConfigDict(strict=True)
    id: UUID
    brain_id: str
    event_type: BrainEventType
    payload: dict[str, Any]
    created_at: datetime
```

**Async Pattern:** Repository Pattern for replay queries using existing `activity_log` table

**Stack:** No Redis yet — PostgreSQL with indexes sufficient

#### 4. Health Check Enhancements

**Type Contract:**
```rust
pub struct HealthResponse {
    pub status: ServiceStatus,
    pub dependencies: DependencyHealth,
}
```

**Async Pattern:** Liveness Probe (Tokio event loop) vs Readiness Probe (dependencies)

#### 5. Integration Patterns — Python → Rust

**Type Contract:**
```protobuf
service EventStream {
  rpc SubscribeBrainEvents(SubscriptionRequest) returns (stream BrainEvent);
}
```

**Async Pattern:** gRPC Bi-directional Streaming, persistent Python → Rust connection

### Implementation Priority

1. **OBS-01** (Logging + Tracing) — Foundation
2. **RTU-01** (WebSocket Hub) — Core infrastructure
3. **Health Check Enhancements** — Quick win
4. **Ghost Mode Buffer** — Nice-to-have

---

## Brain #6 — QA/DevOps

### Observability Strategy

**Metrics to Collect:**
- Request latency (P50, P95, P99) per endpoint
- Error rate by endpoint (4xx, 5xx)
- Active WebSocket connections
- gRPC message latency (Rust ↔ Python)
- Database query latency (PostgreSQL)
- Event loop lag (Tokio, asyncio)

**Prometheus Integration:**
```rust
use prometheus::{Counter, Histogram, Gauge};

lazy_static! {
    static ref HTTP_REQUESTS_TOTAL: Counter = Counter::new(
        "http_requests_total", "Total HTTP requests"
    ).unwrap();
    static ref HTTP_REQUEST_DURATION: Histogram = Histogram::new(
        "http_request_duration_seconds", "HTTP request latency"
    ).unwrap();
}
```

**Exposition:** `/metrics` endpoint for Prometheus scraping

### Health Check Design

**Liveness Probe (`/health/live`):**
- Check Tokio event loop responsiveness
- Spawn task, measure response time
- Return 200 if < 1s, 503 if degraded

**Readiness Probe (`/health/ready`):**
- PostgreSQL connection pool status
- gRPC channel to Python health
- WebSocket hub accepting connections
- Return 200 if all dependencies healthy, 503 if any degraded

### Log Format

**JSON Structured Logging:**
```json
{
  "timestamp": "2026-04-07T12:00:00Z",
  "level": "INFO",
  "trace_id": "123e4567-e89b-12d3-a456-426614174000",
  "request_id": "987fcdeb-51a2-43f1-a456-426614174000",
  "user_id": "abc-123",
  "service": "rust-control-plane",
  "event": "brain_started",
  "duration_ms": 1234,
  "error": null
}
```

**Mandatory Fields:** timestamp, level, trace_id, service, event

### Testing Strategy

**Distributed Tracing E2E:**
- Integration test: HTTP request → Rust → inject trace_id → gRPC → Python → verify in logs
- Fixture: `inject_trace_header()` for pytest
- Verification: `trace_id` present in all log entries across services

**WebSocket Hub Load Test:**
- Target: 1000 concurrent WebSocket connections
- Tool: `tokio` task spawning with `WebSocket::connect_async`
- Metrics: Memory usage, CPU per connection, event broadcast latency
- SLA: < 100ms broadcast latency to 1000 clients

**Reliability Patterns:**
- Circuit Breaker: `tokio-circuit-breaker` for gRPC calls to Python
- Retries: Exponential backoff (1s, 2s, 4s, max 30s) for transient failures
- Timeouts: `tokio::time::timeout` enforced on all external calls (1s default)

### Monitoring Gaps

**What's Missing for Production Ops:**
1. **Alerting** — No alert rules defined (e.g., error rate > 5% for 5min)
2. **Dashboards** — No Grafana dashboards for metrics visualization
3. **Log Aggregation** — All logs to stdout, no centralized logging (ELK, Loki)
4. **Incident Response** — No runbooks for common failures
5. **Capacity Planning** — No capacity limits defined (max WebSocket connections per instance)

### Priority Recommendations

**Critical Path (Blockers):**
1. Structured logging with trace_id propagation
2. Health check endpoints (liveness + readiness)
3. Basic Prometheus metrics exposition

**Important (Reliability):**
4. WebSocket Hub load testing
5. Circuit breaker for gRPC calls
6. Timeout enforcement on all external calls

**Nice-to-Have (Operational Excellence):**
7. Grafana dashboards
8. Alert rules
9. Centralized logging (defer until post-launch)

---

## Dispatch Meta

| Property | Value |
|----------|-------|
| Total brains dispatched | 2 |
| Brains returned successfully | yes |
| Duration | ~2 minutes total |
| Output size | Large (45K+ tokens combined) |

---

## Cross-Brain Synthesis

### Aligned Decisions

**Both brains agree on:**
1. PostgreSQL-first for Ghost Mode (no Redis yet)
2. Structured logging with JSON format
3. Health check separation (liveness vs readiness)
4. tokio-tungstenite for WebSocket Hub
5. Load testing requirement before production

### Trade-offs Identified

**Backend (#5) emphasizes:**
- Type safety (TraceMetadata struct, Protobuf)
- Architecture patterns (Registry, Repository)
- Integration contracts (gRPC streaming)

**QA (#6) emphasizes:**
- Reliability patterns (circuit breakers, retries)
- SLIs/SLOs (latency percentiles, error rates)
- Operational readiness (dashboards, alerting)

### Open Questions for Brain #7

1. **Ghost Mode replay trigger** — Brain #1 needs UX design
2. **Load testing target** — QA needs 1000 connections, but what's the production target?
3. **Event ordering** — What if gRPC delivers out-of-order? Frontend handling?
4. **Monitoring priority** — Prometheus metrics first, or dashboards/alerting?
