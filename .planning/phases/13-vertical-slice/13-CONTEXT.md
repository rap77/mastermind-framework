# Phase 13: Vertical Slice — Brain-Informed Context

> Generated: 2026-04-05 after Brain #4 + #5 + #6 consultation + Brain #7 evaluation
> Brain #7 verdict: APPROVED_WITH_CONDITIONS (72/100)

## Architecture Decisions (Brain-Validated)

### AD-01: API Path = `POST /api/tasks/auto`
- **Why:** FlowDetector forces bidirectional gRPC pattern, exercises 5 layers (JWT → DB → gRPC → orchestration → WS)
- **Brain #5 recommendation:** Superior to `/tasks/create` which only touches 3 layers
- **Brain #7 flag:** The "one line swap" is an API CONTRACT CHANGE, not a URL change. `/api/tasks` uses `{ brief }` body, `/api/tasks/auto` uses `AutoTaskRequest`. Must change URL + request schema + response handling.

### AD-02: Proto Package = `mastermind.v1.BrainRuntime`
- Single RPC: `DispatchTask(DispatchTaskRequest) → DispatchTaskResponse`
- `accepted_at_unix_ms` field for latency measurement
- Generated code is READ-ONLY — never edit directly

### AD-03: Rust Location = `apps/control-plane/`
- Single crate (NOT workspace for VS — workspace decomposition is Phase 15)
- `proto/` directory at monorepo root (single source of truth)
- `build.rs` uses `tonic-build` for Rust codegen

### AD-04: Database = PostgreSQL only for Rust
- **Phase 13 scope:** Only `executions` table in PostgreSQL. Python stays on SQLite.
- **Phase 15 scope:** Dual-write, auth tables migration, full PostgreSQL migration
- 631 existing Python tests continue on `:memory:` SQLite. Zero modifications.
- New PostgreSQL tests in separate `tests/postgres/` directory.

### AD-05: Environment Variable = UNIFY FIRST
- **Brain #7 BLOCKER:** Codebase has TWO names already (`FASTAPI_URL` + `API_URL` + 15 references)
- Pick ONE name, migrate ALL 15 references before any Rust code
- New env var: `CONTROL_PLANE_URL` for Rust gateway, `AGENT_RUNTIME_URL` for Python
- Docker Compose uses these canonical names

### AD-06: Frontend Integration = Server Action swap
- ONE file changes: `apps/web/src/app/actions/tasks.ts`
- Server Action changes fetch target from Python to Rust via env var
- TypeScript proto types coexist in `apps/web/src/proto/` (NOT replacing hand-written types yet)
- JWT in httpOnly cookies stays server-side only

## Test Strategy (5 Layers)

| Layer | What | Count | Runs on |
|-------|------|-------|---------|
| 1. Rust Unit | Handler logic, gRPC client, domain types | 20-30 | `cargo test` |
| 2. Proto Contract | Serialization round-trips, field parity | 5-8 | `cargo test` + `pytest` |
| 3. gRPC Integration | tonic ↔ grpclib wire format | 3-5 | Docker Compose only |
| 4. PostgreSQL Parity | Same ops SQLite + PostgreSQL | 10-15 | `pytest tests/postgres/` |
| 5. E2E Smoke | Full chain: Next.js → Rust → gRPC → Python → UI | 1-2 | Docker Compose only |

**Total after Phase 13:** ~1086 tests (1038 existing + 48 new). Zero regressions.

## Rust Velocity Protocol

| Metric | Python Baseline | Rust | Escape Hatch Trigger |
|--------|----------------|------|---------------------|
| Time to implement | Measure first | TBD | > 2.0x wall-clock |
| LOC (handler) | Measure first | TBD | > 1.5x |
| Test cycle time | Measure first | TBD | > 2.0x |

- **When to measure:** At Phase 13 midpoint (after VS-01 implementation)
- **Baseline measured BEFORE starting** against existing Python endpoint
- **Escape hatch:** Rust only for WebSocket Hub + Adapter Registry
- **Record at:** `.planning/phases/13-vertical-slice/velocity-measurements.md`

## Brain #7 Conditions (ALL non-negotiable)

1. **[BLOCKER] Configuration unification** — Pick ONE env var name, migrate ALL 15 references. Do NOT ship with 3 names.
2. **[BLOCKER] Pre-requisite setup time-boxed** — 1-2 days max for toolchain (rustup, cargo, buf, protoc, PostgreSQL Docker). If > 2 days, that IS a data point for Rust Velocity.
3. **[CONDITION] Rollback plan** — Documented BEFORE first line of Rust. Which files/directories get deleted if escape hatch triggers.
4. **[CONDITION] Local boot time SLI** — Measure current 2-service baseline. Target ≤ 90s for 4 services.
5. **[CONDITION] Velocity Protocol** — Brain #6's 4 metrics with Brain #5's 0.5x trigger for runtime/dev cycle, 2.0x for LOC.

## Brain #7 SLIs (System-Level Indicators)

- **Local Boot Time:** `docker compose up -d` → all services healthy. Target ≤ 90s for 4 services.
- **Time to First Green:** From `cargo init` to first passing gRPC round-trip test. Target ≤ 3 working days.

## Proto Sync CI Gate

```yaml
proto-sync:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: bufbuild/buf-setup-action@v1
    - run: buf lint proto/
    - run: buf generate proto/ --template buf.gen.yaml
    - run: git diff --exit-code apps/api/proto/ apps/control-plane/src/proto/ apps/web/src/proto/
```

Runs on every PR. No exceptions.

## Pre-Requisites (Before Any Rust Code)

1. `buf` CLI installed: `brew install bufbuild/buf/buf`
2. `protoc` available (comes with `buf`)
3. PostgreSQL 16 in Docker Compose (new service in `docker-compose.yml`)
4. `asyncpg` added to `apps/api/pyproject.toml`
5. `testcontainers-postgres` in dev dependencies
6. `proto/` directory at project root with `buf.yaml`, `buf.gen.yaml`, first `.proto`
7. `apps/control-plane/` initialized with `cargo init`
8. Environment variables unified (AD-05) — BLOCKER resolved first
9. Rollback plan documented — CONDITION resolved first
10. Local boot time baseline measured — CONDITION resolved first

## Rollback Plan

If Rust escape hatch triggers or Phase 13 proves non-viable:

| Item | Action | Keep/Delete |
|------|--------|-------------|
| `apps/control-plane/` | Delete entirely | DELETE |
| `proto/` | Keep `.proto` files (useful for documentation) | KEEP |
| Generated proto code | Delete all 3 targets | DELETE |
| PostgreSQL Docker service | Keep if Phase 14 needs it, delete otherwise | CONDITIONAL |
| PostgreSQL parity tests | Keep (validates future migration) | KEEP |
| `asyncpg` dependency | Keep if Phase 14 proceeds | CONDITIONAL |
| Env var unification | KEEP — this is cleanup regardless | KEEP |
| Next.js changes | Revert Server Action to Python direct | REVERT |

## Files to Create/Modify

### NEW files:
- `proto/mastermind/v1/brain_runtime.proto`
- `proto/buf.yaml`
- `proto/buf.gen.yaml`
- `apps/control-plane/Cargo.toml`
- `apps/control-plane/build.rs`
- `apps/control-plane/src/main.rs`
- `apps/control-plane/src/handlers/tasks.rs`
- `apps/control-plane/src/grpc/client.rs`
- `apps/control-plane/src/config.rs`
- `apps/api/mastermind_cli/proto/` (generated Python types)
- `apps/web/src/proto/` (generated TypeScript types)
- `apps/api/tests/postgres/` (PostgreSQL parity tests)
- `apps/api/tests/proto/` (proto contract tests)

### MODIFIED files:
- `docker-compose.yml` (add control-plane + postgres services)
- `apps/web/src/app/actions/tasks.ts` (swap fetch target)
- `apps/api/pyproject.toml` (add asyncpg, grpclib)
- `.github/workflows/ci.yml` (add proto-sync job, Rust test job, PostgreSQL service)
- `.pre-commit-config.yaml` (add proto-sync hook)
- `.env.example` (add CONTROL_PLANE_URL, AGENT_RUNTIME_URL)
