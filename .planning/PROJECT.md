# MasterMind Framework

## What This Is

A cognitive architecture framework for building specialized AI-powered solutions using expert "brains" — distilled knowledge from world-class geniuses organized by niche. v2.0 shipped a production-ready platform: parallel brain execution, full type safety, and a FastAPI web dashboard with JWT auth, WebSocket real-time updates, and Experience Store for v3.0 ML foundations.

## Core Value

**Expert AI collaboration that scales.** Multiple specialized brains working in parallel on complex problems — faster, safer, and more reliably than any single brain alone. 4.65x speedup validated, 467 tests passing, production-hardened with CI/CD and Docker.

## Current Milestone: v2.1 War Room Frontend

**Goal:** Replace the Alpine.js/HTMX dashboard with a Next.js 16 production frontend — a real-time "war room" for orchestrating AI brains visually.

**Target features:**
- Command Center: brief input (Raycast-style) + Bento Grid showing live status of all 24 brains
- The Nexus: real-time DAG visualization with React Flow (replaces D3.js)
- Strategy Vault: results and generated outputs management
- Engine Room: structured logs, API key management, brain YAML config
- WebSocket Dispatcher: centralized WS connection via Zustand store (single connection, per-component subscriptions)

## Current State (v2.0.0 → v2.1 in progress)

- **Python:** 14,275 LOC across `apps/api/mastermind_cli/`
- **Brains:** 24 active (7 Software Dev + 16 Marketing + 1 Master Interviewer)
- **Tests:** 292 unit tests passing (apps/api), 0 failed
- **CI:** 3-tier pipeline (typecheck → tests → semantic) on GitHub Actions
- **Docker:** Multi-stage build, `docker compose up -d` → api:8000, web:3000
- **Auth:** JWT (30min) + refresh rotation (24h), API Keys for CLI access
- **DB:** SQLite WAL mode, aiosqlite, 0.39ms status queries
- **Monorepo:** apps/api/ (Python FastAPI) + apps/web/ (Next.js 16 placeholder)
- **Tag:** v2.0.0 on `master`

## Requirements

### Validated

- ✓ CLI orchestration engine (sequential) — v1.0
- ✓ 23 brains across 2 niches (Software Dev, Marketing) — v1.3.0
- ✓ Brain #8 (Master Interviewer) for discovery — v1.1.0
- ✓ NotebookLM integration for knowledge retrieval — v1.0
- ✓ E2E testing framework — v1.3.0
- ✓ Memory & Learning system — v1.1.0
- ✓ **Type Safety** (TS-01 through TS-07) — Pydantic v2, mypy strict, 0 errors — v2.0
- ✓ **Parallel Execution** (PAR-01 through PAR-09) — DAG, asyncio.TaskGroup, 4.65x speedup — v2.0
- ✓ **Web UI Platform** (UI-01 through UI-10) — FastAPI, JWT, WebSocket, D3.js DAG graph — v2.0
- ✓ **Architecture Foundation** (ARCH-01 through ARCH-05) — ExperienceRecord, BrainMessage protocol — v2.0
- ✓ **Backward Compatibility** (BC-01 through BC-05) — 24 brains, v1.3.0 CLI intact — v2.0
- ✓ **Performance** (PERF-01 through PERF-04) — 4.65x speedup, 0.39ms queries — v2.0
- ✓ **Testing** (TEST-01 through TEST-05) — 467 tests, mypy CI, E2E web UI — v2.0

### Active (v2.1 — War Room Frontend)

- [ ] **Frontend foundation** — Next.js 16 + React 19 + TypeScript + Tailwind 4 initialized in apps/web/
- [ ] **Command Center** — Brief input (Raycast-style) + Magic UI Bento Grid with live brain status
- [ ] **The Nexus** — Real-time DAG with React Flow, nodes illuminate on brain_step_completed events
- [ ] **Strategy Vault** — Results and generated outputs display
- [ ] **Engine Room** — Structured logs viewer, API key management, brain YAML config
- [ ] **WebSocket Dispatcher** — Centralized WS store (Zustand), per-component event subscriptions

### Deferred (v2.2+)

- Production hardening: HTTPS+nginx, rate limiting, MM_SECRET_KEY mandatory, session cleanup
- Semantic routing: replace FlowDetector keyword matching with Claude classifier
- Trufflehog secret scanner in CI
- Docker image push to registry
- Production monitoring and alerting

### Out of Scope

- **Machine learning auto-improvement** — v3.0+ (requires R&D)
- **Full RAG system with vector DB** — v3.0+ (PostgreSQL + pgvector/qdrant)
- **Mobile apps** — Web-first, mobile responsive only
- **Real-time collaborative editing** — v3.0+
- **Multi-tenant SaaS** — Single-tenant deployment only for v2.x
- **Celery/RQ task queues** — asyncio sufficient for single-host

## Context

**Stack:** Python 3.14 (uv), FastAPI, aiosqlite, Pydantic v2, mypy strict, pytest, Docker, GitHub Actions

**Architecture decisions:**
- StatelessCoordinator (Pure Function Architecture): per-request instances, no shared state
- JWT + refresh rotation: stateless, API-friendly, jti for collision prevention
- SQLite WAL over PostgreSQL: no infrastructure dependency for single-host
- sentence-transformers (local): no API cost, runs in CI for semantic regression tests
- HTMX/Alpine.js over React: no build step, SSR-friendly (v2.0 — replaced in v2.1)
- **Next.js 16 + React 19** for v2.1 frontend: Server Components for data, Client Components for real-time
- **React Flow** for DAG visualization: replaces D3.js — better React integration, built-in interactivity
- **Zustand** for WebSocket dispatcher: single WS connection shared across all components
- **shadcn/ui + Magic UI**: shadcn for structure, Magic UI for animated "wow" moments (Bento Grid)

**Technical debt carried into v2.1:**
- SECRET_KEY hardcoded (TODO: load from ENV_VAR)
- YAML export implementation incomplete
- 3 coordinator tests with timestamp comparison flakiness (non-critical)
- `--parallel` flag missing in `orchestrate run` CLI

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| **Include UI in v2.0** | End users can't use CLI; agencies need client-facing interface | ✅ Shipped — FastAPI + HTMX/Alpine.js |
| **Parallel before ML** | Immediate benefit for all users; ML is R&D heavy | ✅ 4.65x speedup validated |
| **Type safety with Pydantic v2** | Validation + JSON serialization + IDE support | ✅ 0 mypy errors, 0 Pyright errors |
| **Web dashboard over desktop** | Cross-platform, easier deployment, browser ubiquity | ✅ Docker → localhost:8000 |
| **Foundation for shared memory** | Design for v3.0 without building full ML | ✅ ExperienceRecord, BrainMessage protocol |
| **CLI alongside UI** | Power users prefer CLI; UI is optional | ✅ Both maintained |
| **SQLite over PostgreSQL** | No infra dependency, sufficient for single-host | ✅ 0.39ms queries, WAL mode |
| **StatelessCoordinator** | Pure Function Architecture → multi-user safe, simpler | ✅ Per-request instances, no race conditions |
| **JWT + refresh rotation** | Stateless, API + web compatible, replay prevention | ✅ UAT: refresh rotation tested 12/12 |
| **HTMX over React** | No build step, SSR-friendly, sufficient for v2.0 dashboard | ✅ Shipped — functional dashboard |
| **Next.js 16 over HTMX** | v2.1 needs real-time UX, component composition, TypeScript | — v2.1 in progress |
| **React Flow over D3.js** | Better React integration, interactivity built-in, less custom code | — v2.1 in progress |
| **Zustand WS Dispatcher** | Single connection, pub/sub by event type, avoids prop drilling | — v2.1 in progress |
| **3-tier CI** | Token cost control: typecheck → tests → semantic | ✅ GitHub Actions running |
| **Multi-stage Docker** | ~50% image size reduction | ✅ Production Docker deployed |

## Vision Notes (v3.0+)

- **Shared Memory Layer**: Centralized brain memory where experiences are stored
- **Cross-Brain Learning**: Brains learn from each other's experiences
- **Hallucination Prevention**: RAG-based fact checking (ExperienceRecord is the foundation)
- **Auto-Improvement**: ML pipeline fine-tuning on successful outcomes
- **PostgreSQL + pgvector**: Migrate from SQLite + JSONB when scale demands it

---
*Last updated: 2026-03-18 after v2.1 milestone started*
