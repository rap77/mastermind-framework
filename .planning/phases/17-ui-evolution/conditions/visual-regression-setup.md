# Visual Regression Baseline Setup — Phase 17

**Created:** 2026-04-08
**Purpose:** Fulfill Brain #7 Condition #3 — Establish screenshot baseline before implementation

## Current State

- **Testing framework:** Playwright (already configured)
- **Test suite:** 407 tests passing
- **Visual regression:** Not yet implemented

## Implementation Plan

### Step 1: Install Playwright Visual Regression Plugin

```bash
# Install Playwright with visual comparison support
pnpm add -D @playwright/test
```

Playwright natively supports visual regression via `toHaveScreenshot()` matcher — no additional plugin needed.

### Step 2: Configure Playwright for Visual Regression

**Update `playwright.config.ts`:**
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  reporter: [
    ['html'],
    ['list'],
    ['github'],
  ],

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure', // Auto-capture on failure
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // Mobile viewports
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 14'] },
    },
  ],

  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
```

### Step 3: Create Baseline Screenshot Script

**Script: `scripts/capture-baselines.ts`**
```typescript
// scripts/capture-baselines.ts
import { chromium, firefox, webkit, Browser, Page, BrowserContext } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

const BASELINE_DIR = path.join(process.cwd(), 'e2e', 'baselines');
const SCREENS_TO_CAPTURE = [
  { route: '/war-room', name: 'war-room-dashboard', waitFor: '[data-testid="brain-grid"]' },
  { route: '/war-room?brain=product-strategy', name: 'war-room-brain-detail', waitFor: '[data-testid="brain-detail-panel"]' },
  { route: '/settings', name: 'settings-page', waitFor: '[data-testid="settings-panel"]' },
  { route: '/analytics', name: 'analytics-dashboard', waitFor: '[data-testid="analytics-chart"]' },
  { route: '/mobile', name: 'mobile-war-room', waitFor: '[data-testid="mobile-brain-list"]' },
];

async function captureBaselines() {
  console.log('🎯 Capturing visual baselines...\n');

  const browsers = [
    { name: 'chromium', launcher: chromium },
    { name: 'firefox', launcher: firefox },
    { name: 'webkit', launcher: webkit },
  ];

  for (const { name, launcher } of browsers) {
    console.log(`📸 Capturing for ${name}...`);

    const browser: Browser = await launcher.launch({
      headless: true,
    });

    const context: BrowserContext = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
    });

    const page: Page = await context.newPage();

    for (const screen of SCREENS_TO_CAPTURE) {
      try {
        console.log(`  → ${screen.name} (${screen.route})`);

        await page.goto(`http://localhost:3000${screen.route}`, {
          waitUntil: 'networkidle',
        });

        // Wait for specific element to load
        await page.waitForSelector(screen.waitFor, { timeout: 5000 });

        // Wait for any animations to complete
        await page.waitForTimeout(1000);

        // Capture full page screenshot
        const screenshotPath = path.join(
          BASELINE_DIR,
          name,
          `${screen.name}.png`
        );

        // Ensure directory exists
        fs.mkdirSync(path.dirname(screenshotPath), { recursive: true });

        await page.screenshot({
          path: screenshotPath,
          fullPage: true,
        });

        console.log(`    ✅ Saved: ${screenshotPath}`);
      } catch (error) {
        console.error(`    ❌ Failed: ${error.message}`);
      }
    }

    await browser.close();
    console.log('');
  }

  console.log('✅ Baseline capture complete!');
  console.log(`📁 Baselines stored in: ${BASELINE_DIR}`);
}

// Run if called directly
if (require.main === module) {
  captureBaselines().catch(console.error);
}

export { captureBaselines };
```

**Add npm script:**
```json
// package.json
{
  "scripts": {
    "capture-baselines": "ts-node scripts/capture-baselines.ts",
    "test:visual": "playwright test e2e/visual-regression.spec.ts"
  }
}
```

### Step 4: Create Visual Regression Tests

**Test: `e2e/visual-regression/brain-panels.spec.ts`**
```typescript
import { test, expect } from '@playwright/test';

test.describe('War Room Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/war-room');
    await page.waitForSelector('[data-testid="brain-grid"]');
    await page.waitForTimeout(1000); // Wait for animations
  });

  test('brain cards layout matches baseline', async ({ page }) => {
    // Capture entire brain grid
    const brainGrid = page.locator('[data-testid="brain-grid"]');

    await expect(brainGrid).toHaveScreenshot('brain-grid.png', {
      maxDiffPixels: 100, // Allow minor rendering differences
    });
  });

  test('individual brain card matches baseline', async ({ page }) => {
    const firstCard = page.locator('[data-testid="brain-card-0"]').first();

    await expect(firstCard).toHaveScreenshot('brain-card.png', {
      maxDiffPixels: 50,
    });
  });

  test('brain card hover state matches baseline', async ({ page }) => {
    const firstCard = page.locator('[data-testid="brain-card-0"]').first();

    await firstCard.hover();
    await page.waitForTimeout(500); // Wait for hover animation

    await expect(firstCard).toHaveScreenshot('brain-card-hover.png', {
      maxDiffPixels: 50,
    });
  });

  test('brain detail panel matches baseline', async ({ page }) => {
    await page.click('[data-testid="brain-card-0"]');
    await page.waitForSelector('[data-testid="brain-detail-panel"]');
    await page.waitForTimeout(500);

    const detailPanel = page.locator('[data-testid="brain-detail-panel"]');
    await expect(detailPanel).toHaveScreenshot('brain-detail-panel.png', {
      maxDiffPixels: 100,
    });
  });

  test('mobile view matches baseline', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForSelector('[data-testid="mobile-brain-list"]');
    await page.waitForTimeout(1000);

    const mobileList = page.locator('[data-testid="mobile-brain-list"]');
    await expect(mobileList).toHaveScreenshot('mobile-brain-list.png', {
      maxDiffPixels: 100,
    });
  });
});
```

**Test: `e2e/visual-regression/interactive-states.spec.ts`**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Interactive States Visual Regression', () => {
  test('brain card swipe states', async ({ page }) => {
    await page.goto('/war-room');
    await page.setViewportSize({ width: 375, height: 667 }); // Mobile
    await page.waitForSelector('[data-testid="mobile-brain-list"]');

    const firstCard = page.locator('[data-testid="brain-card-0"]').first();

    // Simulate swipe left
    await firstCard.evaluate((el) => {
      const startX = el.getBoundingClientRect().right - 50;
      const startY = el.getBoundingClientRect().top + 50;
      const endX = el.getBoundingClientRect().left + 50;

      el.dispatchEvent('touchstart', { touches: [{ clientX: startX, clientY: startY }] });
      el.dispatchEvent('touchmove', { touches: [{ clientX: endX, clientY: startY }] });
    });

    await page.waitForTimeout(500);
    await expect(firstCard).toHaveScreenshot('brain-card-swipe-left.png', {
      maxDiffPixels: 100,
    });
  });

  test('dropdown menu states', async ({ page }) => {
    await page.goto('/war-room');
    await page.waitForSelector('[data-testid="brain-grid"]');

    const menuButton = page.locator('[data-testid="brain-menu-button-0"]').first();
    await menuButton.click();
    await page.waitForSelector('[data-testid="brain-menu-dropdown"]');
    await page.waitForTimeout(300); // Wait for dropdown animation

    const dropdown = page.locator('[data-testid="brain-menu-dropdown"]');
    await expect(dropdown).toHaveScreenshot('brain-menu-dropdown.png', {
      maxDiffPixels: 50,
    });
  });
});
```

### Step 5: Initial Baseline Capture

**Run baseline capture:**
```bash
# Start dev server
pnpm dev

# In another terminal, capture baselines
pnpm capture-baselines
```

**Expected output:**
```
📸 Baselines stored in: /home/rpadron/proy/mastermind/e2e/baselines
├── chromium/
│   ├── war-room-dashboard.png
│   ├── war-room-brain-detail.png
│   ├── settings-page.png
│   ├── analytics-dashboard.png
│   └── mobile-war-room.png
├── firefox/
│   └── (same files)
└── webkit/
    └── (same files)
```

### Step 6: Configure CI/CD for Visual Regression

**GitHub Actions Workflow:**
```yaml
# .github/workflows/visual-regression.yml
name: Visual Regression Tests

on:
  pull_request:
    paths:
      - 'apps/web/**'
      - 'e2e/**'

jobs:
  visual-regression:
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

      - name: Install Playwright browsers
        run: npx playwright install --with-deps

      - name: Run visual regression tests
        run: npx playwright test e2e/visual-regression

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 14

      - name: Upload failed screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: failed-screenshots
          path: e2e/visual-regression/*.png
          retention-days: 14
```

### Step 7: Approval Workflow for New Baselines

**When visual changes are intentional:**

1. **Developer** commits visual changes
2. **CI** detects diff → creates artifact with comparison
3. **Reviewer** checks artifact in GitHub Actions
4. **If approved:** Run baseline update
   ```bash
   # Update specific baseline
   npx playwright test e2e/visual-regression/brain-panels.spec.ts --update-screenshot
   ```
5. **Commit updated baselines**

### Step 8: Ignore Dynamic Content

**For content that changes (timestamps, random IDs), use masking:**

```typescript
test('brain card with dynamic content', async ({ page }) => {
  const card = page.locator('[data-testid="brain-card-0"]').first();

  // Mask dynamic elements before screenshot
  await page.evaluate(() => {
    // Hide timestamps
    document.querySelectorAll('[data-testid="timestamp"]').forEach(el => {
      (el as HTMLElement).style.opacity = '0';
    });

    // Replace random IDs with static text
    document.querySelectorAll('[data-testid="brain-id"]').forEach(el => {
      el.textContent = 'BRAIN-ID-STATIC';
    });
  });

  await expect(card).toHaveScreenshot('brain-card-masked.png');
});
```

## Screenshots to Capture (Priority Order)

### P0 (Critical - Must capture)

| Screen | Route | Component | Why |
|--------|-------|-----------|-----|
| War Room Dashboard | `/war-room` | BrainGrid | Main UI, most visible |
| Brain Detail Panel | `/war-room?brain=X` | BrainDetailPanel | Core interaction |
| Mobile Brain List | `/war-room` (mobile) | MobileBrainList | Mobile UX |

### P1 (Important - Should capture)

| Screen | Route | Component | Why |
|--------|-------|-----------|-----|
| Settings Page | `/settings` | SettingsPanel | Configuration UI |
| Analytics Dashboard | `/analytics` | AnalyticsChart | Data visualization |
| Brain Card States | `/war-room` | BrainCard | Hover, active, disabled |

### P2 (Nice to have - Capture if time)

| Screen | Route | Component | Why |
|--------|-------|-----------|-----|
| Swipe Actions | `/war-room` (mobile) | SwipeableItem | Mobile gesture |
| Dropdown Menus | `/war-room` | DropdownMenu | Interactive state |
| Loading States | `/war-room` | SkeletonLoader | UX feedback |

## Continuous Monitoring

**Diff Thresholds:**
```typescript
// Configure acceptable differences
{
  maxDiffPixels: 100,      // Allow 100 pixels difference
  maxDiffRatio: 0.02,      // Allow 2% of pixels to differ
  threshold: 0.2,          // Color difference threshold (0-1)
}
```

**Failure Handling:**
- Auto-comment on PR with diff images
- Require manual approval for baseline updates
- Block merge if > 10% diff in critical screens

## Success Criteria

- ✅ Baseline screenshots captured for all P0 screens
- ✅ Visual regression tests pass on current codebase
- ✅ CI/CD pipeline configured to run on every PR
- ✅ Review process documented for baseline updates

## References

- Playwright Visual Regression: https://playwright.dev/docs/screenshots
- Visual Regression Testing Best Practices: https://www.smashingmagazine.com/2023/05/visual-regression-testing-web-applications/
- Percy (Alternative): https://percy.io/
