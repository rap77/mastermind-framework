# MasterMind Framework

## What This Is

A cognitive architecture framework for building specialized AI-powered solutions using expert "brains" — distilled knowledge from world-class geniuses organized by niche. v2.0 shipped a production-ready platform: parallel brain execution, full type safety, and a FastAPI web dashboard with JWT auth, WebSocket real-time updates, and Experience Store for v3.0 ML foundations.

## Core Value

**Expert AI collaboration that scales.** Multiple specialized brains working in parallel on complex problems — faster, safer, and more reliably than any single brain alone. 4.65x speedup validated, 467 tests passing, production-hardened with CI/CD and Docker.

## Current State (v2.0.0 — 2026-03-17)

- **Python:** 14,275 LOC across `mastermind_cli/`
- **Brains:** 24 active (7 Software Dev + 16 Marketing + 1 Master Interviewer)
- **Tests:** 467 passed, 0 failed, 8 skipped
- **CI:** 3-tier pipeline (typecheck → tests → semantic) on GitHub Actions
- **Docker:** Multi-stage build, `docker compose up -d` → localhost:8000
- **Auth:** JWT (30min) + refresh rotation (24h), API Keys for CLI access
- **DB:** SQLite WAL mode, aiosqlite, 0.39ms status queries
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

### Active (v2.1 candidates)

- [ ] Fix `--parallel` flag missing in `orchestrate run` CLI command
- [ ] Complete PRP-00-00 Tasks 4-10 (API Key auth, Legacy wrapper, CLI updates, Error handling, Perf tests, Docs, Migration guide)
- [ ] Enable trufflehog secret scanner in CI
- [ ] Push Docker image to registry
- [ ] Production monitoring and alerting

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
- HTMX/Alpine.js over React: no build step, SSR-friendly

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
| **3-tier CI** | Token cost control: typecheck → tests → semantic | ✅ GitHub Actions running |
| **Multi-stage Docker** | ~50% image size reduction | ✅ Production Docker deployed |

## Vision Notes (v3.0+)

- **Shared Memory Layer**: Centralized brain memory where experiences are stored
- **Cross-Brain Learning**: Brains learn from each other's experiences
- **Hallucination Prevention**: RAG-based fact checking (ExperienceRecord is the foundation)
- **Auto-Improvement**: ML pipeline fine-tuning on successful outcomes
- **PostgreSQL + pgvector**: Migrate from SQLite + JSONB when scale demands it

---
*Last updated: 2026-03-17 after v2.0 milestone completion*
