# Phase 07: The Nexus - Research

**Researched:** 2026-03-22
**Domain:** React Flow DAG visualization, dagre layout, WebSocket-driven node illumination, FastAPI graph endpoint
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Entry Point & Navigation**
- Ruta propia: `/nexus` — pantalla dedicada, URL shareable, estado persistente en refresh
- Navegación desde Command Center: Al submitear un brief, navegación inmediata a `/nexus`; arrancar con Nexus Skeleton mientras el backend procesa; cuando llega el `task_id`, los nodos reales emergen del esqueleto
- Scope de tasks: Live-First — muestra la task activa de la sesión actual; footer con flechas `[<] [>]` para navegar entre tasks de la sesión (Zustand en memoria); redirige a Strategy Vault para historial histórico
- Sin auto-redirect: Al terminar una task, el Nexus NO navega automáticamente a otra pantalla

**Idle State (Ghost Architecture)**
- Canvas no vacío: mostrar los 24 nodos en "Blueprint" style — líneas punteadas, opacidad 20%, sin colores de nicho — cargados desde `GET /api/brains`
- Interactivo en idle: Clic en nodo → Side Panel con config estática del cerebro
- Transición a active: Al iniciar un brief, los nodos involucrados se iluminan con color de nicho; el resto se desvanece a 5% de opacidad
- Session counter por nodo: Badge mostrando cuántas veces fue invocado en la sesión (Zustand en memoria)

**Post-Execution (Cooldown Mode)**
- Graph persiste en modo Read-Only (Ghost Trace) al recibir `task_completed`
- Background del canvas cambia de azul oscuro a gris casi negro
- Edges solidifican: `animated: false`, glow verde (success), línea punteada roja parpadeante (error)
- FAB con 3 acciones: `[Enter]` → Command Center, `[V]` → Strategy Vault, `[R]` → re-ejecutar
- Keyboard-first: Auto-focus en FAB al completar
- `[Esc]` → limpia Ghost Trace, vuelve a Ghost Architecture sin salir de `/nexus`

**Node Detail (Side Panel)**
- Panel lateral derecho fijo — canvas se achica ~30% al abrirse
- Datos en ejecución: Status badge, último evento WS, timestamp, niche context
- Datos en idle: Config estática del cerebro (nombre, nicho, capabilities del YAML)
- Live-binding via `useBrainState(id)` — panel actualiza en tiempo real sin re-fetch
- `nodrag nopan` en todos los elementos interactivos dentro del nodo (NEX-03)

**Edge Animations (Hybrid Flow)**
- Base: React Flow `animated: true` nativo (stroke-dashoffset) — 60fps garantizado
- Neon glow via Tailwind 4 `drop-shadow` + color del nicho activo
- Data-Latching: `active` → flujo animado; `complete` → `animated: false`, glow verde; `error` → línea punteada roja parpadeante (`animate-pulse`)
- Star topology: Coordinator como hub central, 24 brains como satélites, agrupados por color de nicho

**Ghost Trace (Data Prep)**
- State Snapshots en brainStore: push de `{ timestamp, brainStates: Map snapshot }` a `historyStack` en Zustand con cada evento WS
- No UI de scrubbing en Phase 07 — data disponible para Phase 08

### Claude's Discretion
- Exacta implementación del Nexus Skeleton (animación de partículas vs. skeleton nodes genéricos)
- Algoritmo dagre — radial layout vs. hierarchical (elegir el que quede mejor visualmente con 24 nodos)
- Exact stroke-width y drop-shadow values para el neon glow
- Cómo manejar la sesión nav footer (`[<] [>]`) si solo hay 1 task en sesión

### Deferred Ideas (OUT OF SCOPE)
- Timeline Scrubbing UI — data (historyStack) se captura en Phase 07; la UI va en Phase 08
- Heatmap de uso histórico — requiere `/api/brains/usage` endpoint (no existe)
- Variable injection at runtime — requiere nueva API de control de ejecución, Phase 09+
- Data Particles (custom SVG) — puntos de luz viajando por edge paths, deferido por riesgo 60fps
- WS events con `duration_ms` y `payload_kb`
- Deep linking `/nexus?task=123&focus=brain-7`
- Parallel Routes (@slot) para Nexus + Command Center simultáneos
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| BE-02 | `GET /api/tasks/{id}/graph` returns React Flow compatible payload with `{ nodes[], edges[], layout_positions }` including initial node positions | Endpoint EXISTS in tasks.py but returns custom `GraphNode`/`GraphEdge` models NOT compatible with React Flow — needs adapter layer and `layout_positions` field added. Gap confirmed by codebase inspection. |
| NEX-01 | DAG of brain dependencies as React Flow graph with custom shadcn/ui Card nodes (NODE_TYPES declared at module level) | `@xyflow/react` v12.10.1 already installed. `NODE_TYPES` at module level is CRITICAL anti-infinite-render pattern confirmed by official docs and prior Phase 05/06 decisions. shadcn `card.tsx` exists. |
| NEX-02 | Nodes illuminate in real-time (border color, glow) as brains start, complete, or fail via WebSocket events | `brainStore.ts` Map<brainId, BrainState> + `useBrainState(id)` selector already proven in Phase 05. WS pipeline fully operational. Node visual update via `data` prop without layout recalculation. |
| NEX-03 | Click a node to see brain details without triggering accidental drag/pan — interactive elements use `nodrag nopan` CSS classes | `nodrag` and `nopan` are confirmed @xyflow/react v12 built-in CSS utility classes. shadcn `Sheet` component needed but NOT installed — must be added in Wave 0. |
</phase_requirements>

---

## Summary

Phase 07 builds on a solid foundation: `@xyflow/react` v12.10.1, Zustand 5, Immer, TanStack Query, and the proven WS→brainStore pipeline are all already installed and battle-tested from Phases 05 and 06. The core challenge is threefold: (1) adapt the existing `GET /api/tasks/{id}/graph` endpoint whose `GraphNode`/`GraphEdge` models do NOT map to React Flow's `Node`/`Edge` types — `id` maps but `from_node` (aliased as `from`) maps to `source`, `to` maps to `target`, and `layout_positions` is absent; (2) build the NexusCanvas with a one-shot dagre layout (the `@dagrejs/dagre` package is NOT installed, must be added); (3) wire WS events to visual node updates without ever mutating the layout positions array.

The critical architectural invariant carried from prior phases: `nodes` array is layout-only and immutable post-mount — brain status is read directly from `brainStore` via `useBrainState(id)` inside each `BrainNode` component. This is proven to work at 60fps with 24 simultaneous events. The `NODE_TYPES` constant at module level (outside JSX) is non-negotiable — violating this causes infinite React Flow re-renders.

The `shadcn Sheet` component for the Side Panel is NOT currently installed (only `card`, `button`, `dialog`, `input` exist). Plan 07-02's Wave 0 must `pnpm dlx shadcn add sheet` before building the panel. The `@dagrejs/dagre` package must also be installed with `pnpm add @dagrejs/dagre`.

**Primary recommendation:** Three clean plans — 07-01 backend adapter (FastAPI), 07-02 NexusCanvas + BrainNode (React Flow + dagre), 07-03 WS illumination wiring (brainStore extensions + edge state machine). Ghost Architecture idle state uses `GET /api/brains` (already working) as the fallback, so BE-02 is enhancement-only (not blocking).

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `@xyflow/react` | 12.10.1 (installed) | React Flow DAG canvas | Already installed, used in prior phases, CSS registered in globals.css |
| `@dagrejs/dagre` | latest | Graph layout positioning | The official React Flow recommended layout library for directed graphs |
| `zustand` + `immer` | 5.0.12 (installed) | brainStore state + historyStack | Already proven at 60fps with RAF batching, O(1) Map selectors |
| `@tanstack/react-query` | v5.91.3 (installed) | Fetch Ghost Architecture initial data | Already configured, `react-query.tsx` provider present |
| `shadcn Sheet` | via shadcn CLI (NOT installed) | Side Panel drawer | shadcn `dialog.tsx` exists, Sheet needs install |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `lucide-react` | 0.577.0 (installed) | Node status icons (check, x, loader) | NEX-03 redundant state communication: color + icon |
| `@types/dagre` | with @dagrejs/dagre | TypeScript types for dagre | Always — this is a TypeScript project |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `@dagrejs/dagre` | `elkjs` | ELK is more powerful for complex graphs but adds complexity the docs explicitly warn against for support; dagre is sufficient for 24-node star topology |
| `@dagrejs/dagre` | Manual radial positions | Pure math radial calculation avoids npm dep but requires custom positioning for 24 nodes, more error-prone |
| shadcn Sheet | custom side panel | Sheet provides accessible, animated drawer with proper focus trapping and keyboard dismiss — do not hand-roll |

**Installation (Wave 0 of Plan 07-02):**
```bash
pnpm add @dagrejs/dagre
pnpm add -D @types/dagre
pnpm dlx shadcn add sheet
```

---

## Architecture Patterns

### Recommended Project Structure
```
apps/web/src/
├── app/(protected)/nexus/
│   └── page.tsx                  # Server Component — fetches Ghost Architecture from /api/brains
├── components/nexus/
│   ├── NexusCanvas.tsx            # 'use client' — ReactFlow + dagre layout (mount only)
│   ├── BrainNode.tsx              # React.memo — reads brainStore via useBrainState(id)
│   ├── NodeStatusIndicator.tsx    # Pure display: icon + color for 5 states
│   ├── HybridFlowEdge.tsx         # Custom edge with neon glow, animated flag, state machine
│   ├── NodeDetailPanel.tsx        # shadcn Sheet, right-side, live via useBrainState(id)
│   ├── CooldownFAB.tsx            # FAB bar with [Enter]/[V]/[R]/[Esc] keyboard shortcuts
│   ├── NexusSkeleton.tsx          # Loading state before brains data arrives
│   └── __tests__/                 # Co-located tests (Vitest)
├── stores/
│   └── brainStore.ts             # EXTEND: add historyStack + sessionInvocationCounts
└── types/
    └── api.ts                    # EXTEND: add TaskGraphNodeSchema, TaskGraphEdgeSchema, ReactFlowGraphSchema
```

### Pattern 1: NODE_TYPES at Module Level (CRITICAL)
**What:** `nodeTypes` object defined OUTSIDE the React component tree, at module scope
**When to use:** ALWAYS — every React Flow implementation without exception
**Why critical:** React Flow uses `nodeTypes` as a dependency in internal effects. If defined inline in JSX/render, the object reference changes every render, causing infinite re-renders and canvas flicker.
```typescript
// Source: reactflow.dev/learn/customization/custom-nodes
// CORRECT — module level, never changes reference
const NODE_TYPES = {
  brainNode: BrainNode,
  coordinatorNode: CoordinatorNode,
} as const

export function NexusCanvas() {
  return <ReactFlow nodeTypes={NODE_TYPES} ... />
}

// WRONG — new object every render = infinite re-renders
export function NexusCanvas() {
  return <ReactFlow nodeTypes={{ brainNode: BrainNode }} ... />  // NEVER do this
}
```

### Pattern 2: Layout-Only Nodes + Zustand State (PROVEN FROM PHASE 05)
**What:** `nodes` array contains only static position data. Brain status is NOT in `nodes` — it's read from `brainStore` inside each `BrainNode` via `useBrainState(id)`.
**When to use:** Always — the invariant that prevents layout recalculation on WS events
```typescript
// Source: Phase 05/06 decisions, STATE.md
// nodes array — LAYOUT ONLY, never mutated after dagre runs
const [nodes] = useState<Node[]>(() => layoutedNodes)  // latched at mount

// BrainNode.tsx — reads live state from brainStore independently
const BrainNode = React.memo(({ id }: NodeProps) => {
  const brainState = useBrainState(id)  // O(1) Map lookup, only re-renders THIS node
  return <NodeStatusIndicator status={brainState?.status ?? 'idle'} />
})
```

### Pattern 3: Dagre One-Shot Layout at Mount
**What:** Run dagre layout exactly once when the component mounts with the 24 blueprint nodes. Latch positions in state. Never re-run on WS events.
**When to use:** During NexusCanvas initialization only
```typescript
// Source: reactflow.dev/examples/layout/dagre
import dagre from '@dagrejs/dagre'

const dagreGraph = new dagre.graphlib.Graph()
dagreGraph.setDefaultEdgeLabel(() => ({}))

function getLayoutedNodes(nodes: Node[], edges: Edge[], direction = 'TB'): Node[] {
  dagreGraph.setGraph({ rankdir: direction, nodesep: 80, ranksep: 100 })

  nodes.forEach((node) => {
    // Use fixed dimensions for blueprint nodes (not node.measured — layout runs before measure)
    dagreGraph.setNode(node.id, { width: 160, height: 60 })
  })
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  dagre.layout(dagreGraph)

  return nodes.map((node) => {
    const { x, y } = dagreGraph.node(node.id)
    return { ...node, position: { x: x - 80, y: y - 30 } }
  })
}

// In NexusCanvas — run ONCE
const layoutedNodes = useMemo(
  () => getLayoutedNodes(blueprintNodes, blueprintEdges),
  []  // Empty deps — layout is mount-time only
)
```

### Pattern 4: brainStore Extensions for Ghost Trace
**What:** Add `historyStack` and `sessionInvocationCounts` to the existing `brainStore`
**When to use:** Extend in Plan 07-03 when wiring WS illumination
```typescript
// Extend brainStore.ts — add to BrainStoreState interface
interface BrainStoreState {
  // Existing
  brains: Map<string, BrainState>
  _queue: BrainState[]
  _rafId: number | null
  updateBrain: (brain: BrainState) => void
  _drainQueue: () => void
  // NEW for Phase 07
  historyStack: Array<{ timestamp: number; snapshot: Map<string, BrainState> }>
  sessionInvocationCounts: Map<string, number>
  pushHistorySnapshot: () => void
  incrementInvocationCount: (brainId: string) => void
}
```

### Pattern 5: Edge State Machine (Data-Latching)
**What:** Edge `animated` flag and style driven by a computed state from brainStore, not stored in nodes array
**When to use:** Plan 07-03 — WS illumination wiring
```typescript
// HybridFlowEdge.tsx reads brainStore to determine edge appearance
// State machine: idle → active (animated) → complete (latched) | error (pulsing)
const sourceState = useBrainState(edge.source)

const edgeStyle = useMemo(() => {
  switch (sourceState?.status) {
    case 'active':   return { animated: true, style: { stroke: nicheColor, filter: 'drop-shadow(0 0 6px currentColor)' } }
    case 'complete': return { animated: false, style: { stroke: '#64FFDA', filter: 'drop-shadow(0 0 4px #64FFDA)' } }
    case 'error':    return { animated: false, className: 'animate-pulse', style: { stroke: '#FF3D00', strokeDasharray: '5,5' } }
    default:         return { animated: false, style: { stroke: '#8892B0', opacity: 0.3 } }
  }
}, [sourceState?.status])
```

### Pattern 6: FastAPI Graph Endpoint Adapter (BE-02)
**What:** `GET /api/tasks/{id}/graph` exists but returns `GraphNode` (id, label, level, state) and `GraphEdge` (from_node, to) — NOT React Flow `Node` (id, position, data) and `Edge` (id, source, target)
**What needs to change:**
1. Add `layout_positions: dict[str, dict] | None` to `TaskGraphResponse` — optional, frontend can compute dagre layout client-side
2. Frontend adapter transforms: `GraphNode → RF Node`, `GraphEdge.from_node → RF Edge.source`, `GraphEdge.to → RF Edge.target`
3. Ghost Architecture fallback: if `task_id` is null, use `GET /api/brains` to build blueprint nodes (already working)

**Decision for Plan 07-01:** Since Coordinator.orchestrate() is not yet wired to task creation (tasks.py:97 TODO), the graph endpoint will return empty `nodes: [], edges: []` for most tasks. Plan 07-01 should:
- Add `layout_positions` field to the response model
- Build the 24-node star topology graph from `GET /api/brains` as the default/fallback
- The frontend always renders the full 24-node Ghost Architecture; task graph data illuminates which nodes were active

### Anti-Patterns to Avoid
- **NODE_TYPES inline in JSX:** Causes infinite re-renders. Must be module-level const.
- **Dagre on every WS event:** Run once at mount, latch positions. WS events only update `brainStore`, never the nodes array.
- **node.measured for initial layout:** When layout runs at mount time, nodes have not been measured yet. Use fixed dimensions (160x60 for brain nodes, 80x80 for coordinator hub).
- **storing brain status in node.data:** Keep `nodes` array layout-only. Status in brainStore. This is the invariant that keeps 60fps.
- **Sheet import from dialog:** Sheet is a separate shadcn component. `pnpm dlx shadcn add sheet` required.
- **Forgetting prefers-reduced-motion:** All CSS animations must check `@media (prefers-reduced-motion: reduce)` — QA requirement.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Graph node positioning | Custom radial math | `@dagrejs/dagre` | Edge crossing minimization, proper spacing for 24 nodes is non-trivial; dagre handles node separation parameters |
| Accessible side drawer | Custom fixed panel | `shadcn Sheet` | Focus trapping, keyboard dismiss, ARIA attributes, animation — all handled; Sheet is already the project's UI framework |
| Animated edges | Custom SVG stroke animation | React Flow `animated: true` | React Flow's built-in stroke-dashoffset animation is GPU-accelerated, tested at 60fps — do not re-implement |
| Node status icons | Custom SVG icon set | `lucide-react` (installed) | CheckCircle, XCircle, Loader2 — already available, consistent with rest of app |
| WS burst batching | New batching mechanism | Existing RAF batching in `brainStore.updateBrain()` | Already proven at Phase 05, handles 24 simultaneous events at 60fps |

**Key insight:** The entire real-time pipeline (WS → Zod validation → RAF batching → Zustand Map → targeted selectors) is proven infrastructure. Phase 07 is a consumer of this pipeline, not a builder of it.

---

## Common Pitfalls

### Pitfall 1: NODE_TYPES Reference Instability
**What goes wrong:** Canvas infinitely re-renders, nodes flicker, React DevTools shows non-stop BrainNode remounts
**Why it happens:** `nodeTypes={{ brainNode: BrainNode }}` inside JSX creates a new object on every render; React Flow's internal useEffect has nodeTypes in deps
**How to avoid:** `const NODE_TYPES = { brainNode: BrainNode }` at module level — NEVER inside a component
**Warning signs:** Visible flicker, console warning "It looks like you've created a new nodeTypes/edgeTypes object"

### Pitfall 2: Dagre with Unmeasured Nodes
**What goes wrong:** All nodes collapse to position (0,0) or overlap
**Why it happens:** If you try to use `node.measured.width/height` (React Flow v12 API) for initial layout, nodes have not been measured yet at first render
**How to avoid:** Use fixed `nodeWidth = 160, nodeHeight = 60` constants for dagre. Mount layout with fixed sizes, not measured sizes.
**Warning signs:** All nodes stacked at origin, or NaN positions in dagre output

### Pitfall 3: Layout Recalculation on WS Events
**What goes wrong:** Canvas "jumps" / pan resets every time a brain status changes
**Why it happens:** `nodes` state is updated with brain status, triggering dagre recalculation, producing new position objects, React Flow interprets as node move
**How to avoid:** `nodes` array NEVER contains brain status. BrainNode reads from brainStore via `useBrainState(id)`. Only `node.data.label` and `node.position` in nodes array.
**Warning signs:** CLS > 0.1 during execution, viewport pan resets

### Pitfall 4: `@dagrejs/dagre` Not Installed
**What goes wrong:** Build error `Cannot find module '@dagrejs/dagre'`
**Why it happens:** dagre is NOT currently in package.json — it is confirmed absent from node_modules
**How to avoid:** Wave 0 task in Plan 07-02: `pnpm add @dagrejs/dagre`
**Warning signs:** TypeScript `Module not found` error at build

### Pitfall 5: shadcn Sheet Not Available
**What goes wrong:** `Cannot find module '@/components/ui/sheet'`
**Why it happens:** Only card, button, dialog, input are installed. Sheet is a separate shadcn component.
**How to avoid:** Wave 0 task in Plan 07-02: `pnpm dlx shadcn add sheet`
**Warning signs:** Import error when building NodeDetailPanel

### Pitfall 6: BE-02 Empty Graph for Pending Tasks
**What goes wrong:** `GET /api/tasks/{id}/graph` returns `{ nodes: [], edges: [] }` for all tasks (Coordinator not wired)
**Why it happens:** `tasks.py:97` — `TODO: Integrate with Coordinator.orchestrate()` — the flow graph is never populated when creating a task
**How to avoid:** Plan 07-01 must build the 24-node star topology from `GET /api/brains` as the default graph. The Nexus always shows the full system map; task-specific subgraph illumination is Phase 08 territory.
**Warning signs:** Empty canvas when navigating to `/nexus` after task creation

### Pitfall 7: React Flow CSS Missing for New Route
**What goes wrong:** Node handles invisible, edges not rendering, layout broken
**Why it happens:** `@xyflow/react/dist/style.css` is already in `globals.css @layer base` — this is fine for new routes since globals.css is app-wide. No action needed.
**Warning signs:** This pitfall is AVOIDED — CSS is already global. Do not add another `@import` in nexus-specific files.

---

## Code Examples

### Verified Pattern: BrainNode with React.memo + nodrag/nopan
```typescript
// Source: Codebase inspection + reactflow.dev/learn/customization/custom-nodes
import React from 'react'
import type { NodeProps } from '@xyflow/react'
import { Handle, Position } from '@xyflow/react'
import { useBrainState } from '@/stores/brainStore'
import { NodeStatusIndicator } from './NodeStatusIndicator'
import { Card, CardContent } from '@/components/ui/card'

// NODE_TYPES must reference this — React.memo prevents cascade re-renders
export const BrainNode = React.memo(function BrainNode({ id, data }: NodeProps) {
  const brainState = useBrainState(id)  // O(1) Map lookup (WS-03 pattern)
  const status = brainState?.status ?? 'idle'

  return (
    <Card className="w-40 relative" data-status={status}>
      <Handle type="target" position={Position.Top} />
      <CardContent className="p-2">
        <NodeStatusIndicator status={status} />
        {/* nodrag nopan on ALL interactive children (NEX-03) */}
        <button className="nodrag nopan text-xs" onClick={() => data.onSelect?.(id)}>
          {data.label as string}
        </button>
      </CardContent>
      <Handle type="source" position={Position.Bottom} />
    </Card>
  )
})
BrainNode.displayName = 'BrainNode'
```

### Verified Pattern: Dagre Layout Function
```typescript
// Source: reactflow.dev/examples/layout/dagre — adapted for star topology
import dagre from '@dagrejs/dagre'
import type { Node, Edge } from '@xyflow/react'

const dagreGraph = new dagre.graphlib.Graph()
dagreGraph.setDefaultEdgeLabel(() => ({}))

const BRAIN_NODE_W = 160
const BRAIN_NODE_H = 60
const COORDINATOR_W = 100
const COORDINATOR_H = 100

export function getLayoutedNodes(nodes: Node[], edges: Edge[]): Node[] {
  dagreGraph.setGraph({ rankdir: 'TB', nodesep: 60, ranksep: 80 })

  nodes.forEach((node) => {
    const isCoordinator = node.id === 'brain-08' || node.type === 'coordinatorNode'
    dagreGraph.setNode(node.id, {
      width: isCoordinator ? COORDINATOR_W : BRAIN_NODE_W,
      height: isCoordinator ? COORDINATOR_H : BRAIN_NODE_H,
    })
  })

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  dagre.layout(dagreGraph)

  return nodes.map((node) => {
    const { x, y, width, height } = dagreGraph.node(node.id)
    return {
      ...node,
      position: { x: x - width / 2, y: y - height / 2 },
      draggable: false,  // Ghost Architecture is non-draggable
    }
  })
}
```

### Verified Pattern: FastAPI Response Adapter (Frontend)
```typescript
// apps/web/src/lib/api.ts — additive, follows existing fetchBrains() pattern
export interface ReactFlowGraphPayload {
  nodes: Array<{ id: string; label: string; level: number; state: string }>
  edges: Array<{ from: string; to: string }>
  layout_positions: Record<string, { x: number; y: number }> | null
}

export async function fetchTaskGraph(taskId: string): Promise<ReactFlowGraphPayload> {
  const apiUrl = process.env.API_URL || 'http://localhost:8000'
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value
  const response = await fetch(`${apiUrl}/api/tasks/${taskId}/graph`, {
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    next: { revalidate: 0 },
  })
  if (!response.ok) throw new Error(`Graph fetch failed: ${response.status}`)
  return response.json()
}
```

### Verified Pattern: brainStore historyStack Extension
```typescript
// Source: Codebase inspection + 07-CONTEXT.md decisions
// Extend brainStore.ts — add pushHistorySnapshot action
pushHistorySnapshot: () => {
  set(state => {
    // Snapshot the current Map (defensive copy)
    const snapshot = new Map(state.brains)
    state.historyStack.push({ timestamp: Date.now(), snapshot })
  })
},
```

### Verified Pattern: Existing WSBrainBridge Subscription
```typescript
// Source: apps/web/src/components/ws/WSBrainBridge.tsx (codebase read)
// The subscribe pattern for new WS event types in NexusCanvas:
useEffect(() => {
  const unsubscribe = subscribe('task_update_batch', (data) => {
    const result = WSMessageSchema.safeParse(data)
    if (!result.success) return
    for (const event of result.data.data) {
      updateBrain({ id: event.brain_id, status: event.status, lastUpdated: event.timestamp })
      pushHistorySnapshot()                      // Ghost Trace (Phase 07 addition)
      incrementInvocationCount(event.brain_id)   // Session counter badge
    }
  })
  return unsubscribe
}, [subscribe, updateBrain, pushHistorySnapshot, incrementInvocationCount])
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `reactflow` package | `@xyflow/react` package | v12 migration | Import path changed; named import not default |
| `node.width/height` | `node.measured.width/height` | v12 | Use fixed dimensions for mount-time layout (not measured) |
| `useNodesState` managing all node data | nodes = layout only, status from external store | Phase 05 decision | Enables O(1) per-brain updates without canvas layout thrash |
| Global dagre graph shared | Module-level singleton dagreGraph | Standard pattern | Avoids recreation cost, safe since layout is mount-only |

**Deprecated/outdated:**
- `reactflow` default import: Use `import { ReactFlow } from '@xyflow/react'` (named import)
- `node.data` for status: Proven anti-pattern in this project — use `brainStore` Map

---

## Open Questions

1. **Dagre layout direction for 24-node star topology**
   - What we know: dagre supports TB (top-bottom), LR (left-right), BT, RL; star topology works with TB having coordinator at level 0
   - What's unclear: Whether 24 satellites will render aesthetically with dagre TB or whether manual radial is better
   - Recommendation: Claude's Discretion — start with `rankdir: 'TB'` and `nodesep: 60`; if it looks bad, switch to a manual radial calculation placing coordinator at center and brains at equal angular intervals. Decision deferred to Plan 07-02 implementer.

2. **`layout_positions` field in BE-02: server-computed vs. client-only**
   - What we know: The field is required by the requirement but frontend can compute dagre client-side; backend adding it would require knowing React Flow coordinate system
   - What's unclear: Whether any benefit comes from server-side position pre-computation
   - Recommendation: Add the `layout_positions` field to the Pydantic model as optional (`None`). Frontend always re-computes with dagre regardless. The field exists for future backend-driven layout (Phase 08).

3. **Nexus Skeleton while waiting for task data**
   - What we know: Claude's Discretion — skeleton nodes genéricos are simpler; particle animation is higher risk
   - Recommendation: Use 24 pulsing skeleton cards with `animate-pulse` Tailwind class (same pattern as shadcn Skeleton component). No particles. Simple, fast, consistent with the rest of the UI.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Vitest 4.1.0 + @testing-library/react 16.3.2 |
| Config file | `apps/web/vitest.config.ts` |
| Quick run command | `cd apps/web && pnpm vitest run --reporter=verbose` |
| Full suite command | `cd apps/web && pnpm vitest run` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| BE-02 | `GET /api/tasks/{id}/graph` returns `layout_positions` field + React Flow compatible shape | unit (pytest) | `cd apps/api && uv run pytest tests/api/test_executions.py -k "graph" -x` | ✅ file exists, needs new test |
| NEX-01 | NODE_TYPES stability — changing BrainState does NOT cause canvas remount | unit (Vitest) | `cd apps/web && pnpm vitest run src/components/nexus/__tests__/NexusCanvas.test.tsx` | ❌ Wave 0 |
| NEX-01 | Dagre positions stable — 24 node positions unchanged between renders | unit (Vitest) | `cd apps/web && pnpm vitest run src/components/nexus/__tests__/layout.test.ts` | ❌ Wave 0 |
| NEX-02 | brainStore historyStack — snapshot pushed on each WS event | unit (Vitest) | `cd apps/web && pnpm vitest run src/stores/__tests__/brainStore.test.ts` | ✅ file exists, needs new cases |
| NEX-02 | BrainNode re-renders only on its own brainId change | unit (Vitest) | `cd apps/web && pnpm vitest run src/components/nexus/__tests__/BrainNode.test.tsx` | ❌ Wave 0 |
| NEX-03 | Click on BrainNode triggers onSelect without triggering drag | unit (Vitest) | `cd apps/web && pnpm vitest run src/components/nexus/__tests__/BrainNode.test.tsx` | ❌ Wave 0 |
| NEX-03 | nodrag nopan classes present on all interactive children | unit (Vitest) | included in BrainNode.test.tsx | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `cd apps/web && pnpm vitest run src/components/nexus/__tests__/ src/stores/__tests__/brainStore.test.ts`
- **Per wave merge:** `cd apps/web && pnpm vitest run`
- **Phase gate:** Full suite (web + api) green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `apps/web/src/components/nexus/__tests__/NexusCanvas.test.tsx` — covers NEX-01 node stability
- [ ] `apps/web/src/components/nexus/__tests__/BrainNode.test.tsx` — covers NEX-02 targeted re-render, NEX-03 nodrag
- [ ] `apps/web/src/components/nexus/__tests__/layout.test.ts` — covers dagre position stability
- [ ] `pnpm add @dagrejs/dagre` — missing dependency for layout tests to resolve
- [ ] `pnpm dlx shadcn add sheet` — missing shadcn component for NodeDetailPanel

---

## Sources

### Primary (HIGH confidence)
- Codebase inspection — `apps/web/src/stores/brainStore.ts`, `wsStore.ts`, `WSBrainBridge.tsx`, `package.json`, `globals.css`, `vitest.config.ts`, `apps/web/src/types/api.ts`
- Codebase inspection — `apps/api/mastermind_cli/api/routes/tasks.py` — confirmed graph endpoint exists with incompatible response model
- `reactflow.dev/examples/layout/dagre` — dagre layout with @xyflow/react v12, including node dimension approach
- `reactflow.dev/learn/customization/custom-nodes` — NODE_TYPES module-level requirement, nodrag/nopan CSS classes
- `reactflow.dev/learn/layouting/layouting` — layout library comparison, dagre recommendation for directed graphs

### Secondary (MEDIUM confidence)
- `@xyflow/react` v12.10.1 package exports (inspected via node require) — confirmed API surface: `ReactFlow`, `useNodesState`, `useEdgesState`, `Handle`, `Position`, `Background`, `Controls`, `applyNodeChanges`, `applyEdgeChanges`
- STATE.md decisions log — NODE_TYPES at module level listed as established architecture decision from Phase 05

### Tertiary (LOW confidence)
- WebSearch result: dagre v12 uses `node.measured` for dynamic layouts — LOW confidence as applicable only to auto-layout (not mount-only); fixed dimensions approach is sufficient for Phase 07 static layout

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages confirmed installed or absent via direct filesystem inspection
- Architecture: HIGH — patterns derived from existing codebase (brainStore, WS pipeline) + official React Flow docs
- BE-02 gap analysis: HIGH — tasks.py read directly, missing `layout_positions` field confirmed, Coordinator TODO confirmed at line 97
- Pitfalls: HIGH — pitfalls 1-5 derived from codebase inspection; pitfall 6 confirmed from tasks.py code
- shadcn Sheet gap: HIGH — `ls apps/web/src/components/ui/` shows only card/button/dialog/input; sheet absent

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable stack, no fast-moving dependencies for this phase)
