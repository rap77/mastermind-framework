# Project Research Summary

**Project:** MasterMind v3.0 — Enterprise Agent Orchestration Platform with Knowledge Distillation
**Domain:** Enterprise SaaS / Multi-Channel AI Agent Platform for LATAM
**Researched:** 2026-04-04
**Confidence:** MEDIUM

## Executive Summary

MasterMind v3.0 is an enterprise-grade agent orchestration platform that combines **Rust (Axum + Tokio) for control plane infrastructure**, **Python (FastAPI) for AI/knowledge execution**, and **TypeScript (Next.js 16) for frontend**, integrated via **gRPC + Protobuf** for type-safe cross-language communication. The platform differentiates through **knowledge distillation** — 7 specialized brain agents pre-loaded with expertise from world-renowned experts (Cagan, Torres, Norman, etc.) that learn from every interaction.

The research validates a **3-service architecture** that builds incrementally on the existing v2.2 foundation (14.5K LOC Python, 15.8K LOC TypeScript, 1027 tests). **Critical insight from Brain #1 + Brain #7 validation:** This is NOT a Big Bang rewrite — it's an evolutionary migration using the **Strangler Fig Pattern**. Rust wraps existing Python brain agents via gRPC, not a rewrite. Python stays as the AI/knowledge service. Rust only owns state management, real-time events, and multi-channel routing — areas where FastAPI WebSocket infrastructure has scalability limits.

**Highest risks identified:** (1) **Rust velocity < 0.5x Python** during Vertical Slice phase — escape hatch activated: Rust reduces to WebSocket Hub + Adapter Registry only; (2) **Big Bang Rewrite trap** — prevented by strangler fig pattern, one vertical slice at a time; (3) **Vite → Next.js architecture mismatch** — NOT a fork, it's pattern extraction (Paperclip uses Vite + React Router, incompatible with Next.js App Router); (4) **Type sync drift across gRPC** — prevented by single-source Protobuf with CI gate; (5) **PostgreSQL migration data loss** — prevented by testing against PostgreSQL from day 1, never SQLite in dev.

## Key Findings

### Recommended Stack

**Evolutionary migration** from validated v2.2 stack (Python FastAPI + Next.js 16 + 7 brain agents) to 3-service architecture. Existing stack remains unchanged — new Rust service added as orchestration layer.

**Core additions:**
- **Rust (Axum 0.7 + Tokio 1.x + tonic 0.11)** — Control plane for auth, WebSocket hub, adapter registry. Zero-cost abstractions, memory safety, Tokio async runtime for thousands of concurrent connections. **Escape hatch:** If velocity < 0.5x Python, Rust only for WebSocket Hub + Adapter Registry.
- **gRPC + Protobuf** — Type-safe communication between Rust/Python/TypeScript. Single `.proto` source → codegen for all 3 languages. Prevents schema drift. Use `tonic` (Rust), `grpclib` (Python), `protoc-gen-es` (TypeScript).
- **PostgreSQL 16 + pgvector 0.5.x** — Migrate from SQLite for concurrent writes, vector embeddings, MVCC. `pgvector` sufficient for v3.0 (no separate vector DB needed). Migration via Alembic with dual-write period.
- **Multi-channel adapters** — WhatsApp Business Cloud API, Instagram Graph API, Email (aiosmtplib). Python SDKs for adapters (mature ecosystem), Rust for routing.
- **Knowledge distillation engine** — Leverages existing `experience_records`, `brain_memory.py`, 7 brain agents. `sentence-transformers` for embeddings, PostgreSQL + pgvector for storage (no separate RAG system for v3.0).

**What NOT to use:**
- ❌ grpcio (Python) — C++ bindings, slower async. Use **grpclib** (pure asyncio)
- ❌ REST/JSON for Rust↔Python — Slower, no type safety. Use **gRPC + Protobuf**
- ❌ SQLite for v3.0 — Locks on write, no pgvector. Use **PostgreSQL 16**
- ❌ OpenAI embeddings — Cost, latency, API key. Use **sentence-transformers** (local, free)
- ❌ Separate vector DB (Qdrant/ChromaDB) — Overkill for v3.0. Use **pgvector**
- ❌ Vite → Next.js "fork" — Architecture mismatch. Extract **UX patterns only**

### Expected Features

**Must have (table stakes) — expected in enterprise platforms:**
- **Rust Control Plane** — JWT auth + RBAC + Execution Engine + Budget Enforcement + Adapter Registry. Multi-tenant isolation per organization.
- **Real-time Hub** — WebSocket server (Tokio-tungstenite) for dashboard monitoring, brain status updates, DAG illumination. Redis pub/sub for cross-service broadcast.
- **Multi-channel Gateway** — WhatsApp + Instagram + Email unified inbox. Webhook receiver, template management, channel router (Brain #8 decides response channel).

**Should have (competitive differentiators):**
- **Knowledge Distillation Engine** — **MOAT:** 7 brains with expertise Cagan/Torres/Norman etc. + learning loop. Experience logging, pattern extraction, Brain #7 evaluation, delta-velocity tracking, template generation.
- **Orchestration Canvas** — React Flow enhanced (extends existing Nexus). Visual DAG with real-time brain execution, drag-drop routing rules, live status updates.

**Defer (v3.1+ or conditional):**
- **Template Marketplace** — CONDITIONAL on 3 LATAM SME interviews + 1 LOI. Single-tenant first, multi-tenant later. v3.0: GitHub repo for templates, not SaaS marketplace.
- **Machine Learning Auto-Improvement** — v4.0+ (R&D heavy, manual loop sufficient for v3.0)
- **Full RAG with Vector DB** — v3.1+ (pgvector sufficient for v3.0 scale)
- **Mobile Apps** — v4.0+ (responsive web + PWA sufficient, WhatsApp is mobile already)

### Architecture Approach

**3-service split** with clear boundaries — Rust (infrastructure), Python (AI/knowledge), Next.js (UX). Integration via gRPC + Protobuf (type-safe contract), WebSocket for real-time events, PostgreSQL as single source of truth.

**Major components:**
1. **Rust Control Plane** (NEW) — Auth (JWT + RBAC), state management, WebSocket hub (tokio-tungstenite), adapter registry (multi-channel routing), cost tracking. Calls Python via gRPC for brain execution.
2. **Python Agent Runtime** (EXISTING, minimal changes) — 7 brain agents, `coordinator.py` (54.2K LOC), `brain_router.py` (23 tests), knowledge distillation, NotebookLM integration, `experience_records` logging. **NO rewrite** — wrap existing orchestration in gRPC service.
3. **Next.js Frontend** (EXISTING, evolves to Paperclip UX) — React Flow canvas, dashboard, monitoring, multi-channel inbox. WebSocket endpoint changes to Rust, TypeScript types auto-generated from Protobuf.
4. **PostgreSQL 16 + pgvector** (NEW, migrate from SQLite) — `organizations`, `tasks`, `executions`, `experience_records`, `activity_log` (event sourcing). Migration via Alembic with dual-write period.
5. **gRPC + Protobuf Contract** (NEW) — `proto/common.proto`, `brain_agent.proto`, `control_plane.proto`. Single source of truth, codegen for Rust/Python/TypeScript. CI gate prevents sync drift.

**Integration strategy:** Strangler Fig Pattern — migrate incrementally, NOT Big Bang. Phase 0: Fork UI patterns only. Phase 1: Vertical slice (1 API path end-to-end through 3 services). Validate 3-service architecture BEFORE committing to full migration.

### Critical Pitfalls

**Top 5 from research (prevent project failure):**

1. **Big Bang Rewrite — Sunk Cost Fallacy** — Attempting to rebuild everything in Rust/PostgreSQL before validating value. **Prevention:** Strangler Fig Pattern, vertical slice first (Phase 1), weekly value delivery, escape hatch if Rust velocity < 0.5x Python. Each phase MUST ship user-facing value, not just infrastructure.

2. **Type Synchronization Drift** — Protobuf definitions diverge from implementations across Rust/Python/TypeScript. **Prevention:** Single-source `.proto` files, generated code is read-only (git pre-commit hook), CI gate for proto sync (fail if generated code differs), versioned contracts (v1 frozen, v2 for breaking changes).

3. **SQLite → PostgreSQL Data Loss** — Schema migration succeeds but queries fail in production (SQLite permissive vs PostgreSQL strict). **Prevention:** Test against PostgreSQL in development from day 1 (never SQLite for app logic), Alembic migrations (no raw SQL), type mapping audit (BOOLEAN, DATETIME differences), migration dry-run on staging.

4. **Vite → Next.js Architecture Mismatch** — Attempting to "fork" Paperclip Vite frontend to Next.js App Router. **Prevention:** Accept reality — NOT a fork, pattern extraction only. Rebuild components using Next.js Server Components + Client Components split. Paperclip uses Vite + React Router (incompatible with Next.js App Router). Extract UX patterns (three-column layout, active agents panel), not code.

5. **Multi-channel Webhook Message Loss** — WhatsApp/Instagram webhooks arrive but are silently dropped (no retry, no dead letter queue). **Prevention:** Webhook handler = write-first, process-later (persist immediately, return 200 OK, background worker processes). Dead letter queue for failed webhooks, idempotency (deduplicate by `webhook_id`), monitoring dashboard (metrics + alerts).

## Implications for Roadmap

Based on research + Brain #1 + Brain #7 validation, suggested phase structure for v3.0:

### Phase 13: UX Pattern Extraction (1-2 weeks)
**Rationale:** Paperclip uses Vite + React Router (incompatible with Next.js App Router). Must extract UX patterns first, establish visual foundation before backend work. **De-risk:** Pattern extraction is low-risk, provides immediate visible progress.

**Delivers:** `apps/web-v3/` with MasterMind branding, 10 UX patterns from Paperclip (three-column layout, active agents panel, cost dashboard, kanban board, command palette, onboarding wizard, run transcript, real-time monitoring).

**Addresses:** Table stakes UX (FEATURES.md — "expected in enterprise platforms")

**Avoids:** Pitfall #5 (Vite → Next.js architecture mismatch) — by treating this as pattern extraction, NOT code copy

**Research flags:** SKIP research-phase — well-documented Next.js patterns, Paperclip code available for reference

### Phase 14: Vertical Slice — Rust + gRPC + PostgreSQL (3-4 weeks)
**Rationale:** Validate 3-service architecture end-to-end BEFORE committing to full migration. Prove Rust velocity is acceptable. If velocity < 0.5x Python, activate escape hatch (Rust only for WebSocket Hub + Adapter Registry).

**Delivers:** 1 API path (`/api/tasks/create`) working through full stack: Next.js → Rust (Axum) → Python (gRPC) → PostgreSQL → Rust WebSocket → Next.js. Protobuf contracts defined and code-generated for all 3 languages.

**Addresses:** Rust Control Plane (FEATURES.md), gRPC type sync (STACK.md), PostgreSQL migration (ARCHITECTURE.md)

**Avoids:** Pitfall #1 (Big Bang Rewrite) — by validating architecture incrementally; Pitfall #2 (Type sync drift) — by setting up proto sync CI gate

**Research flags:** NEEDS research-phase — Rust Axum + tonic integration patterns, grpclib Python gRPC setup, SQLx PostgreSQL migrations

### Phase 15: Rust WebSocket Hub + Orchestration Canvas (2-3 weeks)
**Rationale:** Real-time monitoring is table stakes for orchestration platforms. Extends existing React Flow DAG (Nexus) with Paperclip-style canvas. WebSocket hub is Rust's strength (Tokio concurrency).

**Delivers:** Rust WebSocket server (tokio-tungstenite), Redis pub/sub for cross-service broadcast, React Flow canvas with real-time brain status updates, ping animation, live DAG illumination.

**Addresses:** Real-time Hub (FEATURES.md), Orchestration Canvas (FEATURES.md), Rust WebSocket infrastructure (STACK.md)

**Avoids:** Pitfall #7 (Observability gaps) — by adding distributed tracing BEFORE building canvas

**Research flags:** NEEDS research-phase — Tokio-tungstenite WebSocket patterns, Redis pub/sub integration, React Flow real-time updates

### Phase 16: Multi-channel Gateway — WhatsApp + Instagram + Email (3-4 weeks)
**Rationale:** Pymes LATAM use WhatsApp as primary channel. Multi-channel is competitive differentiator vs Agentify. Python SDKs for adapters are mature, Rust for routing.

**Delivers:** WhatsApp Business Cloud API integration, Instagram Graph API, Email gateway (aiosmtplib), unified inbox UI (Paperclip `RunTranscript` pattern), Brain #8 channel router, webhook queue + dead letter queue.

**Addresses:** Multi-channel Gateway (FEATURES.md), Adapter pattern (ARCHITECTURE.md), webhook reliability (PITFALLS.md)

**Avoids:** Pitfall #4 (Webhook message loss) — by building webhook queue + DLQ BEFORE connecting to real WhatsApp API

**Research flags:** NEEDS research-phase — WhatsApp Business API webhook format, Meta Graph API authentication, rate limiting patterns

### Phase 17: Knowledge Distillation Engine (3-4 weeks)
**Rationale:** MOAT — no competitor has expertise destilada embebida. Leverages existing `experience_records`, `brain_memory.py`, 7 brain agents. Pull forward from original PRP Phase 5 (was too late).

**Delivers:** Experience analytics dashboard, pattern extraction (NLP for grouping similar interactions), Brain #7 auto-evaluation loop, delta-velocity tracking (metric: improvement vs baseline), template generation (successful interactions → reusable templates).

**Addresses:** Knowledge Distillation (FEATURES.md), learning loop (ARCHITECTURE.md), RAG quality (PITFALLS.md)

**Avoids:** Pitfall #6 (RAG quality degradation) — by building success filters BEFORE logging first experience

**Research flags:** SKIP research-phase — leverages existing infrastructure (experience_records, brain_memory.py), well-understood patterns

### Phase 18: Template Marketplace + Enterprise (CONDITIONAL — 4-6 weeks)
**Rationale:** Scale to multiple verticals. **BLOCKED until:** 3 LATAM SME interviews completed + 1 LOI signed. If gate not met → defer to v3.1+.

**Delivers:** Multi-tenant RBAC (per-organization isolation), template marketplace UI (Clipmart-style gallery), one-click deploy (templates por vertical), enterprise adapters (Odoo, Notion, custom webhooks), billing + usage tracking.

**Addresses:** Template Marketplace (FEATURES.md), multi-tenant (ARCHITECTURE.md), build trap prevention (PITFALLS.md)

**Avoids:** Pitfall #8 (Marketplace before validation) — by LOI gate BEFORE writing marketplace code

**Research flags:** NEEDS research-phase (if gate passed) — Multi-tenant RBAC patterns, billing infrastructure, template versioning system

### Phase Ordering Rationale

**Why this order:**
1. **Foundation first** — Phase 13 (UX) establishes visual foundation, Phase 14 (Vertical Slice) validates 3-service architecture. No backend work until architecture proven.
2. **Real-time before multi-channel** — Phase 15 (WebSocket Hub) enables real-time monitoring, required for Phase 16 (Multi-channel) webhook processing visibility.
3. **Knowledge before marketplace** — Phase 17 (Knowledge Distillation) generates templates from learned patterns, Phase 18 (Marketplace) distributes those templates. Marketplace needs content before launch.
4. **Conditional gate** — Phase 18 (Marketplace) blocked by LOI. Prevents build trap (engineering without validation).

**Dependency graph:**
```
Phase 13 (UX) → Phase 14 (Vertical Slice) → Phase 15 (WebSocket Hub)
                                      ↓
                               Phase 16 (Multi-channel)
                                      ↓
                               Phase 17 (Knowledge)
                                      ↓
                         Phase 18 (Marketplace - CONDITIONAL)
```

**How this avoids pitfalls:**
- **Strangler Fig Pattern** (Pitfall #1) — Phases 13-18 migrate incrementally, each delivers user-facing value
- **Type Sync** (Pitfall #2) — Phase 14 sets up proto sync CI gate before any gRPC services
- **PostgreSQL Migration** (Pitfall #3) — Phase 14 tests against PostgreSQL from day 1
- **Vite → Next.js** (Pitfall #5) — Phase 13 treats as pattern extraction, not code copy
- **Webhook Reliability** (Pitfall #4) — Phase 16 builds webhook queue + DLQ before WhatsApp API
- **Build Trap** (Pitfall #8) — Phase 18 blocked by LOI gate

### Research Flags

**Phases likely needing deeper research during planning:**
- **Phase 14 (Vertical Slice):** Rust Axum + tonic integration patterns, grpclib Python gRPC setup, SQLx PostgreSQL migrations, Protobuf codegen workflow
- **Phase 15 (WebSocket Hub):** Tokio-tungstenite WebSocket patterns, Redis pub/sub integration, React Flow real-time updates with WebSocket
- **Phase 16 (Multi-channel):** WhatsApp Business API webhook format, Meta Graph API authentication, rate limiting patterns, email gateway (aiosmtplib) integration
- **Phase 18 (Marketplace):** Multi-tenant RBAC patterns, billing infrastructure, template versioning system (if LOI gate passed)

**Phases with standard patterns (skip research-phase):**
- **Phase 13 (UX Extraction):** Well-documented Next.js Server Components + Client Components split, Paperclip code available for reference
- **Phase 17 (Knowledge Distillation):** Leverages existing infrastructure (experience_records, brain_memory.py, 7 brain agents), well-understood analytics patterns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Official docs verified (Axum, Tokio, tonic, SQLx), but WebSearch unavailable — some version numbers based on training data |
| Features | MEDIUM | Project docs HIGH confidence, but WebSearch limit reached — competitive analysis based on available docs only |
| Architecture | HIGH | Clear 3-service split, validated against existing v2.2 codebase (14.5K LOC Python, 15.8K LOC TypeScript), Strangler Fig Pattern well-established |
| Pitfalls | HIGH | Project context (v2.2 technical debt, BRAIN-FEED anti-patterns) + established software engineering patterns (Big Bang Rewrite failures, SQLite vs PostgreSQL differences) |

**Overall confidence:** MEDIUM

### Gaps to Address

**WebSearch unavailable** (weekly/monthly limit exhausted at 2026-04-13 18:30:03). Some findings based on:
- Project documentation (HIGH confidence — read directly)
- Official library docs (HIGH confidence — verified)
- General software engineering knowledge (MEDIUM confidence — established patterns)
- Training data (LOW confidence — version numbers may be outdated)

**Gaps to validate during implementation:**
- **Rust Python integration patterns:** tonic + grpclib specifics (verify with official docs before Phase 14)
- **WhatsApp Business API webhook reliability:** Meta platform specifics (verify during Phase 16 research-phase)
- **pgvector performance at scale:** Vector DB benchmarks (defer to v3.1+ — not needed for v3.0)
- **Multi-channel architecture patterns:** WhatsApp + IG + email integration (verify during Phase 16 research-phase)

**Mitigation:** Use Context7 MCP server for library docs during phase planning. Vertical slice (Phase 14) will validate Rust velocity vs Python before full commitment.

## Sources

### Primary (HIGH confidence)
- **Project Context Files** (read directly):
  - `.planning/PROJECT.md` — Existing v2.2 stack, technical debt, known issues
  - `.planning/BRAIN-FEED.md` — Anti-patterns tried and rejected (v2.2)
  - `docs/nuevo giro/PRP MasterMind v3.0.md` — Stack DEFINITIVO, Rust/Python split, escape hatch
  - `docs/nuevo giro/PAPERCLIP-UX-AUDIT.md` — 10 UX patterns to extract
  - `/home/rpadron/proy/paperclip/` — Source code analysis (competitive intelligence)

- **Official Documentation** (verified):
  - [Axum Documentation](https://docs.rs/axum/latest/axum/) — Rust web framework
  - [Tokio Documentation](https://docs.rs/tokio/latest/tokio/) — Async runtime
  - [tonic Documentation](https://docs.rs/tonic/latest/tonic/) — gRPC Rust implementation
  - [SQLx Documentation](https://docs.rs/sqlx/latest/sqlx/) — Compile-time checked SQL
  - [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/) — Database migrations
  - [Next.js App Router](https://nextjs.org/docs/app) — Official Next.js docs
  - [pgvector GitHub](https://github.com/pgvector/pgvector) — Vector similarity extension
  - [sentence-transformers](https://www.sbert.net/) — Text embeddings

### Secondary (MEDIUM confidence)
- **Established Software Engineering Patterns:**
  - Strangler Fig Pattern (Martin Fowler) — Incremental migration strategy
  - Big Bang Rewrite Failures (Netscape case study) — Cautionary tale
  - SQLite vs PostgreSQL differences — Type strictness, case sensitivity, transaction isolation
  - Webhook Best Practices — Idempotency, dead letter queues, write-first-process-later
  - gRPC + Protobuf Type Sync — Single-source truth, codegen workflow

### Tertiary (LOW confidence)
- **WebSearch unavailable** (limit exhausted) — Some findings based on:
  - Training data (version numbers may be outdated)
  - General knowledge of Rust/Python/TypeScript ecosystems
  - Project documentation + codebase analysis

**Recommendation:** Verify with Context7 MCP server during phase planning. Vertical slice (Phase 14) will validate Rust velocity before full commitment.

---
*Research completed: 2026-04-04*
*Ready for roadmap: yes*
*Next step: `/mm:new-milestone` to create v3.0 roadmap with automatic brain validation*
