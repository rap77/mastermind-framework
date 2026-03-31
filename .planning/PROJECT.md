# MasterMind Framework

## What This Is

A cognitive architecture framework for building specialized AI-powered solutions using expert "brains" — distilled knowledge from world-class experts organized by niche. v2.2 ships autonomous Claude Code subagents per brain: each agent embeds the intermediary protocol natively, reads a two-level BRAIN-FEED (global + domain), and is dispatched in parallel by the orchestrator — replacing sequential manual skill steps with autonomous expert collaboration.

## Core Value

**Expert AI collaboration that scales.** Multiple specialized brains working in parallel on complex problems — faster, safer, and more reliably than any single brain alone. Now with a real-time visual war room for operators to orchestrate and monitor 24 AI brains across 4 purpose-built screens.

## Current State (v2.2 — shipped 2026-03-30)

- **Python:** ~14,500 LOC across `apps/api/mastermind_cli/`
- **TypeScript:** ~15,800 LOC across `apps/web/src/`
- **Brains:** 24 active (7 Software Dev + 16 Marketing + 1 Master Interviewer)
- **Tests:** 578 backend (pytest) + 407 frontend (vitest) = 985 total, 0 failures (3 RED stubs expected)
- **Brain Agents:** 7 autonomous subagents (`.claude/agents/mm/brain-NN-*/`) with embedded intermediary protocol
- **BRAIN-FEED:** Two-level architecture — `BRAIN-FEED.md` (global) + `BRAIN-FEED-NN-domain.md` × 7
- **Dispatch:** Parallel (Agent tool) via `mm:brain-context` — Brain #7 runs after domain agents barrier
- **Frontend:** Next.js 16 + React 19 + Tailwind 4 + shadcn/ui + Magic UI + React Flow (@xyflow/react v12) + Zustand 5
- **4 Screens:** Command Center, The Nexus (DAG), Strategy Vault, Engine Room
- **Auth:** JWT (30min) + refresh rotation (24h) + httpOnly cookies (CVE-2025-29927 mitigated)
- **DB:** SQLite WAL mode, aiosqlite, cursor pagination with composite (created_at, id) key
- **API Keys:** api_keys_v2 table, prefix/suffix/revoked_at, show-once creation
- **Monorepo:** apps/api/ (Python FastAPI) + apps/web/ (Next.js 16)
- **CI:** 3-tier pipeline (typecheck → tests → semantic) on GitHub Actions
- **Docker:** Multi-stage build, `docker compose up -d` → api:8001 (host), web:3000
- **Tag:** v2.2 on `master`

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
- ✓ **Frontend Foundation** (FND-01 through FND-04, SB-01) — Next.js 16, JWT auth gate, Zod schema bridge — v2.1
- ✓ **WebSocket Infrastructure** (WS-01 through WS-03) — Zustand singleton, RAF batching, Map<brainId> selectors — v2.1
- ✓ **Command Center** (BE-01, CC-01, CC-02, CC-03) — Bento Grid 24 tiles, brief modal, WS live status — v2.1
- ✓ **The Nexus** (BE-02, NEX-01, NEX-02, NEX-03) — React Flow DAG, dagre layout, WS illumination — v2.1
- ✓ **Strategy Vault** (SV-01, SV-02) — Execution history, detail view, Markdown rendering, timeline scrubber — v2.1
- ✓ **Engine Room** (ER-01, ER-02, ER-03) — Virtual scroll logs, API key CRUD, brain YAML viewer — v2.1
- ✓ **UX Polish** (UX-01) — Focus Mode auto-activate, sidebar collapse, idle dimming, Esc exit — v2.1
- ✓ **Brain Agents** (AGT-01 through AGT-04) — 7 autonomous subagents with embedded intermediary protocol, criteria, anti-patterns, smoke tested — v2.2
- ✓ **BRAIN-FEED Split** (FEED-01 through FEED-03) — Two-level architecture, per-brain domain feeds, no cross-domain pollution — v2.2
- ✓ **Baselines** (BASE-01, BASE-02) — 5 pre-migration baselines, Delta-Velocity metric schema — v2.2
- ✓ **Parallel Dispatch** (DISP-01, DISP-02) — Agent tool dispatch, Brain #7 barrier, mm:brain-context updated — v2.2

### Active (v3.0 — Custom Workflow Framework + RAG)

*(No requirements defined yet — start with `/gsd:new-milestone`)*

### Deferred (v3.0 — Custom Workflow Framework + RAG)

- **MasterMind Workflow Framework**: Replace GSD workflows with niche-agnostic orchestration system. Keep GSD strengths (goal-backward, wave parallelization, atomic commits, deviation rules). Add: declarative DSL, pluggable agent registry, brain integration layer, domain-agnostic verification, niche-specific flow templates, custom checkpoint types
- **RAG per agent**: Each brain agent manages its own vector store partition (ChromaDB/Qdrant) — domain knowledge (books) + project memory (accumulated patterns) in separate collections
- **Cross-brain learning**: Brains learn from each other's successful patterns via shared project BRAIN-FEED
- **PostgreSQL + pgvector**: Migrate from SQLite when scale demands it

### Out of Scope

- **Machine learning auto-improvement** — v3.0+ (requires R&D)
- **Full RAG system with vector DB** — v3.0+ (PostgreSQL + pgvector/qdrant)
- **Mobile apps** — Web-first, mobile responsive only
- **Real-time collaborative editing** — v3.0+
- **Multi-tenant SaaS** — Single-tenant deployment only for v2.x
- **Celery/RQ task queues** — asyncio sufficient for single-host

## Context

**Stack:** Python 3.14 (uv), FastAPI, aiosqlite, Pydantic v2, mypy strict, pytest + Next.js 16, React 19, TypeScript, Tailwind 4, Zustand 5, TanStack Query v5, React Flow (@xyflow/react v12), Docker, GitHub Actions

**Technical debt carried into v2.2:**
- SECRET_KEY hardcoded (TODO: load from ENV_VAR)
- YAML export implementation incomplete
- 3 coordinator tests with timestamp comparison flakiness (non-critical)
- `--parallel` flag missing in `orchestrate run` CLI
- WSBrainBridge disconnect() may race with CommandCenterWrapper WS in edge cases
- NexusCanvas uses static star topology (real DAG from BE is proxied but not rendered)
- **Pyright 156 errors in test files** — all in `/tests/`, zero in production `mastermind_cli/`. Introduced in monorepo restructure (commit f4d1315). Were incorrectly assumed pre-existing.
- **uptime/last_called_at hardcoded** — `brain_registry.py:170-171` always returns `uptime: 0.0` and `last_called_at: null`. Visible as "0 uptime" in Command Center UI. Requires tracking from execution history table.
- **prefers-reduced-motion guard missing** — `BrainTile.tsx:159` has TODO for accessibility guard. Planned for Phase 08 Task 4 but not implemented. Severity: low.
- **WebSocket metrics stubs** — `websocket-metrics.ts` lines 91, 112, 132 have TODO for Prometheus/Datadog integration. Severity: low (observability, not functional).

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
| **Next.js 16 over HTMX** | v2.1 needs real-time UX, component composition, TypeScript | ✅ Shipped — 4 production screens |
| **React Flow over D3.js** | Better React integration, interactivity built-in, less custom code | ✅ The Nexus DAG working |
| **Zustand WS Dispatcher** | Single connection, pub/sub by event type, avoids prop drilling | ✅ RAF batching, 60fps at 24-brain burst |
| **React Flow CSS in @layer base** | Tailwind 4 silently breaks handles/edges if imported from tsx | ✅ Required pattern documented |
| **Immer MapSet plugin** | `enableMapSet()` required for Map iteration in Immer set() callbacks | ✅ Documented, prevents silent failures |
| **RAF batching in brainStore** | Queues 24 concurrent events, drains before paint frame | ✅ 60fps maintained during brain burst |
| **CVE-2025-29927 mitigation** | JWT verification at Server Components + Route Handlers (not only middleware) | ✅ Dual-layer verification implemented |
| **INSERT OR IGNORE concurrency** | 24 simultaneous brain completions handled without Redis/Celery | ✅ First writer wins, no duplicates |
| **Cursor pagination (created_at, id)** | Composite key prevents race conditions in concurrent writes | ✅ No duplicated entries |
| **api_keys_v2 table** | Avoids migrating legacy api_keys, no breaking changes | ✅ Prefix/suffix/revoked_at fields |
| **Skill before Agents** | v2.1 uses mm:brain-context skill (manual workflows); workflows become agent system prompts in v2.2 | ✅ Foundation built, v2.2 ready |
| **Two-level BRAIN-FEED** | General project feed + per-brain domain feeds — prevents context pollution, enables agent independence | ✅ Validated v2.2 |
| **model:inherit in agents** | Brain agents use `model: ""` (empty) not `model: inherit` — `inherit` is not a valid keyword, causes silent fallback | ✅ Fixed v2.2 (Phase 11) |
| **Brain #7 barrier pattern** | Evaluator dispatched after domain agents complete, not in parallel — receives outputs as context | ✅ Validated v2.2 |
| **Sentinel scoped grep** | `mcp-elimination` grep scoped to operational files only — `tests/smoke/verify_feed_isolation.sh` line 68 | ✅ Fixed v2.2 (Phase 12) |
| **3-tier CI** | Token cost control: typecheck → tests → semantic | ✅ GitHub Actions running |
| **Multi-stage Docker** | ~50% image size reduction | ✅ Production Docker deployed |

## Vision Notes

### v2.2 — Brain Agents (shipped 2026-03-30)

The brain consultation system evolved in 3 stages:
1. **v2.1 (shipped):** `mm:brain-context` skill with manual workflows → Claude follows instructions to build context, query brains, filter responses
2. **v2.2 (shipped):** Autonomous subagents per brain → intermediary protocol is native behavior, each agent accumulates domain expertise in its own BRAIN-FEED, dispatched in parallel
3. **v3.0:** Agents + RAG → each agent manages its own vector store, knowledge is persistent and searchable

**Architecture (live):**
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
```

### v3.0 — Full RAG + Persistent Learning

- **Per-agent vector stores**: Domain knowledge (books) + project memory (patterns) in separate collections
- **Cross-brain learning**: Agents share successful patterns via project BRAIN-FEED
- **Persistent expertise**: A Frontend agent that worked on 10 projects accumulates 10 projects worth of architecture decisions
- **PostgreSQL + pgvector**: Migrate from SQLite + JSONB when scale demands it

---
*Last updated: 2026-03-30 after v2.2 milestone*
