# gRPC Bridge Design Document

**Phase:** 18 (Multi-channel Gateway)
**Plan:** 18-09 (gRPC Bridge Implementation)
**Date:** 2026-04-11
**Status:** Design Complete

## Overview

This document describes the gRPC communication bridge between the Rust webhook worker (Control Plane) and the Python AI worker (Agent Runtime).

## API Contract

### Service: Worker.ProcessWebhook

**Endpoint:** `mastermind.worker.Worker/ProcessWebhook`
**Request-Response Pattern:** Unary RPC

#### Request Schema (ProcessWebhookRequest)

```protobuf
message ProcessWebhookRequest {
  string trace_id = 1;        // Distributed tracing ID (UUID format)
  string channel = 2;         // Target channel: "whatsapp", "instagram", "email"
  string payload = 3;         // JSON webhook payload (stringified)
  string sender_id = 4;       // Customer identifier (phone number, user ID, email)
  string message_type = 5;    // Message type: "text", "image", "video", "audio", "file"
}
```

**Validation Rules:**
- `trace_id`: Required, must be valid UUID v4 format
- `channel`: Required, must be one of ["whatsapp", "instagram", "email"]
- `payload`: Required, must be valid JSON string
- `sender_id`: Optional, defaults to empty string
- `message_type`: Optional, defaults to "text"

#### Response Schema (ProcessWebhookResponse)

```protobuf
message ProcessWebhookResponse {
  bool success = 1;                    // True if processing succeeded
  string error_message = 2;            // Error details if success=false
  string ai_response = 3;              // Generated AI response text
  string suggested_channel = 4;        // Channel Router's suggested channel
  int64 processing_duration_ms = 5;    // AI processing time in milliseconds
}
```

## Timeout Policy

**AI Processing Timeout:** 5 seconds
**Channel Send Timeout:** 30 seconds
**Total Request Timeout:** 35 seconds

## Retry Policy

**Exponential Backoff:** [1s, 5s, 30s]
- Applied on transient errors
- Max 3 retry attempts before DLQ

## Connection Management

**Max Concurrent Connections:** 5
**Health Check Interval:** 30 seconds
**Reconnect Backoff:** [100ms, 500ms, 1s, 5s]

## Performance Targets

**gRPC Call Latency:** <100ms P95
**AI Processing Latency:** <5s P95
**Channel Send Latency:** <2s P95
**End-to-End Latency:** <30s P95

**Throughput:** 100 webhooks/second per connection

## Error Handling

| gRPC Status | Condition | Retry? |
|-------------|-----------|--------|
| Internal | Database/temporary error | YES (3x) |
| InvalidArgument | Invalid payload | NO |
| Unavailable | Worker down | YES (3x) |
| DeadlineExceeded | Timeout | YES (1x) |

## Implementation Checklist

- [ ] Fix build.rs to compile only worker.proto
- [ ] Create gRPC client module (src/grpc/worker.rs)
- [ ] Add ai_worker_client to WebhookWorker
- [ ] Implement send_to_ai_worker() with gRPC call
- [ ] Generate Python stubs from worker.proto
- [ ] Create Python gRPC server (routers/internal.py)
- [ ] Add delivery status tracking table
- [ ] Record E2E latency after gRPC response
