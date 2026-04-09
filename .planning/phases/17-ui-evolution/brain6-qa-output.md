# Brain #6 (QA/DevOps) — Phase 17 Consultation

> **Phase:** 17 — UI Evolution
> **Date:** 2026-04-08
> **Expertise:** Testing strategies, performance validation, SLO definition

---

## Verified Insights

**From existing codebase + BRAIN-FEED-06:**
- Test baseline: 631 backend (pytest) + 407 frontend (Vitest)
- `uv run pytest` must run from `apps/api/` — NOT from root
- 5 testing layers: Rust unit, Proto contract, gRPC integration, PostgreSQL parity, E2E smoke
- WebSocket SLOs must be defined before implementation
- Phase 16 COMPLETE: Ghost Mode replay (P95 < 500ms), memory per connection < 50KB

---

## Testing Strategy

### UIE-01 (Three-Column Layout)

**Unit Tests (Vitest):**
```typescript
// apps/web/src/components/layout/__tests__/layoutStore.test.ts
describe('layoutStore', () => {
  it('toggles company rail collapse state', async () => {
    const { result } = renderHook(() => useLayoutStore())

    act(() => result.current.toggleCompanyRail())

    expect(result.current.companyRailCollapsed).toBe(true)
  })

  it('persists layout state to localStorage', async () => {
    const { result } = renderHook(() => useLayoutStore())

    act(() => result.current.toggleSidebar())

    // Verify localStorage write
    expect(localStorage.getItem('mastermind-layout')).toContain('sidebarCollapsed')
  })
})
```

**Integration Tests:**
```typescript
// apps/web/src/components/layout/__tests__/ThreeColumnLayout.integration.test.tsx
describe('ThreeColumnLayout Integration', () => {
  it('renders all three columns on desktop viewport', () => {
    // Mock window.innerWidth = 1440 (desktop)
    window.innerWidth = 1440

    render(<ThreeColumnLayout>Content</ThreeColumnLayout>)

    expect(screen.getByTestId('company-rail')).toBeInTheDocument()
    expect(screen.getByTestId('app-sidebar')).toBeInTheDocument()
    expect(screen.getByTestId('content-area')).toBeInTheDocument()
  })

  it('renders single column on mobile viewport', () => {
    // Mock window.innerWidth = 375 (mobile)
    window.innerWidth = 375

    render(<ThreeColumnLayout>Content</ThreeColumnLayout>)

    // CompanyRail and Sidebar should be hidden
    expect(screen.queryByTestId('company-rail')).not.toBeInTheDocument()
    expect(screen.queryByTestId('app-sidebar')).not.toBeInTheDocument()
  })
})
```

**Visual Regression Tests:**
```typescript
// apps/web/e2e/visual/visual-regression.spec.ts
import { test, expect } from '@playwright/test'

test('layout matches snapshot on desktop', async ({ page }) => {
  await page.goto('/command-center')
  await page.waitForSelector('[data-testid="three-column-layout"]')

  // Screenshot comparison (baseline stored in tests/visual/baseline)
  await expect(page).toHaveScreenshot('command-center-desktop.png', {
    maxDiffPixels: 100, // Allow minor rendering differences
  })
})
```

**Responsive Testing:**
- Test breakpoints: 375px (mobile), 768px (tablet), 1440px (desktop)
- Verify collapse behavior at each breakpoint
- Test localStorage persistence across page refreshes

### UIE-02 (Real-time Agent Monitoring)

**Unit Tests:**
```typescript
// apps/web/src/components/monitoring/__tests__/ActiveAgentsPanel.test.tsx
describe('ActiveAgentsPanel', () => {
  it('renders compact view by default', () => {
    render(<ActiveAgentsPanel brains={mockBrains} />)

    expect(screen.getByTestId('compact-view')).toBeInTheDocument()
  })

  it('switches to normal view when density mode changes', () => {
    render(<ActiveAgentsPanel brains={mockBrains} />)

    fireEvent.click(screen.getByTestId('density-mode-normal'))

    expect(screen.getByTestId('normal-view')).toBeInTheDocument()
  })
})
```

**WebSocket Integration Tests:**
```typescript
// apps/web/src/lib/__tests__/wsDispatcher.test.ts
describe('wsDispatcher', () => {
  it('subscribes to agent_status_update events', async () => {
    const handler = vi.fn()
    wsDispatcher.subscribe('agent_status_update', handler)

    // Simulate WS message
    wsDispatcher.dispatch({
      type: 'agent_status_update',
      brainId: 'brain-1',
      status: 'running',
    })

    expect(handler).toHaveBeenCalledWith({
      type: 'agent_status_update',
      brainId: 'brain-1',
      status: 'running',
    })
  })
})
```

**Performance Tests:**
```typescript
// apps/web/src/monitoring/__tests__/performance.test.ts
describe('ActiveAgentsPanel Performance', () => {
  it('renders 24 brains in under 100ms', () => {
    const startTime = performance.now()
    render(<ActiveAgentsPanel brains={generate24Brains()} />)
    const endTime = performance.now()

    expect(endTime - startTime).toBeLessThan(100) // P99 target
  })

  it('updates 24 brains via WS without dropping frames', async () => {
    render(<ActiveAgentsPanel brains={generate24Brains()} />)

    // Simulate 24-brain burst
    for (let i = 0; i < 24; i++) {
      wsDispatcher.dispatch({
        type: 'agent_status_update',
        brainId: `brain-${i}`,
        status: 'running',
      })
    }

    // Wait for RAF drain
    await waitFor(() => {
      expect(screen.getAllByTestId('status-badge-running')).toHaveLength(24)
    })

    // Verify 60fps (16.67ms per frame)
    const frameTime = performance.now() - burstStartTime
    expect(frameTime).toBeLessThan(16.67 * 2) // Allow 2 frames
  })
})
```

### UIE-03 (Cost Dashboard)

**Unit Tests:**
```typescript
// apps/web/src/components/cost/__tests__/costStore.test.ts
describe('costStore', () => {
  it('fetches cost metrics from API', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      totalCost: 50,
      budgetRemaining: 50,
      budgetTotal: 100,
    })

    global.fetch = mockFetch

    const { result } = renderHook(() => useCostStore())

    act(() => result.current.fetchMetrics())

    await waitFor(() => {
      expect(result.current.metrics.totalCost).toBe(50)
    })
  })
})
```

**Data Validation Tests:**
```typescript
// apps/web/src/app/api/cost/metrics.test.ts
describe('GET /api/cost/metrics', () => {
  it('validates cost metrics from Rust event sourcing', async () => {
    // Mock Rust gateway response
    mockRustGateway({
      total_cost: 75.50,
      budget_remaining: 24.50,
      budget_total: 100.00,
    })

    const response = await fetch('/api/cost/metrics')
    const metrics = await response.json()

    // Validate response shape
    expect(metrics.totalCost).toBeGreaterThanOrEqual(0)
    expect(metrics.budgetRemaining).toBeLessThanOrEqual(metrics.budgetTotal)
    expect(metrics.projectedOverage).toBeTypeOf('boolean')
  })
})
```

**Performance Tests:**
```typescript
// apps/web/src/cost/__tests__/performance.test.ts
describe('CostDashboard Performance', () => {
  it('updates cost metrics via WS in under 50ms', async () => {
    render(<CostDashboard />)

    const startTime = performance.now()

    wsDispatcher.dispatch({
      type: 'brain_cost_update',
      brainId: 'brain-1',
      cost: 10.50,
      timestamp: new Date().toISOString(),
    })

    await waitFor(() => {
      expect(screen.getByText('$10.50')).toBeInTheDocument()
    })

    const updateTime = performance.now() - startTime
    expect(updateTime).toBeLessThan(50) // P99 target
  })
})
```

---

## Performance SLOs

### UIE-01 (Three-Column Layout):
| Metric | Target | Measurement |
|--------|--------|-------------|
| Time-to-first-render | < 100ms | Performance API |
| Layout state persistence | < 10ms | localStorage read/write |
| Collapse/expand transition | < 200ms | CSS transition duration |

### UIE-02 (Real-time Agent Monitoring):
| Metric | Target | Measurement |
|--------|--------|-------------|
| 24-brain burst render | 60fps (16.67ms) | RAF batching |
| WS event processing | < 50ms P99 | wsDispatcher latency |
| Density mode switch | < 50ms | Component re-render time |

### UIE-03 (Cost Dashboard):
| Metric | Target | Measurement |
|--------|--------|-------------|
| Cost metrics fetch | < 200ms P99 | API response time |
| WS cost update | < 50ms | wsDispatcher latency |
| QuotaBar render | < 100ms | Component render time |

---

## Test Coverage Targets

**Frontend (Vitest):**
- Baseline: 407 tests (current)
- Phase 17 target: +50 tests (457 total)
- Focus areas:
  - Layout components (15 tests)
  - Monitoring components (20 tests)
  - Cost dashboard (15 tests)

**Backend (pytest):**
- Baseline: 631 tests (current)
- Phase 17 target: +10 tests (641 total)
- Focus areas:
  - Cost metrics API (5 tests)
  - WebSocket integration (5 tests)

**E2E (Playwright):**
- Baseline: 0 tests (new for Phase 17)
- Phase 17 target: +5 tests
- Focus areas:
  - Layout collapse/expand (1 test)
  - Multi-tenant switching (1 test)
  - Agent monitoring (2 tests)
  - Cost dashboard (1 test)

---

## Anti-patterns to Avoid

### QA Violations:
- ❌ **Testing from project root** — Run `uv run pytest` from `apps/api/` only
- ❌ **Missing SLOs** — Define performance targets before implementation
- ❌ **No visual regression tests** — Layout changes need screenshot comparison
- ❌ **No WebSocket testing** — WS events need integration tests
- ❌ **No responsive testing** — Mobile/desktop breakpoints need verification

---

## CI/CD Considerations

**GitHub Actions Workflow:**
```yaml
# .github/workflows/test-phase17.yml
name: Phase 17 Tests

on: [push, pull_request]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - run: pnpm install
      - run: pnpm test # Vitest
      - run: pnpm test:e2e # Playwright

  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: cd apps/api && uv run pytest # Run from apps/api/, NOT root

  visual-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pnpm test:visual # Playwright screenshots
```

**Performance Monitoring:**
- Use Playwright's `performance.now()` for metrics
- Track P50, P90, P99 latencies in CI
- Alert on SLO violations

---

## Deferred Items

**Deferred to Phase 18+ (Multi-channel Gateway):**
- Mobile swipe gesture testing (requires touch device farm)
- Voice command integration testing
- Push notification E2E tests

**Deferred to Phase 19+ (Future enhancements):**
- Load testing for 100+ concurrent users
- Stress testing for 1000+ brains
- Chaos engineering for WebSocket failures

---

## Summary

**Key Decisions:**
1. **Unit tests:** +50 frontend tests (Vitest)
2. **Integration tests:** WebSocket event validation
3. **E2E tests:** +5 Playwright tests (new)
4. **Performance SLOs:** 60fps for 24-brain burst, < 200ms API calls
5. **Visual regression:** Screenshot comparison for layout changes
6. **Responsive testing:** 375px, 768px, 1440px breakpoints

**Next Steps:**
- Synthesize all brain outputs → Brain #7 evaluation
- Write 17-BRAIN-OUTPUTS.md
- Invoke `/mm:plan-phase 17` with GSD skill

---

*Brain #6 consultation complete — 2026-04-08*
