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

### Deferred (v2.2 — Brain Agents)

- **Specialized Brain Agents**: Convert brain consultations from manual skill workflows (mm:brain-context) to autonomous Claude Code subagents — each agent embeds the intermediary protocol, reads its domain BRAIN-FEED, queries its NotebookLM brain, filters responses against code, and accumulates domain-specific patterns
- **Two-level BRAIN-FEED**: Split `.planning/BRAIN-FEED.md` into general project feed + per-brain domain feeds (`BRAIN-FEED-04-frontend.md`, etc.) — each agent reads both, writes only its own
- **Inter-agent coordination**: Orchestrator passes outputs between agents when cross-domain decisions are needed (e.g., frontend + backend API contract alignment)
- Semantic routing: replace FlowDetector keyword matching with Claude classifier
- Production hardening: HTTPS+nginx, rate limiting, MM_SECRET_KEY mandatory, session cleanup
- Trufflehog secret scanner in CI
- Docker image push to registry
- Production monitoring and alerting

### Deferred (v3.0 — Custom Workflow Framework + RAG)

- **MasterMind Workflow Framework**: Replace GSD workflows with niche-agnostic orchestration system. Keep GSD strengths (goal-backward, wave parallelization, atomic commits, deviation rules). Add: declarative DSL, pluggable agent registry, brain integration layer, domain-agnostic verification, niche-specific flow templates, custom checkpoint types
- **Niche flow templates**: Pre-defined workflows for any domain (software dev, marketing campaigns, design systems, content creation) — not hardcoded to git/code/tests
- **RAG per agent**: Each brain agent manages its own vector store partition (ChromaDB/Qdrant) — domain knowledge (books) + project memory (accumulated patterns) in separate collections
- **Cross-brain learning**: Brains learn from each other's successful patterns via shared project BRAIN-FEED
- **Real brain memory**: Agents persist learnings across projects — a Frontend agent that worked on 10 projects has 10 projects worth of architecture decisions
- Auto-improvement: ML pipeline fine-tuning on successful outcomes
- PostgreSQL + pgvector: migrate from SQLite when scale demands it

> Research: `.planning/research/GSD-FRAMEWORK-ANALYSIS.md` — full GSD architecture analysis (12 agents, strengths, limitations, extension points)

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
| **Skill before Agents** | v2.1 uses mm:brain-context skill (manual workflows); workflows become agent system prompts in v2.2 — builds foundation before automation | — v2.1 foundation, v2.2 agents |
| **Two-level BRAIN-FEED** | General project feed + per-brain domain feeds — prevents context pollution, enables agent independence | — planned v2.2 |
| **3-tier CI** | Token cost control: typecheck → tests → semantic | ✅ GitHub Actions running |
| **Multi-stage Docker** | ~50% image size reduction | ✅ Production Docker deployed |

## Vision Notes

### v2.2 — Brain Agents (next after v2.1)

The brain consultation system evolves in 3 stages:
1. **v2.1 (current):** `mm:brain-context` skill with manual workflows → Claude follows instructions to build context, query brains, filter responses
2. **v2.2:** Autonomous subagents per brain → intermediary protocol is native behavior, each agent accumulates domain expertise in its own BRAIN-FEED
3. **v3.0:** Agents + RAG → each agent manages its own vector store, knowledge is persistent and searchable

**Key insight (2026-03-22):** Brains (NotebookLM) are static knowledge — they never learn. The "learning" happens in the intermediary (Claude) via accumulated BRAIN-FEED context. Converting from skill to agents means the intermediary protocol becomes built-in behavior, not a workflow to read and follow. Each agent's domain BRAIN-FEED grows independently, avoiding context pollution.

**Architecture:**
```
Orchestrator (Claude main) → dispatches Brain Agents in parallel
  ├── Brain Agent #N reads: BRAIN-FEED.md (general) + BRAIN-FEED-NN.md (domain)
  ├── Brain Agent #N reads: relevant code
  ├── Brain Agent #N queries: NotebookLM brain (static knowledge)
  ├── Brain Agent #N filters: grep each concern against codebase
  ├── Brain Agent #N updates: BRAIN-FEED-NN.md with new patterns
  └── Brain Agent #N returns: verified insights to orchestrator
```

**Foundation built in v2.1:** The workflow files in `mm:brain-context/workflows/` ARE the system prompts for v2.2 agents. `templates/BRAIN-FEED.md` becomes the template for both general and per-brain feeds.

### v3.0 — Full RAG + Persistent Learning

- **Per-agent vector stores**: Domain knowledge (books) + project memory (patterns) in separate collections
- **Cross-brain learning**: Agents share successful patterns via project BRAIN-FEED
- **Persistent expertise**: A Frontend agent that worked on 10 projects accumulates 10 projects worth of architecture decisions
- **Hallucination prevention**: RAG-based fact checking against ExperienceRecord
- **PostgreSQL + pgvector**: Migrate from SQLite + JSONB when scale demands it

---
*Last updated: 2026-03-18 after v2.1 milestone started*
