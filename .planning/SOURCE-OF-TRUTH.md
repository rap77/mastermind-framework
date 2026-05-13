# MasterMind Framework — Source of Truth

> **Este archivo es la única fuente de la verdad del proyecto.**
> Reemplaza: `PROJECT.md`, `STATE.md`, `ROADMAP.md`
> Última actualización: 2026-05-12

---

## What This Is

A cognitive architecture framework for building specialized AI-powered solutions using expert "brains" — distilled knowledge from world-class experts organized by niche. v2.2 ships autonomous Claude Code subagents per brain: each agent embeds the intermediary protocol natively, reads a two-level BRAIN-FEED (global + domain), and is dispatched in parallel by the orchestrator — replacing sequential manual skill steps with autonomous expert collaboration.

## Core Value

**Expert AI collaboration that scales.** Multiple specialized brains working in parallel on complex problems — faster, safer, and more reliably than any single brain alone. Now with a real-time visual war room for operators to orchestrate and monitor 24 AI brains across 4 purpose-built screens.

---

## Current State

### v2.2 — Shipped (2026-03-30)

- **Python:** ~14,500 LOC across `apps/api/mastermind_cli/`
- **TypeScript:** ~15,800 LOC across `apps/web/src/`
- **Brains:** 24 active (7 Software Dev + 16 Marketing + 1 Master Interviewer)
- **Tests:** 578 backend (pytest) + 407 frontend (vitest) = 985 total, 0 failures
- **Brain Agents:** 7 autonomous subagents (`.claude/agents/mm/brain-NN-*/`) with embedded intermediary protocol
- **BRAIN-FEED:** Two-level — `BRAIN-FEED.md` (global) + `BRAIN-FEED-NN-domain.md` × 7
- **Dispatch:** Parallel (Agent tool) via `mm:brain-context` — Brain #7 runs after domain agents barrier
- **Frontend:** Next.js 16 + React 19 + Tailwind 4 + shadcn/ui + Magic UI + React Flow (@xyflow/react v12) + Zustand 5
- **4 Screens:** Command Center, The Nexus (DAG), Strategy Vault, Engine Room
- **Auth:** JWT (30min) + refresh rotation (24h) + httpOnly cookies (CVE-2025-29927 mitigated)
- **DB:** SQLite WAL mode, aiosqlite, cursor pagination with composite (created_at, id) key
- **Monorepo:** apps/api/ (Python FastAPI) + apps/web/ (Next.js 16)
- **CI:** 3-tier pipeline (typecheck → tests → semantic) on GitHub Actions
- **Docker:** Multi-stage build, `docker compose up -d` → api:8001, rust:3001, web:3002 (host ports; 3000 occupied by prosell in dev)

### v3.0 — In Progress (Milestone: Enterprise Agent Orchestration for LATAM)

**Milestone status as of 2026-04-15:**

```yaml
milestone: v3.0
current_phase: 19
overall_status: VERIFICATION_COMPLETE   # all 6 phases (13-18) complete
last_action:
  actor: "Verification Update (2026-04-15)"
  what: "Updated all verification reports — 818/827 Python (99.0%), 628/628 TypeScript, 0 Rust errors"
  next_step: "Phase 19-05 execution or v3.1 milestone planning"
```

| Phase | Name | Plans | Status | Date |
|-------|------|-------|--------|------|
| 13 | Vertical Slice | 4/4 | ✅ COMPLETE | 2026-04-05 |
| 14 | Knowledge Distillation | 4/4 | ✅ COMPLETE | 2026-04-06 |
| 15 | Rust Control Plane | 6/4 | ✅ COMPLETE | 2026-04-07 |
| 16 | Observability + Real-time Hub | 7/7 | ✅ COMPLETE | — |
| 17 | UI Evolution | — | ✅ COMPLETE | — |
| 18 | Multi-channel Gateway | 10/10 | ✅ COMPLETE | 2026-04-11 |
| 19 | MM-Flow + Audit Trail | 4/5 | 🔄 IN PROGRESS | — |

**Phase 19 detail:**

| Plan | Name | Status |
|------|------|--------|
| 19-01 | Infrastructure foundation (FASE 1) | ✅ COMPLETE |
| 19-02 | CLI Skills Bridge (FASE 2) | ✅ COMPLETE — 2026-04-14 |
| 19-03 | Context Persistence (FASE 3) | ✅ COMPLETE — 2026-04-14 |
| 19-04 | Audit Trail + JWT (FASE 4) | ✅ COMPLETE — 2026-04-14 |
| 19-05 | (next) | 🔄 PENDING |

**Blocker:** Phase 20 requires Phase 19 completion.

---

## Requirements

### Validated (shipped)

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
- ✓ **Frontend Foundation** (FND-01 through FND-04, SB-01) — Next.js 16, JWT auth gate, Zod schema bridge — v2.1
- ✓ **WebSocket Infrastructure** (WS-01 through WS-03) — Zustand singleton, RAF batching, Map<brainId> selectors — v2.1
- ✓ **Command Center** (BE-01, CC-01–CC-03) — Bento Grid 24 tiles, brief modal, WS live status — v2.1
- ✓ **The Nexus** (BE-02, NEX-01–NEX-03) — React Flow DAG, dagre layout, WS illumination — v2.1
- ✓ **Strategy Vault** (SV-01, SV-02) — Execution history, detail view, Markdown rendering, timeline scrubber — v2.1
- ✓ **Engine Room** (ER-01–ER-03) — Virtual scroll logs, API key CRUD, brain YAML viewer — v2.1
- ✓ **UX Polish** (UX-01) — Focus Mode, sidebar collapse, idle dimming, Esc exit — v2.1
- ✓ **Brain Agents** (AGT-01–AGT-04) — 7 autonomous subagents, criteria, anti-patterns, smoke tested — v2.2
- ✓ **BRAIN-FEED Split** (FEED-01–FEED-03) — Two-level architecture, per-brain domain feeds — v2.2
- ✓ **Baselines** (BASE-01, BASE-02) — 5 pre-migration baselines, Delta-Velocity schema — v2.2
- ✓ **Parallel Dispatch** (DISP-01, DISP-02) — Agent tool dispatch, Brain #7 barrier — v2.2
- ✓ **VS** (VS-01–VS-03) — Vertical Slice: Next.js → Rust → gRPC → Python — v3.0 Phase 13
- ✓ **KD** (KD-01–KD-03) — Knowledge Distillation auto-loop — v3.0 Phase 14
- ✓ **RCP** (RCP-01–RCP-03) — Rust Control Plane, PostgreSQL + JWT + event sourcing — v3.0 Phase 15
- ✓ **OBS** (OBS-01) — Observability: structured logging + distributed tracing — v3.0 Phase 16
- ✓ **RTU** (RTU-01) — Real-time Hub: Rust WebSocket — v3.0 Phase 16
- ✓ **UIE** (UIE-01–UIE-03) — UI Evolution: Paperclip patterns in Next.js — v3.0 Phase 17
- ✓ **MCG** (MCG-01) — Multi-channel Gateway: WhatsApp + Instagram + Email — v3.0 Phase 18

### Active (v3.0 Phase 19)

- [ ] **MM-Flow 19-05** — Next plan in Phase 19 (TBD)

### Deferred (v3.1+)

- **Template Marketplace + Multi-tenant:** CONDITIONAL — requires 3 LATAM SME interviews + 1 LOI/paid pilot. Includes Clipmart-style gallery, RBAC per organization, billing, Odoo/Notion/webhook adapters.
- **RAG per agent:** Each brain manages its own vector store (ChromaDB/Qdrant) — domain knowledge (books) + project memory (patterns).
- **Cross-brain learning:** Brains learn from each other's successful patterns via shared BRAIN-FEED.
- **PostgreSQL + pgvector:** Migrate from SQLite when scale demands it.

### Out of Scope

- Machine learning auto-improvement — v3.0+
- Full RAG system with vector DB — v3.0+
- Mobile apps — web-first, mobile responsive only
- Real-time collaborative editing — v3.0+
- Multi-tenant SaaS — single-tenant deployment only for v2.x
- Celery/RQ task queues — asyncio sufficient for single-host

---

## Roadmap

### Milestone: MasterMind v3.0 — Enterprise Agent Orchestration Platform for LATAM

**Defined:** 2026-04-05 | **Phase Start:** 13 (v2.2 ended at Phase 12)

---

#### Phase 13: Vertical Slice ✅ COMPLETE (2026-04-05)

**Goal:** Validate 3-service architecture end-to-end before committing to full Rust build.

**Success Criteria (met):**
1. `POST /api/tasks/auto` flows Next.js → Rust (Axum) → gRPC → Python → UI renders result
2. Single `.proto` generates types for Rust (tonic + prost), Python (grpclib), TypeScript (ts-proto)
3. Rust velocity measured against Python baseline; escape hatch defined (< 0.5x → Rust only for WS Hub + Adapter Registry)
4. PostgreSQL 16 + pgvector running in dev; all 620 existing tests pass

---

#### Phase 14: Knowledge Distillation ✅ COMPLETE (2026-04-06)

**Goal:** Brains learn from every interaction and accumulate expertise over time.

**Success Criteria (met):**
1. Brain #7 auto-evaluates every output → adjusts brain memory after each session
2. Delta-velocity tracking shows improvement vs T1 baseline (210–270s target)
3. Successful interactions auto-generate reusable templates
4. Dashboard shows: recurring patterns, insights, correlation analysis, delta-velocity trends

---

#### Phase 15: Rust Control Plane ✅ COMPLETE (2026-04-07)

**Goal:** State management, auth, and event sourcing migrated to Rust + PostgreSQL.

**Success Criteria (met):**
1. SQLite → PostgreSQL 16 + pgvector via dual-write strategy; all 620 tests pass
2. JWT + RBAC migrated from Python (jose) to Rust (Axum middleware); refresh rotation preserved
3. Immutable `activity_log` via event sourcing — every brain op = event with brain_id, timestamp, type, payload

---

#### Phase 16: Observability + Real-time Hub ✅ COMPLETE

**Goal:** Cross-service debugging visibility + real-time WebSocket infrastructure.

**Success Criteria (met):**
1. Structured logging (Rust tracing) + distributed tracing (trace_id across Rust → gRPC → Python) + health checks for all 3 services
2. Unified log format — operators trace a single request across all 3 services
3. Rust WebSocket Hub (Tokio-tungstenite) handles thousands concurrent connections without GC pauses
4. Ghost Mode buffer (100-event replay) replicated in Tokio + Redis pub/sub

---

#### Phase 17: UI Evolution ✅ COMPLETE

**Goal:** Extract Paperclip UX patterns; rebuild in Next.js 16 App Router (NOT a fork — Paperclip uses Vite).

**Success Criteria (met):**
1. Three-column layout (CompanyRail + Sidebar + Content) with multi-tenant sidebar switcher + responsive mobile
2. Real-time agent monitoring panel: ping animation, status badges, compact density modes
3. Orchestration canvas extends React Flow Nexus with real-time WS updates + cost dashboard (MetricCard, QuotaBar)

---

#### Phase 18: Multi-channel Gateway ✅ COMPLETE (2026-04-11)

**Goal:** Unified inbox across WhatsApp + Instagram + Email with webhook reliability.

**Plans:** 10/10 complete (18-01 through 18-10, including 3 gap-closure plans).

**Success Criteria (met):**
1. WhatsApp Business Cloud API + Instagram Graph API + Email (aiosmtplib) — Rust handles webhooks + routing, Python handles AI
2. Webhook queue with DLQ (dead letter queue), exponential backoff — no dropped messages
3. Unified inbox UI across all channels
4. Channel Router brain agent selects optimal channel for responses

---

#### Phase 19: MM-Flow + Audit Trail 🔄 IN PROGRESS

**Goal:** MM-Flow infrastructure, CLI Skills Bridge, Context Persistence, and Audit Trail + JWT.

**Plans:** 4/5 complete.

| Plan | Status |
|------|--------|
| 19-01 Infrastructure foundation | ✅ COMPLETE |
| 19-02 CLI Skills Bridge | ✅ COMPLETE |
| 19-03 Context Persistence | ✅ COMPLETE |
| 19-04 Audit Trail + JWT | ✅ COMPLETE |
| 19-05 (next) | 🔄 PENDING |

**Key decisions from Phase 19:**
- **TDD for audit auth enforcement:** RED phase (26 failing tests) → GREEN phase (13 routes) ensures complete coverage
- **AST-based gate test:** Catches missing auth at code-analysis time, not runtime
- **backends.sh in `~/.claude/`:** User-local credentials must NOT be committed to repo
- **Stop hook security:** `execFileSync` (not `exec`) — avoids shell injection
- **Stdin timeout pattern:** 3-second timeout with graceful fallback for missing data
- **C5 (Brain #7):** `checkpoint_writer.py` lives in repo (`apps/api/mastermind_cli/mm_flow/`), not `~/.mm-flow/`
- **C6 (Brain #7):** Behavioral criterion — write at pos 8/10 triggers checkpoint; all-read does not

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| VS-01 | Phase 13 | ✅ Complete |
| VS-02 | Phase 13 | ✅ Complete |
| VS-03 | Phase 13 | ✅ Complete |
| KD-01 | Phase 14 | ✅ Complete |
| KD-02 | Phase 14 | ✅ Complete |
| KD-03 | Phase 14 | ✅ Complete |
| RCP-01 | Phase 15 | ✅ Complete |
| RCP-02 | Phase 15 | ✅ Complete |
| RCP-03 | Phase 15 | ✅ Complete |
| OBS-01 | Phase 16 | ✅ Complete |
| RTU-01 | Phase 16 | ✅ Complete |
| UIE-01 | Phase 17 | ✅ Complete |
| UIE-02 | Phase 17 | ✅ Complete |
| UIE-03 | Phase 17 | ✅ Complete |
| MCG-01 | Phase 18 | ✅ Complete |

**Coverage:** 15/15 requirements mapped and delivered ✓

---

## Key Constraints

From Brain #1 + Brain #7 validation:

1. **NOT a fork** — Paperclip uses Vite (incompatible with Next.js App Router). Extract 10 UX patterns and rebuild.
2. **Knowledge Distillation first** — Leverages existing 7 brains + brain_memory.py + experience_records. Zero Rust needed.
3. **Vertical Slice validates architecture** — Proves 3-service split before committing to full Rust build.
4. **Rust escape hatch** — If velocity < 0.5x Python, Rust only for WebSocket Hub + Adapter Registry.
5. **Marketplace is CONDITIONAL** — Requires 3 LATAM SME interviews + 1 LOI — NOT in v3.0.
6. **Strangler Fig Pattern** — Incremental migration, NOT Big Bang rewrite.

---

## Technical Debt

| Item | Location | Severity |
|------|----------|----------|
| SECRET_KEY hardcoded | — | Medium — load from ENV_VAR |
| YAML export incomplete | — | Low |
| 3 coordinator tests with timestamp flakiness | — | Low (non-critical) |
| `--parallel` flag missing in `orchestrate run` CLI | — | Low |
| WSBrainBridge disconnect() potential race | — | Low (edge case) |
| NexusCanvas uses static star topology | — | Low |
| Pyright 156 errors in `/tests/` | tests/ | Medium — zero in production code |
| `uptime/last_called_at` hardcoded | `brain_registry.py:170-171` | Low — visible as "0 uptime" in UI |
| `prefers-reduced-motion` guard missing | `BrainTile.tsx:159` | Low (a11y) |
| WebSocket metrics stubs | `websocket-metrics.ts:91,112,132` | Low (observability, not functional) |

---

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Include UI in v2.0 | End users can't use CLI; agencies need client-facing interface | ✅ FastAPI + HTMX/Alpine.js |
| Parallel before ML | Immediate benefit; ML is R&D heavy | ✅ 4.65x speedup |
| Type safety with Pydantic v2 | Validation + JSON serialization + IDE support | ✅ 0 mypy errors |
| Web dashboard over desktop | Cross-platform, easier deployment | ✅ Docker → localhost:8000 |
| Foundation for shared memory | Design for v3.0 without building full ML | ✅ ExperienceRecord, BrainMessage protocol |
| CLI alongside UI | Power users prefer CLI | ✅ Both maintained |
| SQLite over PostgreSQL | No infra dependency, sufficient for single-host | ✅ 0.39ms queries, WAL mode |
| StatelessCoordinator | Pure Function Architecture → multi-user safe | ✅ Per-request instances, no races |
| JWT + refresh rotation | Stateless, API + web compatible, replay prevention | ✅ Rotation tested 12/12 |
| HTMX over React (v2.0) | No build step, SSR-friendly, sufficient for v2.0 | ✅ Functional dashboard |
| Next.js 16 over HTMX (v2.1) | Real-time UX, component composition, TypeScript | ✅ 4 production screens |
| React Flow over D3.js | Better React integration, interactivity built-in | ✅ The Nexus DAG working |
| Zustand WS Dispatcher | Single connection, pub/sub by event type | ✅ RAF batching, 60fps at 24-brain burst |
| React Flow CSS in @layer base | Tailwind 4 silently breaks handles/edges if imported from tsx | ✅ Required pattern documented |
| Immer MapSet plugin | `enableMapSet()` required for Map iteration in Immer callbacks | ✅ Prevents silent failures |
| RAF batching in brainStore | Queues 24 concurrent events, drains before paint frame | ✅ 60fps maintained |
| CVE-2025-29927 mitigation | JWT verification at Server Components + Route Handlers | ✅ Dual-layer verification |
| INSERT OR IGNORE concurrency | 24 simultaneous brain completions without Redis/Celery | ✅ First writer wins, no duplicates |
| Cursor pagination (created_at, id) | Composite key prevents race conditions in concurrent writes | ✅ No duplicated entries |
| api_keys_v2 table | Avoids migrating legacy api_keys, no breaking changes | ✅ Prefix/suffix/revoked_at |
| Skill before Agents | v2.1 uses mm:brain-context skill; v2.2 upgrades to agent system prompts | ✅ Foundation built |
| Two-level BRAIN-FEED | General project feed + per-brain domain feeds — no context pollution | ✅ Validated v2.2 |
| model:inherit in agents | `model: ""` (empty) — `inherit` is NOT a valid keyword, causes silent fallback | ✅ Fixed v2.2 (Phase 11) |
| Brain #7 barrier pattern | Evaluator dispatched after domain agents complete, not in parallel | ✅ Validated v2.2 |
| Sentinel scoped grep | `mcp-elimination` grep scoped to operational files only | ✅ Fixed v2.2 (Phase 12) |
| 3-tier CI | Token cost control: typecheck → tests → semantic | ✅ GitHub Actions running |
| Multi-stage Docker | ~50% image size reduction | ✅ Production Docker deployed |
| 3-service architecture | Rust (Control Plane) + Python (Agent Runtime) + TypeScript (Frontend) | ✅ Validated Phase 13 |
| Strangler Fig migration | Incremental Rust adoption, not Big Bang rewrite | ✅ Applied Phases 13–18 |
| TDD for audit auth enforcement | 26 failing tests RED → GREEN ensures complete coverage | ✅ Phase 19-04 |
| AST-based gate test | Catches missing auth at code-analysis time, not runtime | ✅ Phase 19-04 |

---

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.14, FastAPI, aiosqlite, Pydantic v2, mypy strict |
| Control Plane | Rust (Axum + Tokio), PostgreSQL 16 + pgvector, gRPC (tonic + prost) |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind 4, Zustand 5, TanStack Query v5, React Flow v12 |
| Testing | pytest + vitest; 818+ backend, 628 frontend |
| Package managers | Python → `uv` | Node.js → `pnpm` |
| CI | GitHub Actions — 3-tier (typecheck → tests → semantic) |
| Infrastructure | Docker multi-stage; `docker compose up -d` → api:8001, rust:3001, web:3002 |
| Protocol | gRPC + Protobuf; `.proto` → Rust + Python + TypeScript types |

---

## Vision

### Brain Evolution Roadmap

1. **v2.1 (shipped):** `mm:brain-context` skill — manual workflows, sequential
2. **v2.2 (shipped):** Autonomous subagents per brain — intermediary protocol is native behavior, parallel dispatch
3. **v3.0 (in progress):** 3-service architecture + real-time hub + multi-channel gateway
4. **v3.1+ (planned):** RAG per agent — each brain manages its own vector store, persistent expertise across projects

### v3.0 Architecture (live)

```
Orchestrator (Claude main) → dispatches Brain Agents in parallel (Agent tool)
  ├── Brain Agent #N reads: BRAIN-FEED.md (global) + BRAIN-FEED-NN-domain.md
  ├── Brain Agent #N reads: relevant code
  ├── Brain Agent #N queries: NotebookLM brain (static knowledge)
  ├── Brain Agent #N filters: grep each concern against codebase
  ├── Brain Agent #N updates: BRAIN-FEED-NN-domain.md with new patterns
  └── Brain Agent #N returns: verified insights to orchestrator
             ↓ (barrier — after all domain agents complete)
Brain Agent #7 (Evaluator) → receives all domain outputs, evaluates synthesis

Rust Control Plane (Axum + Tokio)
  ├── JWT auth + RBAC
  ├── Event sourcing (activity_log)
  ├── WebSocket Hub (real-time brain state events)
  └── gRPC bridge → Python Agent Runtime

Python Agent Runtime (FastAPI)
  ├── Brain orchestration
  ├── Knowledge Distillation loop
  └── Multi-channel Gateway (WhatsApp / Instagram / Email)

Next.js 16 Frontend
  ├── Command Center (24 brain tiles)
  ├── The Nexus (React Flow DAG)
  ├── Strategy Vault (execution history)
  └── Engine Room (logs, API keys, brain configs)
```
