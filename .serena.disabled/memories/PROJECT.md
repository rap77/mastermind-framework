# Project: MasterMind Framework v3.0

**Repo:** mastermind-framework
**URL:** https://github.com/rap77/mastermind-framework
**Stack:** Rust (Axum + Tokio) + Python 3.14 (uv) + TypeScript (Next.js 16)
**Branch:** master | **Last Tag:** v2.2

## Current Status (2026-04-07)

### v3.0 Milestone: Phase 15 COMPLETE, Phase 16 PLANNED

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 15 | Rust Control Plane | ✅ COMPLETE (4/4 plans) |
| Phase 16 | Observability + Real-time Hub | ✅ PLANNED (7/7 plans) |

### Phase 15: Rust Control Plane — COMPLETE ✅

**Commit:** 9017118
**Duration:** ~10 hours execution
**Tests:** 682 Python + 407 Frontend passing

**Implemented:**
- PostgreSQL 16 + pgvector foundation (7 tables)
- JWT auth + RBAC middleware (2 roles: admin, operator)
- Dual-write migration with Saga pattern
- Event sourcing with immutable `activity_log`
- gRPC client (tonic 0.11) for Python communication
- `tracing` 0.1 + `tracing-subscriber` 0.3 configured

**Brain #7 Validation:** APPROVED (6/6 conditions addressed)

### Phase 16: Observability + Real-time Hub — PLANNED ✅

**Commit:** 9946a14
**Plans:** 7 plans (~12-15 hours estimated)

**Scope:**
- 16-01: Structured logging (Rust tracing + Python structlog)
- 16-02: Distributed tracing (trace_id propagation, gRPC interceptor)
- 16-03: Health checks (liveness + readiness with dependency checks)
- 16-04: WebSocket Hub foundation (bounded channels, max_connections=2000)
- 16-05: Ghost Mode buffer (in-memory ring buffer, replay endpoint)
- 16-06: Metrics exposition (Prometheus `/metrics` endpoint)
- 16-07: Load testing suite (k6 scripts for 1000 connections)

**Brain #7 Validation:** APPROVED_WITH_CONDITIONS (72/100, 6 conditions incorporated)

## Key Architecture Decisions

1. **Rust Control Plane:** 65% of stack (Axum 0.7 + Tokio 1.x)
2. **Python Agent Runtime:** 35% of stack (FastAPI + IA)
3. **TypeScript Frontend:** Fork Paperclip UI (41 pages + 94 components)
4. **Communication:** gRPC/Protobuf between Rust ↔ Python
5. **Observability:** OpenTelemetry + Prometheus + Ghost Mode (WS replay)

## Package Managers (OBLIGATORY)

- **Python:** `uv` siempre (pip/poetry/conda prohibidos)
- **Node.js:** `pnpm` siempre (npm/yarn prohibidos)
- **Rust:** `cargo` estándar

## Development Commands

```bash
# Python runtime (uv)
uv run pytest                    # Run tests from apps/api/
uv sync                          # Sync dependencies
uv add <package>                 # Add dependency

# Node.js (pnpm)
pnpm install                     # Install dependencies
pnpm add <package>               # Add dependency
pnpm dev                         # Dev server

# Git
git tag v0.1.0 -m "description"  # Tag version
```

## Brain-Aware Commands (USE THESE INSTEAD OF gsd:)

| Command | What it does |
|---------|-------------|
| `/mm:new-milestone` | Brain #1 + #7 validate → `/gsd:new-milestone` |
| `/mm:plan-phase N` | 6 domain brains → Brain #7 → `/gsd:plan-phase` |
| `/mm:execute-phase N` | Brain #7 validates → `/gsd:execute-phase` |
| `/mm:complete-phase N` | Execute + auto BRAIN-FEED update |

## Recent Commits

```
9946a14 docs(16): update ROADMAP with Phase 16 plans (7 plans)
3b929c8 docs(16): create Phase 16 plans - Observability + Real-time Hub
9017118 docs(phase-15): complete Rust Control Plane execution
358d29b docs(15-04): complete event sourcing plan + Phase 15 complete
```

## Next Steps

**Recommended:** `/mm:execute-phase 16` — Execute Phase 16 with Brain #7 validation
**Alternative:** `/mm:new-milestone` — Plan next milestone (Phase 17+)
