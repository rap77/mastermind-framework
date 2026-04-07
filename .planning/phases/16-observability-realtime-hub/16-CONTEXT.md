# Phase 16 — Implementation Context
> Generated: 2026-04-07T07:10:00Z
> Status: Brain consultation complete — APPROVED_WITH_CONDITIONS

---

## Goal

Cross-service debugging visibility + real-time WebSocket infrastructure for monitoring brain agents in production.

---

## [IMPLEMENTED REALITY]

**Phase 15 COMPLETE — Rust Control Plane operational:**
- Axum 0.7 + Tokio 1.x with PostgreSQL 16 + pgvector
- JWT auth + RBAC middleware implemented
- Event sourcing with immutable `activity_log`
- gRPC client (tonic 0.11) for Python communication
- `tracing` 0.1 + `tracing-subscriber` 0.3 in Cargo.toml
- 682 Python tests passing, 407 frontend tests passing

**Current Gaps:**
- No structured logging (println! in Rust, print() in Python)
- No distributed tracing (trace_id not propagated)
- No Prometheus metrics
- Health checks are basic (`/health` returns static JSON)
- WebSocket backend on FastAPI (needs Rust migration)

---

## [CORRECTED ASSUMPTIONS — Brain #7 Systems Gaps]

❌ "Ghost Mode is nice-to-have" → ✅ **Ghost Mode is co-requirement** with RTU-01
❌ "UnboundedSender for WebSocket" → ✅ **Bounded channel (256 buffer)** required
❌ "No max_connections limit" → ✅ **max_connections = 2000** constant required
❌ "gRPC bi-directional streaming from start" → ✅ **Start with unary, measure first**
❌ "Direct PostgreSQL queries for Ghost Mode replay" → ✅ **In-memory ring buffer** required

---

## Concrete Implementation Decisions

### OBS-01: Structured Logging + Distributed Tracing

**Stack:**
```toml
# Rust (add to Cargo.toml)
tracing = "0.1.40"
tracing-subscriber = { version = "0.3.18", features = ["json", "env-filter", "registry"] }
tracing-opentelemetry = "0.22.0"
opentelemetry = "0.21.0"
opentelemetry-otlp = "0.14.0"
opentelemetry-semantic-conventions = "0.14.0"

# Python (add via uv add)
structlog = "24.1.0"
opentelemetry-api = "1.22.0"
opentelemetry-sdk = "1.22.0"
opentelemetry-instrumentation-logging = "0.43b0"
```

**Trace Metadata Type Contract:**
```rust
// rust_control_plane/src/tracing/metadata.rs
use serde::Serialize;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize)]
pub struct TraceMetadata {
    pub trace_id: Uuid,
    pub request_id: Uuid,
    pub user_id: Option<Uuid>,
}

impl Into<Metadata> for TraceMetadata {
    fn into(self) -> Metadata {
        let mut md = Metadata::new();
        md.insert("trace-id", self.trace_id.to_string());
        md.insert("request-id", self.request_id.to_string());
        if let Some(uid) = self.user_id {
            md.insert("user-id", uid.to_string());
        }
        md
    }
}
```

**Axum Middleware for trace_id injection:**
```rust
// rust_control_plane/src/tracing/middleware.rs
use axum::extract::Request;
use uuid::Uuid;

pub async fn inject_trace_middleware(
    req: Request,
    next: Next,
) -> Response {
    let trace_id = Uuid::new_v4();
    let request_id = Uuid::new_v4();

    // Store in request extensions for handlers to access
    req.extensions_mut().insert(TraceMetadata {
        trace_id,
        request_id,
        user_id: None, // Extract from JWT if present
    });

    next(req).await
}
```

**gRPC Interceptor (Condition #4 — specify BEFORE writing code):**
```rust
// rust_control_plane/src/grpc/interceptor.rs
use tonic::Request;
use crate::tracing::metadata::TraceMetadata;

pub struct TraceInterceptor;

impl tonic::service::Interceptor for TraceInterceptor {
    fn call(&mut self, mut req: Request<()>) -> tonic::Status {
        if let Some(metadata) = req.metadata_mut().get("trace-id") {
            // Inject trace_id into gRPC metadata for Python
            req.metadata_mut().insert("trace-id", metadata);
        }
        Ok(req)
    }
}
```

**Python structlog Configuration:**
```python
# apps/api/mastermind_cli/observability/logging.py
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
```

### RTU-01: WebSocket Hub + Ghost Mode (Co-requirement)

**WebSocket Hub with bounded channels (Condition #2):**
```rust
// rust_control_plane/src/websocket/hub.rs
use dashmap::DashMap;
use tokio::sync::{mpsc, broadcast, Mutex};
use std::sync::Arc;
use std::collections::VecDeque;

const MAX_CONNECTIONS: usize = 2000; // Condition #3
const CHANNEL_BUFFER: usize = 256;    // Condition #2

pub struct WebSocketHub {
    // User-specific channels with BOUNDED buffer
    connections: Arc<DashMap<UserId, mpsc::Sender<ClientMessage, CHANNEL_BUFFER>>>,

    // Global broadcast channel
    global_events: broadcast::Sender<SystemEvent>,

    // Ghost Mode buffer (in-memory ring buffer, Condition #6)
    ghost_buffer: Arc<Mutex<VecDeque<StoredEvent>>>,
}

#[derive(Debug, Clone)]
pub enum ClientMessage {
    BrainStarted(BrainStartedEvent),
    BrainCompleted(BrainCompletedEvent),
    BrainFailed(BrainFailedEvent),
    BrainRouted(BrainRoutedEvent),
}

pub struct StoredEvent {
    pub id: Uuid,
    pub event_type: BrainEventType,
    pub payload: JsonValue,
    pub created_at: DateTime<Utc>,
}
```

**Ghost Mode Ring Buffer (Condition #6 — thundering herd mitigation):**
```rust
// rust_control_plane/src/websocket/ghost_mode.rs
use std::collections::VecDeque;
use tokio::sync::Mutex;

const GHOST_BUFFER_SIZE: usize = 100;

pub struct GhostModeBuffer {
    events: Arc<Mutex<VecDeque<StoredEvent>>>,
}

impl GhostModeBuffer {
    pub fn new() -> Self {
        Self {
            events: Arc::new(Mutex::new(VecDeque::with_capacity(GHOST_BUFFER_SIZE))),
        }
    }

    pub fn push(&self, event: StoredEvent) {
        let mut events = self.events.blocking_lock();
        if events.len() >= GHOST_BUFFER_SIZE {
            events.pop_front(); // Remove oldest
        }
        events.push_back(event);
    }

    pub fn replay(&self) -> Vec<StoredEvent> {
        self.events.blocking_lock().iter().cloned().collect()
    }
}
```

**Unary gRPC first (Condition #5 — defer bi-directional streaming):**
```protobuf
// events.proto
syntax = "proto3";

package mastermind.events.v1;

service EventStream {
  // START with unary (Condition #5)
  rpc PublishBrainEvent(BrainEvent) returns (EventAck);

  // TODO: Add streaming when metrics prove unary is bottleneck
  // rpc SubscribeBrainEvents(SubscriptionRequest) returns (stream BrainEvent);
}

message BrainEvent {
  string event_id = 1;
  string trace_id = 2;
  BrainEventType event_type = 3;
  string brain_id = 4;
  string payload_json = 5;
  int64 created_at_unix_ms = 6;
}

message EventAck {
  bool success = 1;
  string error = 2;
}
```

### Health Checks — Liveness vs Readiness

**Liveness Probe (`/health/live`):**
```rust
// rust_control_plane/src/health/live.rs
pub async fn liveness_probe() -> impl IntoResponse {
    // Check Tokio event loop responsiveness
    let start = std::time::Instant::now();
    tokio::task::yield_now().await;
    let elapsed = start.elapsed();

    if elapsed.as_secs() < 1 {
        (StatusCode::OK, json({"status": "alive"}))
    } else {
        (StatusCode::SERVICE_UNAVAILABLE, json({"status": "degraded"}))
    }
}
```

**Readiness Probe (`/health/ready`):**
```rust
// rust_control_plane/src/health/ready.rs
pub async fn readiness_check(
    State(state): State<AppState>,
) -> impl IntoResponse {
    let checks = tokio::join!(
        check_postgres(&state.pool),
        check_grpc_python(),
        // check_redis() // TODO: Phase 16 adds Redis for pub/sub
    );

    let all_healthy = checks.0.is_ok() && checks.1.is_ok();

    if all_healthy {
        (StatusCode::OK, json({"status": "ready"}))
    } else {
        (StatusCode::SERVICE_UNAVAILABLE, json({
            "status": "not_ready",
            "postgres": format!("{:?}", checks.0),
            "grpc_python": format!("{:?}", checks.1),
        }))
    }
}
```

### Prometheus Metrics

**Metrics Endpoint (`/metrics`):**
```rust
// rust_control_plane/src/metrics/prometheus.rs
use prometheus::{Counter, Histogram, Gauge, Registry, TextEncoder};
use lazy_static::lazy_static;
use std::sync::Arc;

lazy_static! {
    static ref REGISTRY: Registry = Registry::new();
    static ref HTTP_REQUESTS_TOTAL: Counter = Counter::new(
        "http_requests_total",
        "Total HTTP requests"
    ).unwrap();
    static ref HTTP_REQUEST_DURATION: Histogram = Histogram::with_registry(
        "http_request_duration_seconds",
        "HTTP request latency",
        REGISTRY.clone()
    ).unwrap();
    static ref WEBSOCKET_CONNECTIONS: Gauge = Gauge::new(
        "websocket_connections_active",
        "Active WebSocket connections"
    ).unwrap();
}

pub async fn metrics_endpoint() -> impl IntoResponse {
    let encoder = TextEncoder::new();
    let metric_families = REGISTRY.gather();
    let mut buffer = Vec::new();
    encoder.encode(&metric_families, &mut buffer).unwrap();

    (
        StatusCode::OK,
        [(header::CONTENT_TYPE, "text/plain; version=0.0.4")],
        buffer,
    )
}
```

---

## Execution Order

1. **16-01:** Structured logging (Rust tracing + Python structlog)
2. **16-02:** Distributed tracing (trace_id propagation, gRPC interceptor)
3. **16-03:** Health checks (liveness + readiness with dependency checks)
4. **16-04:** WebSocket Hub foundation (tokio-tungstenite + bounded channels + max_connections ceiling)
5. **16-05:** Ghost Mode buffer (in-memory ring buffer + replay endpoint)
6. **16-06:** Metrics exposition (Prometheus `/metrics` endpoint)
7. **16-07:** Load testing suite (k6 scripts for 1000 connections)

**Estimated:** 7 plans, ~20-25 tasks, ~12-15 hours

---

## Success Criteria (from Brain #7)

**SLI-1:** Ghost Mode Replay Latency — P95 < 500ms for last 100 events
**SLI-2:** Memory per WS Connection — < 50KB at steady state, total Hub < 100MB at 1000 connections
**SLI-3:** gRPC Trace Propagation Rate — 100% of cross-service requests carry trace_id
**SLI-4:** Connection Rejection — Connections beyond max_connections (2000) receive HTTP 429

---

## Files Modified

- `rust_control_plane/Cargo.toml` — Add tracing, WebSocket, Prometheus deps
- `rust_control_plane/src/main.rs` — Configure tracing subscriber
- `rust_control_plane/src/tracing/` — NEW: metadata, middleware, interceptor
- `rust_control_plane/src/websocket/` — NEW: hub, ghost_mode
- `rust_control_plane/src/health/` — Enhanced: live, ready endpoints
- `rust_control_plane/src/metrics/` — NEW: prometheus integration
- `apps/api/mastermind_cli/observability/` — NEW: logging.py, tracer.py

---

## Next Step

Delegate to GSD planner with this context.
