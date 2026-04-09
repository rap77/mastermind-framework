# Mobile Testing Strategy — Phase 17

**Created:** 2026-04-08
**Purpose:** Fulfill Brain #7 Condition #1 — Device farm strategy for swipe gestures

## Current State

- **Stack:** Next.js 16 + Playwright (already configured)
- **Testing framework:** Vitest (407 tests passing)
- **Mobile challenge:** Swipe gestures in War Room panels require real device validation

## Strategy: Hybrid Approach (Phased)

### Phase 1: Local Emulator Testing (Immediate — Week 1)

**Tools:**
- Playwright's built-in device emulation (already available)
- Chrome DevTools Device Mode
- iOS Simulator via Xcode (if on Mac)
- Android Emulator via Android Studio

**Coverage:**
```javascript
// playwright.config.ts - Devices to test
devices: [
  { name: 'iPhone 14 Pro', viewport: { width: 393, height: 852 } },
  { name: 'iPhone SE', viewport: { width: 375, height: 667 } },
  { name: 'Pixel 5', viewport: { width: 393, height: 851 } },
  { name: 'iPad Mini', viewport: { width: 768, height: 1024 } },
]
```

**Swipe Gesture Tests:**
```typescript
// Example: Swipe left on brain panel
test('swipe left to reveal brain actions', async ({ page }) => {
  await page.goto('/war-room');
  const panel = page.locator('[data-testid="brain-panel-1"]');

  await panel.evaluate((el) => {
    const startX = el.getBoundingClientRect().right - 50;
    const startY = el.getBoundingClientRect().top + 50;
    const endX = el.getBoundingClientRect().left + 50;

    // Simulate swipe
    el.dispatchEvent('touchstart', { touches: [{ clientX: startX, clientY: startY }] });
    el.dispatchEvent('touchmove', { touches: [{ clientX: endX, clientY: startY }] });
    el.dispatchEvent('touchend');
  });

  await expect(page.locator('[data-testid="brain-actions"]')).toBeVisible();
});
```

**Acceptance Criteria:**
- ✅ All swipe gestures work on iOS Simulator
- ✅ All swipe gestures work on Android Emulator
- ✅ Touch targets ≥ 44x44px (WCAG 2.5.5)
- ✅ No horizontal scroll on swipe actions

### Phase 2: Cloud Device Farm (Week 2-3)

**Recommended:** BrowserStack (over Sauce Labs)

**Rationale:**
- Better Playwright integration
- More comprehensive device coverage
- Superior debugging tools (video + screenshots)
- Latency matching real-world conditions

**Cost Analysis (2026 estimates):**

| Plan | Monthly | Concurrent Sessions | Devices |
|------|---------|---------------------|---------|
| **Starter** | $39 | 1 | 2000+ |
| **Team** | $199 | 5 | 2000+ |
| **Enterprise** | Custom | Unlimited | 2000+ |

**Recommendation:** Start with **Starter ($39/month)** for Phase 17 validation, upgrade to Team if parallel testing needed.

**Setup Commands:**
```bash
# Install BrowserStack Playwright plugin
pnpm add -D @browserstack/playwright

# Authenticate
export BROWSERSTACK_USERNAME=<your_username>
export BROWSERSTACK_ACCESS_KEY=<your_key>

# Run on BrowserStack
npx playwright test --project=browserstack-iphone-14
npx playwright test --project=browserstack-pixel-5
```

**Playwright Config Update:**
```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: 'browserstack-iphone-14',
      use: {
        connectOptions: {
          wsEndpoint: `wss://cdp.browserstack.com/playwright?caps=${encodeURIComponent(JSON.stringify({
            'browser': 'iphone-14',
            'browser_version': '16',
            'os': 'ios',
            'os_version': '16',
            'real_mobile': 'true',
          }))}`,
        },
      },
    },
    {
      name: 'browserstack-pixel-5',
      use: {
        connectOptions: {
          wsEndpoint: `wss://cdp.browserstack.com/playwright?caps=${encodeURIComponent(JSON.stringify({
            'browser': 'google-pixel-5',
            'browser_version': '12',
            'os': 'android',
            'os_version': '12',
            'real_mobile': 'true',
          }))}`,
        },
      },
    },
  ],
});
```

### Phase 3: CI/CD Integration (Week 3)

**GitHub Actions Workflow:**
```yaml
# .github/workflows/mobile-test.yml
name: Mobile Tests

on:
  pull_request:
    paths:
      - 'apps/web/**'
  workflow_dispatch:

jobs:
  browserstack:
    runs-on: ubuntu-latest
    if: github.event_name == 'workflow_dispatch'  # Manual trigger to save costs
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install pnpm
        uses: pnpm/action-setup@v2

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Install Playwright browsers
        run: npx playwright install --with-deps

      - name: Run BrowserStack tests
        env:
          BROWSERSTACK_USERNAME: ${{ secrets.BROWSERSTACK_USERNAME }}
          BROWSERSTACK_ACCESS_KEY: ${{ secrets.BROWSERSTACK_ACCESS_KEY }}
        run: npx playwright test --project=browserstack-*

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: browserstack-results
          path: playwright-report/
```

**Cost Optimization:**
- Run BrowserStack tests **manually** before merges (workflow_dispatch)
- Run emulator tests on **every PR** (free)
- Weekly scheduled full device farm run (Sunday 2am)

### Phase 4: Physical Device Validation (Week 4 - Optional)

**If budget allows ($0-50):**

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Used devices** | $50-100 one-time | Real hardware, network conditions | Limited coverage |
| **Device lending** | $0 | Free, variety | Shipping time |
| **Local testing** | $0 (borrow friends' phones) | Real-world conditions | Not reproducible |

**Recommendation:** Borrow 3-4 devices (iPhone 12+, Pixel 5+, iPad Mini) for final validation.

## Device Coverage Matrix

| Device | OS | Screen Size | Priority | Test Frequency |
|--------|-------|-------------|----------|----------------|
| iPhone 14 Pro | iOS 16 | 393x852 | P0 | Every PR (emulator) |
| iPhone SE | iOS 16 | 375x667 | P1 | Weekly (emulator) |
| Pixel 5 | Android 12 | 393x851 | P0 | Every PR (emulator) |
| Samsung Galaxy S21 | Android 12 | 360x800 | P1 | Weekly (BrowserStack) |
| iPad Mini | iOS 16 | 768x1024 | P2 | Bi-weekly (emulator) |

## Swipe Gesture Test Scenarios

1. **Left swipe** → Reveal brain actions (edit, delete, archive)
2. **Right swipe** → Quick actions (duplicate, favorite)
3. **Pull to refresh** → Reload brain status
4. **Pinch to zoom** → Brain visualization detail view
5. **Long press** → Context menu

## Success Metrics

- ✅ All swipe gestures work on 5+ real devices
- ✅ Touch response time < 100ms (measured via Performance API)
- ✅ No accidental triggers (false positive rate < 5%)
- ✅ Accessibility: swipe gestures have keyboard alternatives

## Rollout Criteria

Phase 17 execution starts when:
1. ✅ Emulator tests pass locally
2. ✅ BrowserStack account created ($39 committed)
3. ✅ GitHub Actions workflow deployed
4. ✅ At least 2 physical devices available for final validation

## References

- Playwright Mobile Guide: https://playwright.dev/docs/emulation
- BrowserStack Playwright: https://www.browserstack.com/docs/playwright
- WCAG 2.5.5 (Touch Target Size): https://www.w3.org/WAG/WCAG21/Understanding/target-size.html
