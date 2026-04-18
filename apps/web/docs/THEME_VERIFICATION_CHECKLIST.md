# Theme Verification Checklist

This checklist provides a systematic approach to manually verify that all screens and components render correctly in both light and dark modes.

## Pre-verification Setup

### Environment
- [ ] Dev server running: `cd apps/web && pnpm dev`
- [ ] Application accessible at `http://localhost:3000`
- [ ] Tests passing: `817/817` (run `pnpm test` from `apps/web/`)
- [ ] Browser DevTools open (for theme switching)
- [ ] Screen resolution: 1920x1080 or higher recommended

### Tools
- [ ] Browser DevTools (Cmd+Option+I / Ctrl+Shift+I)
- [ ] Color contrast checker (optional: [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/))
- [ ] Screen reader (optional: for accessibility testing)

## Theme Switching

### Toggle Theme
1. Click the theme toggle button in the top-right corner
2. Verify the theme switches smoothly (200ms transition)
3. Check that all components update without flicker
4. Verify no console errors during theme switch

### Manual Theme Override (for testing)
```javascript
// Force light mode
document.documentElement.classList.remove('dark')

// Force dark mode
document.documentElement.classList.add('dark')
```

## Light Mode Verification

### Command Center (`/command-center`)

#### BrainTile Components
- [ ] **Background**: `bg-card` or `bg-muted` renders correctly
- [ ] **Text**: `text-foreground` is readable on all tiles
- [ ] **Borders**: `border-border` visible but not overpowering
- [ ] **Status colors**:
  - [ ] Active: `nexus-text-active` (cyan) visible
  - [ ] Complete: `nexus-text-complete` (green) visible
  - [ ] Error: `nexus-text-error` (red) visible
  - [ ] Idle: `nexus-text-idle` (slate) visible
- [ ] **Hover states**: `hover:bg-muted/50` provides feedback
- [ ] **Focus rings**: `focus:ring-primary` appears on keyboard navigation

#### ClusterGroup
- [ ] **Color variants**: Cyan (software), Purple (marketing), Zinc (master) render correctly
- [ ] **Opacity levels**: 50, 200, 800, 950 shades are distinct
- [ ] **Borders**: `border-{color}-200` in light mode
- [ ] **Backgrounds**: `bg-{color}-50` for light backgrounds

### Nexus (`/nexus`)

#### Canvas Background
- [ ] **Default**: `--nexus-canvas-bg-default` (oklch(0.12 0 0)) renders correctly
- [ ] **Cooldown mode**: `--nexus-canvas-bg` (oklch(0.145 0 0)) applies in cooldown
- [ ] **Transition**: Smooth background transition when entering cooldown

#### React Flow Nodes
- [ ] **Brain nodes**:
  - [ ] Idle: `--color-brain-idle` (slate) with `opacity-40`
  - [ ] Active: `--color-brain-active` (cyan) with glow effect
  - [ ] Complete: `--color-brain-complete` (green) with checkmark
  - [ ] Error: `--color-brain-error` (red) with pulse animation
- [ ] **Selected nodes**: `ring-2 ring-primary` visible
- [ ] **Node backgrounds**: `bg-card` or `bg-muted` consistent
- [ ] **Text**: `text-foreground` readable on all nodes

#### React Flow Edges
- [ ] **Idle edges**: `--color-brain-idle` with `opacity-30`
- [ ] **Active edges**: `--color-brain-active` with drop-shadow glow
- [ ] **Complete edges**: `--color-brain-complete` with drop-shadow glow
- [ ] **Error edges**: `--color-brain-error` with `animate-pulse`
- [ ] **Animations**: Smooth stroke-dashoffset for active edges

#### FAB (Floating Action Button)
- [ ] **Background**: `bg-primary` renders correctly
- [ ] **Text**: `text-primary-foreground` has sufficient contrast
- [ ] **Hover**: `hover:bg-primary/90` provides feedback
- [ ] **Position**: Fixed position maintained across theme switch

### Strategy Vault (`/strategy-vault`)

#### Execution List
- [ ] **Borders**: `border-border` visible between items
- [ ] **Backgrounds**: `bg-card` for list items
- [ ] **Text**: `text-foreground` for titles, `text-muted-foreground` for metadata
- [ ] **Status badges**:
  - [ ] Active: `status-active-border` (cyan)
  - [ ] Complete: `status-complete-border` (green)
  - [ ] Error: `status-error-border` (red)

#### Snapshots
- [ ] **Backgrounds**: `bg-primary` for snapshot cards
- [ ] **Text**: `text-primary-foreground` readable on primary background
- [ ] **Hover**: `hover:scale-105` animation works smoothly

#### Detail View
- [ ] **Backgrounds**: `bg-muted/30` for subtle overlays
- [ ] **Borders**: `border-border` for separators
- [ ] **Code blocks**: Syntax highlighting readable in light mode

### Engine Room (`/engine-room`)

#### Headers
- [ ] **Text**: `text-foreground` for all headings
- [ ] **Borders**: `border-primary` for emphasized sections
- [ ] **Backgrounds**: `bg-muted` for header backgrounds

#### API Key Manager
- [ ] **Input fields**: `bg-background` with `border-border`
- [ ] **Buttons**: `bg-primary` with `text-primary-foreground`
- [ ] **Status indicators**: Proper color coding (green for valid, red for invalid)

### Flow Designer (`/flow-designer`)

#### Node Styling
- [ ] **Brain nodes**: Use `var(--color-surface-primary)` for backgrounds
- [ ] **Adapter nodes**: Use `var(--color-surface-adapter)` for backgrounds
- [ ] **Selected nodes**: Use `var(--color-node-brain-border)` for borders
- [ ] **Text**: `text-foreground` readable on all node types

#### Connections
- [ ] **Default**: `border-border` for inactive connections
- [ ] **Active**: `--color-brain-active` for active connections
- [ ] **Complete**: `--color-brain-complete` for completed connections
- [ ] **Error**: `--color-brain-error` for error connections

#### Toolbar
- [ ] **Background**: `bg-muted` for toolbar
- [ ] **Buttons**: `bg-primary` for actions
- [ ] **Icons**: `text-foreground` for inactive, `text-primary-foreground` for active

### Simulation (`/simulation`)

#### Event Log
- [ ] **Inherits Flow Designer theming**: All visual elements themed correctly
- [ ] **Timeline**: `border-border` for timeline lines
- [ ] **Events**: `bg-card` for event cards
- [ ] **Status colors**:
  - [ ] Success: `text-success` (green)
  - [ ] Error: `text-error` (red)
  - [ ] Info: `text-info` (blue)

#### Playback Controls
- [ ] **Buttons**: `bg-primary` with `text-primary-foreground`
- [ ] **Progress bar**: `bg-primary` for progress, `bg-muted` for track
- [ ] **Time display**: `text-foreground` for current time

## Dark Mode Verification

Repeat all checks from Light Mode with the `.dark` class applied.

### Additional Dark Mode Checks

#### Contrast Verification
- [ ] **Text readability**: All `text-foreground` text is readable on dark backgrounds
- [ ] **Borders**: `border-border` visible but not harsh (uses `oklch(1 0 0 / 10%)`)
- [ ] **Inputs**: `bg-background` provides sufficient contrast for text input

#### Glow Effects
- [ ] **Active nodes**: `--color-brain-active` glow is visible but not overwhelming
- [ ] **Complete nodes**: `--color-brain-complete` glow is subtle
- [ ] **Active edges**: Drop-shadow glow effects are visible

#### Canvas Backgrounds
- [ ] **Nexus default**: `--nexus-canvas-bg-default` (oklch(0.06 0 0)) renders correctly
- [ ] **Nexus cooldown**: `--nexus-canvas-bg` (oklch(0.08 0 0)) applies correctly

## Accessibility Verification

### Motion Preferences
- [ ] **Reduced motion**: All animations respect `prefers-reduced-motion`
- [ ] **Shake animation**: Suppressed when reduced motion is preferred
- [ ] **Pulse animation**: Suppressed when reduced motion is preferred
- [ ] **Spin animation**: Suppressed when reduced motion is preferred

### Keyboard Navigation
- [ ] **Focus rings**: `focus:ring-primary` visible on all interactive elements
- [ ] **Tab order**: Logical tab order through all screens
- [ ] **Skip links**: (if implemented) Skip to content links work

### Screen Reader
- [ ] **Icon labels**: All icons have `aria-hidden="true"` or `aria-label`
- [ ] **Status communication**: Status communicated via text, not just color
- [ ] **Semantic HTML**: Proper use of headings, landmarks, and lists

## Responsive Verification

### Mobile (< 768px)
- [ ] **Layout variables**: `--company-rail-width` and `--sidebar-width` set to 0
- [ ] **Navigation**: Mobile navigation renders correctly
- [ ] **Touch targets**: All interactive elements are at least 44x44px
- [ ] **Text readability**: No text clipping or overflow

### Tablet (768px - 1024px)
- [ ] **Layout**: Sidebar and company rail render correctly
- [ ] **Nexus canvas**: Responsive to tablet screen size
- [ ] **Flow designer**: Nodes and connections visible without scrolling

## Performance Verification

### Theme Switch Performance
- [ ] **Switch time**: Theme switch completes in < 200ms
- [ ] **No layout shift**: No visible layout shift during theme switch
- [ ] **No flicker**: No white flash during theme switch
- [ ] **Smooth transitions**: All colors transition smoothly

### Rendering Performance
- [ ] **Frame rate**: 60fps during animations (check DevTools Performance tab)
- [ ] **Paint time**: Minimal repaints during theme switch
- [ ] **Memory**: No memory leaks during repeated theme switches

## Known Issues

### Current Issues
- None at this time

### Fixed Issues
- All issues from Phase D1 code review have been addressed:
  - Hex colors replaced with token names in comments
  - Design token documentation created
  - Theme verification checklist created

## Reporting Issues

When reporting theme-related issues, include:

1. **Browser and version**: (e.g., Chrome 123, Safari 17)
2. **Screen resolution**: (e.g., 1920x1080)
3. **Theme**: Light or dark mode
4. **URL**: The specific page where the issue occurs
5. **Steps to reproduce**: Detailed steps to reproduce the issue
6. **Screenshot**: If visual, include a screenshot
7. **DevTools console**: Any console errors or warnings

## Automated Testing

While this checklist focuses on manual verification, automated tests should cover:

- [ ] Unit tests for theme toggle logic
- [ ] Integration tests for token application
- [ ] Visual regression tests for theme changes
- [ ] Accessibility tests for contrast ratios
- [ ] Performance tests for theme switch speed

## Related Documentation

- [Design Tokens Reference](./DESIGN_TOKENS.md)
- [Phase D1 Implementation](../../../../../.planning/phase-D1-theme-aware/README.md)
- [Accessibility Guidelines](./ACCESSIBILITY.md)

---

**Last Updated**: 2026-04-18
**Phase**: D1 - All Screens Theme-Aware
**Status**: All 817 tests passing
