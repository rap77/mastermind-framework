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

## 2026-04-05 — Phase 13 Vertical Slice: Frontend Architecture Decisions

### Verified Insights

**Vertical slice path: POST /api/tasks (Server Action in actions/tasks.ts)**
- ROADMAP specifies POST /api/tasks/create — maps to createTask() Server Action
- Single-line change: swap FASTAPI_URL -> RUST_GATEWAY_URL on line 66 of actions/tasks.ts
- Validates full chain: user action -> Server Action -> Rust -> gRPC -> Python -> response -> UI -> WS
- GET /api/brains would be WRONG — it only validates Server Component read, not user action round-trip

**TanStack Query IS used in codebase (corrected earlier assumption)**
- 5 Client Components use useQuery/useMutation: ExecutionDetail, ExecutionList, APIKeyManager, KeyListTable, KeyCreateDialog
- Server Components (command-center, nexus) use fetchBrains() from lib/api.ts directly
- Two distinct data-fetching patterns coexist already: Server-only (lib/api.ts) and Client-side (TanStack Query)
- For vertical slice: NO TanStack Query change needed — task creation is a Server Action mutation

**Type coexistence strategy: proto-generated types in new directory, NOT replacing types/api.ts**
- types/api.ts has 9 hand-written Zod schemas used across 17+ files
- Vertical slice response shape is { task_id: string } — trivially simple
- New types/proto/ directory for generated types — zero existing file changes
- Runtime validation: derive Zod schema from proto type at the Route Handler boundary

**Rust gateway URL configuration: RUST_GATEWAY_URL env var, NOT next.config.ts rewrites**
- Rewrites cannot read httpOnly cookies and transform into Authorization headers
- Each Route Handler / Server Action already has its own API_URL variable — surgical migration per path
- Server Actions keep reading cookies server-side, add Bearer token, call Rust instead of Python
- Global API_URL change would break all paths — violates Strangler Fig

**Testing: Integration test for Server Action + one E2E smoke test**
- MSW is WRONG for Server Actions (they run server-side, not browser) — use real test server instead
- Integration: mock RUST_GATEWAY_URL to test Axum server, verify round-trip
- E2E: one Playwright test for brief submission -> task created -> WS channel opens
- Performance observable: measure round-trip vs Python-direct baseline, target < 50ms overhead

**Architecture implication: current proxy pattern is EXACTLY right for Strangler Fig**
- Server Actions = security boundary (read httpOnly cookie, add Bearer token)
- Route Handlers = same pattern for client-initiated fetches
- Phase 15 migration = URL swap per handler, zero architecture changes

### Deferred Items
📅 When Phase 15 migrates ALL paths to Rust, consider removing FASTAPI_URL entirely and unifying on RUST_GATEWAY_URL
📅 When proto-generated types grow complex (multiple services), evaluate Zod schema auto-generation from .proto definitions
📅 TanStack Query's staleTime (30s for brains, 60s for executions) may need adjustment when Rust gateway introduces latency — measure and tune in Phase 16

## 2026-04-08 — Phase 17 Frontend Architecture Consultation

### Verified Insights

**1. Multi-tenant State (companyStore) — localStorage sync + Tab coordination**
- Use Zustand `persist` middleware with `createJSONStorage` (handles JSON serialization)
- Cross-tab sync: Listen to browser `storage` event in store initialization, merge on `company-context` key changes
- Active company switching: `activeCompanyId` update → `queryClient.invalidateQueries({ queryKey: ['company-context'] })` → TanStack Query refetches all dependent queries
- Pattern follows `layoutStore.ts`: Immer + persist + targeted selectors (`useActiveCompany()`, `useCompanyList()`)
- State structure: `Map<companyId, CompanyState>` wrapped in Immer for O(1) lookups without cascade re-renders

**2. Drag-and-Drop (@dnd-kit) — Isolate from React Flow pan/zoom**
- `@dnd-kit` NOT in package.json — requires pnpm add (no npm violation)
- Critical isolation: Sortable container needs `touch-action: none` + `stopPropagation` on pointer events to prevent React Flow canvas interaction
- Performance at 24+ companies: Wrap reordering logic in `useTransition()` (React 19 concurrent feature) — keeps UI responsive while DOM reflows in background
- Note: React 19 concurrent features NOT yet used in codebase (grep verified zero `useTransition`/`useDeferredValue`) — this is new for Phase 17

**3. ActiveAgentsPanel Performance — Extend brainStore RAF pattern**
- Reuse existing `brainStore.ts` RAF batching: 16ms drain cycle, max 24 events per frame
- Each agent row uses `useBrainState(id)` targeted selector — O(1) Map lookup prevents cascade re-renders across 24 rows
- NO separate RAF loop needed — extend existing `_drainQueue()` to handle agent panel events
- Render budget: 60fps = 16.67ms per frame. 24 brain updates × ~0.5ms each = ~12ms total, safe within budget

**4. Cost Data Sourcing — Rust event sourcing, not Python API**
- Source from Rust `activity_log` table (event-sourced, consistent with agent actions)
- Avoid Python aggregation layer — introduces latency vs direct Rust reads
- Caching: TanStack Query with `staleTime: 30s` + `refetchInterval: 60s` for quota-critical metrics
- SWR pattern: Show cached MetricCard immediately, background refetch updates when data arrives
- Existing `react-query.tsx` already configured: staleTime 30s, gcTime 5min, refetchOnWindowFocus false

**5. Command Palette (Cmd+K) — Radix Command + async indexing**
- Radix UI components: `@base-ui/react` v1.3.0 already in package.json (Base UI, not Radix UI — shadcn Nova preset uses Base UI primitives)
- For Command component specifically: Need to verify if Command exists in Base UI or use `cmdk` library (not in package.json today)
- Keyboard shortcut: Global `useEffect` with `addEventListener('keydown')`, MUST include cleanup function to prevent memory leaks
- Async indexing: If content > 1000 items, use Web Worker for search index building — prevents main thread jank
- Search input: Use `useDeferredValue` (React 19) to prioritize typing responsiveness over list updates

**6. Mobile Gestures — Pointer Events + touch-action isolation**
- Use Pointer Events (not Touch Events) for unified mouse/touch/stylus handling
- React Flow conflict resolution: `touch-action: pan-y` on side panels, `touch-action: none` on drag handles
- Prevent viewport scroll interference: Block `wheel`/`touchmove` propagation when user interacts with graph canvas
- Animations: CSS transforms + opacity only (GPU compositor) — never width/height (causes layout reflow)
- Existing `touch-action` usage found in `NexusPage.tsx` + button/input components — pattern established

### Implementation Gaps (Verified via Grep)

🔴 **Missing libraries for Phase 17:**
- `@dnd-kit` — Not in package.json, requires pnpm add
- Command palette library — `cmdk` or Radix Command not in package.json. Base UI v1.3.0 exists but Command component availability unknown
- `useTransition`/`useDeferredValue` — Zero usage in codebase today, new React 19 concurrent features for Phase 17

🔴 **Cross-tab sync pattern NOT established:**
- `layoutStore.ts` uses `persist` middleware but NO `storage` event listener for cross-tab sync
- Phase 17 companyStore must implement this pattern (not copy existing layoutStore)

✅ **Existing patterns confirmed:**
- RAF batching: `brainStore.ts` lines 44-66 — queue, drain, 16ms cycle
- Targeted selectors: `useBrainState(id)` pattern in brainStore, `useSidebarCollapsed()` in layoutStore
- TanStack Query: 12 files use `useQuery`/`useMutation`, provider configured in `react-query.tsx`
- Zustand + Immer: 6 stores use this pattern (brainStore, layoutStore, wsStore, orchestratorStore, logFilterStore, replayStore)

### Performance Observables

For each Phase 17 feature, measure before/after:

**Multi-tenant company switcher:**
- Metric: Time from company switch click to first data render (target < 100ms)
- Tool: React DevTools Profiler + `performance.now()` timestamps in store action

**Drag-and-drop company ordering:**
- Metric: Frames dropped during drag operation (target: 0 dropped frames at 60fps)
- Tool: Chrome DevTools Performance tab, record drag session, check "Frames" timeline

**ActiveAgentsPanel with 24 brains:**
- Metric: FPS during 24-brain simultaneous update (target: 60fps sustained)
- Tool: `console.time()` around `_drainQueue()` + React DevTools Profiler

**Cost dashboard (MetricCard + QuotaBar):**
- Metric: Time to interactive (TTI) with cached data (target < 50ms)
- Tool: Lighthouse "Performance" score + Chrome DevTools Network panel (verify SWR background refetch)

**Command palette:**
- Metric: Input lag when typing search query (target < 16ms per keystroke)
- Tool: `performance.mark()` before/after search filter, Chrome DevTools Performance "Main" thread

**Mobile gestures:**
- Metric: Gesture response time (target < 100ms from touchstart to visual feedback)
- Tool: Chrome DevTools Performance tab, record gesture, check "Event Timing" section

### Anti-Pattern Alerts

❌ **Don't use npm for @dnd-kit** — pnpm only (Stack Hard-Lock violation if using npm)

❌ **Don't create new RAF loop for agent panel** — reuse existing `brainStore._drainQueue()` pattern. Multiple RAF loops = frame budget fragmentation

❌ **Don't invalidate all queries on company switch** — use scoped `queryKey: ['company-context']` only. Broad invalidation = unnecessary refetch waterfall

❌ **Don't block main thread for command palette indexing** — if > 1000 items, use Web Worker. Main thread indexing = typing jank

❌ **Don't use width/height animations for mobile gestures** — transforms + opacity only (GPU compositor). Layout animations = reflow = dropped frames

❌ **Don't let React Flow capture all pointer events** — `stopPropagation()` on dnd-kit handlers, `touch-action` CSS on containers. Conflict = unusable drag/drop

### Sync Cross-References

[SYNC: BF-05-005] → BRAIN-FEED-05-backend.md > Cost Data Sources. Frontend needs Rust activity_log endpoint contract (shape, pagination, auth). Owner: Brain #5 Backend.

[SYNC: BF-05-006] → BRAIN-FEED-05-backend.md > Company Context API. Frontend needs `/api/companies` endpoint for multi-tenant list + active company switching. Owner: Brain #5 Backend.

[SYNC: BF-05-007] → BRAIN-FEED-05-backend.md > Real-time Cost Events. Should cost quota updates come via WS (from Rust event sourcing) or polling? Owner: Brain #5 Backend.

## 2026-04-08 — Phase 17 Frontend Architecture Consultation

### Verified Insights

**1. Multi-tenant State (companyStore) — localStorage sync + Tab coordination**
- Use Zustand `persist` middleware with `createJSONStorage` (handles JSON serialization)
- Cross-tab sync: Listen to browser `storage` event in store initialization, merge on `company-context` key changes
- Active company switching: `activeCompanyId` update → `queryClient.invalidateQueries({ queryKey: ['company-context'] })` → TanStack Query refetches all dependent queries
- Pattern follows `layoutStore.ts`: Immer + persist + targeted selectors (`useActiveCompany()`, `useCompanyList()`)
- State structure: `Map<companyId, CompanyState>` wrapped in Immer for O(1) lookups without cascade re-renders

**2. Drag-and-Drop (@dnd-kit) — Isolate from React Flow pan/zoom**
- `@dnd-kit` NOT in package.json — requires pnpm add (no npm violation)
- Critical isolation: Sortable container needs `touch-action: none` + `stopPropagation` on pointer events to prevent React Flow canvas interaction
- Performance at 24+ companies: Wrap reordering logic in `useTransition()` (React 19 concurrent feature) — keeps UI responsive while DOM reflows in background
- Note: React 19 concurrent features NOT yet used in codebase (grep verified zero `useTransition`/`useDeferredValue`) — this is new for Phase 17

**3. ActiveAgentsPanel Performance — Extend brainStore RAF pattern**
- Reuse existing `brainStore.ts` RAF batching: 16ms drain cycle, max 24 events per frame
- Each agent row uses `useBrainState(id)` targeted selector — O(1) Map lookup prevents cascade re-renders across 24 rows
- NO separate RAF loop needed — extend existing `_drainQueue()` to handle agent panel events
- Render budget: 60fps = 16.67ms per frame. 24 brain updates × ~0.5ms each = ~12ms total, safe within budget

**4. Cost Data Sourcing — Rust event sourcing, not Python API**
- Source from Rust `activity_log` table (event-sourced, consistent with agent actions)
- Avoid Python aggregation layer — introduces latency vs direct Rust reads
- Caching: TanStack Query with `staleTime: 30s` + `refetchInterval: 60s` for quota-critical metrics
- SWR pattern: Show cached MetricCard immediately, background refetch updates when data arrives
- Existing `react-query.tsx` already configured: staleTime 30s, gcTime 5min, refetchOnWindowFocus false

**5. Command Palette (Cmd+K) — Radix Command + async indexing**
- Radix UI components: `@base-ui/react` v1.3.0 already in package.json (Base UI, not Radix UI — shadcn Nova preset uses Base UI primitives)
- For Command component specifically: Need to verify if Command exists in Base UI or use `cmdk` library (not in package.json today)
- Keyboard shortcut: Global `useEffect` with `addEventListener('keydown')`, MUST include cleanup function to prevent memory leaks
- Async indexing: If content > 1000 items, use Web Worker for search index building — prevents main thread jank
- Search input: Use `useDeferredValue` (React 19) to prioritize typing responsiveness over list updates

**6. Mobile Gestures — Pointer Events + touch-action isolation**
- Use Pointer Events (not Touch Events) for unified mouse/touch/stylus handling
- React Flow conflict resolution: `touch-action: pan-y` on side panels, `touch-action: none` on drag handles
- Prevent viewport scroll interference: Block `wheel`/`touchmove` propagation when user interacts with graph canvas
- Animations: CSS transforms + opacity only (GPU compositor) — never width/height (causes layout reflow)
- Existing `touch-action` usage found in `NexusPage.tsx` + button/input components — pattern established

### Implementation Gaps (Verified via Grep)

🔴 **Missing libraries for Phase 17:**
- `@dnd-kit` — Not in package.json, requires pnpm add
- Command palette library — `cmdk` or Radix Command not in package.json. Base UI v1.3.0 exists but Command component availability unknown
- `useTransition`/`useDeferredValue` — Zero usage in codebase today, new React 19 concurrent features for Phase 17

🔴 **Cross-tab sync pattern NOT established:**
- `layoutStore.ts` uses `persist` middleware but NO `storage` event listener for cross-tab sync
- Phase 17 companyStore must implement this pattern (not copy existing layoutStore)

✅ **Existing patterns confirmed:**
- RAF batching: `brainStore.ts` lines 44-66 — queue, drain, 16ms cycle
- Targeted selectors: `useBrainState(id)` pattern in brainStore, `useSidebarCollapsed()` in layoutStore
- TanStack Query: 12 files use `useQuery`/`useMutation`, provider configured in `react-query.tsx`
- Zustand + Immer: 6 stores use this pattern (brainStore, layoutStore, wsStore, orchestratorStore, logFilterStore, replayStore)

### Performance Observables

For each Phase 17 feature, measure before/after:

**Multi-tenant company switcher:**
- Metric: Time from company switch click to first data render (target < 100ms)
- Tool: React DevTools Profiler + `performance.now()` timestamps in store action

**Drag-and-drop company ordering:**
- Metric: Frames dropped during drag operation (target: 0 dropped frames at 60fps)
- Tool: Chrome DevTools Performance tab, record drag session, check "Frames" timeline

**ActiveAgentsPanel with 24 brains:**
- Metric: FPS during 24-brain simultaneous update (target: 60fps sustained)
- Tool: `console.time()` around `_drainQueue()` + React DevTools Profiler

**Cost dashboard (MetricCard + QuotaBar):**
- Metric: Time to interactive (TTI) with cached data (target < 50ms)
- Tool: Lighthouse "Performance" score + Chrome DevTools Network panel (verify SWR background refetch)

**Command palette:**
- Metric: Input lag when typing search query (target < 16ms per keystroke)
- Tool: `performance.mark()` before/after search filter, Chrome DevTools Performance "Main" thread

**Mobile gestures:**
- Metric: Gesture response time (target < 100ms from touchstart to visual feedback)
- Tool: Chrome DevTools Performance tab, record gesture, check "Event Timing" section

### Anti-Pattern Alerts

❌ **Don't use npm for @dnd-kit** — pnpm only (Stack Hard-Lock violation if using npm)

❌ **Don't create new RAF loop for agent panel** — reuse existing `brainStore._drainQueue()` pattern. Multiple RAF loops = frame budget fragmentation

❌ **Don't invalidate all queries on company switch** — use scoped `queryKey: ['company-context']` only. Broad invalidation = unnecessary refetch waterfall

❌ **Don't block main thread for command palette indexing** — if > 1000 items, use Web Worker. Main thread indexing = typing jank

❌ **Don't use width/height animations for mobile gestures** — transforms + opacity only (GPU compositor). Layout animations = reflow = dropped frames

❌ **Don't let React Flow capture all pointer events** — `stopPropagation()` on dnd-kit handlers, `touch-action` CSS on containers. Conflict = unusable drag/drop

### Sync Cross-References

[SYNC: BF-05-005] → BRAIN-FEED-05-backend.md > Cost Data Sources. Frontend needs Rust activity_log endpoint contract (shape, pagination, auth). Owner: Brain #5 Backend.

[SYNC: BF-05-006] → BRAIN-FEED-05-backend.md > Company Context API. Frontend needs `/api/companies` endpoint for multi-tenant list + active company switching. Owner: Brain #5 Backend.

[SYNC: BF-05-007] → BRAIN-FEED-05-backend.md > Real-time Cost Events. Should cost quota updates come via WS (from Rust event sourcing) or polling? Owner: Brain #5 Backend.
