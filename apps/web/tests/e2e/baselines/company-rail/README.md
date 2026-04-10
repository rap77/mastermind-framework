# Visual Regression Baselines

This directory stores baseline screenshots for visual regression testing.

## Purpose

Visual regression tests ensure that UI changes don't accidentally break existing layouts or designs. Baselines are captured **before** major layout modifications and used as reference for future comparisons.

## Brain #7 Mitigation

- **Baseline Capture:** Screenshots captured before layout changes (Phase 17-02)
- **Automation:** Tests run on every PR (via GitHub Actions in Phase 18)
- **Mobile Testing:** Includes mobile, tablet, and desktop viewports
- **Accessibility:** Tests include keyboard navigation and screen reader checks

## Directory Structure

```
baselines/company-rail/
├── desktop-expanded.png    # 1920x1080 - CompanyRail expanded
├── desktop-collapsed.png   # 1920x1080 - CompanyRail collapsed
├── tablet-view.png         # 768x1024  - Tablet layout
├── mobile-view.png         # 375x667   - Mobile single column
└── README.md               # This file
```

## Usage

### Capture Baselines

```bash
# From apps/web directory
pnpm exec playwright test tests/e2e/visual-baseline.spec.ts
```

### Compare Against Baselines (Future)

```bash
# Run visual regression tests
pnpm exec playwright test tests/e2e/visual-baseline.spec.ts --update-snapshots
```

## Viewport Sizes

- **Desktop:** 1920x1080 (Full HD)
- **Tablet:** 768x1024 (iPad Portrait)
- **Mobile:** 375x667 (iPhone SE)

## WCAG Compliance

All visual tests verify:
- ✅ Color contrast ratios (WCAG 2.1 AA)
- ✅ Icons + color coding (Brain #3 requirement)
- ✅ Keyboard navigation (Tab, Enter, Arrow keys)
- ✅ Screen reader announcements (ARIA labels)

## Notes

- Baselines are committed to git for version control
- Update baselines intentionally after approved design changes
- Failed tests indicate unintended visual regressions
- Use `--update-snapshots` flag only after reviewing changes
