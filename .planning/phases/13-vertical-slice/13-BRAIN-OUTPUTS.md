# Phase 13 — Domain Brain Outputs
> Generated: 2026-04-05T15:00:00Z
> Status: complete

## Brain #5 — Backend Architecture

### 1. API Path Selection: `POST /api/tasks/auto`

`/tasks/auto` is superior to `/tasks/create` because FlowDetector forces a bidirectional gRPC pattern (Python returns `detected_flow`). This exercises 5 layers: JWT auth → database → gRPC → background orchestration → WebSocket notification. `/tasks/create` only touches 3 layers.

### 2. Proto Contract: `mastermind.v1.BrainRuntime`

```protobuf
package mastermind.v1;

service BrainRuntime {
  rpc DispatchTask(DispatchTaskRequest) returns (DispatchTaskResponse);
}

message DispatchTaskRequest {
  string task_id = 1;
  string brain_id = 2;
  string brief = 3;
  map<string, string> context = 4;
}

message DispatchTaskResponse {
  string task_id = 1;
  string status = 2;
  string detected_flow = 3;
  int64 accepted_at_unix_ms = 4;  // latency measurement
}
```

Single RPC, structured fields (no string blobs), `accepted_at_unix_ms` for latency measurement.

### 3. Rust Project Structure

```
apps/control-plane/         ← Rust service (single crate, NOT workspace for VS)
  src/
    main.rs                 ← Axum server + tonic client startup
    handlers/
      tasks.rs              ← POST /api/tasks/auto handler
    grpc/
      client.rs             ← tonic client wrapper
    config.rs               ← env vars + settings
  proto/                     ← symlink or reference to root proto/
  Cargo.toml
  build.rs                   ← tonic-build codegen

proto/                       ← MONOREPO ROOT (single source of truth)
  mastermind/
    v1/
      brain_runtime.proto
  buf.yaml
  buf.gen.yaml
```

### 4. PostgreSQL Strategy — CRITICAL CORRECTION

**Phase 13 does NOT implement dual-write.** Rust writes only to PostgreSQL. Python's 631 tests stay on SQLite. Only the `executions` table exists in PostgreSQL for Phase 13. Auth tables migrate in Phase 15.

### 5. Rust Velocity Protocol

3 dimensions measured at midpoint:
- **Runtime:** p50/p99 latency for the vertical slice endpoint (Rust vs Python)
- **Dev cycle:** Edit-build-test cycle time (cargo test vs pytest)
- **LOC:** Lines of code for equivalent functionality

Escape hatch triggers if ANY dimension < 0.5x Python. Baseline measured BEFORE starting against existing Python endpoint.

---

## Brain #4 — Frontend Integration

### 1. API Path: `POST /api/tasks/auto` via Server Action

Task creation goes through a Server Action (`actions/tasks.ts`), NOT a Route Handler or TanStack Query. The vertical slice swaps ONE line in ONE file: the Server Action changes its fetch target from Python FastAPI to Rust Axum. The rest is backend work.

`GET /api/brains` would be WRONG — it only proves you can change a URL, not that the architecture works.

### 2. TypeScript Types: Coexistence, Not Replacement

For the vertical slice, auto-generated proto types go in `apps/web/src/proto/`. They coexist with existing hand-written types. Only the vertical slice endpoint uses proto-generated types. No query hooks change. No stores change.

### 3. Rust Gateway URL Configuration

```typescript
// apps/web/src/actions/tasks.ts
const API_BASE = process.env.CONTROL_PLANE_URL || 'http://localhost:8001';
```

Single environment variable. Falls back to existing Python URL for non-VS endpoints.

### 4. Frontend Testing: Server Action Integration Test

One vitest integration test that mocks the Rust gateway response, verifies the Server Action constructs the correct request and handles the response. No E2E needed for VS — the smoke test (Layer 5) covers the full chain.

### 5. Server Components vs Client Components

Task creation uses Server Actions (Server Components). The Server Action runs on the server, calls Rust, returns to the client. This is the CORRECT pattern because:
- JWT in httpOnly cookies only accessible server-side
- No CORS issues (server-to-server call)
- Already the existing pattern in the codebase

---

## Brain #6 — QA/DevOps Testing Strategy

### 1. Five Test Layers (ordered by value)

| Layer | What | Tool | Target |
|-------|------|------|--------|
| 1. Rust Unit Tests | Handler logic, gRPC client, domain types | `cargo test` | 20-30 |
| 2. Proto Contract Tests | Serialization round-trips, field name parity | `cargo test` + `pytest` | 5-8 |
| 3. gRPC Integration Tests | tonic ↔ grpclib wire format | Docker Compose + `pytest` | 3-5 |
| 4. PostgreSQL Parity Tests | Same ops on SQLite + PostgreSQL | `pytest` parametrized | 10-15 |
| 5. E2E Smoke Test | Full chain: Next.js → Rust → gRPC → Python → UI | Docker Compose + script | 1-2 |

### 2. PostgreSQL Migration — DatabaseConnection Abstraction

**CRITICAL:** Zero SQLAlchemy, Zero Alembic, Zero ORM in the project. All DDL is raw SQL in `DatabaseConnection` methods. Strategy: extract `DatabaseConnection` into a protocol/ABC with two implementations: `SQLiteConnection` and `PostgreSQLConnection`.

**SQLite vs PostgreSQL divergence points (WILL break if not handled):**
- TIMESTAMP: SQLite stores TEXT, PostgreSQL has native type
- Boolean: SQLite 0/1 works as boolean, PostgreSQL strict BOOLEAN
- JSON: SQLite TEXT, PostgreSQL JSONB (loses indexing with TEXT)
- Safe: UUID TEXT PRIMARY KEY, no AUTOINCREMENT used

### 3. Proto Sync CI Gate

```yaml
proto-sync:
  name: Proto Sync Gate
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: bufbuild/buf-setup-action@v1
    - run: buf lint proto/
    - run: buf generate proto/ --template buf.gen.yaml
    - run: git diff --exit-code apps/api/proto/ apps/rust/src/proto/ apps/web/src/proto/
```

Runs on every PR. Catches: invalid proto syntax, generated code drift, direct edits to generated code.

### 4. Dual-Write: NOT Phase 13

Phase 13 proves PostgreSQL works alongside SQLite. Phase 15 implements dual-write. Phase 13 scope: write to PostgreSQL, read from PostgreSQL, verify parity with SQLite via separate test directory.

### 5. Rust Velocity Measurement

| Metric | Python Baseline | Rust | Escape Hatch Trigger |
|--------|----------------|------|---------------------|
| Time to implement | TBD | TBD | > 2.0x wall-clock |
| LOC (handler) | TBD | TBD | > 1.5x |
| LOC (tests) | TBD | TBD | > 2.0x |
| Test cycle time | TBD | TBD | > 2.0x |

Record at: `.planning/phases/13-vertical-slice/velocity-measurements.md`

### 6. Pre-Requisites Before Writing Rust

1. `buf` CLI installed (`brew install bufbuild/buf/buf`)
2. `protoc` available
3. PostgreSQL 16 in Docker Compose
4. `asyncpg` in `apps/api/pyproject.toml`
5. `testcontainers-postgres` in dev dependencies
6. `proto/` directory at project root with `buf.yaml`, `buf.gen.yaml`, first `.proto`
7. `apps/control-plane/` initialized with `cargo init`

### 7. Test Count Impact

- Existing: 631 backend + 407 frontend = 1038 (ZERO failures)
- After Phase 13: ~654 backend + 407 frontend + ~25 Rust = ~1086 total
- ZERO impact on existing 1038 tests (all stay on SQLite)

## Dispatch Meta

| Property | Value |
|----------|-------|
| Total brains dispatched | 3 |
| All returned successfully | yes |
| Brains consulted | #4 Frontend, #5 Backend, #6 QA |
