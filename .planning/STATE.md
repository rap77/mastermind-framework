# MM-Flow Milestone State Tracker

**Tracker:** `.planning/STATE.md` (Global milestone state)
**Last Updated:** 2026-05-14

---

## Current Status

**Operational objective overlay (2026-07-14):** `multi-channel-gateway` remains
active until its canonical WhatsApp ingest slice is archived. MCG0-MCG6 are
implemented/tested; production rollout remains disabled pending retention approval
and at-rest verification. After MCG6, archive this objective and then run the
dedicated next-objective activation command.

```yaml
---
milestone: v3.2
current_phase: 0
overall_status: PLANNING
last_action:
  actor: "Milestone v3.1 closed (2026-05-14)"
  what: "All 98 subtasks complete, 100% acceptance criteria verified, services running live"
  timestamp: "2026-05-14T00:00:00Z"
  next_step: "Archive multi-channel-gateway, then activate the next objective through the dedicated command"
```

---

## Milestone History

### v3.1 — CLOSED ✅ (2026-05-14)

**Scope:** Observability + Intelligent Orchestration + UI Evolution

| Task | Name | Subtasks | Status |
|------|------|----------|--------|
| A | Foundation Integrity | 16 | ✅ COMPLETE |
| B | Observability Core | 35 | ✅ COMPLETE |
| C | Intelligent Orchestration | 57 | ✅ COMPLETE |
| D | UI Evolution | 20 | ✅ COMPLETE |

**Test suite at close:** 1111 Python + 950 Frontend = 2061 total, 0 failures
**Services:** api:8001, rust:3001, web:3002, postgres:5434 — all healthy

**Key deliverables:**
- `trace_id` propagated end-to-end (Next.js → Rust → Python)
- WebSocket Hub: real-time brain state events
- `brain_registry` PostgreSQL (7 brains, no hardcoded dict)
- Multi-provider dispatch (Anthropic / OpenRouter / Z.ai) with quality/balanced/budget profiles
- Brain #7 post-session evaluation + `quality_score` + `ExperienceLogger`
- `/orchestrate` — three-column War Room (BrainList + OrchestrationCanvas + OutputPanel + StatusTimeline)
- Auto backend-switch when token budget depleted

### v3.0 — HISTORICAL MILESTONE CLOSURE (2026-04-15)

The original milestone was closed from phase artifacts. The broad Phase 18 claim
was later superseded: only the canonical WhatsApp inbound text slice is currently
implemented/tested, while production enablement and broader gateway scope remain
deferred. Phase 19 subsequently closed 5/5.

### v2.2 — CLOSED ✅ (2026-03-30)

Brain agents + BRAIN-FEED two-level architecture. Tag: `v2.2`.

---

## Next: v3.2 Candidates

| Priority | Item | Description |
|----------|------|-------------|
| 🔴 HIGH | Phase 20 | Start v3.2 execution (pgvector schema + LangSmith foundation) |
| 🔴 HIGH | RAG per agent | Each brain manages its own vector store (ChromaDB/Qdrant) |
| 🟡 MEDIUM | Patterns dashboard | Brain #7 accumulated data — visualize in UI |
| 🟡 MEDIUM | Cross-brain learning | Brains share successful patterns via BRAIN-FEED |
| 🟢 CONDITIONAL | Template Marketplace | Requires 3 LATAM SME interviews + 1 LOI first |
