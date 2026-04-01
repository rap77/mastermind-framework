# BRAIN-FEED-04 — Frontend Domain Feed

> Written by Brain #4 (Frontend). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-03-28

---

## State & Rendering Engine

- `Map<brainId, BrainState>` in Zustand — O(1) lookups, Immer for immutable updates
- `useBrainState(id)` targeted selector — prevents cascade re-renders (not `useStore()`)
- RAF batching in `brainStore` (not WS handler) — queues burst events, drains before paint
- WS is a module singleton (`wsDispatcher`) — lazy init inside `connect()` action, `typeof window` guard
- **React Compiler: DISABLED** — double-memoization conflicts with `React.memo` on React Flow nodes
- **No inline NODE_TYPES** — always module level, no exceptions
- **No layout recalculation on WS events** — positions are locked after dagre runs
- **WS updates touch only `data` prop of nodes** — never positions, never topology

---

## React Flow Internals

- `NODE_TYPES` declared at **module level** (never inline in JSX) — prevents infinite re-render loop
- `EDGE_TYPES` same rule
- dagre layout runs **once** via `useState` initializer — never recalculate on WS updates
- nodes array is layout-only — brain state comes from `brainStore` directly
- React Flow CSS in `globals.css @layer base` — Tailwind 4 silently breaks handles otherwise

---

## Performance & Quality Radar

- `cookies()` is async in Next.js 16 — `await cookies()` required
- React Flow CSS in `@layer base` — without this, edge handles break silently
- Zustand RAF batching prevents dropped frames when 24 brains fire simultaneously
- `CLUSTER_CONFIGS` data-driven array — add niches without touching component code
- TanStack Query `staleTime: 30s` — brains config is stable data, no refetch on focus
- Animation policy (LOCKED): opacity + transform ONLY — width/height causes layout reflow and will be rejected

---

## Anti-patterns (Frontend)

- `useStore()` for brain state → use `useBrainState(id)` targeted selector
- WS reconnect on every render → use module singleton with ref counting
- Inline `NODE_TYPES` in JSX → use module-level constant
- Recalculate dagre on data update → lock positions after first dagre run
- `tailwind.config.js` → use `@theme` in globals.css (no CSS-only config support in v4)
- ICE Scoring prevents over-engineering — only implement animations with ICE ≥ 15

---

## SYNC Cross-References

Sync: WS token handoff protocol — [SYNC: BF-05-001] → BRAIN-FEED-05-backend.md > Auth & Security. Frontend must know the /api/auth/token handshake sequence. Owner: Brain #5 Backend.
Sync: httpOnly cookie confirmation — [SYNC: BF-05-002] → BRAIN-FEED-05-backend.md > Auth & Security. Frontend must NOT attempt JS cookie read. Owner: Brain #5 Backend.
Sync: Zod API contracts — [SYNC: BF-05-003] → BRAIN-FEED-05-backend.md > API Design. Confirmed: apps/web/src/types/api.ts + login/actions.ts. Frontend validates API responses with Zod — needs contract shape. Owner: Brain #5 Backend.
Sync: Error response standard — [SYNC: BF-05-004] → BRAIN-FEED-05-backend.md > API Design. Frontend maps 500/429 to user messages — needs the shape. Owner: Brain #5 Backend.

---

## 2026-03-31 — Agent Restructuring Plan Review (Phase 12)

### Verified Insights

**WS Architecture — actual file is wsStore.ts (NOT wsDispatcher.ts)**
- wsDispatcher.ts does not exist in this codebase. The WS singleton is wsStore.ts (useWSStore, Zustand store with pub/sub)
- wsStore dispatches by msg.type → subscriber handlers. New event types = new subscribe() call, NOT a new store file
- All WS validation happens in WSBrainBridge via WSMessageSchema.safeParse — silent fail path silently discards events that don't match the schema

**Actual WS event type is 'task_update_batch' (not 'status_change')**
- WSMessageSchema: z.literal('task_update_batch') — must be widened to discriminated union for brain_routing
- BrainEventSchema has no 'result' field — completed events today carry no payload. Silent data loss if result lands unschema'd.

**brain_routing event — recommended approach**
- DO NOT add a second top-level subscribe() call that bypasses Zod validation
- Widen WSMessageSchema to z.discriminatedUnion('type', [...existing, BrainRoutingEventSchema])
- Handle in WSBrainBridge as a second subscribe block in the same component — maps from/to to brainStore status transitions
- brain_routing must update data props only — NEVER positions (dagre locked after first run)

**brainStore — result field needed, routing chain NOT needed**
- Add result?: Record<string, unknown> to BrainState interface
- DO NOT add Map<taskId, RoutingChain> — routing is transient topology, not persistent state
- historyStack already snapshots routing transitions with no changes needed
- RISK: large result objects in brainStore bloat historyStack snapshots — store result_ref only, fetch full on demand

**New Zod schemas required**
- BrainRoutingEventSchema: { type: 'brain_routing', from: string, to: string, sub_task_id: uuid }
- ExperienceSchema: { id: uuid, output_json: record(unknown), duration_ms: nonneg int, status: enum, custom_metadata?: record(unknown) }
- ExperiencesResponseSchema: array of ExperienceSchema
- result field in BrainEventSchema: result?: record(unknown) — optional to avoid breaking idle/active/error events

**New /api/experiences proxy**
- Pattern: follow /api/executions/[id]/route.ts verbatim — await params, await cookies(), proxy with Bearer token
- TanStack Query staleTime: 30s (same as brains config — stable data)

### Deferred Items

📅 If result objects grow beyond ~10KB, evaluate moving result storage out of brainStore.brains Map to avoid historyStack memory bloat — relevant when Phase 12 ships and real results start flowing
