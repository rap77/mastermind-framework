# Load Testing Guide — Phase 16 Plan 07

## Prerequisites Installation

### 1. Install protoc (protobuf compiler)
```bash
sudo apt-get install protobuf-compiler
# OR
sudo snap install protobuf
```

### 2. Install k6 (load testing tool)
```bash
sudo snap install k6
# OR
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### 3. Build Rust Control Plane with gRPC
```bash
cd /home/rpadron/proy/mastermind/rust_control_plane
cargo build
```

## Running Load Tests

### 1. Start Rust Control Plane
```bash
cd /home/rpadron/proy/mastermind/rust_control_plane
cargo run
```

### 2. Run k6 WebSocket Load Test (1000 connections)
```bash
cd /home/rpadron/proy/mastermind/rust_control_plane/tests
k6 run k6-websocket-load.js
```

**Expected Output:**
- 1000 concurrent connections established
- P95 replay latency < 500ms (SLI-1)
- < 1% connection errors
- 99%+ trace_id presence (SLI-3)

### 3. Run k6 Connection Limit Test (SLI-4)
```bash
cd /home/rpadron/proy/mastermind/rust_control_plane/tests
k6 run k6-connection-limit.js
```

**Expected Output:**
- First 2000 connections: Success
- Connections 2001+: HTTP 429 errors

### 4. Run Rust Integration Tests
```bash
cd /home/rpadron/proy/mastermind/rust_control_plane
cargo test --test load_test -- --nocapture
```

**Tests:**
- `ghost_mode_replay_p95_latency`: Validates SLI-1
- `memory_per_connection`: Validates SLI-2
- `trace_propagation_100_percent`: Validates SLI-3
- `connection_limit_429`: Validates SLI-4

### 5. Run Python WebSocket Tests
```bash
cd /home/rpadron/proy/mastermind/apps/api
uv run pytest tests/test_websocket_events.py -v -s
```

### 6. Verify Prometheus Metrics
```bash
curl http://localhost:8080/metrics
```

**Expected Metrics:**
- `websocket_connections_active`: ~1000 during load test
- `http_requests_total`: Counter for all HTTP requests
- `http_request_duration_seconds`: Histogram with P95 < 500ms for replay endpoint

## SLI Validation Checklist

- [ ] **SLI-1**: Ghost Mode Replay P95 Latency < 500ms
  - k6: `replay_latency{p(95)} < 500`
  - Rust test: `ghost_mode_replay_p95_latency` passes

- [ ] **SLI-2**: Memory per Connection < 50KB
  - Rust test: `memory_per_connection` passes
  - Total Hub < 100MB at 1000 connections

- [ ] **SLI-3**: 100% trace_id Propagation
  - k6: `trace_id_presence{rate} > 0.99`
  - Python test: `test_websocket_trace_id_propagation` passes

- [ ] **SLI-4**: Connection Rejection Beyond 2000
  - k6: `connection_429{rate} > 0.05` after 2000 connections
  - Rust test: `connection_limit_429` passes

## Troubleshooting

### protoc not found
```bash
# Install protobuf compiler
sudo apt-get install protobuf-compiler
```

### k6 not found
```bash
# Install k6
sudo snap install k6
```

### Rust build fails
```bash
# Clean and rebuild
cd /home/rpadron/proy/mastermind/rust_control_plane
cargo clean
cargo build
```

### WebSocket connection refused
```bash
# Ensure Rust control plane is running
cd /home/rpadron/proy/mastermind/rust_control_plane
cargo run
```

### Python tests fail with ImportError
```bash
# Install dependencies
cd /home/rpadron/proy/mastermind/apps/api
uv add websockets pytest pytest-asyncio
```

## Interpreting Results

### k6 Output
- `replay_latency{p(95)}`: Should be < 500ms
- `connection_errors{rate}`: Should be < 0.01 (1%)
- `trace_id_presence{rate}`: Should be > 0.99 (99%)

### Cargo Test Output
- All 4 SLI tests should pass
- Memory per connection should be < 50KB
- P95 latency should be < 500ms

### Prometheus Metrics
- `websocket_connections_active`: Should peak at 1000
- `http_request_duration_seconds_bucket{le="0.5"}`: Should have high count for replay endpoint
