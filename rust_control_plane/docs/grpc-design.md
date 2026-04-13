# gRPC Design: Rust ↔ Python AI Worker Bridge

## Overview

gRPC service for webhook processing between Rust control plane and Python AI worker. Enables end-to-end message flow from webhook receipt → AI processing → channel-specific delivery.

## API Contract

### Service: Worker.ProcessWebhook

**Request**: ProcessWebhookRequest
```protobuf
string trace_id           # Distributed trace ID (for observability)
string channel            # "whatsapp" | "instagram" | "email"
string payload            # JSON webhook payload
string sender_id          # Customer/account identifier
string message_type       # "text" | "image" | "video" | etc.
```

**Response**: ProcessWebhookResponse
```protobuf
bool success                      # Success indicator
string error_message              # Error details if success=false
string ai_response                # Generated response text
string suggested_channel          # Channel Router recommendation
int64 processing_duration_ms      # Round-trip time in ms
```

### Timeout Policy

- AI processing timeout: 5s (reasonable for LLM inference)
- Channel send timeout: 30s (includes external API call)
- gRPC deadline: 35s total (5s AI + 30s channel)

### Retry Policy

**Transient Errors** (RETRY):
- Unavailable: Python worker down → exponential backoff [100ms, 500ms, 1s, 5s]
- DeadlineExceeded: AI timeout → retry with longer timeout
- Internal: Database connection failure → retry 3 times

**Non-Transient Errors** (NO RETRY → DLQ):
- InvalidArgument: Malformed payload → immediate DLQ
- PermissionDenied: Auth failure → immediate DLQ
- NotFound: Customer not found → immediate DLQ

## Error Handling

### gRPC Status Code Mapping

| gRPC Status | Meaning | Handler |
|-------------|---------|---------|
| OK | Success | Continue to channel send |
| InvalidArgument | Malformed request | DLQ (no retry) |
| Internal | Server error (DB, etc) | Retry with backoff |
| Unavailable | Python worker down | Retry with exponential backoff |
| DeadlineExceeded | AI timeout | Retry with longer timeout |
| PermissionDenied | Auth issue | DLQ (no retry) |

### Error Translation

```rust
// Rust error handling in client
match grpc_response {
    Ok(response) if response.success => {
        // Success: continue to channel send
    }
    Ok(response) => {
        // AI processing failed with reason in response.error_message
        // Determine if transient or permanent based on error content
    }
    Err(tonic::Status::Unavailable(_)) => {
        // Transient: retry with exponential backoff
    }
    Err(tonic::Status::DeadlineExceeded(_)) => {
        // Transient: retry with longer deadline
    }
    Err(tonic::Status::InvalidArgument(_)) => {
        // Permanent: send to DLQ
    }
    Err(e) => {
        // Other errors: log and DLQ
    }
}
```

## Connection Management

### Connection Pooling

- Max concurrent connections: 5
- Connection reuse: Keep-alive every 30s
- Connection cleanup: Automatic on drop

### Health Check

- Ping interval: 30s
- Timeout: 5s
- Strategy: HTTP/2 PING frame (automatic with tonic)

### Reconnect Policy

If connection fails:
1. Initial retry: 100ms
2. Next retries: 500ms, 1s, 5s (capped)
3. Max retries: 5
4. Then: fallback to DLQ with "worker_unavailable" reason

### Fallback Behavior

If gRPC unavailable:
- Queue webhook to DLQ immediately with reason="worker_unavailable"
- Update messages.status = "failed"
- Alert: "AI worker gRPC endpoint unreachable"
- Recovery: Automated retry when worker comes back online

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| gRPC call latency (P95) | <100ms | Excludes AI processing |
| Throughput | 100 webhooks/sec | Per single connection |
| Memory per connection | <10MB | Peak during processing |
| E2E latency (P95) | <30s | Including AI processing |

## Implementation Details

### Rust Client (src/grpc/mod.rs)

```rust
pub struct AiWorkerClient {
    client: WorkerClient<Channel>,
    config: GrpcConfig,
}

impl AiWorkerClient {
    pub async fn new(addr: &str) -> Result<Self>
    pub async fn process_webhook(&self, req: ProcessWebhookRequest) -> Result<ProcessWebhookResponse>
}
```

### Python Server (apps/api/routers/internal.py)

```python
class WorkerService(WorkerBase):
    async def ProcessWebhook(self, stream):
        req = await stream.recv()
        # Route to channel sender based on req.channel
        # Return ProcessWebhookResponse
```

### Initialization

**Rust (main.rs)**:
- Initialize gRPC client with address from env: PYTHON_AI_WORKER_ADDR (default: http://127.0.0.1:50051)
- Pass to WebhookWorker during creation
- Error: Fall back to DLQ if connection fails on startup

**Python (app.py)**:
- Start gRPC server on port 50051
- Register WorkerService handler
- Log startup message: "gRPC server listening on 0.0.0.0:50051"

## Observability

### Metrics

- `grpc_worker_calls_total{status,channel}`: Counter of gRPC calls
- `grpc_worker_latency_seconds{quantile,channel}`: Latency histogram
- `grpc_worker_errors_total{error_type,channel}`: Error counter

### Traces

- Span name: "worker.ProcessWebhook"
- Attributes: trace_id, channel, sender_id, message_type
- Status: OK | ERROR (with error code)

### Logs

- [INFO] "gRPC ProcessWebhook called" (trace_id, channel)
- [WARN] "gRPC call failed" (trace_id, error)
- [ERROR] "AI worker unavailable" (with retry backoff info)

## Future Enhancements

- Connection pooling with connection reuse
- Load balancing across multiple Python workers
- Circuit breaker pattern for failing workers
- Distributed tracing integration with OpenTelemetry
- Custom compression for large payloads
