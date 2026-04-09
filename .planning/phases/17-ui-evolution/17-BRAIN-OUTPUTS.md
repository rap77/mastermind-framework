# 17-BRAIN-OUTPUTS.md — Phase 17 Domain Brain Consultation

> **Phase:** 17 — UI Evolution
> **Date:** 2026-04-08
> **Orchestrator:** Phase planning workflow
> **Cross-brain communication:** Option D (file-based)

---

## Executive Summary

**4 Domain Brains Consulted:**
- ✅ Brain #2 (UX Research) — Information architecture, interaction patterns
- ✅ Brain #3 (UI Design) — Component architecture, design system
- ✅ Brain #4 (Frontend) — State management, WebSocket integration
- ✅ Brain #6 (QA) — Testing strategy, performance SLOs

**3 Requirements Analyzed:**
- UIE-01: Three-column layout (CompanyRail + Sidebar + Content)
- UIE-02: Real-time agent monitoring panel with density modes
- UIE-03: Cost dashboard with MetricCard + QuotaBar

**Key Decisions:**
1. **Layout:** Three-column with CSS Grid, instant transitions (ICE 6.7 < 15)
2. **Monitoring:** Density modes (compact/normal/detailed) + chunking by niche
3. **Cost dashboard:** Rust event sourcing (activity_log) + WebSocket updates
4. **State management:** 3 Zustand stores (layout, brain, cost)
5. **DnD library:** @dnd-kit for company rail (not custom)
6. **Mobile bottom nav:** 4 items (Command Center, Nexus, Vault, Engine Room)
7. **Testing:** +50 frontend tests, +5 E2E tests (Playwright)

**Open Questions Answered:**
- Q1: DnD library → @dnd-kit (Brain #3, #4)
- Q2: Cost data source → Rust event sourcing (Brain #4)
- Q3: Command palette scope → 4 categories (Brain #4)
- Q4: Onboarding skip → YES, with trade-offs (Brain #2)
- Q5: Mobile bottom nav → 4 items (Brain #2, #3)

---

## Brain #2 (UX Research) — Key Insights

### UIE-01 (Three-Column Layout)
**Information Architecture:**
- CompanyRail: max 7 companies (Miller's Law: 7±2)
- AppSidebar: 4 nav items (Hick's Law compliance)
- Content Area: progressive disclosure for complexity

**Mobile Responsive Strategy:**
- Bottom nav: 4 items only (no hamburger menu)
- Swipe gestures: horizontal swipe to switch screens
- Full-screen content: back button for navigation depth

**ICE Score for layout transitions:**
- Impact: 4 × Confidence: 5 / Effort: 3 = **6.7** — BELOW 15 threshold
- **Decision:** Instant width change (200ms CSS transition max)

### UIE-02 (Real-time Agent Monitoring)
**The Problem:** 24 brains > Miller's Law (7±2) → cognitive overload

**Solution: Density Modes + Chunking**
1. **Compact Mode (default):** Grid view, 2 data points per brain
2. **Normal Mode:** Card view, 4 data points per brain
3. **Detailed Mode:** Single brain full-screen, 8+ data points

**Chunking Strategy:**
- Auto-group by niche (4-6 groups)
- Command Palette for fuzzy search
- MRU (Most Recently Used): top 5 brains first
- Active group: only show brains in current session

**Ping Animation (ICE Score):**
- Impact: 8 × Confidence: 5 / Effort: 2 = **20** — ABOVE 15 threshold
- **Decision:** APPROVED (reuse existing BrainTile ping)

### UIE-03 (Cost Dashboard)
**Cognitive Load Prevention:**
- Default view: 3-5 key metrics only (Miller's Law lower bound)
- Progressive disclosure: "Show details" button
- Color semantics: Green (within budget), Amber (warning > 80%), Red (over budget)

**QuotaBar Pattern:**
- Primary metric: % of budget consumed
- Visual: Horizontal bar with color gradient
- Secondary text: "$X of $Y spent"
- Tertiary text: "Z days remaining"

**MetricCard Hierarchy:**
1. P0 (always visible): Total cost, budget remaining
2. P1 (default visible): Cost per brain (top 5), projected overage
3. P2 (on demand): Cost per execution, trends over time

### Open Questions Answered
**Q4: Onboarding skip flow?**
- YES, users can skip onboarding
- Minimal setup: 5 minutes (company name, 1-3 brains, budget)
- Full setup: 15 minutes (templates, knowledge base, advanced config)
- Show "Setup incomplete" badge if user skipped

**Q5: Mobile bottom nav items?**
- 4 items: Command Center, Nexus, Vault, Engine Room
- Excluded: CompanyRail (move to settings), Properties panel (modal)
- Rationale: 4 items = well below Hick's Law limit (log₂(4) = 2 bits)

---

## Brain #3 (UI Design) — Key Insights

### UIE-01 (Three-Column Layout)
**Component Hierarchy (Atomic Design):**
```
Template: ThreeColumnLayout
  ├─ Organism: CompanyRail
  ├─ Organism: AppSidebar
  └─ Template: ContentArea
      └─ Organism: PropertiesPanel
```

**CSS Variables (globals.css):**
```css
:root {
  --company-rail-width: 180px;
  --company-rail-width-collapsed: 60px;
  --sidebar-width: 240px;
  --sidebar-width-collapsed: 60px;
  --transition-duration: 200ms;
}

@media (max-width: 768px) {
  :root {
    --company-rail-width: 0px;
    --sidebar-width: 0px;
  }
}
```

**5-State System Application:**
- **CompanyRail:** Default (gray bg), Hover (elevation+1), Active (selected border)
- **AppSidebar:** Default (transparent), Hover (elevation+1), Active (highlighted)
- **PropertiesPanel:** Default (closed), Active (open sheet)

**Tonal Elevation (dark mode):**
```css
--elevation-0: rgba(255, 255, 255, 0.00); /* Surface */
--elevation-1: rgba(255, 255, 255, 0.05); /* Hover */
--elevation-2: rgba(255, 255, 255, 0.10); /* Active */
--elevation-3: rgba(255, 255, 255, 0.15); /* Modal */
```

### UIE-02 (Real-time Agent Monitoring)
**Component Hierarchy:**
```
Organism: ActiveAgentsPanel
  ├─ Molecule: DensityModeSelector
  ├─ Organism: CompactView (4-6 columns)
  ├─ Organism: NormalView (2-3 columns)
  └─ Organism: DetailedView (1 column)
```

**StatusBadge Color Semantics:**
```typescript
const statusColors = {
  idle: 'oklch(var(--color-muted-foreground))',      // Gray
  running: 'oklch(var(--color-primary))',             // Blue
  completed: 'oklch(var(--color-success))',           // Green
  failed: 'oklch(var(--color-error))',                // Red
  routing: 'oklch(var(--color-warning))',             // Amber
}
```

**PingAnimation Specs:**
```css
@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

.animate-ping {
  animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
}

@media (prefers-reduced-motion: reduce) {
  .animate-ping { animation: none; }
}
```

### UIE-03 (Cost Dashboard)
**Component Hierarchy:**
```
Organism: CostDashboard
  ├─ Molecule: QuotaBar (progress visualization)
  ├─ Molecule: MetricCard (repeated)
  └─ Molecule: CostBreakdown
```

**QuotaBar Color Semantics:**
```css
--color-quota-success: oklch(0.65 0.15 150); /* Green */
--color-quota-warning: oklch(0.70 0.12 80);  /* Amber */
--color-quota-error: oklch(0.65 0.15 25);    /* Red */

.quota-bar {
  background: linear-gradient(
    to right,
    var(--color-quota-success) 0%,
    var(--color-quota-warning) 80%,
    var(--color-quota-error) 100%
  );
}
```

**Animation Specs:**
| Animation | Purpose | Duration | Easing |
|-----------|---------|----------|--------|
| Ping | Orientation | 1000ms | cubic-bezier(0,0,0.2,1) |
| Status badge transition | Feedback | 200ms | ease-out |
| QuotaBar fill | Feedback | 300ms | ease-in-out |
| Panel slide-in | Orientation | 250ms | ease-out |

### Accessibility Checklist
- ✅ Color contrast ≥ 4.5:1 (OKLCH auto-complies)
- ✅ Icon + text label for status indicators (8% daltonism)
- ✅ Keyboard navigation (Tab/Enter for all interactive elements)
- ✅ Focus-visible ring with 3:1 contrast minimum
- ✅ ARIA labels for screen readers
- ✅ Semantic HTML (nav, main, aside, header)

### Open Questions Answered
**Q1: DnD library?**
- USE @dnd-kit (not custom)
- Rationale: Accessibility built-in, performance optimized, battle-tested

**Q5: Mobile bottom nav?**
- 4 items (matches Brain #2 UX response)
- Component: MobileBottomNav with 44x44px touch targets

---

## Brain #4 (Frontend) — Key Insights

### UIE-01 (Three-Column Layout) — layoutStore
**Store Design:**
```typescript
interface LayoutState {
  companyRailCollapsed: boolean
  sidebarCollapsed: boolean
  propertiesPanelOpen: boolean
  densityMode: 'compact' | 'normal' | 'detailed'

  toggleCompanyRail: () => void
  toggleSidebar: () => void
  togglePropertiesPanel: () => void
  setDensityMode: (mode) => void
}

export const useLayoutStore = create<LayoutState>()(
  persist(
    (set) => ({ /* ... */ }),
    { name: 'mastermind-layout' }
  )
)
```

**Performance Considerations:**
- Use Immer middleware for immutable updates
- Targeted selectors: `useLayoutStore((s) => s.companyRailCollapsed)`
- localStorage persistence is async — handle hydration gracefully

### UIE-02 (Real-time Agent Monitoring) — Extend brainStore
**Current Structure (preserve):**
```typescript
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

**Extension:**
```typescript
interface MonitoringState {
  densityMode: 'compact' | 'normal' | 'detailed'
  filteredBrains: Brain[]
  setDensityMode: (mode) => void
  setFilteredBrains: (brains) => void
}
```

**WebSocket Integration:**
```typescript
wsDispatcher.subscribe('agent_status_update', (event) => {
  brainStore.setState((state) => {
    const brain = state.brains.get(event.brainId)
    if (brain) {
      brain.status = event.status // Update ONLY data prop
    }
  })
})
```

**RAF Batching Preservation (CRITICAL):**
```typescript
// Pattern: Queue burst events, drain before paint
const eventQueue = []
const drainQueue = () => {
  brainStore.setState((state) => {
    // Apply all updates in single setState call
  })
}
requestAnimationFrame(drainQueue)
```

### UIE-03 (Cost Dashboard) — costStore
**Store Design:**
```typescript
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

  fetchMetrics: () => Promise<void>
  refreshMetrics: () => Promise<void>
}

export const useCostStore = create<CostState>()(
  subscribeWithSelector((set, get) => ({ /* ... */ }))
)
```

**Data Fetching Strategy:**
- **TanStack Query:** Initial fetch + refetch on window focus
- **WebSocket updates:** Real-time metric updates (brain completion)
- **Hybrid approach:** TanStack Query for baseline, WS for incremental

### WebSocket Integration
**New Event Types:**
```typescript
export const WSMessageSchema = z.discriminatedUnion('type', [
  // EXISTING
  z.object({ type: z.literal('task_update_batch') }),

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

### Performance Considerations
**Invariants (from BRAIN-FEED-04):**
- React Compiler: DISABLED (conflicts with React.memo on RF nodes)
- NO inline NODE_TYPES — always module level
- WS updates touch only `data` prop — never positions, never topology
- RAF batching in brainStore — queues burst events, drains before paint
- Targeted selectors — prevents cascade re-renders

**Anti-patterns to Avoid:**
```typescript
// ❌ WRONG (breaks RAF batching)
wsDispatcher.subscribe('agent_status_update', (event) => {
  brainStore.setState((state) => { /* ... */ }) // Direct setState
})

// ✅ CORRECT (preserves RAF batching)
wsDispatcher.subscribe('agent_status_update', (event) => {
  eventQueue.push(event) // Queue event
  requestAnimationFrame(drainQueue) // Drain before paint
})
```

### Open Questions Answered
**Q1: DnD library?**
- @dnd-kit (same as Brain #3 UI)
- Technical rationale: Uses React refs (not context), accessibility built-in

**Q2: Cost data source?**
- RUST event sourcing (activity_log table)
- API route: `/api/cost/metrics` → Rust gateway → PostgreSQL
- Rationale: O(1) append-only writes, partitioned by month, < 50ms latency

**Q3: Command palette scope?**
- 4 categories: Navigation, Brain Actions, Company Actions, Settings
- Keyboard shortcut: Cmd/Ctrl+K
- Fuzzy search over all items

---

## Brain #6 (QA) — Key Insights

### UIE-01 (Three-Column Layout)
**Unit Tests (Vitest):**
- layoutStore: toggle collapse state, localStorage persistence
- ThreeColumnLayout: desktop/mobile rendering

**Integration Tests:**
- Responsive testing: 375px (mobile), 768px (tablet), 1440px (desktop)
- Collapse behavior at each breakpoint
- localStorage persistence across page refreshes

**Visual Regression Tests:**
```typescript
// Playwright screenshot comparison
await expect(page).toHaveScreenshot('command-center-desktop.png', {
  maxDiffPixels: 100,
})
```

### UIE-02 (Real-time Agent Monitoring)
**Unit Tests:**
- ActiveAgentsPanel: compact/normal/detailed view switching
- wsDispatcher: agent_status_update event subscription

**WebSocket Integration Tests:**
```typescript
wsDispatcher.subscribe('agent_status_update', handler)
wsDispatcher.dispatch({ type: 'agent_status_update', brainId: 'brain-1', status: 'running' })
expect(handler).toHaveBeenCalledWith({ /* ... */ })
```

**Performance Tests:**
```typescript
// 24-brain burst render
render(<ActiveAgentsPanel brains={generate24Brains()} />)
expect(endTime - startTime).toBeLessThan(100) // P99 target

// 24-brain burst without dropping frames
for (let i = 0; i < 24; i++) {
  wsDispatcher.dispatch({ type: 'agent_status_update', /* ... */ })
}
await waitFor(() => expect(frameTime).toBeLessThan(16.67 * 2)) // 60fps
```

### UIE-03 (Cost Dashboard)
**Unit Tests:**
- costStore: fetch metrics from API
- MetricCard: render with correct props

**Data Validation Tests:**
```typescript
// Rust event sourcing validation
mockRustGateway({ total_cost: 75.50, budget_remaining: 24.50, budget_total: 100.00 })
const metrics = await fetch('/api/cost/metrics')
expect(metrics.totalCost).toBeGreaterThanOrEqual(0)
expect(metrics.budgetRemaining).toBeLessThanOrEqual(metrics.budgetTotal)
```

**Performance Tests:**
```typescript
// WS cost update latency
wsDispatcher.dispatch({ type: 'brain_cost_update', brainId: 'brain-1', cost: 10.50 })
await waitFor(() => expect(updateTime).toBeLessThan(50)) // P99 target
```

### Performance SLOs
**UIE-01:**
| Metric | Target |
|--------|--------|
| Time-to-first-render | < 100ms |
| Layout state persistence | < 10ms |
| Collapse/expand transition | < 200ms |

**UIE-02:**
| Metric | Target |
|--------|--------|
| 24-brain burst render | 60fps (16.67ms) |
| WS event processing | < 50ms P99 |
| Density mode switch | < 50ms |

**UIE-03:**
| Metric | Target |
|--------|--------|
| Cost metrics fetch | < 200ms P99 |
| WS cost update | < 50ms |
| QuotaBar render | < 100ms |

### Test Coverage Targets
**Frontend (Vitest):**
- Baseline: 407 tests
- Phase 17 target: +50 tests (457 total)
- Focus: Layout (15), Monitoring (20), Cost (15)

**Backend (pytest):**
- Baseline: 631 tests
- Phase 17 target: +10 tests (641 total)
- Focus: Cost API (5), WebSocket (5)

**E2E (Playwright):**
- Baseline: 0 tests
- Phase 17 target: +5 tests
- Focus: Layout (1), Multi-tenant (1), Monitoring (2), Cost (1)

### CI/CD Considerations
**GitHub Actions Workflow:**
```yaml
jobs:
  frontend:
    - pnpm install
    - pnpm test # Vitest
    - pnpm test:e2e # Playwright

  backend:
    - cd apps/api && uv run pytest # Run from apps/api/, NOT root

  visual-regression:
    - pnpm test:visual # Playwright screenshots
```

---

## Cross-Brain Consensus

### Agreed Decisions (all 4 brains aligned):
1. **Layout architecture:** Three-column with CSS Grid
2. **State management:** 3 Zustand stores (layout, brain, cost)
3. **DnD library:** @dnd-kit (not custom)
4. **Mobile bottom nav:** 4 items (Command Center, Nexus, Vault, Engine Room)
5. **Performance target:** 60fps for 24-brain burst (RAF batching preserved)
6. **Accessibility:** WCAG 2.1 AA compliance (color contrast, ARIA labels, keyboard nav)
7. **Testing strategy:** +50 frontend tests, +5 E2E tests

### Trade-offs Identified:
1. **Animation vs Performance:** Layout transitions rejected (ICE 6.7 < 15)
2. **Information Density vs Cognitive Load:** Density modes required for 24 brains
3. **Custom vs Library DnD:** @dnd-kit chosen (maintenance burden vs performance)
4. **Rust vs Python for Cost:** Rust chosen (performance vs complexity)

### Risks Highlighted:
1. **RAF batching preservation:** Critical for 60fps (Brain #4 frontend invariant)
2. **Mobile responsiveness:** Desktop-first legacy, need mobile-first testing
3. **WebSocket scalability:** 24-brain burst may overwhelm current wsDispatcher
4. **Visual regression:** Layout changes need screenshot comparison

---

## Next Steps

1. ✅ **Domain brain consultation complete** — 4 brains consulted, outputs written
2. ⏭️ **Brain #7 evaluation** — Read 17-BRAIN-OUTPUTS.md, provide synthesis + scoring
3. ⏭️ **Write 17-CONTEXT.md** — Update with brain-informed decisions
4. ⏭️ **Invoke `/mm:plan-phase 17`** — Create 6 PLAN.md files with GSD skill

---

**File created:** 2026-04-08
**Ready for:** Brain #7 (Critical Evaluator) review
