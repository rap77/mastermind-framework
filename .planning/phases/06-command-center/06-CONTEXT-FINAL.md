# Phase 06: Command Center - Final Context

**Status:** ✅ Ready for Planning
**Brain-07 Veredict:** CONDITIONAL APPROVAL (Score: 8.5/10)
**Date:** 2026-03-20

---

## Executive Summary

Phase 06 construye el **Command Center** — Bento Grid visual de 24 cerebros con modal de brief input. Los usuarios pueden ver el estado en vivo de los cerebros y enviar briefs desde interfaz estilo Raycast.

**Arquitectura Validada:** El Orquestador (brain-08) decide QUÉ cerebros interactúan (3-6 típicos), no los 24 simultáneamente. Esto resuelve las preocupaciones de performance y carga cognitiva.

---

## Core Architecture Decisions

### 1. Orquestador-Driven Activation

**Brain-08 (Master Interviewer) Role:**
- Analiza el brief del usuario
- Decide QUÉ cerebros se necesitan según el caso
- Solo cerebros ACTIVOS se destacan con neones/animaciones
- Resto permanece idle o colapsado en sus nichos

**Impact on Phase 06:**
- Bento Grid asume subset activo (no todos animados)
- WebSocket lifecycle manejado por Orquestador
- Max concurrent connections: 3-6 (típico), 8-10 (peak)

### 2. Niche-Based Progressive Disclosure

**Nichos como unidades (no tiles individuales):**
- Master (1): zinc-100 — Steady Pulse
- Software (7): cyan-400 — Scanning Line
- Marketing (16): purple-500 — Glow Expansion

**User Interactions:**
- Collapse/expand nichos enteros
- Solo cerebros ACTIVOS en interacción actual se destacan
- Idle: minimalista, ghost context
- Active: eleva (2x1 o 2x2), revela métricas

### 3. Hybrid State Management

**Zustand 5 (Client) + TanStack Query (Server):**
- `brainStore` (Map-based): Client state, clustering, UI transitions
- TanStack Query: Server state sync, caching, GET /api/brains

**WebSocket Integration:**
- Orquestador managea connect/disconnect
- Solo cerebros activos tienen WS connection
- RAF batching para burst events (probado en Phase 05)

---

## Technical Stack (Validated by Brains)

### Frontend (brain-04)
- **Framework:** Next.js 16 (App Router) + React 19
- **Components:** WarRoomDashboard, ClusterGroup, BrainTile, BrainDetailModal
- **Styling:** Tailwind 4 + shadcn/ui + Magic UI (BorderBeam)
- **State:** Zustand 5 + TanStack Query v5
- **Performance:** INP < 200ms, 60fps (opacity/transform only)

### Backend (brain-05)
- **Architecture:** Clean + Screaming (domain-driven)
- **Data Models:** Brain, BrainStatusUpdate, CommandCenterRegistry
- **API:** Hybrid REST (initial sync) + WebSocket (real-time)
- **Auth:** JWT RS256, Refresh Tokens rotativos

### QA/DevOps (brain-06)
- **Testing:** Test Pyramid (70% unit / 20% integration / 10% E2E)
- **Tools:** Vitest, Pytest, Playwright, k6
- **SLOs:** p99 frame rate > 55fps
- **CI/CD:** Trunk-Based + Feature Flags + Canary (1% → 10% → 100%)

### UX Research (brain-02)
- **Validated:** Niche-level disclosure > tile-level
- **Concern:** Ghost Context affordance (necesita signifier claro)
- **Mitigation:** prefers-reduced-motion guard (CRITICAL)

---

## Brain-07 Approval Conditions (Non-Blocking for Phase 06)

| # | Condición | Blocking? | Owner |
|---|-----------|-----------|-------|
| 1 | Guardrail Metrics (hard cap concurrent brains) | No | Orquestador (brain-08) |
| 2 | Pre-mortem selection logic + Manual Override | No | Orquestador (brain-08) |
| 3 | Checklist + Anti-patrones implementation | No | Framework |
| 4 | Reference Class Forecasting (UI scalability) | No | UX Research |

**Not Blocking:** Las condiciones 1-2 son sobre el Orquestador (fuera de Phase 06), 3 es framework-level, 4 puede iterarse post.

---

## Implementation Phases

### Phase 06 Scope (3 Plans)

**Plan 06-01:** GET /api/brains endpoint (Backend)
- Source from brain_registry.py
- Return: name, niche, status, uptime, last_called_at
- Tests: Pytest integration

**Plan 06-02:** Command Center page (Frontend)
- Bento Grid con semantic clustering
- Brain tiles con status animations
- per-brain Zustand selectors
- CSS animations (60fps)

**Plan 06-03:** Brief input modal (Frontend)
- shadcn/ui Command + cmdk
- Multi-line textarea auto-expand
- Cmd+Enter shortcut
- POST /api/tasks integration

### Out of Scope (Phase 07-08)
- The Nexus (DAG visualization)
- Strategy Vault (execution history)
- Engine Room (logs, config, API keys)
- Focus Mode

---

## Key Technical Decisions

**From Phase 05 (Re-used):**
- ✅ JWT auth (httpOnly cookies, CVE-2025-29927 mitigation)
- ✅ WebSocket proven end-to-end
- ✅ RAF batching for 60fps (Immer pattern learned)
- ✅ Zod schema bridge (types/api.ts)

**New for Phase 06:**
- ✅ Orquestador-driven activation (resolves WebSocket concern)
- ✅ Niche-level progressive disclosure (resolves cognitive load)
- ✅ TanStack Query for server state sync
- ✅ prefers-reduced-motion guard (accessibility)

---

## Risk Assessment

| Risk | Mitigation | Status |
|------|-----------|--------|
| Memory leaks (WS listeners) | Orquestador limita conexiones activas | ✅ Mitigated |
| Cognitive load (24 tiles) | Niche-level disclosure + subset activo | ✅ Mitigated |
| 60fps drop (animations) | opacity/transform only + RAF batching | ✅ Proven (Phase 05) |
| Ghost Context affordance | Signifiers en hover + testing | ⚠️ Needs validation |

---

## Success Criteria (From ROADMAP.md)

1. ✅ `GET /api/brains` returns all 24 brains — Bento Grid from live API data
2. ✅ User sees 24 brain tiles with live status via WebSocket
3. ✅ Brain tiles animate on status changes (60fps maintained)
4. ✅ User can open brief modal with Cmd+Enter and submit real task

---

## Next Steps

**Now:** `/gsd:plan-phase 06` — Create 3 implementation plans

**Inputs for gsd-planner:**
- This CONTEXT-FINAL.md
- BRAIN-02-FRONTEND-CONTEXT.md
- BRAIN-05-BACKEND-CONTEXT.md
- BRAIN-06-QA-CONTEXT.md
- BRAIN-07-EVALUATION-REVISED.md
- 06-CONTEXT.md (original UX decisions)

---

*Context validated by 5 expert brains + user clarification*
*Brain-07 Score: 8.5/10 — CONDITIONAL APPROVAL*
