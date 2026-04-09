# RAF Batching Validation Plan — Phase 17

**Created:** 2026-04-08
**Purpose:** Fulfill Brain #7 Condition #2 — Measure 60fps at 24-brain burst

## The Challenge

**Scenario:** War Room displays 24 brain cards simultaneously with real-time status updates.

**Risk:** Without proper React batching, each brain update could trigger:
- 24 separate re-renders
- 24 separate layout recalculations
- 24 separate paint cycles
- **Result:** Jank, dropped frames, < 30fps

**Goal:** Maintain 60fps (16.67ms per frame) even during burst updates.

## Acceptance Criteria

- ✅ **P99 frame time < 16.67ms** (60fps)
- ✅ **No long tasks (> 50ms)** in Chrome DevTools
- ✅ **RAF callback duration < 5ms** per frame
- ✅ **Layout thrashing < 10%** of total frame time

## Validation Strategy

### Tool 1: React DevTools Profiler

**Setup:**
```bash
# Install React DevTools Profiler (if not present)
pnpm add -D @welldone-software/why-did-you-render
```

**Usage:**
```typescript
// apps/web/src/profiling.ts (dev only)
if (process.env.NODE_ENV === 'development') {
  const whyDidYouRender = require('@welldone-software/why-did-you-render');
  whyDidYouRender(React, {
    trackAllPureComponents: true,
    trackHooks: true,
    logOnDifferentValues: true,
  });
}

// Component opt-in
BrainCard.whyDidYouRender = true;
```

**Measurement Protocol:**

1. Open Chrome DevTools → **Profiler** tab
2. Click **Record** → Trigger 24-brain update (simulate status change)
3. Stop recording after 5 seconds
4. Analyze flame graph:
   - Look for **committing 24 components** (bad)
   - Look for **batched commit** (good)
   - Check **rendered at least once** vs **rendered multiple times**

**Pass Criteria:**
- Single commit for all 24 brains
- No re-renders during status update
- Total commit time < 10ms

### Tool 2: Chrome Performance Tab

**Measurement Protocol:**

1. Open Chrome DevTools → **Performance** tab
2. Check **Screenshots** and **Memory** checkboxes
3. Click **Record** → Trigger 24-brain burst update
4. Stop after 5 seconds
5. Analyze:

**Key Metrics:**
```
Frame Rate:
├── FPS: 60 (target)
├── Long Tasks: 0 (target)
└── Main Thread:
    ├── Scripting: < 10ms per frame
    ├── Rendering: < 5ms per frame
    └── Painting: < 3ms per frame
```

**What to Look For:**
- ❌ **Red triangles** = Long tasks (> 50ms)
- ❌ **Multiple "Layout"** events per frame = Layout thrashing
- ✅ **Consistent 16.67ms frames** = 60fps

**Pass Criteria:**
- Zero long tasks during burst
- Frame time P99 < 16.67ms
- No layout thrashing (single Layout event per frame)

### Tool 3: Custom RAF Instrumentation

**Implementation:**
```typescript
// apps/web/src/utils/raf-monitor.ts
export class RAFMonitor {
  private frameTimings: number[] = [];
  private rafId: number | null = null;
  private isRecording = false;

  startRecording() {
    this.frameTimings = [];
    this.isRecording = true;
    this.measureFrame();
  }

  private measureFrame = () => {
    if (!this.isRecording) return;

    const start = performance.now();
    
    requestAnimationFrame(() => {
      const end = performance.now();
      const frameTime = end - start;
      this.frameTimings.push(frameTime);
      
      if (this.frameTimings.length < 300) { // 5 seconds @ 60fps
        this.measureFrame();
      } else {
        this.isRecording = false;
        this.reportStats();
      }
    });
  }

  private reportStats() {
    const sorted = [...this.frameTimings].sort((a, b) => a - b);
    const p50 = sorted[Math.floor(sorted.length * 0.50)];
    const p95 = sorted[Math.floor(sorted.length * 0.95)];
    const p99 = sorted[Math.floor(sorted.length * 0.99)];
    const max = sorted[sorted.length - 1];

    console.log('🎯 RAF Performance Stats:', {
      frames: this.frameTimings.length,
      p50: `${p50.toFixed(2)}ms`,
      p95: `${p95.toFixed(2)}ms`,
      p99: `${p99.toFixed(2)}ms`,
      max: `${max.toFixed(2)}ms`,
      droppedFrames: this.frameTimings.filter(t => t > 16.67).length,
    });

    return { p50, p95, p99, max };
  }

  stopRecording() {
    this.isRecording = false;
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
    }
  }
}

// Usage in War Room component
const monitor = new RAFMonitor();

const triggerBurstUpdate = () => {
  monitor.startRecording();
  
  // Trigger 24-brain update
  setBrainStatuses(prev => prev.map(brain => ({
    ...brain,
    status: 'processing',
    lastUpdated: Date.now(),
  })));
};
```

**Automated Test:**
```typescript
// apps/web/src/__tests__/performance/raf-batching.test.ts
import { test, expect } from '@playwright/test';
import { RAFMonitor } from '@/utils/raf-monitor';

test('24-brain burst maintains 60fps', async ({ page }) => {
  await page.goto('/war-room');
  
  // Inject RAF monitor
  await page.evaluate(() => {
    window.rafMonitor = new RAFMonitor();
  });

  // Start monitoring
  await page.evaluate(() => window.rafMonitor.startRecording());

  // Trigger burst update
  await page.click('[data-testid="trigger-burst-update"]');

  // Wait for 5 seconds
  await page.waitForTimeout(5000);

  // Get stats
  const stats = await page.evaluate(() => window.rafMonitor.reportStats());

  // Assert 60fps
  expect(stats.p99).toBeLessThan(16.67); // P99 < 16.67ms
  expect(stats.droppedFrames).toBe(0); // No dropped frames
});
```

### Tool 4: Lighthouse Performance Audit

**Setup:**
```bash
# Install Lighthouse CI
pnpm add -D @lhci/cli
```

**Config:**
```javascript
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000/war-room'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'metrics:fps': ['error', { minScore: 0.9 }],
        'metrics:layout-shift': ['error', { maxNumericValue: 0.1 }],
      },
    },
  },
};
```

**Run:**
```bash
# Start dev server
pnpm dev

# Run Lighthouse CI
lhci autorun
```

**Pass Criteria:**
- Performance score ≥ 90
- Cumulative Layout Shift (CLS) < 0.1
- No FPS drops below 55

## Implementation Checklist

### Phase 1: Pre-Implementation Baseline

- [ ] Run React DevTools Profiler on current War Room
- [ ] Document current frame rate during idle (baseline)
- [ ] Document current frame rate during 12-brain update
- [ ] Identify current bottlenecks (if any)

### Phase 2: Implementation with RAF Batching

**Technique:**
```typescript
// Use React 18's automatic batching + explicit batching
import { startTransition, useDeferredValue } from 'react';

const WarRoom = () => {
  const [brains, setBrains] = useState<Brain[]>([]);
  
  // Defer non-critical updates
  const deferredBrains = useDeferredValue(brains);

  const handleBurstUpdate = (newStatuses: BrainStatus[]) => {
    // Critical update - immediate
    startTransition(() => {
      setBrains(prev => prev.map(brain => ({
        ...brain,
        status: newStatuses[brain.id],
      })));
    });
  };

  return (
    <div>
      {deferredBrains.map(brain => (
        <BrainCard key={brain.id} brain={brain} />
      ))}
    </div>
  );
};
```

**Optimization Techniques:**
1. **React.memo** for BrainCard (prevent re-render if props unchanged)
2. **useTransition** for low-priority updates
3. **useDeferredValue** for non-critical UI
4. **Virtualization** (react-window) if > 50 brains
5. **Batch state updates** (single setState vs multiple)

### Phase 3: Post-Implementation Validation

- [ ] Re-run React DevTools Profiler
- [ ] Re-run Chrome Performance tab
- [ ] Re-run custom RAF instrumentation
- [ ] Compare before/after metrics
- [ ] Document improvements

## Continuous Monitoring

**Performance Budget:**
```javascript
// next.config.js
module.exports = {
  experimental: {
    cpus: 1, // Simulate low-end device
  },
  // Add performance hints
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
};
```

**CI/CD Integration:**
```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  pull_request:
    paths:
      - 'apps/web/**'

jobs:
  raf-batching:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      
      - name: Install pnpm
        uses: pnpm/action-setup@v2
      
      - name: Install dependencies
        run: pnpm install --frozen-lockfile
      
      - name: Build
        run: pnpm build
      
      - name: Start server
        run: ppm start &

      - name: Wait for server
        run: npx wait-on http://localhost:3000

      - name: Run RAF performance test
        run: npx playwright test raf-batching.test.ts

      - name: Lighthouse CI
        run: npx lhci autorun
```

## Success Metrics Summary

| Metric | Target | Tool | Frequency |
|--------|--------|------|-----------|
| P99 frame time | < 16.67ms | RAF Monitor | Every PR |
| Long tasks | 0 | Chrome Performance | Every PR |
| React commits | 1 per burst | React DevTools | Every PR |
| Layout thrashing | < 10% | Chrome Performance | Every PR |
| Performance score | ≥ 90 | Lighthouse | Every PR |

## Rollback Criteria

If any of these occur during implementation:
1. P99 > 20ms for 3 consecutive builds → Revert batching approach
2. Long tasks > 100ms → Investigate blocking code
3. Memory leak (heap grows > 100MB over 5 min) → Check useEffect cleanup

## References

- React 18 Automatic Batching: https://react.dev/blog/2022/03/29/react-v18#automatic-batching
- Chrome DevTools Performance: https://developer.chrome.com/docs/devtools/performance
- RAF Pattern Guide: https://developer.mozilla.org/en-US/docs/Web/API/window/requestAnimationFrame
- Lighthouse Performance: https://web.dev/performance-scoring/
