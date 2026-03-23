# Roadmap: MasterMind Framework

## Milestones

- ✅ **v2.0 Production Platform** — Phases 1–4 (shipped 2026-03-17)
- 🚧 **v2.1 War Room Frontend** — Phases 5–8 (in progress)
- 📋 **v2.2 Brain Agents** — Autonomous subagents per brain, two-level BRAIN-FEED, inter-agent coordination
- 📋 **v3.0 Custom Workflow Framework + RAG** — Replace GSD, declarative DSL, pluggable agents, per-agent vector stores
- 📋 **v3.1 OpenClaw Integration** — Brain agents as OpenClaw skills, omnichannel (22+ channels), voice, native apps

## Phases

<details>
<summary>✅ v2.0 Production Platform (Phases 1–4) — SHIPPED 2026-03-17</summary>

- [x] Phase 1: Type Safety Foundation (3/3 plans) — completed 2026-03-13
- [x] Phase 2: Parallel Execution Core (4/4 plans) — completed 2026-03-13
- [x] Phase 3: Web UI Platform (4/4 plans) — completed 2026-03-13
- [x] Phase 4: Experience Store & Production (5/5 plans) — completed 2026-03-14

See full details: `.planning/milestones/v2.0-ROADMAP.md`

</details>

### 🚧 v2.1 War Room Frontend (In Progress)

**Milestone Goal:** Replace Alpine.js/HTMX dashboard with a Next.js 16 war room — real-time visual orchestration of 24 AI brains across 4 screens.

- [x] **Phase 5: Foundation, Auth & WebSocket Infrastructure** — Next.js 16 scaffolded, auth gate working, WS dispatcher + BrainStore proven end-to-end against FastAPI ✅ (completed 2026-03-20)
- [x] **Phase 6: Command Center** — 24-brain Bento Grid with live status tiles + Raycast-style brief input modal ✅ (completed 2026-03-20)
- [ ] **Phase 7: The Nexus** — Real-time React Flow DAG visualization, nodes illuminate on WebSocket events
- [ ] **Phase 8: Strategy Vault, Engine Room & UX Polish** — Execution history, live logs, API key management, brain YAML config, Focus Mode

## Phase Details

### Phase 5: Foundation, Auth & WebSocket Infrastructure
**Goal**: Users can log in securely and the real-time WebSocket pipeline is proven end-to-end — every subsequent phase builds on this without revisiting auth, CSS cascades, or WS architecture.
**Depends on**: Phase 4 (v2.0 — FastAPI backend, JWT auth system, WebSocket server)
**Requirements**: FND-01, FND-02, FND-03, FND-04, SB-01, WS-01, WS-02, WS-03
**Success Criteria** (what must be TRUE):
  1. User can log in via the Next.js login page and land in the app with a JWT stored as an httpOnly cookie; accessing any protected route without a valid JWT redirects back to login
  2. `npm run build` completes without errors — React Flow CSS renders correctly (node handles and edges visible in production build), Magic UI @keyframes animations play, WebSocket initialization does not crash SSR
  3. The Zod schema generator runs and produces `apps/web/src/types/api.ts` matching current Pydantic models; a TypeScript error surfaces immediately when a backend model changes
  4. A single WebSocket connection is established on first navigation and survives client-side route changes with zero reconnects; 24 simultaneous brain events do not cause visible UI freeze (60fps maintained via RAF batching and per-brain Map selectors)
**Plans**: 4 plans created

Plans:
- [x] 05-00: Vitest testing infrastructure — 15 test scaffolds, config, setup.ts
- [x] 05-01: Scaffold Next.js 16 app (Tailwind 4, shadcn/ui new-york, Magic UI) — verify React Flow CSS in globals.css @layer base, animated component smoke test, `npm run build` clean
- [x] 05-02: Implement JWT auth gate — login page, httpOnly cookie token storage, proxy.ts route protection, JWT verification in Server Components (CVE-2025-29927 mitigation), FastAPI CORS with allow_credentials=True
- [x] 05-03: Build Zod schema bridge (SB-01) + Zustand stores (wsStore singleton, brainStore with Immer + Map<brainId, BrainState>) + WSBrainBridge + RAF batching — prove WS→BrainStore pipeline end-to-end against FastAPI backend with real brain events
- [x] 05-04: Fix Immer mutation error in brainStore RAF batching — wrap _queue mutations inside set() callback for mutable draft

### Phase 6: Command Center
**Goal**: Users can submit a brief via the war room's command interface and watch 24 AI brain tiles update in real-time on the Bento Grid — the core orchestration loop is visible and interactive.
**Depends on**: Phase 5
**Requirements**: BE-01, CC-01, CC-02, CC-03
**Success Criteria** (what must be TRUE):
  1. `GET /api/brains` returns all 24 brains with name, niche, status, uptime, and last_called_at — the Bento Grid renders from live API data, not hardcoded fixtures
  2. User sees all 24 brain tiles in the Bento Grid with live status (idle / active / complete / error) fed from WebSocket events; status updates without a page reload
  3. Brain tiles animate on status changes: pulse during active execution, checkmark on completion, red indicator on error — animations do not drop below 60fps when all 24 update simultaneously
  4. User can open the brief input modal with Cmd+Enter, type a multi-line brief, and submit it — the modal is full-screen (not a single-line command palette), and submission triggers a real task in the backend
**Plans**: 3 plans created

Plans:
- [x] 06-01: Add `GET /api/brains` endpoint to FastAPI backend (apps/api/) — source from brain_registry.py, return name/niche/status/uptime/last_called_at, add tests ✅
- [x] 06-02: Build Command Center page — Magic UI Bento Grid with 24 brain tiles, per-brain Zustand selectors (useBrainState(id)), status color classes and CSS animations ✅
- [x] 06-03: Build brief input modal — shadcn/ui Command + cmdk + multi-line textarea, Cmd+Enter shortcut, POST /api/tasks integration, WS connection initiation on task start ✅

### Phase 7: The Nexus
**Goal**: Users can watch the exact dependency graph of running brains illuminate in real-time — nodes glow as brains activate and complete, and clicking a node reveals brain details without interfering with canvas navigation.
**Depends on**: Phase 6
**Requirements**: BE-02, NEX-01, NEX-02, NEX-03
**Success Criteria** (what must be TRUE):
  1. `GET /api/tasks/{id}/graph` returns a React Flow compatible payload with `{ nodes[], edges[], layout_positions }` including initial node positions
  2. User sees a DAG of brain dependencies as a React Flow graph with custom shadcn/ui Card nodes positioned via dagre layout — the graph reflects the actual dependency structure and loads from the API
  3. Nodes illuminate in real-time as brains execute: border color and glow change on brain WebSocket events — illumination causes no layout shifts or pan resets during execution
  4. User can click a node to view brain details without accidentally triggering drag or pan — all interactive elements inside nodes use `nodrag nopan` CSS classes
**Plans**: 3 plans created

**Plans:** 2/3 plans executed

Plans:
- [ ] 07-01-PLAN.md — FastAPI graph endpoint adapter: add layout_positions field, fix edge source/target field names for React Flow compatibility
- [ ] 07-02-PLAN.md — NexusCanvas: dagre layout (mount-once), NODE_TYPES at module level, BrainNode (React.memo + nodrag/nopan), NodeDetailPanel, NexusSkeleton, CooldownFAB, /nexus page
- [ ] 07-03-PLAN.md — WS illumination: HybridFlowEdge state machine, brainStore historyStack + sessionInvocationCounts, Cooldown Mode, brief submission → /nexus navigation

### Phase 8: Strategy Vault, Engine Room & UX Polish
**Goal**: Users can audit past executions with formatted brain outputs, monitor live logs with filtering, manage API keys, inspect brain YAML config, and enter Focus Mode during active execution — the war room is complete.
**Depends on**: Phase 7
**Requirements**: SV-01, SV-02, ER-01, ER-02, ER-03, UX-01
**Success Criteria** (what must be TRUE):
  1. User can view a paginated list of past executions showing status, brief text, duration, and brain count; selecting an execution reveals formatted Markdown output from each participating brain in an accordion layout with copy-to-clipboard per brain
  2. User can view live structured logs in the Engine Room with virtual scrolling, filter by log level (info/warn/error), and toggle auto-follow — powered by react-logviewer connected to the WebSocket log stream
  3. User can manage API keys: view masked keys, create a new key (shown once in full), and revoke an existing key
  4. User can view the YAML configuration of any brain and copy it to clipboard
  5. User can activate Focus Mode during active execution — the sidebar collapses, idle brain tiles dim, and active execution elements are highlighted
**Plans**: 4 plans created

Plans:
- [ ] 08-01: Build Strategy Vault — execution list with pagination (status/brief/duration/brain count), individual execution view (accordion per brain, react-markdown, copy-to-clipboard)
- [ ] 08-02: Build Engine Room logs — react-logviewer wired to WS log events, level filtering (info/warn/error), auto-follow toggle, download as .txt
- [ ] 08-03: Build Engine Room config — API key management (list/create/revoke, show-once pattern), brain YAML viewer with clipboard copy
- [ ] 08-04: Implement Focus Mode (UX-01) — sidebar collapse, idle tile dimming, active execution element highlighting

## Progress

**Execution Order:** 5 → 6 → 7 → 8

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Type Safety Foundation | v2.0 | 3/3 | Complete | 2026-03-13 |
| 2. Parallel Execution Core | v2.0 | 4/4 | Complete | 2026-03-13 |
| 3. Web UI Platform | v2.0 | 4/4 | Complete | 2026-03-13 |
| 4. Experience Store & Production | v2.0 | 5/5 | Complete | 2026-03-14 |
| 5. Foundation, Auth & WS Infrastructure | v2.1 | 5/5 | ✅ Complete | 2026-03-20 |
| 6. Command Center | v2.1 | 3/3 | ✅ Complete | 2026-03-20 |
| 7. The Nexus | 2/3 | In Progress|  | - |
| 8. Strategy Vault, Engine Room & UX Polish | v2.1 | 0/4 | Not started | - |

---

### 📋 v2.2 Brain Agents (after v2.1)

**Milestone Goal:** Convert brain consultations from manual skill workflows to autonomous Claude Code subagents. Each agent embeds the intermediary protocol, maintains domain-specific memory, and accumulates expertise across phases.

**Evolution path:** `mm:brain-context` workflows (v2.1) → agent system prompts (v2.2). No work is thrown away.

**Key changes:**
- 7 brain subagents (`.claude/agents/brain-NN-*.md`) with built-in intermediary protocol
- Two-level BRAIN-FEED: `BRAIN-FEED.md` (project general) + `BRAIN-FEED-NN-*.md` (per-brain domain)
- Orchestrator dispatches agents in parallel (today: Claude follows workflows sequentially)
- Each agent filters responses against code and updates its domain feed autonomously
- Inter-agent coordination for cross-domain decisions (API contracts, state ownership)

**Phases:** TBD — will be planned as `/gsd:new-milestone v2.2` after v2.1 ships.

### 📋 v3.0 Custom Workflow Framework + RAG (future)

**Milestone Goal:** Replace GSD with MasterMind's own niche-agnostic workflow framework. Keep GSD's proven patterns (goal-backward, wave parallelization, atomic commits, deviation rules). Add brain integration at every gate, declarative DSL, pluggable agents, and niche-specific flow templates. Plus per-agent RAG for persistent brain memory.

**Research completed:** `.planning/research/GSD-FRAMEWORK-ANALYSIS.md` — full GSD architecture analysis (12 agents, 5 layers, strengths, limitations, 6 extension points identified).

**Key differentiators vs GSD:**
- Declarative orchestration DSL (YAML workflows instead of 300+ line bash scripts)
- Pluggable agent registry (add agents without touching orchestrator code)
- Brain integration layer (intermediary protocol at every workflow gate)
- Domain-agnostic verification (pluggable anti-pattern detectors per niche)
- Niche-specific flow templates (software dev, marketing, design, content — not just code)
- Custom checkpoint types (brain-approval, customer-feedback, stakeholder-review)
- Per-agent RAG (ChromaDB/Qdrant) — domain knowledge + project memory in separate collections
- Persistent brain expertise across projects

**Phases:** TBD — requires v2.2 agent infrastructure. GSD analysis provides the blueprint.

---
*Roadmap updated: 2026-03-22 — v2.2 and v3.0 milestones added (architectural vision)*
