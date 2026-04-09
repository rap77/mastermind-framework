# Brain #4 (Frontend) — Phase 17 Consultation

> **Phase:** 17 — UI Evolution
> **Date:** 2026-04-08
> **Expertise:** React patterns, state management, WebSocket integration, performance optimization

---

## Verified Insights

**From existing codebase + BRAIN-FEED-04:**
- wsDispatcher.ts singleton + brainStore RAF batching (preserved)
- React Compiler: DISABLED (conflicts with React.memo on RF nodes)
- NO inline NODE_TYPES — always module level
- WS updates touch only `data` prop — never positions, never topology
- `cookies()` is async in Next.js 16 — `await cookies()` required
- React Flow CSS in `@layer base` — handles break without this
- Zustand targeted selectors (useBrainState) — prevents cascade re-renders
- TanStack Query staleTime: 30s for stable data
- 407 tests passing (Vitest)

---

## State Management Strategy

### UIE-01 (Three-Column Layout) — layoutStore

**Store Design:**
```typescript
// apps/web/src/stores/layoutStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface LayoutState {
  // Column collapse states
  companyRailCollapsed: boolean
  sidebarCollapsed: boolean
  propertiesPanelOpen: boolean

  // Density mode for monitoring panel
  densityMode: 'compact' | 'normal' | 'detailed'

  // Actions
  toggleCompanyRail: () => void
  toggleSidebar: () => void
  togglePropertiesPanel: () => void
  setDensityMode: (mode: 'compact' | 'normal' | 'detailed') => void
}

export const useLayoutStore = create<LayoutState>()(
  persist(
    (set) => ({
      companyRailCollapsed: false,
      sidebarCollapsed: false,
      propertiesPanelOpen: false,
      densityMode: 'compact',

      toggleCompanyRail: () => set((state) => ({ companyRailCollapsed: !state.companyRailCollapsed })),
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      togglePropertiesPanel: () => set((state) => ({ propertiesPanelOpen: !state.propertiesPanelOpen })),
      setDensityMode: (mode) => set({ densityMode: mode }),
    }),
    {
      name: 'mastermind-layout', // localStorage key
    }
  )
)
```

**Performance Considerations:**
- Use Immer middleware for immutable updates (prevents bugs)
- Targeted selectors: `useLayoutStore((s) => s.companyRailCollapsed)` — NOT `useLayoutStore()`
- localStorage persistence is async — handle hydration gracefully

### UIE-02 (Real-time Agent Monitoring) — Extend brainStore

**Current brainStore Structure (from BRAIN-FEED-04):**
```typescript
// apps/web/src/stores/brainStore.ts
interface BrainState {
  brains: Map<string, Brain> // O(1) lookups
  historyStack: BrainSnapshot[]
}

interface Brain {
  id: string
  name: string
  status: 'idle' | 'active' | 'complete' | 'error'
  data: Record<string, unknown> // WS updates touch ONLY this
}
```

**Extension for Monitoring Panel:**
```typescript
// ADD to brainStore (don't replace)
interface MonitoringState {
  // New: Density mode tracking per user
  densityMode: 'compact' | 'normal' | 'detailed'
  setDensityMode: (mode: 'compact' | 'normal' | 'detailed') => void

  // New: Filtered brains list (for chunking by niche)
  filteredBrains: Brain[]
  setFilteredBrains: (brains: Brain[]) => void
}
```

**WebSocket Integration:**
```typescript
// apps/web/src/lib/wsDispatcher.ts
// EXISTING: wsDispatcher singleton with subscribe() pattern

// NEW: Subscribe to agent monitoring events
wsDispatcher.subscribe('agent_status_update', (event) => {
  // Update brainStore with new status
  brainStore.setState((state) => {
    const brain = state.brains.get(event.brainId)
    if (brain) {
      brain.status = event.status // Update ONLY data prop, NOT positions
    }
  })
})
```

**RAF Batching Preservation:**
```typescript
// EXISTING: brainStore RAF batching (BRAIN-FEED-04 line 11)
// DO NOT modify this — 24-brain burst requires 60fps

// Pattern: Queue burst events, drain before paint
const eventQueue = []
const drainQueue = () => {
  // Process all queued events at once
  brainStore.setState((state) => {
    // Apply all updates in single setState call
  })
}
requestAnimationFrame(drainQueue)
```

### UIE-03 (Cost Dashboard) — costStore

**New Store Design:**
```typescript
// apps/web/src/stores/costStore.ts
import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'

interface CostMetrics {
  totalCost: number
  budgetRemaining: number
  budgetTotal: number
  costPerBrain: Map<string, number>
  projectedOverage: boolean
}

interface CostState {
  metrics: CostMetrics
  isLoading: boolean
  error: string | null

  // Actions
  fetchMetrics: () => Promise<void>
  refreshMetrics: () => Promise<void>
}

export const useCostStore = create<CostState>()(
  subscribeWithSelector((set, get) => ({
    metrics: {
      totalCost: 0,
      budgetRemaining: 100, // $100 default
      budgetTotal: 100,
      costPerBrain: new Map(),
      projectedOverage: false,
    },
    isLoading: false,
    error: null,

    fetchMetrics: async () => {
      set({ isLoading: true, error: null })
      try {
        // Data source: Rust event sourcing (see Q2 below)
        const response = await fetch('/api/cost/metrics')
        const metrics = await response.json()
        set({ metrics, isLoading: false })
      } catch (error) {
        set({ error: 'Failed to fetch cost metrics', isLoading: false })
      }
    },

    refreshMetrics: async () => {
      await get().fetchMetrics()
    },
  }))
)
```

**Data Fetching Strategy:**
- **TanStack Query:** Use for initial fetch + refetch on window focus
- **WebSocket updates:** Use for real-time metric updates (brain completion)
- **Hybrid approach:** TanStack Query for baseline, WS for incremental updates

---

## React Patterns

### UIE-01 (Three-Column Layout)

**Component Pattern:**
```typescript
// apps/web/src/components/layout/ThreeColumnLayout.tsx
"use client"

import { useLayoutStore } from '@/stores/layoutStore'

export function ThreeColumnLayout({ children }: { children: ReactNode }) {
  const { companyRailCollapsed, sidebarCollapsed } = useLayoutStore()

  return (
    <div className="grid grid-cols-[auto_1fr] md:grid-cols-[180px_240px_1fr]">
      <CompanyRail collapsed={companyRailCollapsed} />
      <AppSidebar collapsed={sidebarCollapsed} />
      <main>{children}</main>
    </div>
  )
}
```

**Responsive Implementation:**
- **Desktop (≥768px):** CSS Grid with 3 columns
- **Mobile (<768px):** CSS Grid with 1 column + bottom nav
- **Tailwind classes:** `grid-cols-[180px_240px_1fr] md:grid-cols-1`

**Performance:**
- Avoid re-renders: Use `React.memo` for CompanyRail/AppSidebar
- CSS Grid handles layout (no JS layout calculations)
- Collapse state is boolean (cheap to compare)

### UIE-02 (Real-time Agent Monitoring)

**Component Pattern:**
```typescript
// apps/web/src/components/monitoring/ActiveAgentsPanel.tsx
"use client"

import { useLayoutStore } from '@/stores/layoutStore'
import { useBrainStore } from '@/stores/brainStore'

export function ActiveAgentsPanel() {
  const { densityMode } = useLayoutStore((s) => s.densityMode)
  const brains = useBrainStore((s) => Array.from(s.brains.values()))

  // Chunk by niche (max 7 per group, Miller's Law)
  const brainsByNiche = groupByNiche(brains)

  return (
    <div className="grid grid-cols-4 md:grid-cols-6">
      {densityMode === 'compact' && <CompactView brains={brains} />}
      {densityMode === 'normal' && <NormalView brains={brains} />}
      {densityMode === 'detailed' && <DetailedView brains={brains} />}
    </div>
  )
}
```

**WebSocket Integration:**
```typescript
// apps/web/src/components/monitoring/ActiveAgentsPanel.tsx
"use client"

import { useEffect } from 'react'
import { wsDispatcher } from '@/lib/wsDispatcher'

export function ActiveAgentsPanel() {
  useEffect(() => {
    // Subscribe to agent status updates
    const unsubscribe = wsDispatcher.subscribe('agent_status_update', (event) => {
      // brainStore RAF batching handles updates
      console.log('Agent status updated:', event.brainId, event.status)
    })

    return () => unsubscribe()
  }, [])

  // Render component...
}
```

**Performance Optimization:**
- **Targeted selectors:** `useBrainStore((s) => Array.from(s.brains.values()))` — NOT `useBrainStore()`
- **RAF batching:** brainStore queues burst events, drains before paint (60fps)
- **Density mode:** CSS-based (compact/normal/detailed) — no JS re-renders

### UIE-03 (Cost Dashboard)

**Component Pattern:**
```typescript
// apps/web/src/components/cost/CostDashboard.tsx
"use client"

import { useCostStore } from '@/stores/costStore'
import { useQuery } from '@tanstack/react-query'

export function CostDashboard() {
  const { metrics, isLoading } = useCostStore()

  // TanStack Query for initial fetch
  const { data } = useQuery({
    queryKey: ['cost-metrics'],
    queryFn: async () => {
      const response = await fetch('/api/cost/metrics')
      return response.json()
    },
    staleTime: 30_000, // 30 seconds
  })

  // WebSocket for real-time updates
  useEffect(() => {
    const unsubscribe = wsDispatcher.subscribe('brain_cost_update', (event) => {
      // Update costStore incrementally
      useCostStore.getState().updateBrainCost(event.brainId, event.cost)
    })

    return () => unsubscribe()
  }, [])

  return (
    <div className="grid grid-cols-3 gap-4">
      <MetricCard label="Total Cost" value={metrics.totalCost} />
      <MetricCard label="Budget Remaining" value={metrics.budgetRemaining} />
      <QuotaBar current={metrics.totalCost} total={metrics.budgetTotal} />
    </div>
  )
}
```

---

## WebSocket Integration

### Extending wsDispatcher for New Event Types

**Current Pattern (from BRAIN-FEED-04):**
```typescript
// apps/web/src/lib/wsDispatcher.ts
class WSDispatcher {
  subscribe(eventType: string, handler: (event: WSMessage) => void) {
    // Register handler for event type
    this.handlers.set(eventType, handler)
  }

  dispatch(message: WSMessage) {
    const handler = this.handlers.get(message.type)
    if (handler) {
      handler(message)
    }
  }
}
```

**New Event Types for Phase 17:**
```typescript
// ADD to WSMessageSchema (Zod validation)
export const WSMessageSchema = z.discriminatedUnion('type', [
  // EXISTING
  z.object({ type: z.literal('task_update_batch'), /* ... */ }),

  // NEW: Agent monitoring
  z.object({
    type: z.literal('agent_status_update'),
    brainId: z.string(),
    status: z.enum(['idle', 'running', 'completed', 'failed', 'routing']),
  }),

  // NEW: Cost updates
  z.object({
    type: z.literal('brain_cost_update'),
    brainId: z.string(),
    cost: z.number(),
    timestamp: z.string(),
  }),
])
```

**Subscription Pattern:**
```typescript
// apps/web/src/components/monitoring/ActiveAgentsPanel.tsx
useEffect(() => {
  const unsubscribe = wsDispatcher.subscribe('agent_status_update', (event) => {
    // Update brainStore (RAF batching handles performance)
  })

  return () => unsubscribe()
}, [])
```

---

## Performance Considerations

### RAF Batching Preservation (CRITICAL)

**From BRAIN-FEED-04 line 11:**
> RAF batching in brainStore (not WS handler) — queues burst events, drains before paint

**Invariant:**
- WS handler → ADD to event queue (NOT setState)
- RAF → DRAIN queue (single setState call)
- Result: 60fps at 24-brain burst

**Anti-pattern to Avoid:**
```typescript
// ❌ WRONG (breaks RAF batching)
wsDispatcher.subscribe('agent_status_update', (event) => {
  brainStore.setState((state) => {
    // Direct setState on every WS event = dropped frames
  })
})

// ✅ CORRECT (preserves RAF batching)
wsDispatcher.subscribe('agent_status_update', (event) => {
  eventQueue.push(event) // Queue event
  if (!drainScheduled) {
    drainScheduled = true
    requestAnimationFrame(drainQueue) // Drain before paint
  }
})
```

### Targeted Selectors (Prevent Cascade Re-renders)

**Anti-pattern from BRAIN-FEED-04 line 12:**
> useStore() for brain state → use useBrainState(id) targeted selector

```typescript
// ❌ WRONG (cascade re-renders)
const brains = useBrainStore() // Re-renders on ANY brain update

// ✅ CORRECT (targeted selector)
const brains = useBrainStore((s) => Array.from(s.brains.values())) // Re-renders only when brains Map changes
```

### React Flow Integration (Cost Overlay)

**From BRAIN-FEED-04 line 18:**
> WS updates touch only `data` prop of nodes — never positions, never topology

```typescript
// ❌ WRONG (recalculates layout)
node.position = { x: new_x, y: new_y } // Triggers dagre re-run

// ✅ CORRECT (updates data only)
node.data = { ...node.data, cost: new_cost } // No layout recalculation
```

---

## Anti-patterns to Avoid

### Frontend Violations:
- ❌ **inline NODE_TYPES in JSX** — Always module level (BRAIN-FEED-04 line 24)
- ❌ **useStore() for brain state** — Use targeted selectors (BRAIN-FEED-04 line 45)
- ❌ **WS reconnect on every render** — Use module singleton with ref counting (BRAIN-FEED-04 line 46)
- ❌ **Recalculate dagre on data update** — Lock positions after first dagre run (BRAIN-FEED-04 line 48)
- ❌ **Direct setState on WS events** — Use RAF batching (BRAIN-FEED-04 line 11)
- ❌ **cookies() without await** — Next.js 16 requires async (BRAIN-FEED-04 line 34)

---

## Testing Recommendations

### Unit Tests (Vitest):
```typescript
// apps/web/src/stores/__tests__/layoutStore.test.ts
import { renderHook, act } from '@testing-library/react'
import { useLayoutStore } from '../layoutStore'

describe('layoutStore', () => {
  it('toggles company rail collapse state', () => {
    const { result } = renderHook(() => useLayoutStore())

    act(() => {
      result.current.toggleCompanyRail()
    })

    expect(result.current.companyRailCollapsed).toBe(true)
  })
})
```

### Integration Tests:
```typescript
// apps/web/src/components/__tests__/ThreeColumnLayout.test.tsx
import { render, screen } from '@testing-library/react'
import { ThreeColumnLayout } from '../ThreeColumnLayout'

describe('ThreeColumnLayout', () => {
  it('renders all three columns on desktop', () => {
    render(<ThreeColumnLayout>Content</ThreeColumnLayout>)

    expect(screen.getByTestId('company-rail')).toBeInTheDocument()
    expect(screen.getByTestId('app-sidebar')).toBeInTheDocument()
    expect(screen.getByTestId('content-area')).toBeInTheDocument()
  })
})
```

### E2E Tests (Playwright):
```typescript
// apps/web/e2e/layout.spec.ts
import { test, expect } from '@playwright/test'

test('user can collapse and expand company rail', async ({ page }) => {
  await page.goto('/command-center')

  // Click collapse button
  await page.click('[data-testid="company-rail-collapse"]')

  // Verify collapsed state
  await expect(page.locator('[data-testid="company-rail"]')).toHaveClass(/collapsed/)
})
```

---

## Open Questions Answered

### Q1: DnD library — @dnd-kit for company rail or custom?

**Answer:** USE @dnd-kit (same as Brain #3 UI)

**Technical Rationale:**
1. **Performance:** Uses React refs, not context (avoids re-renders)
2. **Accessibility:** Keyboard drag-drop built-in (screen reader support)
3. **TypeScript:** Full type safety
4. **Maintenance:** Battle-tested by Paperclip

**Implementation:**
```typescript
// apps/web/src/components/layout/CompanyRail.tsx
import { DndContext, closestCenter, PointerSensor, useSensor } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'

const pointerSensor = useSensor(PointerSensor, {
  activationConstraint: {
    distance: 8, // 8px drag threshold
  },
})

<DndContext sensors={[pointerSensor]} collisionDetection={closestCenter}>
  <SortableContext items={companies} strategy={verticalListSortingStrategy}>
    {companies.map((company) => (
      <CompanyTile key={company.id} company={company} />
    ))}
  </SortableContext>
</DndContext>
```

### Q2: Cost data source — Rust event sourcing or Python API?

**Answer:** RUST event sourcing (activity_log table)

**Technical Rationale:**
1. **Performance:** Rust activity_log is append-only (O(1) write)
2. **Scalability:** PostgreSQL partitions by month (Phase 15)
3. **Latency:** Direct Rust → PostgreSQL (< 50ms) vs Python proxy (+100ms)
4. **Event sourcing:** Cost metrics are derived events (natural fit)

**API Design:**
```rust
// rust_control_plane/src/cost.rs
pub async fn get_cost_metrics(
    State(pool): State<PgPool>,
    Query(params): Query<CostQuery>,
) -> Result<Json<CostMetrics>, AppError> {
    let metrics = sqlx::query_as!(
        CostMetrics,
        r#"
        SELECT
            SUM(cost) as total_cost,
            budget_remaining,
            budget_total
        FROM activity_log
        WHERE created_at >= $1
        "#,
        params.start_date
    )
    .fetch_one(&pool)
    .await?;

    Ok(Json(metrics))
}
```

**Next.js Route Handler:**
```typescript
// apps/web/src/app/api/cost/metrics/route.ts
import { NextRequest } from 'next/server'
import { RUST_GATEWAY_URL } from '@/lib/config'

export async function GET(request: NextRequest) {
  const response = await fetch(`${RUST_GATEWAY_URL}/api/cost/metrics`, {
    headers: {
      Authorization: `Bearer ${await getAuthToken(request)}`,
    },
  })

  return response.json()
}
```

### Q3: Command palette scope — What actions to support?

**Answer:** 4 categories (matches Brain #2 UX)

1. **Navigation:** Jump to screens (Command Center, Nexus, Vault, Engine Room)
2. **Brain Actions:** Trigger brain execution (e.g., "Run Product Strategy brain")
3. **Company Actions:** Switch companies, create new company
4. **Settings:** Open API keys, view brain YAML config

**Component:**
```typescript
// apps/web/src/components/command-palette/CommandPalette.tsx
"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

const commandCategories = [
  { id: 'navigation', label: 'Go to...', items: [
    { id: 'command-center', label: 'Command Center', icon: Target, action: () => router.push('/command-center') },
    { id: 'nexus', label: 'The Nexus', icon: Network, action: () => router.push('/nexus') },
  ]},
  { id: 'brains', label: 'Run brain...', items: [
    { id: 'run-product', label: 'Product Strategy', action: () => runBrain('product-strategy') },
  ]},
  { id: 'companies', label: 'Switch company...', items: companies.map((c) => ({
    id: c.id,
    label: c.name,
    action: () => switchCompany(c.id),
  }))},
]

// Keyboard shortcut: Cmd/Ctrl+K
// Fuzzy search over all items
// Categorized results
```

---

## Summary

**Key Decisions:**
1. **State management:** 3 Zustand stores (layout, brain, cost)
2. **WebSocket integration:** Extend wsDispatcher with 2 new event types
3. **Performance:** Preserve RAF batching, targeted selectors, no layout recalc
4. **DnD library:** @dnd-kit (not custom)
5. **Cost data source:** Rust event sourcing (not Python API)
6. **Command palette:** 4 categories (navigation, brains, companies, settings)

**Next Steps:**
- Brain #6 (QA) — Testing strategy + performance SLOs

---

*Brain #4 consultation complete — 2026-04-08*
