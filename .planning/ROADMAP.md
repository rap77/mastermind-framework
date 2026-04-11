# Roadmap: MasterMind v3.0

**Milestone:** Enterprise Agent Orchestration Platform with Knowledge Distillation for LATAM
**Defined:** 2026-04-05
**Phase Start:** 13 (v2.2 ended at Phase 12)
**Granularity:** Coarse

## Phases

- [ ] **Phase 13: Vertical Slice** — Prove 3-service architecture (Next.js → Rust → gRPC → Python)
- [x] **Phase 14: Knowledge Distillation** — Auto-learning loop with existing 7 brains (completed 2026-04-06)
- [x] **Phase 15: Rust Control Plane** — PostgreSQL + JWT auth + event sourcing (completed 2026-04-07)
- [ ] **Phase 16: Observability + Real-time Hub** — Cross-service logging + WebSocket infrastructure
- [ ] **Phase 17: UI Evolution** — Extract Paperclip UX patterns, rebuild in Next.js
- [x] **Phase 18: Multi-channel Gateway** — WhatsApp + Instagram + Email unified inbox (completed 2026-04-11)

## Phase Details

### Phase 13: Vertical Slice

**Goal:** Validate 3-service architecture works end-to-end before committing to full Rust build

**Depends on:** Nothing (first phase of v3.0)

**Requirements:** VS-01, VS-02, VS-03

**Success Criteria** (what must be TRUE):

1. User can trigger one API path (`POST /api/tasks/auto`) from Next.js → Rust (Axum) → gRPC → Python (FastAPI) → response → UI renders result
2. Single `.proto` file generates types for Rust (tonic + prost), Python (grpclib), and TypeScript (ts-proto) without manual type definitions
3. Rust velocity is measured against Python baseline — if < 0.5x Python at midpoint, escape hatch activates (Rust only for WebSocket Hub + Adapter Registry)
4. PostgreSQL 16 + pgvector is running in development with all 620 existing tests passing (dual-write migration: SQLite + PostgreSQL simultaneously)

**Plans:**

4/4 plans executed
- [ ] 13-02-PLAN.md — Protobuf contract + Rust Control Plane project setup
- [ ] 13-03-PLAN.md — Backend vertical slice: Python gRPC + Rust client + PostgreSQL + Axum handler
- [ ] 13-04-PLAN.md — Frontend integration + Docker Compose + velocity report

---

### Phase 14: Knowledge Distillation

**Goal:** Brains learn from every interaction and accumulate expertise over time

**Depends on:** Nothing (can run in parallel with Phase 13)

**Requirements:** KD-01, KD-02, KD-03

**Success Criteria** (what must be TRUE):

1. Brain #7 automatically evaluates every brain output → feedback → adjusts brain memory after each orchestration session
2. Delta-velocity tracking shows improvement vs T1 baseline (210-270s target) — operators see brains getting faster
3. Successful interactions automatically generate reusable templates — Brain #1 suggests templates based on recurring patterns across sessions
4. Dashboard shows: recurring patterns per brain, insights over time, correlation analysis between brains, delta-velocity trends

**Plans:** 4/4 plans complete

- [ ] 14-01-PLAN.md — Quality score + rejection filter + TTL (Foundation)
- [ ] 14-02-PLAN.md — High-value detection + post-session hook (Auto-evaluation loop)
- [ ] 14-03-PLAN.md — Template storage + extraction (Template generation)
- [ ] 14-04-PLAN.md — Dashboard API + metrics (Dashboard)

---

### Phase 15: Rust Control Plane

**Goal:** State management, auth, and event sourcing migrated to Rust with PostgreSQL

**Depends on:** Phase 13 (Vertical Slice validation)

**Requirements:** RCP-01, RCP-02, RCP-03

**Success Criteria** (what must be TRUE):

1. SQLite successfully migrates to PostgreSQL 16 + pgvector via dual-write strategy (no data loss, all 620 tests pass)
2. JWT auth + RBAC migrated from Python (jose) to Rust (Axum middleware) — role-based access control per organization, refresh token rotation preserved
3. Immutable `activity_log` table via event sourcing — every brain operation = event with brain_id, timestamp, type, payload for temporal queries and audit trail

**Plans:** 6/4 plans complete

- [ ] 15-01-PLAN.md — PostgreSQL 16 + pgvector foundation + Rust project structure (Wave 1)
- [ ] 15-02-PLAN.md — JWT auth + RBAC migrated from Python to Rust (Wave 2)
- [ ] 15-03-PLAN.md — SQLite → PostgreSQL migration via dual-write strategy (Wave 3)
- [ ] 15-04-PLAN.md — Immutable event sourcing for activity_log with temporal queries (Wave 4)

---

### Phase 16: Observability + Real-time Hub

**Goal:** Cross-service debugging visibility + real-time WebSocket infrastructure for monitoring

**Depends on:** Phase 15 (Rust Control Plane foundation)

**Requirements:** OBS-01, RTU-01

**Success Criteria** (what must be TRUE):

1. Structured logging (Rust tracing crate) + distributed tracing (trace_id propagated across Rust → gRPC Python → response) + health checks for all 3 services
2. Unified log format for debugging cross-service failures — operators can trace a single request across all 3 services
3. Rust WebSocket Hub (Tokio-tungstenite) handles thousands of concurrent connections without GC pauses — events: brain_started, brain_completed, brain_routed, brain_failed
4. Ghost Mode buffer (100-event replay) replicated in Tokio + Redis pub/sub for cross-service broadcast

**Plans:** 7 plans

- [ ] 16-01-PLAN.md — Structured logging (Rust tracing + Python structlog)
- [ ] 16-02-PLAN.md — Distributed tracing (trace_id propagation, gRPC interceptor)
- [ ] 16-03-PLAN.md — Health checks (liveness + readiness with dependency checks)
- [ ] 16-04-PLAN.md — WebSocket Hub foundation (tokio-tungstenite + bounded channels + max_connections ceiling)
- [ ] 16-05-PLAN.md — Ghost Mode buffer (in-memory ring buffer + replay endpoint)
- [ ] 16-06-PLAN.md — Metrics exposition (Prometheus `/metrics` endpoint)
- [ ] 16-07-PLAN.md — Load testing suite (k6 scripts for 1000 connections)

---

### Phase 17: UI Evolution

**Goal:** Extract Paperclip UX patterns and rebuild in Next.js 16 App Router (NOT a fork — Paperclip uses Vite)

**Depends on:** Phase 16 (Real-time Hub for WebSocket updates)

**Requirements:** UIE-01, UIE-02, UIE-03

**Success Criteria** (what must be TRUE):

1. Three-column layout (CompanyRail + Sidebar + Content) rebuilt in Next.js 16 with multi-tenant sidebar switcher and responsive mobile (swipe gestures, bottom nav)
2. Real-time agent monitoring panel with ping animation, status badges (idle/running/completed/failed), compact density modes — ActiveAgentsPanel pattern from Paperclip
3. Orchestration canvas extends existing React Flow Nexus with real-time WebSocket updates — cost dashboard with MetricCard per brain (tokens, duration, cost) and budget enforcement visual (QuotaBar pattern)

**Plans:** TBD

---

### Phase 18: Multi-channel Gateway

**Goal:** Unified inbox across WhatsApp + Instagram + Email with webhook reliability

**Depends on:** Phase 16 (Real-time Hub for webhook processing)

**Requirements:** MCG-01

**Success Criteria** (what must be TRUE):

1. WhatsApp Business Cloud API + Instagram Graph API + Email (aiosmtplib) adapters working — Rust handles webhooks + routing, Python handles AI processing
2. Webhook queue with dead letter queue (DLQ) for reliability — no dropped messages, operators can retry failed webhooks
3. Unified inbox UI across all channels — operators see WhatsApp, Instagram, and Email messages in one place
4. Channel Router (new brain agent) selects optimal channel for responses — automatic channel selection based on context

**Plans:** 8/10 plans executed

**Original Plans (Complete):**
- [x] 18-01-PLAN.md — Webhook receiver with HMAC verification, queue depth monitoring
- [x] 18-02-PLAN.md — DLQ with exponential backoff retry
- [x] 18-03-PLAN.md — E2E latency SLI measurement
- [x] 18-04-PLAN.md — WhatsApp adapter (parser + sender)
- [x] 18-05-PLAN.md — Instagram adapter (parser + sender)
- [x] 18-06-PLAN.md — Email adapter (parser + sender)
- [x] 18-07-PLAN.md — Unified inbox UI (3-pane layout)

**Gap Closure Plans (Created 2026-04-11):**
- [ ] 18-08-PLAN.md — Fix queue depth monitoring, webhook route registration, SQLX compilation (gaps #1, #2, #3, #14)
- [ ] 18-09-PLAN.md — Implement gRPC bridge, AI worker integration, delivery status tracking (gaps #4, #7, #10, #15)
- [ ] 18-10-PLAN.md — DLQ API endpoints, DOMPurify, thread merge UI, Channel Router (gaps #5, #6, #8, #9, #11, #12, #13)

**Gap Summary:** 15 verification gaps identified, grouped into 3 closure plans
- **Wave 1 (18-08):** Critical infrastructure blockers (queue depth, route registration, compilation)
- **Wave 2 (18-09):** gRPC bridge and integration gaps (AI worker, delivery status, E2E latency)
- **Wave 3 (18-10):** Feature gaps and security (DLQ API, DOMPurify, thread merge, Channel Router)
---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 13. Vertical Slice | 4/4 | Complete | ✅ 2026-04-05 |
| 14. Knowledge Distillation | 4/4 | Complete   | 2026-04-06 |
| 15. Rust Control Plane | 6/4 | Complete    | 2026-04-07 |
| 16. Observability + Real-time Hub | 0/7 | Not started | - |
| 17. UI Evolution | 0/3 | Not started | - |
| 18. Multi-channel Gateway | 8/10 | In Progress|  |

**Overall Progress:** 3/15 requirements delivered (20%)

---

## Traceability

All v3.0 requirements mapped to phases:

| Requirement | Phase | Status |
|-------------|-------|--------|
| VS-01 | Phase 13 | ✅ Complete |
| VS-02 | Phase 13 | ✅ Complete |
| VS-03 | Phase 13 | ✅ Complete |
| KD-01 | Phase 14 | Pending |
| KD-02 | Phase 14 | Pending |
| KD-03 | Phase 14 | Pending |
| RCP-01 | Phase 15 | Pending |
| RCP-02 | Phase 15 | Pending |
| RCP-03 | Phase 15 | Pending |
| OBS-01 | Phase 16 | Pending |
| RTU-01 | Phase 16 | Pending |
| UIE-01 | Phase 17 | Pending |
| UIE-02 | Phase 17 | Pending |
| UIE-03 | Phase 17 | Pending |
| MCG-01 | Phase 18 | Pending |

**Coverage:** 15/15 requirements mapped ✓

---

## Key Constraints

From Brain #1 + Brain #7 validation:

1. **NOT a fork** — Paperclip uses Vite (incompatible with Next.js App Router). Extract 10 UX patterns and rebuild.
2. **Knowledge Distillation first** — Leverages existing 7 brains + brain_memory.py + experience_records. Zero Rust needed.
3. **Vertical Slice validates architecture** — Proves 3-service split before committing to full Rust build.
4. **Rust escape hatch** — If velocity < 0.5x Python, Rust only for WebSocket Hub + Adapter Registry.
5. **Marketplace is CONDITIONAL** — Requires 3 LATAM SME interviews + 1 LOI — NOT in this milestone.
6. **Strangler Fig Pattern** — Incremental migration, NOT Big Bang rewrite.

---
*Roadmap created: 2026-04-05*
*Last updated: 2026-04-07 (Phase 16 plans: 7 plans ready)*
*Ready for execution: `/mm:execute-phase 16`*
