# 104. Definitive Operating Roadmap

## 1. Purpose

Consolidate the fragmented roadmap, canonical architecture, and runtime state into one operating document that answers:

- what is already done
- what is half-done
- what is missing
- what should be done next
- what must be true before the next step

This document is the working reconciliation layer. It does not replace the other canonical docs; it orders them.

## 2. Source Priority

When documents disagree, use this order:

1. Active `.planning/changes/<objective>/execution-state.json` plus its objective package
2. `.planning/HANDOFF-CURRENT.md` and `.planning/roadmap/*`
3. `.planning/FRAMEWORK-STATUS.md`
4. `docs/canonical/*` architecture and contract docs
5. `.planning/.mm-flow/runtime-state.json` and phase-specific closure summaries as legacy phase state
6. `.planning/ROADMAP.md` and `.planning/ROADMAP-v3.2.md` as historical snapshots

## 3. Audit Result

### 3.1 Reliable facts

- v2.2 is shipped and stable.
- Phases 13-17 have historical closure artifacts. Phase 18's broad completion
  claim is superseded by the narrower, evidence-backed canonical ingest status.
- Phase 19 formal closure exists in `19-05-SUMMARY.md` and declares Phase 20 unblocked.
- The canonical architecture layer for harnesses, loops, memory, registry, and selector policy already exists in `docs/canonical/`.

### 3.2 State drift

- `SOURCE-OF-TRUTH.md` and `ROADMAP.md` lag behind newer phase summaries.
- `ROADMAP-v3.2.md` defines the next major execution lane, but it is not the only active planning source.
- Legacy `runtime-state.json` shows phase 21 in an execution wave, but the
  objective-package workflow currently has `multi-channel-gateway` active. The
  legacy phase lane must not override objective activation state.
- The objective roadmap already marks several earlier objectives as done/canonized, including the project-state / collaboration / dashboard / scheduler family.

## 4. State by Category

### 4.1 Implemented

| Item | Type | Evidence | Status |
|---|---|---|---|
| v2.2 autonomous brain agents | runtime | `SOURCE-OF-TRUTH.md`, `PROJECT.md` | shipped |
| Parallel dispatch + BRAIN-FEED split | runtime | `SOURCE-OF-TRUTH.md` | shipped |
| UI / WebSocket / auth / base platform | runtime | `SOURCE-OF-TRUTH.md` | shipped |
| Phase 13: Vertical Slice | milestone | `ROADMAP.md` | complete |
| Phase 14: Knowledge Distillation | milestone | `ROADMAP.md` | complete |
| Phase 15: Rust Control Plane | milestone | `ROADMAP.md` | complete |
| Phase 16: Observability + Real-time Hub | milestone | `ROADMAP.md`, `SOURCE-OF-TRUTH.md` | complete |
| Phase 17: UI Evolution | milestone | `ROADMAP.md`, `SOURCE-OF-TRUTH.md` | complete |
| Phase 18: Multi-channel Gateway | milestone | canonical `116`, active objective package | canonical WhatsApp ingest implemented/tested; broad gateway deferred |
| Phase 19 closure (MM-Flow) | milestone | `19-05-SUMMARY.md` | complete |
| Core harness/loop/memory/registry canon | docs | `63`, `64`, `65`, `67`, `68`, `71`, `73`, `100`, `102`, `103` | canonized |
| Objective-roadmap foundation set | docs | `objective roadmap + canonical docs` | canonized |

### 4.2 Halfway

| Item | Why halfway | Needed next |
|---|---|---|
| v3.2 RAG lane | runtime is already in phase 21, but the phase 20/21 package is not canonically packaged | one authoritative execution package |
| Phase 20-21: pgvector + LangSmith + RAG pilot | roadmap exists, but the code-level slice and phase summaries are not unified here | implementation, tests, runtime instrumentation, phase backfill |
| Loop selector implementation | spec scaffold exists, code does not | selector service + tests + runtime envelope wiring |
| Selection/telemetry coupling | docs exist, runtime wiring is partial | persist selection history and cost/quality metadata |

### 4.3 Missing

| Item | Why missing | Blocker |
|---|---|---|
| Code-level reusable `LoopSelector` | current work is documentation/spec level | implementation slice not started in code |
| Full harness runtime using the canonical contracts | contracts exist, runtime binding does not | need first executable slice |
| RAG per agent scale-out | roadmap defined, not yet fully executed here | Phase 20-23 chain |
| Cross-brain learning v3.3 | explicitly deferred | OEC + SLI gates on v3.2 |

## 5. Definitive Operating Order

This is the logical execution order I recommend going forward.

### 5.1 Core

1. Project state and memory
2. Capability registry
3. Runtime envelope
4. Source registry and evidence lineage

Acceptance for this layer:
- state is resumable
- memory is project-scoped
- registry is machine-readable
- every run emits a structured envelope

### 5.2 Harnesses

1. Discovery Harness
2. Design Harness
3. Implementation Harness
4. Verification Harness
5. Review Harness
6. Recovery Harness
7. Archive Harness

Acceptance for this layer:
- each harness declares inputs, outputs, and supported loops
- the selector can choose the smallest safe harness
- verification and recovery are explicit

### 5.3 Loops

1. Tool Loop
2. Goal Loop
3. Verification Loop
4. Reflection Loop
5. Review Loop
6. Recovery Loop
7. Heartbeat Loop
8. Canonization Loop

Acceptance for this layer:
- loop choice is deterministic for the same context
- ambiguity routes to discovery/clarification
- every loop has a clear exit condition

### 5.4 Selection and Routing

1. Classify objective
2. Check risk, scope, budget, and approvals
3. Query registry
4. Query memory
5. Rank candidates
6. Select minimum sufficient harness + loop
7. Emit selection envelope

Acceptance for this layer:
- selection is explainable
- no hidden fallback
- alternatives are recorded
- token minimization is respected

### 5.5 Telemetry and Verification

1. Token/cost/quality telemetry
2. Verification gates
3. Review gates
4. Recovery when needed

Acceptance for this layer:
- costs are tracked per run and per objective
- quality is measurable, not anecdotal
- rework is visible

### 5.6 Domain Expansion

1. RAG per agent
2. RAG evaluation gate
3. Knowledge ingestion
4. RAG scale-out
5. Cross-brain learning

Acceptance for this layer:
- Brain #1 proves the pattern first
- contamination is prevented
- recall and latency gates pass before scale-out

## 6. Phase Ledger

### 6.1 Historical closed phases and reconciled Phase 18

#### Phase 13 - Vertical Slice
- Deliverable: 3-service end-to-end slice
- Pre-reqs: none
- Acceptance: Next.js -> Rust -> gRPC -> Python round-trip, single proto, performance escape hatch defined, PostgreSQL baseline verified

#### Phase 14 - Knowledge Distillation
- Deliverable: auto-learning loop and reusable templates
- Pre-reqs: phase 13 validation
- Acceptance: Brain #7 evaluates outputs, templates are generated, deltas are tracked

#### Phase 15 - Rust Control Plane
- Deliverable: PostgreSQL + JWT + event sourcing
- Pre-reqs: phase 13
- Acceptance: dual-write migration, auth migration, immutable activity log

#### Phase 16 - Observability + Real-time Hub
- Deliverable: structured logging, tracing, WebSocket hub
- Pre-reqs: phase 15
- Acceptance: traceability across services, real-time events, ghost mode replay, load readiness

#### Phase 17 - UI Evolution
- Deliverable: Next.js App Router UI rebuilt from extracted patterns
- Pre-reqs: phase 16
- Acceptance: three-column layout, realtime monitoring panel, orchestration canvas, mobile behavior

#### Phase 18 - Multi-channel Gateway
- Deliverable proven: secure WhatsApp inbound text canonical ingest
- Pre-reqs: phase 16
- Acceptance proven: raw-byte authenticity, canonical normalization, atomic durable persistence before ACK, concurrency/failure/readiness/observability tests
- Deferred: Instagram/Email, outbound, inbox/read APIs, dispatcher/worker recovery,
  deletion worker, subject access, application-level encryption and production
  retention/at-rest approval

#### Phase 19 - MM-Flow + Audit Trail
- Deliverable: workflow bridge, context persistence, audit trail, formal closure
- Pre-reqs: phases 01-04 of phase 19
- Acceptance: `19-05-SUMMARY.md` exists, Phase 19 closure is declared complete, Phase 20 is unblocked

### 6.2 Next phases

#### Phase 20 - pgvector Schema + LangSmith Foundation
- Deliverables: `brain_embeddings`, HNSW index, runtime `sentence-transformers`, `similarity_search()`, LangSmith instrumentation, OEC baseline
- Prereqs: pgvector active, runtime dependencies ready, baseline measurement sessions available
- Acceptance: all success criteria in `ROADMAP-v3.2.md` are met

#### Phase 21 - RAG Pilot (Brain #1 only)
- Deliverables: `domain_knowledge` retrieval, `project_memory` retrieval, explicit retrieved context injection, latency tracing
- Prereqs: Phase 20
- Acceptance: top-5 domain recall, top-3 memory recall, P99 latency within budget, `rag_enabled: true`

#### Phase 21.5 - RAG Evaluation Gate
- Deliverables: A/B test, recall@5 validation, contamination checks, quality delta measurement
- Prereqs: Phase 21
- Acceptance: RAG beats cold baseline by required quality delta and stays under latency ceiling

#### Phase 22 - Knowledge Ingestion (Manual)
- Deliverables: idempotent ingest script, two collections per brain, ingestion report
- Prereqs: Phase 21.5 gate passed
- Acceptance: 7 brains × 2 collections populated and queryable

#### Phase 23 - RAG Scale-Out
- Deliverables: RAG enabled for brains 2-7, LangSmith cost/latency reporting, guardrails
- Prereqs: Phase 22
- Acceptance: Recall@5 and quality delta pass across all brains

### 6.3 Deferred

- Cross-brain learning v3.3
- Template marketplace / multi-tenant expansion
- Any objective not yet gated by current evidence thresholds

## 7. Implementation Recommendation

If the goal is to stop fragmenting the project, the next practical move is:

1. treat this document as the operating roadmap
2. treat `docs/canonical/README.md` as the index
3. treat phase-specific summaries as the executable truth for in-flight work
4. stop using legacy roadmaps as independent sources of planning authority

## 8. Exit Criteria

This document is complete when:

- implemented, halfway, and missing are unambiguous
- the phase order is clear
- prerequisites and acceptance criteria are explicit
- the source hierarchy is documented
- no roadmap fragment is being used as a hidden source of truth
