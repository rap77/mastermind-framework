# gRPC Bridge Design: Rust ↔ Python Worker Communication

## Overview
This document defines the gRPC contract between the Rust control plane (webhook worker) and Python AI processing service. This bridge enables end-to-end webhook processing with proper latency tracking and delivery status updates.

## API Contract

### Service Definition
**Service:** `mastermind.worker.Worker`
**Method:** `ProcessWebhook`
**Purpose:** Process incoming webhooks through AI pipeline and send responses via appropriate channel

### Request Schema

```protobuf
message ProcessWebhookRequest {
  string trace_id = 1;        // Distributed tracing ID (UUID)
  string channel = 2;         // Target channel: "whatsapp", "instagram", "email"
  string payload = 3;         // JSON webhook payload (stringified)
  string sender_id = 4;       // Customer identifier (phone number, user ID, email)
  string message_type = 5;    // Message type: "text", "image", "video", "audio", "file"
}
```

**Validation Rules:**
- `trace_id`: Required, must be valid UUID format
- `channel`: Required, must be one of: ["whatsapp", "instagram", "email"]
- `payload`: Required, must be valid JSON string
- `sender_id`: Optional, defaults to empty string
- `message_type`: Optional, defaults to "text"

### Response Schema

```protobuf
message ProcessWebhookResponse {
  bool success = 1;                    // True if processing succeeded
  string error_message = 2;            // Error details if success=false
  string ai_response = 3;              // Generated AI response text
  string suggested_channel = 4;        // Channel Router's suggested channel
  int64 processing_duration_ms = 5;    // AI processing time in milliseconds
}
```

**Response Cases:**
- **Success:** `success=true`, `ai_response` contains generated message
- **Failure:** `success=false`, `error_message` contains details

## Error Handling

### gRPC Status Code Mapping

| gRPC Status | Condition | Retry Policy | DLQ Eligible |
|-------------|-----------|--------------|--------------|
| `Internal` | Database connection failed | Yes (exponential backoff) | No |
| `InvalidArgument` | Invalid payload format | No | Yes |
| `NotFound` | Message/channel not found | No | Yes |
| `Unavailable` | Python worker down | Yes (exponential backoff) | No |
| `DeadlineExceeded` | AI processing timeout | Yes (longer timeout) | No |
| `PermissionDenied` | API key invalid | No | Yes |
| `ResourceExhausted` | Rate limit hit | Yes (backoff) | No |

### Error Translation: gRPC → Rust Error Types

```rust
pub enum Error {
    GrpcError(String),           // Generic gRPC communication error
    AiProcessingFailed(String),  // AI worker returned success=false
    InvalidPayload(String),      // InvalidArgument → DLQ
    WorkerUnavailable(String),   // Unavailable → Retry
    Timeout(String),             // DeadlineExceeded → Retry
}
```

## Connection Management

### Connection Pooling
- **Max concurrent connections:** 5
- **Connection reuse:** Keep-alive for 60s
- **Connection timeout:** 5s initial handshake

### Health Check
- **Ping interval:** Every 30s
- **Ping timeout:** 5s
- **Failed ping threshold:** 3 consecutive failures → reconnect

### Reconnect Policy
- **Backoff sequence:** [100ms, 500ms, 1s, 5s, 10s]
- **Max retries:** Unlimited (with backoff)
- **Fallback behavior:** If gRPC unavailable after max backoff, queue to DLQ with reason "gRPC_unavailable"

### Fallback Behavior
When gRPC is unavailable:
1. Log warning: "AI worker unavailable, queuing to DLQ"
2. Add event to DLQ table with reason: "gRPC_unavailable"
3. Continue processing next webhook (don't block queue)

## Performance Targets

### Latency Goals
- **gRPC call overhead:** <100ms P95 (network + serialization)
- **AI processing:** <5s P95 (configured timeout)
- **Channel send:** <2s P95 (WhatsApp/Instagram/Email API)
- **Total E2E:** <30s P95 (including all steps)

### Throughput Goals
- **Per connection:** 100 webhooks/sec
- **With 5 connections:** 500 webhooks/sec
- **Burst capacity:** 1000 webhooks/sec (with queue buffering)

### Memory Goals
- **Per connection:** <10MB
- **Total gRPC overhead:** <50MB (5 connections)
- **Message buffer:** 1MB per webhook (payload size limit)

## Timeout Policy

### Request Timeouts
- **AI processing timeout:** 5s (configurable via `AI_WORKER_TIMEOUT`)
- **Channel send timeout:** 30s (WhatsApp/Instagram/Email API SLA)
- **Total webhook timeout:** 35s (AI + channel send)

### Timeout Handling
1. **AI timeout:** Return `DeadlineExceeded`, trigger retry with longer timeout
2. **Channel timeout:** Log error, update delivery status to "failed", don't retry
3. **Total timeout:** Move to DLQ with reason "timeout"

## Retry Policy

### Transient Errors (Retry)
- `Internal` (database errors)
- `Unavailable` (worker down)
- `ResourceExhausted` (rate limits)
- `DeadlineExceeded` (timeout)

### Backoff Sequence
- **Attempt 1:** Immediate
- **Attempt 2:** 1s delay
- **Attempt 3:** 5s delay
- **Attempt 4:** 30s delay
- **Attempt 5+:** 60s delay

### Permanent Errors (No Retry → DLQ)
- `InvalidArgument` (malformed payload)
- `NotFound` (missing channel/config)
- `PermissionDenied` (auth errors)
- `AlreadyExists` (duplicate message ID)

## Security Considerations

### Authentication
- **Development:** No authentication (localhost only)
- **Production:** mTLS certificates between Rust and Python services

### Authorization
- **Rust → Python:** No authorization needed (internal service)
- **Python → External APIs:** API keys in environment variables

### Payload Validation
- **Max payload size:** 1MB
- **Required fields:** `trace_id`, `channel`, `payload`
- **Channel whitelist:** ["whatsapp", "instagram", "email"]

## Monitoring & Observability

### Metrics to Track
- `grpc_client_latency_seconds{channel, status}` - gRPC call latency
- `grpc_client_requests_total{channel, status}` - Request count by status
- `grpc_client_connections_current` - Active connection count
- `grpc_client_retries_total{reason}` - Retry count by reason

### Logging
- **Request:** Log `trace_id`, `channel`, `payload_size` at INFO level
- **Response:** Log `success`, `processing_duration_ms` at INFO level
- **Errors:** Log full error details at ERROR level
- **Retries:** Log retry attempt number and backoff duration at WARN level

### Distributed Tracing
- **Trace ID propagation:** Pass `trace_id` from webhook → gRPC → Python
- **Span naming:** "grpc_client.process_webhook"
- **Span tags:** `channel`, `message_type`, `success`

## Testing Strategy

### Unit Tests
- Mock gRPC client responses
- Test error handling for each status code
- Verify retry logic with backoff

### Integration Tests
- Start real Python gRPC server
- Send test webhooks from Rust worker
- Verify end-to-end flow

### Load Tests
- 100 concurrent webhooks
- Measure P50/P95/P99 latency
- Verify connection pooling behavior

## Configuration

### Environment Variables
- `AI_WORKER_ADDRESS`: gRPC server address (default: "http://127.0.0.1:50051")
- `AI_WORKER_TIMEOUT`: Request timeout in seconds (default: 5)
- `GRPC_MAX_CONNECTIONS`: Max connection pool size (default: 5)
- `GRPC_HEALTH_CHECK_INTERVAL`: Health check interval in seconds (default: 30)

### Feature Flags
- `GRPC_ENABLED`: Enable/disable gRPC bridge (default: true)
- `GRPC_FALLBACK_TO_DLQ`: Queue to DLQ when unavailable (default: true)

## Implementation Checklist

- [ ] Create Protobuf contract (`proto/worker.proto`)
- [ ] Generate Rust client code (`tonic-build`)
- [ ] Implement `AiWorkerClient` in Rust
- [ ] Update `send_to_ai_worker()` to use gRPC client
- [ ] Generate Python server code (`grpcio-tools`)
- [ ] Implement `WorkerService` in Python
- [ ] Add gRPC server to FastAPI startup
- [ ] Integrate with channel senders (WhatsApp/Instagram/Email)
- [ ] Add delivery status tracking table
- [ ] Update latency measurement (after AI processing)
- [ ] Add integration tests
- [ ] Add metrics and logging
- [ ] Document configuration and deployment

## References
- [gRPC Rust Documentation](https://docs.rs/tonic/latest/tonic/)
- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
- [Protobuf Language Guide](https://protobuf.dev/programming-guides/proto3/)
