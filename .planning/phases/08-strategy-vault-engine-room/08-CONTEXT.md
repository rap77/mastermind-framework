# Phase 08: Strategy Vault, Engine Room & UX Polish - Context

**Gathered:** 2026-03-23
**Status:** Ready for brain consultation + planning

<domain>
## Phase Boundary

Strategy Vault, Engine Room, and Focus Mode complete the v2.1 War Room. Users can audit past executions with formatted brain outputs (Strategy Vault), monitor live logs with filtering and dynamic nicho grouping (Engine Room), manage API keys & view brain YAML config (Engine Room), and enter Focus Mode during active execution for cleaner visuals.

**Critical architectural discovery:** Phase 07 assumed static star topology (all 24 brains always visible), but Phase 08 implements the **dynamic DAG per task** (master → active nichos → active brains) that Phase 07 requires. This decision unblocks Phase 07 visual checkpoint verification and enables scalability to 50+ brains in v2.2.

</domain>

<decisions>
## Implementation Decisions

### 1. Dynamic DAG Visualization (Architectural Foundation for Phase 08-01 Backend)

#### Progressive Niche Expansion (Drill-Down Pattern)
- **Macro state:** DAG displays Master Node connected to Niche Clusters (collapsed). Shows overall flow: Master → Marketing → Ads → Done.
- **Activation:** When Orchestrator activates a nicho (e.g., "Inventory"), that niche node expands automatically or on double-click, revealing Brain Executor nodes inside.
- **Visual containment:** Brains "live" in a nicho-colored container. When a brain completes, its container can collapse to make space for the next phase.
- **Scalability:** Handles 24 brains today, scales to 50+ in v2.2 without visual "spaghetti."
- **React Flow:** Uses sub-graphs (parent node = Niche, child nodes = Brains). Native React Flow support.

#### Trace-Back Impact (Error Propagation)
- **Brain error origin:** Red intense (bg-red-600), glow pulse.
- **Niche impact:** Container border turns red dotted (not full red). Sibling brains pause (yellow/orange).
- **Upstream trace:** Edge connecting Master to failed Niche turns red, shows "flow blocked" animation (pulse stops).
- **Master resilience:** Master Node shows alert icon, but other nichos continue in green. Lets you see if error isolated or cascaded.
- **Diagnostic clarity:** Instantly locates failure origin and its impact scope.

#### Pulse & Reveal (Execution Animation)
- **Initial state:** All nichos appear as "Nuclear Nodes" (miniature icons with nicho name) in constellation around Master.
- **Activation pulse:** When Coordinator sends data to nicho, edge pulses with intense light. Nicho Cluster expands with Framer Motion zoom-in.
- **Sticky active state:** Active nicho stays expanded showing Brain Executors. When task completes and passes to next nicho, previous nicho fades to 40% opacity (Ghost state) but stays visible showing results.
- **Linear progression:** Creates "chain of revelation" showing execution path + current step simultaneously.
- **Visual traceability:** You see the journey taken while watching current progress.

#### Snapshot Scrubbing (Replay Logic for Strategy Vault)
- **Initial view:** Past executions shown as frozen graph in final state (static).
- **Scrubber bar:** Timeline at bottom with milestone snapshots (e.g., "Master init", "Nicho Marketing active", "Brain Ads completed").
- **State jumps:** Dragging scrubber jumps between snapshots (not animate every WS event). Like paging through a technical manual, not watching a movie.
- **Log sync:** Moving slider to point X auto-scrolls live logs panel to corresponding timestamp.
- **Performance benefit:** Lightweight storage (state snapshots, not all WS events). Fast navigation (jump to second 45 instantly).
- **Forensic tool feel:** Engineering-focused, not video playback.

**Backend Requirement (Phase 08-01):** GraphEdge response includes:
```json
{
  "nodes": [
    { "id": "master", "type": "master" },
    { "id": "niche-marketing", "type": "niche_cluster", "niche_id": "marketing" },
    { "id": "brain-inst", "type": "brain_executor", "parent": "niche-marketing", "niche_id": "marketing" }
  ],
  "edges": [
    { "source": "master", "target": "niche-marketing", "execution_mode": "sequential" },
    { "source": "niche-marketing", "target": "brain-inst", "execution_mode": "parallel" }
  ]
}
```

### 2. Live Log UX (Engine Room Logs)

#### Focus-Driven Dynamic Console (Smart Tail)
- **Contextual hub:** No single fixed terminal. Panel automatically shows only logs from active Nicho (e.g., Marketing streams, then automatically switches to Inventory).
- **Brain toggling (Interleaved):** Logs from individual brains are interleaved like `docker-compose logs`, but each line has a color Badge showing brain name/id.
- **Isolation mode:** Click DAG node → terminal filters to only that brain's logs. Deep dive without losing global scroll context.
- **Performance:** Single react-virtuoso viewport (Virtual Scrolling) for all 24 brains, unlimited lines. RAM-efficient regardless of volume.
- **Auto-follow:** Default enabled. Newest logs appear at bottom. Manual scroll disables auto-follow temporarily.
- **Filter by level:** (info/warn/error) toggleable, persists during session.

**Library:** react-virtuoso for virtual scrolling + react-logviewer baseline + custom brain-badge component

### 3. Focus Mode (UX Polish)

#### Context-Aware Focus (Smart Handoff)
- **Auto-trigger on task start:** When POST /api/tasks succeeds, Zustand orchestrator_state → 'running' → Focus Mode activates softly (not jarring).
  - Sidebar collapses to icons only
  - Idle nichos dim to 30% opacity
  - Active Nexus + Logs expand to 90% of viewport
  - Transition via AnimatePresence (Framer Motion)
- **Manual override visible:** [F] button or floating badge shows "Focus Active". Press [F] or Esc to exit if you need Engine Room (e.g., adjust API key mid-run).
- **Re-entry logic:** If you exit Focus while task running, system doesn't force you back. "Glow" perimeter reminder shows active process. Zero friction, full control.
- **Zustand state:** `isFocusMode` mapped to `orchestrator_state === 'running'` with `user_override: true` to break automatic behavior temporarily.

**Visual transition:** Sidebar collapse + grid layout shift handled by Framer Motion AnimatePresence. Smooth, not abrupt.

### 4. Strategy Vault (Execution History)

#### Execution List View
- **Pagination:** 10-20 past executions per page, paginated
- **Sort order:** Newest first (default)
- **List columns:** Status badge (success/error/running), brief text (first 100 chars), duration, brain count, timestamp
- **Filtering:** (Optional for v2.1) Can defer to v2.2 if scope tight

#### Individual Execution Detail
- **Accordion per brain:** Each participating brain has a collapsible section with its formatted output
- **Markdown rendering:** react-markdown with Smart-GFM (see below)
- **Copy-to-clipboard:** Per-brain output button + whole execution download as .txt
- **DAG visualization:** Replays with Snapshot Scrubbing (milestone-based jumps, not animate all events)
- **Logs sidebar:** Synced to scrubber timeline

#### Smart-GFM (Markdown Parsing)
- **Base:** react-markdown + GFM plugins (tables, checklists, strikethrough)
- **Custom components:** Map custom syntax (e.g., `:::chart ... :::`) or HTML tags to React components
  - `:::chart ... :::` → Recharts visualization
  - Code blocks → react-syntax-highlighter (VS Code styling)
  - Tables → shadcn/ui DataTable (sortable, filterable)
  - Inline icons → Lucide React
- **Security + speed:** No MDX execution (zero arbitrary code risk). Instant render. Storage remains plain Markdown string in DB.
- **Zero friction for brains:** Backend outputs pure Markdown. Frontend maps to interactive components.
- **Future-proof:** Change Recharts impl without touching saved executions.

### 5. Engine Room Config

#### API Key Management
- **List view:** Masked keys (show first 8 + last 4 chars), creation date, last used, actions (revoke)
- **Create new:** Modal → show full key once + copy-to-clipboard + warning "you won't see this again"
- **Revoke:** Confirm dialog, immediate revocation

#### Brain YAML Viewer
- **Read-only display:** Full brain YAML config from brain_registry.py
- **Syntax highlighting:** react-syntax-highlighter with YAML language
- **Copy-to-clipboard:** Full YAML button for copy + paste

**Note:** Engine Room is lower priority than Live Logs + Focus Mode + Strategy Vault. It's mostly CRUD operations.

### Claude's Discretion

- Exact Framer Motion easing functions for Pulse & Reveal animation
- Exact color values for Trace-Back Impact (red intensity, orange pause state)
- Sparkline implementation for "activity last 30s" in brain tiles (already in Phase 06, reuse)
- Exact tile dimming percentage (currently 30% for idle, 40% for Ghost, 5% for inactive)
- Virtual scrolling buffer size for react-virtuoso logs (balance latency vs RAM)

</decisions>

<specifics>
## Specific Ideas

- **"The War Room operates on three levels":** Macro (Pulse & Reveal across nichos), Meso (focus on active nicho logs), Micro (Deep Dive into one brain's logs via click). This hierarchy matches how engineers debug.
- **"Error as a narrative":** Trace-Back Impact doesn't just highlight the error — it shows the chain of dependency that caused it. Helps you understand if it's a nicho's fault or a Master issue.
- **"Execution is a story":** Pulse & Reveal leaves a trail. Strategy Vault replays that trail via Snapshot Scrubbing. You can see exactly where the flow branched or stopped.
- **"Smart defaults, escape hatches":** Focus Mode auto-activates (racing car telemetry) but [Esc] lets you leave without feeling trapped. Same with logs — they follow the active nicho, but you can click a DAG node to isolate.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets

- **brainStore.ts** — Map<brainId, BrainState> + useBrainState(id) selector. Extend with historyStack array for Ghost Trace snapshots.
- **wsStore.ts + WSBrainBridge.tsx** — WS connection tested end-to-end. Phase 08 subscribes to same store.
- **NexusCanvas.tsx** — React Flow DAG from Phase 07. Phase 08-01 extends with sub-graph nodes (Niche Clusters).
- **shadcn/ui components** — Card, Button, Sheet (for side panels), DataTable, Accordion (for Strategy Vault), Dialog (API key modals)
- **Magic UI** — BorderBeam, Bento Grid (reuse from Command Center for animations)
- **Framer Motion** — AnimatePresence already used. Leverage for Focus Mode transitions.
- **react-virtuoso** — Not yet in project but perfect for log streaming (single viewport, virtual scrolling)
- **react-markdown** — Lightweight GFM parser. Add custom components for Smart-GFM mapping.

### Established Patterns

- **Per-brain selectors:** `useBrainState(id)` prevents cascade re-renders. Log panel uses same pattern.
- **Zod validation:** WS events validated before Zustand updates (already established Phase 05+).
- **RAF batching:** brainStore batches updates before paint (60fps guaranteed). Logs follow same pattern.
- **TanStack Query:** GET /api/tasks/{id}/graph cached for 30s. Execution history paginated query.
- **Server Actions:** POST /api/tasks/create, GET /api/executions/history, POST /api/keys/revoke all via Server Actions.

### Integration Points

- `/engine-room` route → new page.tsx under apps/web/src/app/(protected)/engine-room/
- `/strategy-vault` route → execution list + detail view
- Nexus page (`/nexus`) → extend with Snapshot Scrubbing replay layer
- BriefInputModal.tsx → Already navigates to `/nexus` on submit. Phase 08 adds Focus Mode transition.
- Backend: GraphEdge endpoint (`GET /api/tasks/{id}/graph`) enhanced with sub-graph structure + execution_mode field (Phase 08-01 CRITICAL)
- Backend: New endpoints for Phase 08-01:
  - GET /api/executions/history (paginated list)
  - GET /api/executions/{id} (detail view)
  - GET /api/keys (list masked keys)
  - POST /api/keys (create new)
  - DELETE /api/keys/{id} (revoke)

### Backend Gap (Phase 08-01 BLOCKER)

- GraphEdge response missing niche_id + parent-child relationships for sub-graphs
- Execution history endpoints missing (must be created Phase 08-01 or blocking Phase 08-02)
- API key management endpoints missing

</code_context>

<deferred>
## Deferred Ideas

- **Animated full-DAG replay** — Deferred in favor of Snapshot Scrubbing. Can be added post-v2.1 if needed.
- **Heatmap of brain usage over time** — Requires historical metrics. Phase 08-02 with real DB data.
- **Variable injection at runtime** — Inject parameters mid-execution. Requires new backend API. Phase 09+.
- **Parallel Routes for dual-monitor setup** — `/nexus` and `/command-center` visible simultaneously. Phase 08 or v2.2.
- **WS events with latency/payload metrics** — Extend schema with duration_ms + payload_kb for realistic edge speed/thickness. Phase 08 deferred to keep WS schema stable.

</deferred>

---

*Phase: 08-strategy-vault-engine-room*
*Context gathered: 2026-03-23*
*Discussed: Dynamic DAG (Progressive Niche Expansion, Trace-Back Impact, Pulse & Reveal, Snapshot Scrubbing), Live Log UX (Focus-Driven Dynamic Console), Focus Mode (Context-Aware Smart Handoff), Strategy Vault (Smart-GFM Markdown), Engine Room (API keys + YAML viewer)*
