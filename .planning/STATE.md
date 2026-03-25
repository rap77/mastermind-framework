---
gsd_state_version: 1.0
milestone: v2.1
milestone_name: War Room Frontend
status: complete
stopped_at: "v2.1 ARCHIVED — milestone complete, ready for /gsd:new-milestone v2.2"
last_updated: "2026-03-25T00:00:00.000Z"
last_activity: 2026-03-25 — v2.1 milestone archived, tagged, RETROSPECTIVE.md created
progress:
  total_phases: 4
  completed_phases: 4
  total_plans: 16
  completed_plans: 21
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-18)

**Core value:** Expert AI collaboration that scales — real-time visual war room for 24 AI brains
**Current focus:** v2.1 Phase 5 — Foundation, Auth & WebSocket Infrastructure

## Current Position

Phase: 7 of 8 (The Nexus) — Plan 3 of 3 COMPLETE (awaiting human checkpoint)
Plan: 07-03 (WS Illumination)
Status: Phase 07-03 complete ✅ — Wave 3 done, awaiting human visual verification checkpoint
Last activity: 2026-03-22 — Phase 07-03 COMPLETE (2 tasks, 21 tests, 7 files modified)

Progress: [██████████] 100% (31/28 plans complete)

## Performance Metrics

**Velocity (v2.0 baseline):**
- Total plans completed (v2.0): 17
- Average duration: 30 min/plan
- Total execution time: ~8.5 hours

**v2.1 By Phase (targets):**

| Phase | Plans | Status |
|-------|-------|--------|
| 05 Foundation + WS | 5 | 5/5 complete (05-00, 05-01, 05-02, 05-03, 05-04) |
| 06 Command Center | 3 | 3/3 complete (06-01, 06-02, 06-03) |
| 07 The Nexus | 3 | 3/3 complete (07-01, 07-02, 07-03) ✅ |
| 08 Vault + Engine Room | 4 | Not started |

**Plan durations:**
| Phase 05-foundation-auth-ws P00 | 15 | 6 tasks | 17 files |
| Phase 05-foundation-auth-ws P01 | 30 | 3 tasks | 9 files |
| Phase 05-foundation-auth-ws P02 | 24 | 5 tasks | 10 files |
| Phase 05-foundation-auth-ws P03 | 18 | 6 tasks | 8 files |
| Phase 05-foundation-auth-ws P04 | 77 | 1 tasks | 1 files |
| Phase 06 P02 | 52 | 4 tasks | 16 files |
| Phase 06-command-center P03 | 2843 | 4 tasks | 14 files |
| Phase 07-the-nexus P01 | 5 | 2 tasks | 2 files |
| Phase 07-the-nexus P02 | 7 | 3 tasks | 13 files |
| Phase 07-the-nexus P03 | 12 | 2 tasks | 7 files |
| Phase 08-strategy-vault-engine-room P01 | 14 | 7 tasks | 20 files |
| Phase 08-strategy-vault-engine-room P02 | 12 | 7 tasks | 14 files |
| Phase 08-strategy-vault-engine-room P03 | 11 | 8 tasks | 15 files |
| Phase 08-strategy-vault-engine-room P04 | 26 | 7 tasks | 15 files |
| Phase 08-strategy-vault-engine-room P05 | 12 | 3 tasks | 3 files |

## Accumulated Context

### Decisions

Key v2.1 architecture decisions (full log in PROJECT.md):
- [v2.1]: Vitest over Jest — ESM-native, faster, better Next.js 16 integration (05-00)
- [v2.1]: Co-located __tests__ directories — tests beside source files for discoverability (05-00)
- [v2.1]: Next.js 16 + React 19 + Tailwind 4 — all versions verified, no tailwind.config.js (CSS-only config) (05-01)
- [v2.1]: shadcn/ui Nova preset (base-ui) with OKLCH color system — modern, perceptually uniform (05-01)
- [v2.1]: React Flow CSS must be in globals.css @layer base (not tsx imports) — Tailwind 4 silently breaks handles otherwise (05-01)
- [v2.1]: Zustand 5 for WS dispatcher (module singleton) + brainStore (Map<brainId, BrainState> + Immer)
- [v2.1]: WS lazy init (inside connect() action, typeof window guard) — module-level crashes SSR at build time
- [v2.1]: JWT verified at Server Components + Route Handlers (not only proxy.ts) — CVE-2025-29927 mitigation
- [v2.1]: RAF batching for WS burst events (24 brains completing simultaneously = 24 setState calls outside React 19 auto-batching)
- [v2.1]: nodes array in React Flow is layout-only (never mutates) — brain state read from brainStore directly
- [Phase 05-foundation-auth-ws]: Next.js 16 + React 19 + Tailwind 4 scaffolded with OKLCH colors
- [Phase 05-foundation-auth-ws]: React Flow CSS in @layer base prevents Tailwind 4 cascade bug
- [Phase 05-foundation-auth-ws P02]: jose for JWT verification (Edge Runtime compatible, not jsonwebtoken)
- [Phase 05-foundation-auth-ws P02]: httpOnly cookie storage (mitigates XSS vs localStorage)
- [Phase 05-foundation-auth-ws P02]: Dual-layer JWT verification (proxy.ts + AuthGuardLayout) mitigates CVE-2025-29927
- [Phase 05-foundation-auth-ws P02]: React 19 useActionState pattern for Server Actions
- [Phase 05-foundation-auth-ws P02]: FastAPI CORS explicit origins (wildcard + credentials prohibited)
- [Phase 05-foundation-auth-ws P03]: Manual parity Zod schema generator (not OpenAPI auto-generation) — simpler, no backend introspection
- [Phase 05-foundation-auth-ws P03]: RAF batching in brainStore (not WS handler) — queues 24 events, drains before paint, maintains 60fps
- [Phase 05-foundation-auth-ws P03]: useBrainState(id) targeted selector — prevents cascade re-renders, O(1) Map lookup
- [Phase 05-foundation-auth-ws P03]: WS token handoff via /api/auth/token — server-side cookie read, token not in client bundle
- [Phase 05-foundation-auth-ws P03]: Immer middleware for Map<brainId, BrainState> — structural sharing, immutable updates
- [Phase 06]: TanStack Query v5 for server state with 30s staleTime
- [Phase 06]: ICE Scoring validated animations: only pulse, checkmark, shake implemented (glow, scan deferred)
- [Phase 06]: Data-driven clustering via CLUSTER_CONFIGS array for extensibility
- [Phase 06]: Eager Loading pattern for N+1 prevention: single query fetches all brains with niche field
- [Phase 07-the-nexus]: GraphEdge drops from_node/alias — source/target direct fields match React Flow Edge type
- [Phase 07-the-nexus]: layout_positions always null in v2.1 — client dagre layout, field stubbed for Phase 08 backend-driven layout
- [Phase 07-the-nexus]: NODE_TYPES_EXPORT named export from NexusCanvas — allows test isolation to verify module-level reference stability without rendering canvas
- [Phase 07-the-nexus]: dagreGraph module-level singleton with clearNode/clearEdge before each call — guarantees positional stability across multiple getLayoutedNodes invocations
- [Phase 07-the-nexus]: enableMapSet() in brainStore — Immer requires MapSet plugin for Map iteration in set() callbacks (new Map(state.brains) fails silently without it)
- [Phase 07-the-nexus]: EDGE_TYPES at module level in NexusCanvas — same invariant as NODE_TYPES, prevents infinite re-render in React Flow; EDGE_TYPES_EXPORT added for test isolation
- [Phase 08-strategy-vault-engine-room]: INSERT OR IGNORE for execution_writer concurrency — first writer wins, 24 simultaneous brain completions handled without Redis
- [Phase 08-strategy-vault-engine-room]: Separate api_keys_v2 table with prefix/suffix/revoked_at — avoids migrating legacy api_keys, no breaking changes
- [Phase 08-strategy-vault-engine-room]: GraphEdge sub-graph as optional field on existing TaskGraphResponse — backward compat with Phase 07 NexusCanvas
- [Phase 08-strategy-vault-engine-room]: smart-gfm.tsx extension (not .ts): JSX components require .tsx — OXC rejects JSX in .ts files in Vite
- [Phase 08-strategy-vault-engine-room]: LogsPanel shows all outputs at index 0: full history visible at start of replay, filter only on active scrub
- [Phase 08-strategy-vault-engine-room]: NotFoundError custom class for 404 detection in TanStack Query retry logic — allows 404 to redirect vs 5xx to error state
- [Phase 08-strategy-vault-engine-room]: react-virtuoso for O(1) memory virtual scroll in Engine Room logs (overscan=10)
- [Phase 08-strategy-vault-engine-room]: Empty filterLevels Set = show nothing (all levels toggled off = zero logs, not pass-through)
- [Phase 08-strategy-vault-engine-room]: logFilterStore: manual JSON serialization for Set (avoids Zustand persist middleware Set issue)
- [Phase 08-strategy-vault-engine-room]: framer-motion replaced with CSS transitions: not installed, Tailwind transition classes achieve equivalent layout shift
- [Phase 08-strategy-vault-engine-room]: OrchestratorStore isFocusMode computed inline per action (state===running && !userOverride) — no selector middleware needed for scalar state
- [Phase 08-strategy-vault-engine-room]: KeyCreateDialog show-once: createdKey in React state only, cleared on handleClose, never reaches localStorage
- [Phase 08-strategy-vault-engine-room]: Phase08Integration uses store-level integration (not full app mount) — avoids Next.js router complexity in jsdom while verifying real store interactions
- [Phase 08-strategy-vault-engine-room]: useBrainStore.setState() direct override in tests — RAF batching makes updateBrain() non-deterministic in test environment

### Pending Todos

None for v2.1 yet. v2.0 known items:
- Fix 3 coordinator tests with timestamp flakiness (non-critical)
- YAML export implementation incomplete (technical debt)

### Blockers/Concerns

- **BE-01 gap:** `GET /api/brains` endpoint MISSING from FastAPI — must be added in Phase 6 plan 06-01 before Bento Grid can use live data
- **BE-02 validation:** `GET /api/tasks/{id}/graph` exists but exact React Flow Node/Edge compatibility needs verification — Phase 7 plan 07-01
- **React Compiler:** Leave disabled for v2.1 — double-memoization conflicts with React.memo on React Flow nodes unvalidated

## Session Continuity

Last session: 2026-03-24T11:37:52.487Z
Stopped at: Completed 08-05: Integration Tests — Phase 08 COMPLETE, v2.1 COMPLETE
Resume file: None

**Phase 05 Results:**
- Plans completed: 5/5 (05-00, 05-01, 05-02, 05-03, 05-04 gap closure)
- UAT: 13/13 passing
- Verification: 8/8 requirements
- Gap closed: Immer mutation error in brainStore
- Technical debt: 6 items documented

Next command: `/gsd:plan-phase 06-command-center` (plan Phase 06)
OR: `/gsd:execute-phase 06-command-center` (if plans already exist)
