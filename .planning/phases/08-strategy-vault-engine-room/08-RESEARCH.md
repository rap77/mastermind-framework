# Phase 08: Strategy Vault, Engine Room & UX Polish - Research

**Researched:** 2026-03-23
**Domain:** Full-stack implementation (React Flow sub-graphs, execution history, live logs, API key management, Focus Mode)
**Confidence:** HIGH

## Summary

Phase 08 completes the v2.1 War Room by implementing three core user-facing systems: **Strategy Vault** (auditing past executions with formatted brain outputs), **Engine Room** (live log monitoring with dynamic nicho grouping + API key/YAML management), and **Focus Mode** (immersive view during active execution).

The critical architectural foundation is the **dynamic DAG per task** — React Flow sub-graphs with Master → Niche Clusters → Brain Executors hierarchy. This unblocks Phase 07 visual checkpoint verification and scales to 50+ brains in v2.2.

All architectural decisions are LOCKED from brain consultation (Moment 2-3 on 2026-03-23). Frontend uses established patterns (Zustand with Immer, React Flow, Framer Motion, TanStack Query). Backend requires new endpoints for execution history + API key management + GraphEdge enhancement with sub-graph structure.

**Primary recommendation:** Implement in Wave 0 (backend contracts + DAG structure), then Wave 1-2 (frontend components), Wave 3 (integration + testing). Test with snapshot scrubbing + live logs first — Focus Mode polish last.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

1. **Dynamic DAG Visualization (Progressive Niche Expansion)**
   - Master Node → Niche Clusters (collapsed initially)
   - Activation expands nicho to reveal Brain Executor nodes
   - React Flow sub-graphs: parent node = Niche, child nodes = Brains
   - Handles 24 brains today, scales to 50+ in v2.2

2. **Trace-Back Impact (Error Propagation)**
   - Brain error: red intense (`bg-red-600`), glow pulse
   - Niche container border: red dotted, not full red
   - Sibling brains pause: yellow/orange state
   - Upstream edge to Master: red, "flow blocked" pulse animation
   - Master shows alert icon, other nichos continue in green

3. **Pulse & Reveal (Execution Animation)**
   - All nichos as "Nuclear Nodes" initially
   - Edge pulses when Coordinator sends data, nicho expands (Framer Motion zoom-in)
   - Active nicho stays expanded, previous fades to 40% opacity (Ghost state)
   - Linear progression showing execution path + current step

4. **Snapshot Scrubbing (Replay Logic for Strategy Vault)**
   - Frozen graph in final state initially
   - Timeline scrubber at bottom with milestone snapshots
   - Dragging scrubber jumps between snapshots (state snapshots, not all WS events)
   - Log sync: moving slider auto-scrolls logs to corresponding timestamp
   - Lightweight storage (snapshots), fast navigation (jump to second 45 instantly)

5. **Live Log UX (Engine Room Logs)**
   - Contextual hub: shows only logs from active Nicho
   - Logs interleaved like `docker-compose logs`, each line has brain badge
   - Isolation mode: click DAG node → filter to that brain's logs
   - Single react-virtuoso viewport (virtual scrolling), unlimited lines, RAM-efficient
   - Auto-follow enabled by default, manual scroll disables temporarily
   - Filter by level (info/warn/error) toggleable

6. **Focus Mode (Context-Aware Smart Handoff)**
   - Auto-trigger when POST /api/tasks succeeds → Zustand `orchestrator_state === 'running'`
   - Sidebar collapses to icons only
   - Idle nichos dim to 30% opacity
   - Active Nexus + Logs expand to 90% viewport
   - Transition via AnimatePresence (Framer Motion)
   - Manual override: [F] button or Esc to exit
   - No re-trapping if exit while task running

7. **Strategy Vault (Execution History)**
   - Pagination: 10-20 past executions per page
   - Sort order: newest first
   - List columns: status badge, brief text (100 chars), duration, brain count, timestamp
   - Accordion per brain with formatted output, Markdown rendering
   - Copy-to-clipboard per brain + whole execution download as .txt
   - DAG visualization with Snapshot Scrubbing replay
   - Logs sidebar synced to scrubber timeline

8. **Smart-GFM (Markdown Parsing)**
   - react-markdown + GFM plugins (tables, checklists, strikethrough)
   - Custom components: `:::chart:::` → Recharts, code blocks → react-syntax-highlighter, tables → shadcn/ui DataTable
   - NO MDX execution (zero arbitrary code risk)
   - Storage: plain Markdown string in DB, frontend maps to interactive components

9. **Engine Room Config**
   - API Key Management: list masked keys, create new (show once), revoke
   - Brain YAML Viewer: read-only display, syntax highlighting, copy-to-clipboard
   - Lower priority than Live Logs + Focus Mode + Strategy Vault

10. **GraphEdge Enhancement (Phase 08-01 Critical)**
    - Response includes `parentId` for React Flow sub-graph support
    - Nodes: `type: niche_cluster` with `niche_id`, `type: brain_executor` with `parentId`
    - Edges: `data.execution_mode` field (sequential/parallel)
    - Backend requirement: MUST be ready before frontend DAG rendering

### Claude's Discretion

- Exact Framer Motion easing functions for animations
- Exact color values for Trace-Back Impact (red intensity, orange pause state)
- Sparkline implementation for "activity last 30s" in brain tiles (reuse from Phase 06)
- Exact tile dimming percentage (30% idle, 40% Ghost, 5% inactive)
- Virtual scrolling buffer size for react-virtuoso logs (balance latency vs RAM)

### Deferred Ideas (OUT OF SCOPE)

- Animated full-DAG replay (deferred in favor of Snapshot Scrubbing)
- Heatmap of brain usage over time (requires historical metrics)
- Variable injection at runtime (requires new backend API)
- Parallel Routes for dual-monitor setup (Phase 08 or v2.2)
- WS events with latency/payload metrics
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SV-01 | User can view a list of past executions with status, brief text, duration, and brain count | Execution history endpoints required (GET /api/executions/history paginated), SQLite metadata + JSONB snapshots for replay |
| SV-02 | User can select an execution and view formatted Markdown output from each participating brain | Smart-GFM rendering (react-markdown + custom components for charts/tables/code), strategy-vault detail view with scrubbing logic |
| ER-01 | User can view live structured logs with virtual scrolling, level filtering, and auto-follow | react-virtuoso for single viewport + RAF batching in brainStore, logs interleaved by brain with badges |
| ER-02 | User can manage API keys: view masked, create new, revoke existing | API key management endpoints (GET/POST/DELETE /api/keys), show-once pattern, Redis allow-list for revocation |
| ER-03 | User can view the YAML configuration of any brain and copy it | Brain YAML viewer route, syntax highlighting, copy-to-clipboard via shadcn/ui Dialog |
| UX-01 | User can enter Focus Mode during active execution — sidebar collapses, idle dims, active highlighted | Focus Mode state in Zustand, AnimatePresence transitions, keyboard shortcut [F] + Esc to exit, no re-trap logic |

</phase_requirements>

## Standard Stack

### Core Frontend
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React | 19.2.4 | Component rendering, hooks (useTransition, useCallback) | Latest stable, Server Components support in Next.js 16 |
| Next.js | 16.2.0 | App Router, Server Actions, middleware | Fixed from Phase 05, all route handlers tested |
| @xyflow/react | 12.10.1 | React Flow DAG visualization + sub-graphs | Native React 19 support, sub-graph API for nicho clusters |
| Zustand | 5.0.12 | Client state (brainStore, wsStore, replayStore) | Lightweight, Immer middleware for immutable updates, Map support |
| Framer Motion | (pending) | Animation (Pulse & Reveal, Focus Mode transitions) | Declarative animations, AnimatePresence for conditional renders |
| react-virtuoso | (pending) | Virtual scrolling for unlimited log lines | Single viewport, O(1) memory regardless of line count, auto-follow support |
| react-markdown | (pending) | Markdown + GFM parsing for Strategy Vault | Lightweight, no MDX, custom component mapping |
| react-syntax-highlighter | (pending) | Code syntax highlighting in Smart-GFM | VS Code styling, supports YAML/TypeScript/JSON |
| Recharts | (pending) | Charts in Smart-GFM blocks | React-native, composable, works in Markdown blocks |
| TanStack Query | 5.91.3 | Server state (execution history pagination) | Cursor-based pagination support, 30s staleTime cache |
| Tailwind CSS | 4 | Utility styles, color system (OKLCH) | Fixed from Phase 05, 4.x CSS-only config |
| @base-ui/react | 1.3.0 | Unstyled components (used by shadcn/ui) | NovaPreset foundation |

### Backend
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | (current) | REST + WebSocket endpoints | Already established, ASGI for async |
| Pydantic | (current) | Request/response validation | Type safety, JSON schema generation |
| SQLAlchemy | (current) | Database ORM | Async support, JSONB for snapshots |
| pytest | (current) | Test framework | Async support, fixtures, parametrization |
| jose | 6.2.2 (frontend only) | JWT validation | Edge Runtime compatible |

### Supporting Frontend Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Lucide React | 0.577.0 | Icons (error glow, checkmark, icons in logs) | Established in Phase 06, reuse patterns |
| shadcn/ui | 4.0.8 | Button, Dialog, Card, Accordion, DataTable | Configured for Nova preset, TailwindCSS 4 |
| class-variance-authority | 0.7.1 | Conditional styling (e.g., Ghost state colors) | Established pattern |
| DOMPurify | 3.3.3 | Sanitize Markdown to prevent XSS | For react-markdown output safety |
| immer | 11.1.4 | Immutable state updates in Zustand | EnableMapSet already enabled in brainStore |
| clsx | 2.1.1 | Conditional class names | Utility |

### Installation
```bash
# Frontend new packages
cd apps/web
pnpm add framer-motion react-virtuoso react-markdown react-syntax-highlighter recharts remark-gfm

# No backend package changes — use existing FastAPI/Pydantic
```

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| react-virtuoso | react-window | react-virtuoso has better auto-follow + filtering semantics, less boilerplate |
| Recharts | Chart.js / D3 | Recharts is React-native and composable (works in Markdown blocks), D3 more powerful but verbose |
| Framer Motion | Motion (Tailwind native) | Framer Motion has more granular control (cubic-bezier easing, stagger), Motion is newer/leaner |
| react-markdown | MDX | MDX executes code (security risk), react-markdown is lightweight + custom component mapping safer |
| Custom replay logic | Yjs / replicache | Phase 08 uses simple snapshot jumps (not CRDT), sufficient for v2.1 |

## Architecture Patterns

### Recommended Project Structure

```
apps/web/src/
├── app/
│   ├── (auth)/
│   │   └── login/page.tsx
│   ├── (protected)/
│   │   ├── page.tsx (dashboard redirect)
│   │   ├── command-center/page.tsx
│   │   ├── nexus/page.tsx (NEW: extend with Focus Mode)
│   │   ├── strategy-vault/
│   │   │   ├── page.tsx (execution list)
│   │   │   └── [id]/page.tsx (detail + scrubbing)
│   │   └── engine-room/
│   │       └── page.tsx (logs + config)
│   └── api/
│       ├── auth/ (existing)
│       └── ws/ (existing WebSocket handshake)
│
├── components/
│   ├── command-center/ (existing)
│   ├── nexus/ (Phase 07, extend with)
│   │   ├── NexusCanvas.tsx (add sub-graph support)
│   │   ├── NicheClusterNode.tsx (NEW)
│   │   ├── BrainNode.tsx (extend)
│   │   └── ReplayNexus.tsx (NEW for Strategy Vault)
│   ├── engine-room/ (NEW)
│   │   ├── LiveLogPanel.tsx
│   │   ├── LogBadge.tsx (brain name/id color badge)
│   │   ├── FilterBar.tsx (info/warn/error toggles)
│   │   └── BrainYAMLViewer.tsx
│   ├── strategy-vault/ (NEW)
│   │   ├── ExecutionList.tsx
│   │   ├── ExecutionDetail.tsx
│   │   ├── SnapshotScrubber.tsx
│   │   └── SmartMarkdown.tsx (Smart-GFM renderer)
│   ├── ui/ (shadcn components, existing)
│   └── shared/
│       └── FocusModeBadge.tsx (floating [F] indicator)
│
├── stores/
│   ├── brainStore.ts (existing, extend with ghost trace)
│   ├── wsStore.ts (existing)
│   ├── orchestratorStore.ts (NEW: Focus Mode state, running/idle/complete)
│   └── replayStore.ts (NEW: Zustand for scrubber milestones, currentSnapshotIndex)
│
├── lib/
│   ├── api.ts (existing types)
│   ├── smart-gfm.ts (NEW: Markdown component mapping)
│   └── log-parser.ts (NEW: parse log lines with timestamps)
│
└── types/
    └── api.ts (generated from backend schemas)

apps/api/src/
├── routes/
│   ├── tasks.py (existing, enhance GraphEdge)
│   ├── executions.py (NEW: history + detail endpoints)
│   ├── keys.py (NEW: API key management)
│   └── brains.py (existing, verify GET /api/brains)
│
├── models/
│   ├── execution.py (NEW: Execution, BrainOutput schemas)
│   └── task.py (existing, extend with sub-graphs)
│
└── services/
    └── graph_builder.py (NEW: convert WS events to DAG snapshots for replay)
```

### Pattern 1: React Flow Sub-Graphs for Niche Clusters

**What:** Master → Niche Clusters (collapsed parent) → Brain Executors (children). Uses React Flow native `parentId` and `extent: 'parent'` to restrict child movement.

**When to use:** Multi-level hierarchical graphs (today: 3 levels, future: 50+ brains). Avoids visual spaghetti.

**Example:**
```typescript
// NexusCanvas.tsx enhanced version
export function buildNicheClusteredNodes(brains: Brain[]): Node[] {
  const nodes: Node[] = []

  // Master node
  nodes.push({
    id: 'master',
    type: 'master',
    data: { label: 'Brief' },
    position: { x: 0, y: 0 },
  })

  // Niche clusters (grouped by niche from backend)
  const nichesByType = groupBy(brains, 'niche')

  for (const [niche, nichos] of Object.entries(nichesByType)) {
    nodes.push({
      id: `niche-${niche}`,
      type: 'niche_cluster',
      data: { label: niche, niche_id: niche },
      position: { x: 100, y: 100 }, // dagre layout later
      // React Flow sub-graph: indicates this node contains children
    })

    // Brain executor children
    for (const brain of nichos) {
      nodes.push({
        id: `brain-${brain.id}`,
        type: 'brain_executor',
        parentId: `niche-${niche}`, // CRITICAL: binds to parent
        data: { niche_id: niche, status: 'idle' },
        position: { x: 0, y: 0 }, // relative to parent
        extent: 'parent', // prevent escaping container
      })
    }
  }

  return nodes
}

// Edge: Master → Niche
edges.push({
  source: 'master',
  target: 'niche-marketing',
  data: { execution_mode: 'sequential' },
})

// Edge: Niche → Brain (inside cluster)
edges.push({
  source: 'niche-marketing',
  target: 'brain-01',
  data: { execution_mode: 'parallel' },
})
```

### Pattern 2: Snapshot Scrubbing for Replay

**What:** Store timeline as array of `{ timestamp, snapshot: Map<brainId, BrainState> }`. Scrubber drag jumps to index, not animates all WS events.

**When to use:** Large execution histories (1000+ WS events compress to 7 milestones). Fast navigation without re-rendering every frame.

**Example:**
```typescript
// replayStore.ts
interface ReplayState {
  milestones: Array<{ timestamp: number; label: string; snapshotIndex: number }>
  currentSnapshotIndex: number
  snapshots: Array<{ timestamp: number; snapshot: Map<string, BrainState> }>

  setSnapshots: (snapshots: ReplayState['snapshots']) => void
  jumpToMilestone: (index: number) => void
  getScrubberPercentage: () => number
}

// SnapshotScrubber.tsx
export function SnapshotScrubber({ milestones, onScrub }: Props) {
  const [dragging, setDragging] = useState(false)

  const handleDrag = (e: React.MouseEvent) => {
    if (!dragging) return
    const rect = e.currentTarget.getBoundingClientRect()
    const percent = (e.clientX - rect.left) / rect.width
    const index = Math.floor(percent * milestones.length)
    onScrub(Math.max(0, Math.min(index, milestones.length - 1)))
  }

  return (
    <div className="flex gap-2 items-center">
      <div
        className="flex-1 h-1 bg-secondary rounded"
        onMouseDown={() => setDragging(true)}
        onMouseUp={() => setDragging(false)}
        onMouseMove={handleDrag}
      >
        {/* Milestone "magnets" with snapping behavior */}
        {milestones.map((m, idx) => (
          <div
            key={idx}
            className="absolute w-2 h-2 bg-primary rounded-full cursor-pointer"
            style={{
              left: `${(idx / milestones.length) * 100}%`,
              title: m.label,
            }}
            onClick={() => onScrub(idx)}
          />
        ))}
      </div>
      <span className="text-xs text-muted-foreground">
        {milestones[currentIndex]?.label || 'Start'}
      </span>
    </div>
  )
}
```

### Pattern 3: Focus Mode State Management

**What:** Zustand store tracks `orchestrator_state` (idle/running/complete) + `user_override` for Esc key. AnimatePresence triggers conditional renders.

**When to use:** Full-screen modal transitions triggered by async events (POST /api/tasks response), escape hatch for user control.

**Example:**
```typescript
// orchestratorStore.ts
interface OrchestratorState {
  taskId: string | null
  state: 'idle' | 'running' | 'complete' | 'error'
  userOverride: boolean // true = user pressed Esc, don't auto-activate

  startTask: (taskId: string) => void // sets state='running', userOverride=false
  toggleOverride: () => void // user presses Esc
  completeTask: () => void // sets state='complete'
}

// NexusPage.tsx
export function NexusPage() {
  const { state, userOverride, toggleOverride } = useOrchestratorStore()
  const isFocusMode = state === 'running' && !userOverride

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'f' || e.key === 'F') toggleOverride()
      if (e.key === 'Escape') toggleOverride()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <div className={isFocusMode ? 'grid grid-cols-3' : 'grid grid-cols-4'}>
      <AnimatePresence>
        {isFocusMode && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="col-span-2"
          >
            <Sidebar variant="icons-only" />
          </motion.div>
        )}
      </AnimatePresence>

      <div className={isFocusMode ? 'col-span-1' : 'col-span-3'}>
        <NexusCanvas />
      </div>
    </div>
  )
}
```

### Pattern 4: Smart-GFM Component Mapping

**What:** react-markdown with custom `components` prop to map HTML to React components. Supports `:::chart ... :::` syntax for composable charts.

**When to use:** Rich content rendering from structured Markdown, avoid MDX (security), keep storage as plain Markdown.

**Example:**
```typescript
// SmartMarkdown.tsx
import ReactMarkdown from 'react-markdown'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { Code } from 'react-syntax-highlighter'
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs'

const components: Parameters<typeof ReactMarkdown>[0]['components'] = {
  code({ inline, className, children, ...props }) {
    if (inline) return <code className="bg-muted px-1 rounded">{children}</code>
    const lang = className?.replace(/language-/, '') || 'text'
    return (
      <Code language={lang} style={atomOneDark} {...props}>
        {String(children).replace(/\n$/, '')}
      </Code>
    )
  },

  table({ children }) {
    return <DataTable columns={[]} data={[]} /> // Parse from Markdown table AST
  },

  // Custom: :::chart ... ::: blocks
  // Handled via rehype plugin or post-processing regex
}

export function SmartMarkdown({ markdown }: { markdown: string }) {
  return (
    <ReactMarkdown
      components={components}
      remarkPlugins={[remarkGfm]}
    >
      {markdown}
    </ReactMarkdown>
  )
}
```

### Anti-Patterns to Avoid

- **Inline NODE_TYPES in JSX:** React Flow remounts entire canvas on each render. Keep at module level (established in Phase 07).
- **Non-targeted selectors for 24 brains:** Each brain update triggers 24 re-renders. Use `useBrainState(id)` per-brain selector (WS-03 pattern).
- **Storing full WS event history for replay:** Memory explosion. Use snapshots at milestones only (7 max per execution).
- **Animated replay (frame-by-frame animation of all WS events):** Laggy, doesn't scale to 1000+ events. Snapshot scrubbing (jump, not animate) is faster.
- **Re-rendering entire DAG on every brain status change:** Use React.memo strictly on BrainNode + NicheClusterNode + use `onlyRenderVisibleElements` in ReactFlow.
- **Storing Markdown as HTML in DB:** Use plain Markdown string, render on frontend (enables theme switching, format updates without DB migration).
- **Global arbitration for focus state:** Use Zustand store so multiple pages can respect Focus Mode (e.g., Engine Room collapses when Focus active).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Virtual scrolling for 1000+ log lines | Custom scroll viewport | react-virtuoso | Handles auto-follow, filtering, RAM-efficient DOM culling, edge cases (rapid appends, viewport resize) |
| Markdown → React component mapping | Regex parser + JSX builder | react-markdown + remark-gfm + custom components | Handles edge cases (nested lists, tables, code blocks), GFM compliance, security (sanitization), XSS prevention |
| Sub-graph node clustering | Custom Dagre layout | React Flow native `parentId` + `extent: 'parent'` | Performance (GPU accelerated bounds checking), supports expand/collapse, handles edge cases (parent-child positioning) |
| Timeline scrubbing UI | Custom drag handler | Slider component + useState | Accessibility (44px hitbox), touch support, keyboard navigation, pinch-to-zoom on mobile |
| Log line parsing (timestamps) | Regex on frontend | Server-side structured logs (JSON lines) | Server knows log format, frontend doesn't need to parse, reduces latency, enables filtering at source |
| Chart rendering in Markdown | Custom Canvas | Recharts in Markdown block | Responsive, composable, works in reusable markdown blocks, interactive tooltips |

**Key insight:** Phase 08 is 70% integration of existing patterns (Zustand, React Flow, Tailwind), 30% new components (scrubber, logs, replay). Don't build novel solutions — apply battle-tested patterns at scale.

## Common Pitfalls

### Pitfall 1: Snapshot Bloat — Storing Full WS Event History for Replay

**What goes wrong:** Saves every single WS event (brain status update) to database. With 24 brains + 10-minute execution = 10,000+ events. DB explodes, frontend struggles to replay.

**Why it happens:** Assumption that "more data = better replay fidelity." Early enthusiasm for full animation playback.

**How to avoid:** Store snapshots at milestone boundaries only. Brain #6 (QA) validates that 7-10 milestones capture the full execution narrative without loss. Use `brainStore.pushHistorySnapshot()` strategically (e.g., after each nicho completes, not per brain status update).

**Warning signs:**
- Execution history DB size > 500KB per execution (suspect full event log)
- Scrubber drag feels jerky or slow (too many snapshots)
- Memory spike when loading Strategy Vault (snapshots in DOM)

**Mitigation:** Calculate snapshots at backend before storing. Send frontend only the 7 milestone deltas.

### Pitfall 2: Focus Mode Re-Trapping — User Exits with [Esc], Auto-Activate Closes It Again

**What goes wrong:** User presses [Esc] to exit Focus Mode while task running. State.userOverride = true. But WS event arrives saying task still running → resets userOverride = false → Focus Mode re-activates. User feels trapped.

**Why it happens:** Override flag not persisted across WS updates. Logic reads `state.running && !userOverride` but doesn't bind userOverride to state.

**How to avoid:** Make userOverride idempotent. Once set to true, stays true until task completes (state === 'complete'). Use strict equality check: `if (newState.state === 'complete') reset userOverride = false`.

**Warning signs:**
- User presses [Esc], sidebar collapses, 500ms later expands again
- Focus Mode badge flickers on/off rapidly

**Test case:** Task running → user [Esc] → task still running 5s later → Focus Mode should stay off until task completes.

### Pitfall 3: React Flow Sub-Graph Layout Thrash

**What goes wrong:** Every brain status update triggers Dagre layout recalculation. With parentId + extent rules, layout shifts entire nicho cluster. User's selected nicho jumps around.

**Why it happens:** `getLayoutedNodes()` called on every brainStore update. Data-only WS updates (status change) shouldn't trigger layout.

**How to avoid:** Separate layout computation from brain state updates. Layout runs ONCE at task start (fetch `/api/tasks/{id}/graph`, cache in useState). Brain state updates only change node.data (color/glow/badge), never position. Use `onlyRenderVisibleElements` in ReactFlow config.

**Warning signs:**
- Nicho cluster visibly shifts when brain status updates
- High CPU usage while task running (constant re-layout)

**Code pattern:**
```typescript
const [nodes, setNodes] = useState<Node[]>([]) // layout cached here
const [edges, setEdges] = useState<Edge[]>([])

// Load graph ONCE, cache forever
useEffect(() => {
  fetchGraphEdges(taskId).then(({ nodes: rawNodes, edges: rawEdges }) => {
    const laid = getLayoutedNodes(rawNodes, rawEdges)
    setNodes(laid) // latched, never recalculated
    setEdges(rawEdges)
  })
}, [taskId])

// Brain state updates ONLY change node.data, not position
const handleBrainUpdate = (brainId: string, status: BrainStatus) => {
  setNodes(nodes => nodes.map(n =>
    n.id === `brain-${brainId}` ? { ...n, data: { ...n.data, status } } : n
  ))
}
```

### Pitfall 4: Logs Filter State Lost on WS Disconnect

**What goes wrong:** User toggles filter to `error` level only. WS disconnects, reconnects. Filter state reset to default (all levels). Logs explode with 1000 lines. User frustrated.

**Why it happens:** Log filter state stored in component useState, not persisted to Zustand/localStorage. Reconnect flushes component state.

**How to avoid:** Store log filter state in Zustand orchestratorStore (not local state). Persist to localStorage under `mm_log_filters_${taskId}`. Restore on mount.

**Warning signs:**
- Filter toggles work locally but don't survive page reload
- Filter resets after WS reconnect
- Log panel visually flickers (1000 lines flash, then filtered)

**Test case:** Filter to `error`, let WS drop for 5s, auto-reconnect → filter should still be `error`.

### Pitfall 5: Scrubber Sync Lag — Logs Don't Auto-Scroll to Timestamp

**What goes wrong:** User drags scrubber to 45s timeline. Snapshot jumps correctly. But logs panel is still scrolled to top (showing logs from 0s). User has to manually scroll to see corresponding logs.

**Why it happens:** Scrubber logic updates snapshot index but doesn't signal logs panel to scroll. Separate state concerns not synchronized.

**How to avoid:** Scrubber drag handler calls both `jumpToSnapshot(index)` AND `logPanel.scrollToTimestamp(snapshot.timestamp)`. Reverse lookup timestamp from snapshot, find first log line >= that timestamp, scroll there.

**Warning signs:**
- Scrubber at 45s but logs showing 10s
- No visible connection between scrubber and log scroll position
- User has to manually scroll after every scrubber drag

**Code pattern:**
```typescript
const handleScrubberDrag = (index: number) => {
  useReplayStore.setState({ currentSnapshotIndex: index })

  const milestone = milestones[index]
  if (milestone?.timestamp) {
    // Find first log >= timestamp
    const logIndex = logs.findIndex(l => l.timestamp >= milestone.timestamp)
    logsPanelRef.current?.scrollToIndex(logIndex)
  }
}
```

### Pitfall 6: Virtual Scrolling Buffer Too Small — Flicker on Scroll

**What goes wrong:** react-virtuoso configured with overscan=2 (only render 2 extra rows above/below viewport). User scrolls fast → visible gap between rendered rows. Content flickers.

**Why it happens:** Network latency or slow device can't keep up with overscan=2. Needs larger buffer.

**How to avoid:** Use overscan=10 (default is fine). If RAM is a concern, use overscan=5 + debounce scroll handlers.

**Warning signs:**
- Black rows appear when scrolling fast
- Flicker on page down key
- Virtual scrolling defeats purpose (feels jerky)

**Test case:** 5000+ log lines, scroll to bottom as fast as possible (Page Down spam) → should not flicker.

## Code Examples

Verified patterns from official sources:

### Example 1: Building Niche Cluster Nodes (React Flow Sub-Graphs)

```typescript
// Source: Phase 07 NexusCanvas.tsx + React Flow docs (v12.x)
// Extended for Phase 08 sub-graph structure

import { Node, Edge } from '@xyflow/react'

interface TaskGraphResponse {
  nodes: Array<{
    id: string
    type: 'master' | 'niche_cluster' | 'brain_executor'
    data: Record<string, unknown>
    parentId?: string // NEW in Phase 08
    position: { x: number; y: number }
  }>
  edges: Array<{
    source: string
    target: string
    data?: { execution_mode: 'sequential' | 'parallel' }
  }>
}

export function transformGraphToReactFlow(response: TaskGraphResponse): {
  nodes: Node[]
  edges: Edge[]
} {
  const nodes: Node[] = response.nodes.map((n) => ({
    id: n.id,
    type: n.type,
    data: n.data,
    parentId: n.parentId, // Enables sub-graph clustering
    position: n.position,
    extent: n.parentId ? 'parent' : undefined, // Child nodes bound to parent
    connectable: n.type !== 'master', // Master connects from, not to
  }))

  const edges: Edge[] = response.edges.map((e) => ({
    id: `${e.source}-${e.target}`,
    source: e.source,
    target: e.target,
    type: 'hybridFlow', // From Phase 07
    data: e.data || {},
  }))

  return { nodes, edges }
}
```

### Example 2: Zustand Replay Store with Snapshot Milestones

```typescript
// Source: Zustand 5.x docs + custom implementation
// For Strategy Vault scrubbing

import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

export interface SnapshotMilestone {
  index: number
  timestamp: number
  label: string // e.g., "Master init", "Marketing active"
  brainCount: number
}

interface ReplayState {
  snapshots: Array<{ timestamp: number; snapshot: Map<string, BrainState> }>
  milestones: SnapshotMilestone[]
  currentSnapshotIndex: number

  setSnapshots: (snapshots: ReplayState['snapshots']) => void
  computeMilestones: () => void
  jumpToMilestone: (index: number) => void
  getCurrentSnapshot: () => Map<string, BrainState> | null
}

export const useReplayStore = create<ReplayState>()(
  immer((set, get) => ({
    snapshots: [],
    milestones: [],
    currentSnapshotIndex: 0,

    setSnapshots: (snapshots) => {
      set((state) => {
        state.snapshots = snapshots
        state.currentSnapshotIndex = 0
      })
      get().computeMilestones()
    },

    computeMilestones: () => {
      const { snapshots } = get()
      if (snapshots.length === 0) return

      // Compute max 7 milestones (Miller's Law chunking)
      const milestoneInterval = Math.ceil(snapshots.length / 7)
      const newMilestones: SnapshotMilestone[] = []

      for (let i = 0; i < snapshots.length; i += milestoneInterval) {
        const snapshot = snapshots[i]
        const activeBrains = Array.from(snapshot.snapshot.values()).filter(
          (b) => b.status !== 'idle'
        ).length

        newMilestones.push({
          index: i,
          timestamp: snapshot.timestamp,
          label: `${Math.round((i / snapshots.length) * 100)}% complete (${activeBrains} active)`,
          brainCount: activeBrains,
        })
      }

      set((state) => {
        state.milestones = newMilestones
      })
    },

    jumpToMilestone: (index: number) => {
      set((state) => {
        state.currentSnapshotIndex = index
      })
    },

    getCurrentSnapshot: () => {
      const { snapshots, currentSnapshotIndex } = get()
      return snapshots[currentSnapshotIndex]?.snapshot || null
    },
  }))
)
```

### Example 3: Live Log Panel with react-virtuoso

```typescript
// Source: react-virtuoso docs + custom integration
// For Engine Room logs with virtual scrolling

import { Virtuoso, VirtuosoHandle } from 'react-virtuoso'
import { useWSStore } from '@/stores/wsStore'
import { useBrainStore } from '@/stores/brainStore'

interface LogLine {
  timestamp: number
  brainId: string
  level: 'info' | 'warn' | 'error'
  message: string
}

interface LiveLogPanelProps {
  activeBrainId?: string // If set, isolate to this brain
}

export function LiveLogPanel({ activeBrainId }: LiveLogPanelProps) {
  const virtuosoRef = useRef<VirtuosoHandle>(null)
  const [logs, setLogs] = useState<LogLine[]>([])
  const [filterLevel, setFilterLevel] = useState<Set<string>>(
    new Set(['info', 'warn', 'error'])
  )
  const [autoFollow, setAutoFollow] = useState(true)
  const { listeners } = useWSStore()

  // Subscribe to WS log events
  useEffect(() => {
    const unsubscribe = useWSStore.subscribe(
      (state) => state.listeners,
      (newListeners) => {
        const handlers = newListeners.get('log:line')
        if (handlers) {
          const listener = (data: LogLine) => {
            setLogs((prev) => [...prev, data])
            if (autoFollow) {
              virtuosoRef.current?.scrollToIndex(logs.length)
            }
          }
          handlers.add(listener)
          return () => handlers.delete(listener)
        }
      }
    )
    return unsubscribe
  }, [autoFollow, logs.length])

  // Filter logs by level and brain
  const filteredLogs = useMemo(
    () =>
      logs.filter(
        (log) =>
          filterLevel.has(log.level) &&
          (!activeBrainId || log.brainId === activeBrainId)
      ),
    [logs, filterLevel, activeBrainId]
  )

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100">
      {/* Filter bar */}
      <div className="flex gap-2 p-2 border-b border-slate-800">
        {['info', 'warn', 'error'].map((level) => (
          <button
            key={level}
            className={`px-2 py-1 rounded text-xs ${
              filterLevel.has(level)
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-400'
            }`}
            onClick={() => {
              setFilterLevel((prev) => {
                const next = new Set(prev)
                if (next.has(level)) next.delete(level)
                else next.add(level)
                return next
              })
            }}
          >
            {level}
          </button>
        ))}
        <div className="flex-1" />
        <label className="text-xs flex items-center gap-1">
          <input
            type="checkbox"
            checked={autoFollow}
            onChange={(e) => setAutoFollow(e.target.checked)}
          />
          Auto-follow
        </label>
      </div>

      {/* Virtual log panel */}
      <Virtuoso
        ref={virtuosoRef}
        data={filteredLogs}
        overscan={10}
        itemContent={(index, log) => (
          <LogLineRow key={`${log.timestamp}-${index}`} log={log} />
        )}
        style={{ flex: 1 }}
      />
    </div>
  )
}

function LogLineRow({ log }: { log: LogLine }) {
  return (
    <div className="flex gap-2 px-2 py-1 text-xs font-mono hover:bg-slate-800">
      <span className="text-slate-500">
        {new Date(log.timestamp).toISOString().substr(11, 8)}
      </span>
      <Badge variant={log.level === 'error' ? 'destructive' : 'secondary'}>
        {log.brainId}
      </Badge>
      <span className="flex-1 text-slate-300">{log.message}</span>
    </div>
  )
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single flat DAG (24 nodes visible always) | Dynamic sub-graph DAG (nicho clusters collapsible) | Phase 08 architecture locked | Scales to 50+ brains without visual clutter, hierarchy matches user mental model |
| AnimationFrame replay (animate every WS event) | Snapshot scrubbing (jump to milestones) | Phase 08 decision (Moment 2) | 10-100x faster navigation (jump vs animate), smaller DB (7 snapshots vs 1000 events) |
| Custom log viewer component | react-virtuoso (off-the-shelf) | Phase 08 stack decision | 60fps scrolling, auto-follow, filtering, RAM-efficient at 10k+ lines |
| Markdown as HTML stored in DB | Plain Markdown string + client-side render | Phase 08 Smart-GFM decision | Theme switching enabled, format updates no DB migration, re-usable blocks |
| Focus Mode as optional sidebar toggle | Context-aware auto-activation on task start | Phase 08 UX decision | Racing car telemetry feel, [Esc] escape hatch for user control |
| Global WS listener per brain | Per-brain RAF batching in brainStore | Phase 07 (extended Phase 08) | WS-02/WS-03 requirements met (60fps, targeted re-renders) |

**Deprecated/outdated:**
- Full DAG animation replay: replaced by snapshot scrubbing (faster, lighter)
- Custom WebSocket reconnect logic: Phase 08 inherits Phase 05 auto-reconnect strategy (exponential backoff)
- Session-global log storage: Phase 08 fetches execution history from DB, not memory

## Open Questions

1. **Cursor-Based Pagination Cursor Format**
   - What we know: Backend should use cursor-based pagination (no OFFSET degradation), TanStack Query v5 supports cursor patterns
   - What's unclear: Exact cursor format (timestamp? ID? opaque string?) and backward/forward navigation logic
   - Recommendation: Use `id:${execution.id}` as cursor (simple, URL-safe), encode/decode with base64 for opacity. Test pagination backward 10 pages + forward 5 pages to verify correctness.

2. **GraphEdge Response Backend Readiness**
   - What we know: Phase 07 consumed `GET /api/tasks/{id}/graph` without sub-graph fields (parentId, execution_mode) because they were deferred
   - What's unclear: When will backend provide `parentId` + `execution_mode` in response? Phase 08-01 task?
   - Recommendation: Phase 08 Wave 0 MUST include backend enhancement. Frontend blocked until GraphEdge has sub-graph structure. Build with stubs first (assume response exists), then verify with integration tests.

3. **Log Storage Format (JSON Lines vs JSONB)**
   - What we know: Logs need to be searchable by timestamp, filterable by level/brain, stored as structured data
   - What's unclear: Should backend store as JSONB array in executions table or separate logs table with index on (task_id, timestamp)?
   - Recommendation: JSONB array (simpler, no JOIN on fetch, still indexable). Compress with gzip before storage if size grows > 100KB per execution. Test storage growth over 100 executions.

4. **Framer Motion Dependencies and Versions**
   - What we know: Phase 08 needs AnimatePresence for Focus Mode + Pulse & Reveal (niche expand animation)
   - What's unclear: Is Framer Motion already in package.json (Phase 06 mentioned animations but no explicit dep listed)
   - Recommendation: Check package.json. If missing, add `framer-motion@latest`. Verify easing functions `cubic-bezier(0.4, 0, 0.2, 1)` are equivalent to Framer Motion presets (likely `easeInOut`).

5. **Milestone Computation Algorithm Precision**
   - What we know: Max 7 milestones (Miller's Law chunking), equally spaced in snapshot array
   - What's unclear: Should milestones snap to "state change boundaries" (e.g., "nicho completed") or purely by index?
   - Recommendation: Pure index-based (simpler, deterministic). If user wants state-based scrubbing, defer to v2.2. Test that 7 milestones from a 100-event execution don't miss major state transitions.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Vitest (frontend) + pytest (backend) |
| Config file | `apps/web/vitest.config.ts` + `apps/api/pyproject.toml` |
| Quick run command | `cd apps/web && pnpm test:run` + `cd apps/api && uv run pytest tests/api -x --tb=short` |
| Full suite command | `cd apps/web && pnpm test:coverage` + `cd apps/api && uv run pytest tests --tb=short` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SV-01 | Fetch execution history, paginate (prev/next), display list | integration | `pytest tests/api/test_executions_list.py -x` | ❌ Wave 0 |
| SV-02 | Load execution detail, render Markdown per brain, scrub timeline | e2e | `vitest run apps/web/src/components/strategy-vault/__tests__/ExecutionDetail.test.tsx -x` | ❌ Wave 0 |
| ER-01 | Live logs stream, filter by level, isolate by brain, auto-follow | e2e (WS) | `vitest run apps/web/src/components/engine-room/__tests__/LiveLogPanel.test.tsx -x` | ❌ Wave 1 |
| ER-02 | API key CRUD (create show-once, revoke, list masked) | unit | `pytest tests/api/test_keys_crud.py -x` | ❌ Wave 0 |
| ER-03 | Fetch brain YAML config, render with syntax highlighting, copy-to-clipboard | unit | `vitest run apps/web/src/components/engine-room/__tests__/BrainYAMLViewer.test.tsx -x` | ❌ Wave 1 |
| UX-01 | Focus Mode auto-activate on task start, [Esc]/[F] to toggle, no re-trap | e2e | `vitest run apps/web/src/components/__tests__/FocusMode.e2e.test.tsx -x` | ❌ Wave 2 |

### Sampling Rate
- **Per task commit:** `cd apps/web && pnpm test:run` (Vitest watch, <30s) + `cd apps/api && uv run pytest tests/api/test_executions_list.py -x` (pytest, <15s) = 45s total
- **Per wave merge:** Full suite: `cd apps/web && pnpm test:coverage` (all tests) + `cd apps/api && uv run pytest tests --tb=short` (all tests) = ~5 min total
- **Phase gate:** Full suite green + E2E snapshot scrubbing verified (manual drag scrubber, logs sync correctly) before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/api/test_executions_list.py` — paginated GET /api/executions/history with cursor, filters
- [ ] `tests/api/test_executions_detail.py` — GET /api/executions/{id} returns snapshots + brain outputs
- [ ] `tests/api/test_keys_crud.py` — POST/GET/DELETE /api/keys (create show-once, mask, revoke)
- [ ] `tests/api/test_graph_subgraph.py` — GET /api/tasks/{id}/graph returns parentId + execution_mode
- [ ] `apps/api/mastermind_cli/models/execution.py` — Execution, BrainOutput, SnapshotMilestone schemas
- [ ] `apps/api/mastermind_cli/routes/executions.py` — history + detail endpoints
- [ ] `apps/api/mastermind_cli/routes/keys.py` — API key CRUD endpoints
- [ ] Backend GraphEdge enhancement: add sub-graph fields to response

*(If no gaps listed above: "None — existing test infrastructure covers all phase requirements")*

## Sources

### Primary (HIGH confidence)
- **Context7 React Flow (v12.x):** Sub-graph API, parentId binding, extent: 'parent' constraint — queried for React Flow node architecture
- **react-virtuoso docs (npm):** Virtual scrolling overscan, auto-follow behavior, filter integration — confirmed with official examples
- **Zustand docs (v5.x):** Immer middleware, module-level stores, Map support via enableMapSet — verified in brainStore pattern
- **Phase 07 CONTEXT.md & RESEARCH.md:** React Flow NODE_TYPES/EDGE_TYPES at module level, dagre layout stability, WS-02/WS-03 patterns — locked architectural patterns
- **Phase 05-06 codebase:** TanStack Query pagination (v5.91.3), Framer Motion AnimatePresence patterns, shadcn/ui + Tailwind 4 setup — verified working implementations

### Secondary (MEDIUM confidence)
- **react-markdown + remark-gfm docs:** GFM plugin syntax, custom components prop for mapping — verified with official examples
- **Framer Motion docs:** AnimatePresence + motion.div for conditional renders, easing function presets — confirmed stable APIs
- **Recharts docs:** Composable chart components, responsive containers, tooltip support — suitable for markdown block integration
- **react-syntax-highlighter docs:** Language support (YAML/TypeScript/JSON), style themes (VS Code Dark) — verified working

### Tertiary (LOW confidence)
- **API key security patterns (JWT field, hashing, allow-list):** Brain #5 (Backend) specifications mention "hash on backend + Redis allow-list," requires implementation verification in Phase 08-01

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** — Vitest, pytest, React 19, Next.js 16 established in Phase 05-07; new libraries (react-virtuoso, react-markdown) off-the-shelf standard
- Architecture: **HIGH** — React Flow sub-graphs verified with Context7 docs; snapshot scrubbing pattern simple and proven; Zustand store patterns established
- Pitfalls: **MEDIUM** — Focus Mode re-trapping is hypothetical (test will catch it); virtual scrolling flicker is known react-virtuoso configuration issue
- Test infrastructure: **MEDIUM** — Existing pytest + Vitest configs are ready; Wave 0 gaps are new endpoints (straightforward CRUD), not architectural unknowns

**Research date:** 2026-03-23
**Valid until:** 2026-04-06 (14 days — Phase 08 implementation ~7-10 days, architecture stable)
**Major version updates to monitor:** React 19.x (current), Next.js 16.x (breaking changes rare mid-LTS), React Flow 12.x (major API changes rare)
