# Accessibility Audit Plan — Phase 17

**Created:** 2026-04-08
**Purpose:** Fulfill Brain #7 Condition #4 — WCAG 2.1 AA compliance verification

## Compliance Target

**Standard:** WCAG 2.1 Level AA
**Scope:** Phase 17 UI components (War Room panels, mobile interactions)
**Enforcement:** Manual testing + automated tools + CI/CD integration

## Testing Approach: Hybrid (Automated + Manual)

### Automated Testing (80% of issues)

**Tool: axe-core (Deque)**
- Industry standard for accessibility testing
- Integrates with Playwright, Chrome DevTools, CI/CD
- Covers 57% of WCAG 2.1 AA success criteria
- Zero false positives

**Installation:**
```bash
pnpm add -D @axe-core/playwright
```

**Integration with Playwright:**
```typescript
// e2e/accessibility/axe-core.spec.ts
import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test.describe('Accessibility - Automated', () => {
  test.beforeEach(async ({ page }) => {
    await injectAxe(page);
  });

  test('War Room homepage has no accessibility violations', async ({ page }) => {
    await page.goto('/war-room');
    await page.waitForSelector('[data-testid="brain-grid"]');

    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true },
    });
  });

  test('Brain detail panel has no violations', async ({ page }) => {
    await page.goto('/war-room');
    await page.click('[data-testid="brain-card-0"]');
    await page.waitForSelector('[data-testid="brain-detail-panel"]');

    // Check only the detail panel (not entire page)
    await checkA11y(page, '[data-testid="brain-detail-panel"]', {
      detailedReport: true,
    });
  });

  test('Mobile view has no violations', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/war-room');
    await page.waitForSelector('[data-testid="mobile-brain-list"]');

    await checkA11y(page);
  });

  test('Swipe actions are keyboard accessible', async ({ page }) => {
    await page.goto('/war-room');

    // Tab to first brain card
    await page.keyboard.press('Tab');
    await page.keyboard.press('Enter'); // Activate

    // Check that action menu is accessible
    await expect(page.locator('[data-testid="brain-menu"]')).toBeVisible();

    await checkA11y(page, '[data-testid="brain-menu"]');
  });
});
```

**CI/CD Integration:**
```yaml
# .github/workflows/accessibility.yml
name: Accessibility Tests

on:
  pull_request:
    paths:
      - 'apps/web/**'
  workflow_dispatch:

jobs:
  axe-core:
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

      - name: Run accessibility tests
        run: npx playwright test e2e/accessibility/axe-core.spec.ts

      - name: Upload accessibility report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: axe-report
          path: playwright-report/a11y-report.html
```

### Manual Testing (20% of issues — requires human judgment)

**Why manual?** Automated tools cannot detect:
- Keyboard navigation flow (logical tab order)
- Screen reader announcements (correct labels, context)
- Focus visibility (visible focus indicators)
- Color contrast ratios (subject to design judgment)
- Content comprehensibility (cognitive accessibility)

#### Manual Test 1: Keyboard Navigation

**Protocol:**
1. Unplug mouse / disable trackpad
2. Navigate War Room using **only Tab, Shift+Tab, Enter, Space, Arrow keys**
3. Verify:

| Check | Pass Criteria |
|----------------------|
| **Tab order** | Logical top-to-bottom, left-to-right |
| **Focus visible** | Clear focus indicator on all interactive elements |
| **Skip links** | "Skip to main content" link exists |
| **Modal trap** | Tab cycles within modal, not behind it |
| **Escape key** | Closes modals/dropdowns |
| **Enter/Space** | Activates buttons, links, checkboxes |

**Test Script:**
```typescript
// Manual test checklist (print and execute)
const keyboardChecklist = {
  'Can I reach all interactive elements with Tab?': false,
  'Is the tab order logical?': false,
  'Is focus always visible?': false,
  'Can I operate swipe gestures with Arrow keys?': false,
  'Can I close modals with Escape?': false,
  'Can I navigate brain cards with Arrow keys?': false,
};
```

**Acceptance Criteria:**
- ✅ All interactive elements reachable via keyboard
- ✅ Tab order matches visual layout
- ✅ Focus indicator visible (WCAG 2.4.7 — Focus Visible)
- ✅ No keyboard traps (user can exit any component)

#### Manual Test 2: Screen Reader Testing

**Required Screen Readers:**

| Platform | Screen Reader | Why |
|----------|---------------|-----|
| **Windows** | NVDA (free) | Most popular Windows screen reader |
| **macOS** | VoiceOver (built-in) | Default for Mac/iOS users |
| **iOS** | VoiceOver (built-in) | Mobile testing |

**NVDA Setup (Windows):**
1. Download: https://www.nvaccess.org/download/
2. Install with default settings
3. **Key commands:**
   - `NVDA + Q` → Quit
   - `NVDA + Tab` → Read current element
   - `NVDA + Down` → Read all content
   - `H` → Next heading
   - `L` → Next list
   - `B` → Next button
   - `Enter` → Activate link/button

**VoiceOver Setup (macOS):**
1. System Preferences → Accessibility → VoiceOver → Enable
2. **Key commands:**
   - `Cmd + F5` → Toggle VoiceOver
   - `VO + Right` → Next element
   - `VO + Left` → Previous element
   - `VO + Shift + Down` → Interact with element
   - `Enter` → Activate

**Test Protocol:**

1. **Announcement check:** Navigate War Room and verify:
   - ✅ Brain cards announced as "Brain Card [name], button"
   - ✅ Status updates announced ("Brain Product Strategy is now processing")
   - ✅ Actions announced ("Edit button", "Delete button")
   - ✅ Error messages announced ("Error: Failed to update brain status")

2. **Navigation check:**
   - ✅ Landmarks available ("Main", "Navigation", "Complementary")
   - ✅ Headings hierarchy (h1 → h2 → h3, no skipped levels)
   - ✅ Lists used for related items (brain cards in `<ul>`)

3. **Forms check:**
   - ✅ Labels announced before inputs
   - ✅ Required fields indicated
   - ✅ Error messages announced and linked to inputs

**Pass Criteria:**
- ✅ All interactive elements have accessible names
- ✅ Status changes announced without focus (ARIA live regions)
- ✅ Icons have text alternatives (`aria-label` or visually hidden text)

#### Manual Test 3: Color Contrast Check

**Tool:** axe DevTools (Chrome extension) or Colour Contrast Analyser (CCA)

**WCAG 2.1 AA Requirements:**

| Text Size | Contrast Ratio | Example |
|-----------|----------------|---------|
| **Normal text (< 18pt)** | 4.5:1 | Body text, labels |
| **Large text (≥ 18pt)** | 3:1 | Headings, UI labels |
| **UI components** | 3:1 | Borders, focus indicators |

**Test Protocol:**

1. Install axe DevTools Chrome extension
2. Navigate to War Room
3. Open axe DevTools → "Contrast" tab
4. Click on each text element to check ratio

**Critical Checks:**
- ✅ Brain card titles vs background (4.5:1)
- ✅ Status indicators (green/yellow/red) vs background (3:1)
- ✅ Button text vs button background (4.5:1)
- ✅ Link text vs background (4.5:1)
- ✅ Error messages vs background (4.5:1)

**If contrast fails:**
- Darken text color
- Lighten background color
- Add text shadow/border for better separation
- Use larger font size (≥ 18pt) to reduce ratio requirement

#### Manual Test 4: Touch Target Size (Mobile)

**WCAG 2.5.5:** Touch targets ≥ 44x44 CSS pixels

**Test Protocol:**

1. Open Chrome DevTools → Device Mode
2. Select mobile device (iPhone 14, Pixel 5)
3. Use Ruler tool to measure touch targets

**Critical Checks:**
- ✅ Brain card swipe areas ≥ 44px height
- ✅ Action buttons (edit, delete) ≥ 44x44px
- ✅ Menu triggers ≥ 44x44px
- ✅ Checkbox/toggle switches ≥ 44x44px

**If too small:**
- Increase padding/margin
- Use larger icons
- Expand tap target area with CSS (`::before` pseudo-element)

## WCAG 2.1 AA Checklist (Phase 17 Specific)

### Perceivable

| Criterion | Component | Test Method | Status |
|-----------|-----------|-------------|--------|
| **1.1.1** Non-text Content | Brain icons, status indicators | Alt text, aria-label | ⏳ TODO |
| **1.3.1** Info and Relationships | Brain card hierarchy | Semantic HTML (headings, lists) | ⏳ TODO |
| **1.3.2** Meaningful Sequence | Tab order | Keyboard test | ⏳ TODO |
| **1.4.3** Contrast (Minimum) | All text vs backgrounds | Axe DevTools | ⏳ TODO |
| **1.4.10** Reflow | Mobile viewport (no horizontal scroll @ 320px) | DevTools mobile emulation | ⏳ TODO |
| **1.4.11** Non-text Contrast | Status indicators, borders | Visual inspection | ⏳ TODO |
| **1.4.12** Text Spacing | No loss of content on 200% zoom | Browser zoom test | ⏳ TODO |

### Operable

| Criterion | Component | Test Method | Status |
|-----------|-----------|-------------|--------|
| **2.1.1** Keyboard | All interactions | Keyboard-only navigation | ⏳ TODO |
| **2.1.4** Character Key Shortcuts | No single-key shortcuts (except disable) | Code review | ⏳ TODO |
| **2.4.3** Focus Order | Logical tab sequence | Keyboard test | ⏳ TODO |
| **2.4.7** Focus Visible | Clear focus indicator | Visual inspection | ⏳ TODO |
| **2.5.1** Pointer Gestures | Swipe gestures have keyboard alternatives | Manual test | ⏳ TODO |
| **2.5.2** Pointer Cancellation | No accidental triggers on touch | Manual test | ⏳ TODO |
| **2.5.5** Target Size | Touch targets ≥ 44x44px | DevTools ruler | ⏳ TODO |

### Understandable

| Criterion | Component | Test Method | Status |
|-----------|-----------|-------------|--------|
| **3.1.1** Language of Page | `<html lang="es">` | Code inspection | ⏳ TODO |
| **3.2.1** On Focus | No context change on focus | Keyboard test | ⏳ TODO |
| **3.2.2** On Input | No context change on input | Form test | ⏳ TODO |
| **3.3.2** Labels or Instructions | Form inputs have labels | Axe-core | ⏳ TODO |
| **3.3.4** Error Prevention | Confirmation for destructive actions | Manual test | ⏳ TODO |

### Robust

| Criterion | Component | Test Method | Status |
|-----------|-----------|-------------|--------|
| **4.1.2** Name, Role, Value | ARIA attributes correct | Axe-core + screen reader | ⏳ TODO |

## ARIA Live Regions (Real-time Updates)

**Problem:** When brain status updates without page refresh, screen readers miss the change.

**Solution:** ARIA live regions announce changes automatically.

**Implementation:**
```tsx
// BrainStatusIndicator.tsx
export function BrainStatusIndicator({ status }: { status: BrainStatus }) {
  return (
    <div
      role="status"
      aria-live="polite"  // Announces when user is idle
      aria-atomic="true"  // Announces entire content, not just change
      data-testid="brain-status-indicator"
    >
      <span className={`status-badge status-${status}`}>
        {status === 'processing' && '⏳ Processing'}
        {status === 'complete' && '✅ Complete'}
        {status === 'error' && '❌ Error'}
      </span>
    </div>
  );
}
```

**Live Region Types:**

| aria-live value | When to use | Example |
|-----------------|-------------|---------|
| **off** (default) | No announcement | Static content |
| **polite** | Wait until user pauses | Status updates, progress |
| **assertive** | Interrupt immediately | Critical errors, alerts |

## Audit Timeline

### Week 1: Automated Testing

- [ ] Install axe-core Playwright plugin
- [ ] Create automated test suite
- [ ] Run baseline scan on current codebase
- [ ] Document violations (create GitHub issues)

### Week 2: Manual Testing - Keyboard

- [ ] Execute keyboard navigation protocol
- [ ] Fix tab order issues
- [ ] Add visible focus indicators
- [ ] Verify all interactions work without mouse

### Week 3: Manual Testing - Screen Readers

- [ ] Install NVDA (Windows) or VoiceOver (macOS)
- [ ] Execute screen reader protocol
- [ ] Fix missing labels/announcements
- [ ] Add ARIA live regions for status updates
- [ ] Verify semantic HTML (headings, landmarks)

### Week 4: Manual Testing - Visual & Mobile

- [ ] Run color contrast checks (axe DevTools)
- [ ] Verify touch target sizes (mobile)
- [ ] Test zoom to 200% (reflow check)
- [ ] Final audit + documentation

## Success Criteria

Phase 17 execution starts when:
- ✅ **Zero** WCAG Level A violations (automated)
- ✅ **≤ 5** AA violations (only contrast + focus visible allowed)
- ✅ Keyboard navigation fully functional
- ✅ Screen reader announcements verified
- ✅ CI/CD pipeline blocks merges with new violations

## Continuous Monitoring

**Pre-commit Hook:**
```json
// package.json
{
  "scripts": {
    "test:a11y": "npx playwright test e2e/accessibility",
    "lint:a11y": "pnpm eslint --plugin jsx-a11y apps/web/**"
  }
}
```

**Husky Hook:**
```bash
# .husky/pre-commit
pnpm test:a11y || echo "⚠️ Accessibility issues detected"
```

## References

- WCAG 2.1 Quick Reference: https://www.w3.org/WAI/WCAG21/quickref/
- axe-core Documentation: https://www.deque.com/axe/
- NVDA User Guide: https://www.nvaccess.org/files/nvda/documentation/userGuide.html
- VoiceOver Guide: https://www.apple.com/accessibility/voiceover/
- ARIA Live Regions: https://www.w3.org/WAI/ARIA/apg/
- Playwright Accessibility: https://playwright.dev/docs/accessibility-testing
