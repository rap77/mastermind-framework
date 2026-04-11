# Requirements: MasterMind v3.0

**Defined:** 2026-04-05
**Core Value:** Enterprise agent orchestration platform with knowledge distillation from world-class experts for LATAM

## v3.0 Requirements

### Vertical Slice (VS) — Architecture Validation

- [x] **VS-01**: One API path round-trips end-to-end: Next.js → Rust (Axum) → gRPC → Python (FastAPI) → response → UI renders. Proves 3-service architecture works before committing to full Rust build.
- [x] **VS-02**: Single `.proto` source auto-generates types for Rust (tonic + prost), Python (grpclib), and TypeScript (ts-proto). Proto Sync CI gate prevents type drift across services.
- [x] **VS-03**: Rust velocity is measured against Python baseline during VS phase. If Rust velocity < 0.5x Python at midpoint, escape hatch activates: Rust only for WebSocket Hub + Adapter Registry, rest stays Python.

### Knowledge Distillation (KD) — Competitive Moat

- [ ] **KD-01**: Brain #7 evaluates every brain output → feedback → adjusts brain memory. Delta-Velocity tracking measures improvement vs T1 baseline (210-270s target). Auto-learning loop runs after each orchestration session.
- [x] **KD-02**: Successful interactions automatically generate reusable templates. Brain #1 suggests templates based on recurring patterns across sessions. Templates storeable in per-brain knowledge base.
- [ ] **KD-03**: Dashboard shows: recurring patterns per brain, insights over time, correlation analysis between brains, delta-velocity trends. Operators see what brains learned and how expertise accumulates.

### Rust Control Plane (RCP) — Foundation

- [x] **RCP-01**: SQLite migrates to PostgreSQL 16 + pgvector. Dual-write migration strategy (SQLite + PostgreSQL simultaneously → read migration → primary switch → SQLite removal). SQLx compile-time verified queries. All 620 existing tests pass against PostgreSQL.
- [ ] **RCP-02**: JWT auth + RBAC migrated from Python (jose) to Rust (Axum middleware). Role-based access control per organization. Refresh token rotation preserved. CVE-2025-29927 mitigation replicated in Rust.
- [ ] **RCP-03**: Immutable `activity_log` table via event sourcing. Every brain operation = event with brain_id, timestamp, type, payload. Temporal queries for analytics. Audit trail across all services.

### UI Evolution (UIE) — Paperclip Pattern Extraction

- [ ] **UIE-01**: Three-column layout (CompanyRail + Sidebar + Content) extracted from Paperclip UX audit, rebuilt in Next.js 16 App Router. Multi-tenant sidebar switcher. Responsive mobile (swipe gestures, bottom nav).
- [ ] **UIE-02**: Real-time agent monitoring panel with ping animation, status badges (idle/running/completed/failed), compact density modes. ActiveAgentsPanel pattern from Paperclip, adapted for brain agents.
- [ ] **UIE-03**: Orchestration canvas extends existing React Flow Nexus with real-time WebSocket updates. Cost dashboard with MetricCard per brain (tokens, duration, cost). Budget enforcement visual (QuotaBar pattern).

### Observability (OBS) — Cross-Service

- [ ] **OBS-01**: Structured logging (Rust tracing crate) + distributed tracing (trace_id propagated across Rust → gRPC → Python → response) + health checks for all 3 services. Unified log format for debugging cross-service failures.

### Real-time Hub (RTU) — WebSocket Infrastructure

- [ ] **RTU-01**: Rust WebSocket Hub (Tokio-tungstenite) replaces FastAPI WebSocket. Handles thousands of concurrent connections without GC pauses. Events: brain_started, brain_completed, brain_routed, brain_failed. Ghost Mode buffer (100-event replay) replicated in Tokio. Redis pub/sub for cross-service broadcast.

### Multi-channel Gateway (MCG) — LATAM Focus

- [x] **MCG-01**: WhatsApp Business Cloud API + Instagram Graph API + Email (aiosmtplib) adapters. Rust handles webhooks + routing, Python handles AI processing. Webhook queue with dead-letter queue (DLQ) for reliability. Unified inbox across all channels. Channel Router (new brain agent) for optimal channel selection.

## v3.1+ Requirements (Deferred)

### Template Marketplace + Enterprise

- **TMP-01**: Clipmart-style template gallery with pre-built agent configurations per vertical (Software Dev Agency, Marketing Agency, Customer Support)
- **TMP-02**: Multi-tenant isolation via PostgreSQL RLS (row-level security) per company_id
- **TMP-03**: Billing + usage tracking with provider-level cost breakdown
- **TMP-04**: Enterprise adapters: Odoo, Notion, custom webhook

### Advanced RAG

- **RAG-01**: Per-agent vector stores (ChromaDB/Qdrant) — domain knowledge (books) + project memory (accumulated patterns) in separate collections
- **RAG-02**: Cross-brain learning via shared project BRAIN-FEED patterns

## Out of Scope

| Feature | Reason |
|---------|--------|
| Machine learning auto-improvement | Requires R&D, beyond v3.0 scope |
| Mobile native apps | Web-first, mobile responsive only |
| Real-time collaborative editing | v4.0+ |
| Celery/RQ task queues | asyncio sufficient for single-host |
| Full RAG with separate vector DB | pgvector sufficient for <10M vectors in v3.0 |
| Vite frontend (Paperclip) | Incompatible with Next.js App Router — patterns extracted, code NOT copied |
| Big Bang rewrite | Strangler Fig pattern mandatory — incremental migration |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| VS-01 | Phase 13 | Complete |
| VS-02 | Phase 13 | Complete |
| VS-03 | Phase 13 | Complete |
| KD-01 | Phase 14 | Pending |
| KD-02 | Phase 14 | Complete |
| KD-03 | Phase 14 | Pending |
| RCP-01 | Phase 15 | Complete |
| RCP-02 | Phase 15 | Pending |
| RCP-03 | Phase 15 | Pending |
| OBS-01 | Phase 16 | Pending |
| RTU-01 | Phase 16 | Pending |
| UIE-01 | Phase 17 | Pending |
| UIE-02 | Phase 17 | Pending |
| UIE-03 | Phase 17 | Pending |
| MCG-01 | Phase 18 | Complete |

**Coverage:**
- v3.0 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-05*
*Last updated: 2026-04-05 after roadmap creation with 6 phases (13-18)*
