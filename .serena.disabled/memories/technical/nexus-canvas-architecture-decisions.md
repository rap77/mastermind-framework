# NexusCanvas Architecture Decisions — Phase 07 Wave 2

## Decision: Module-Level NODE_TYPES and EDGE_TYPES
**Rule:** NODE_TYPES and EDGE_TYPES MUST be at module level, never inline or in component body.

**Why:** React Flow's default behavior checks `nodeTypes !== prevNodeTypes` on every render. Inline definitions (inside component or in render) fail this check, causing React Flow to warn and recalculate handles unnecessarily. Brain-07 (expert reviewer) flagged this as critical.

**How to apply:**
```typescript
// ✅ CORRECT
const NODE_TYPES = { custom: BrainNode }
export function NexusCanvas() { ... }

// ❌ WRONG
export function NexusCanvas() {
  const nodeTypes = { custom: BrainNode }  // Recalculates every render
  return <ReactFlow nodeTypes={nodeTypes} ... />
}
```

## Decision: dagre Layout Calculated Once at Mount
**Rule:** dagre layout must be calculated ONCE via `useState` initializer, never recalculated.

**Why:** Recalculating layout on every render causes:
- Jitter/flickering as node positions change
- Performance degradation (dagre is O(n²) for n nodes)
- Loss of user viewport stability

**How to apply:**
```typescript
const [layoutedNodes] = useState(() => {
  const layoutedNodes = getLayoutedNodes(nodes, edges, 'TB')
  return layoutedNodes
})
// layoutedNodes never changes after initial calculation
```

## Decision: Ghost Architecture — Inactive Nodes Dimmed
**Rule:** Inactive nodes use `elevation: none` and `box-shadow: none`. Only active nodes get shadows.

**Why:** Distinguishes active (illuminated) nodes from inactive (ghost) nodes visually. Brain-02 confirmed: "ghost nodes have no elevation, only active nodes cast shadows."

**How to apply:**
```typescript
// buildBlueprintNodes()
const ghostNode = {
  ...node,
  data: { ...node.data, ghost: true },
  style: { opacity: 0.5, borderStyle: 'dashed' }
}
const activeNode = {
  ...node,
  style: {
    boxShadow: '0 0 8px rgba(100, 255, 218, 0.6)',
    elevation: '1'
  }
}
```

## Decision: useBrainState(id) Targeted Selector
**Rule:** Use `useBrainState(id)` targeted selector in components, not `useStore(state => state.allBrains)`.

**Why:**
- Global selector causes ALL subscribers to re-render when ANY brain updates
- Targeted selector (O(1) Map.get) prevents cascade re-renders
- With 24 brains and RAF batching, cascade re-renders cause frame drops

**How to apply:**
```typescript
// ✅ CORRECT — only re-renders when brain-01 changes
const brainState = useBrainState('brain-01')

// ❌ WRONG — re-renders for ALL brain changes
const allBrains = useStore(state => state.allBrains)
const brainState = allBrains.find(b => b.id === 'brain-01')
```

## Decision: RAF Batching for WS Burst Events
**Rule:** Batch rapid WS events (brain_step_completed, task_completed) using RAF to prevent React batching overflow.

**Why:** 24 brains completing simultaneously = 24 setState calls outside React auto-batching window. Without RAF batching, each setState triggers a render → 24 renders = frame drop.

**How to apply:**
```typescript
// In brainStore WS handler
const pushHistorySnapshot = () => {
  // RAF batching: queue updates, drain before paint
  if (!rafHandle) {
    rafHandle = requestAnimationFrame(() => {
      // All pending updates flush here
      rafHandle = null
    })
  }
}
```

## Decision: Immer enableMapSet() Required
**Rule:** Call `enableMapSet()` from Immer when using `Map<K, V>` data structures.

**Why:** Immer doesn't support Map mutations by default (only plain objects and arrays). Without enableMapSet(), mutations are silently ignored.

**How to apply:**
```typescript
import { enableMapSet } from 'immer'
enableMapSet()  // Once at app startup

// Now this works
produce(draftState, draft => {
  draft.brainMap.set('brain-01', newState)
})
```

## Decision: nodes Array is Layout-Only
**Rule:** React Flow `nodes` array is layout-only (from dagre). Brain state lives in brainStore Map, not in nodes.

**Why:** Separates concerns:
- dagre calculates layout (position, size)
- brainStore manages state (status, data)
- NexusCanvas renders nodes from brainStore data, not React Flow node data

**How to apply:**
```typescript
// Layout from dagre (never changes)
const layoutedNodes = getLayoutedNodes(...)

// State from brainStore (updates with WS events)
const brainState = useBrainState(nodeId)

// Render uses both
const nodeStyle = {
  ...layoutedNode.style,
  opacity: brainState.complete ? 1 : 0.5
}
```

## Decision: Cooldown Mode is Canvas-Level State
**Rule:** Cooldown Mode is managed at NexusCanvas level, not in brainStore.

**Why:** Cooldown Mode affects canvas background color (not individual brain state). Mixing canvas-level UI state into brainStore pollutes a domain-specific store.

**How to apply:**
```typescript
export function NexusCanvas() {
  const [cooldownMode, setCooldownMode] = useState(false)

  // WS event: task_completed → enable cooldown
  useEffect(() => {
    const unsub = useWSStore.subscribe(
      state => state.taskCompleted,
      () => setCooldownMode(true)
    )
    return unsub
  }, [])

  return (
    <div style={{
      background: cooldownMode ? '#111113' : '#0B0C10'
    }}>
      {/* canvas */}
      <CooldownFAB onReset={() => setCooldownMode(false)} />
    </div>
  )
}
```

## Decision: HybridFlowEdge 4-State State Machine
**Rule:** Edge colors follow a 4-state pattern:
- `idle/undefined`: muted slate
- `active`: neon cyan (bright animation)
- `complete`: latched green (solid, no animation)
- `error`: vivid red (pulsing)

**Why:** Visual language matches BrainNode states and provides at-a-glance feedback for edge traversal.

**How to apply:**
```typescript
const getEdgeColor = (state) => {
  switch(state) {
    case 'active': return '#64FFDA'  // neon cyan
    case 'complete': return '#10B981'  // latched green
    case 'error': return '#FF3D00'  // vivid red
    default: return '#8892B0'  // muted slate
  }
}
```
