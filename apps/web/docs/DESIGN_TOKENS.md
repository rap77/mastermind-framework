# Design Tokens Reference

## Overview

This document describes all design tokens used in the MasterMind Framework web application. Tokens are defined in `apps/web/src/app/globals.css` and consumed via Tailwind utility classes or CSS custom properties.

## Token Hierarchy

### Level 1: Tailwind Base Colors (shadcn/ui)

Base color tokens from the shadcn/ui component library. These are the foundation of our color system.

| Token | Description | Usage |
|-------|-------------|-------|
| `--primary` | Primary brand color | CTAs, links, primary actions |
| `--secondary` | Secondary brand color | Secondary actions, alternative backgrounds |
| `--muted` | Muted/background color | Subtle backgrounds, disabled states |
| `--border` | Border/divider color | Borders, dividers, outlines |
| `--foreground` | Primary text color | Body text, primary content |
| `--muted-foreground` | Secondary text color | Labels, secondary content |
| `--destructive` | Error/danger color | Error states, destructive actions |
| `--accent` | Accent color | Hover states, highlights |
| `--card` | Card background | Card components, panels |
| `--popover` | Popover background | Dropdowns, tooltips, popovers |

### Level 2: Semantic Tokens

Semantic aliases for Tailwind base colors that provide intent-based naming.

| Token | Maps To | Usage |
|-------|---------|-------|
| `--color-primary` | `var(--primary)` | Primary actions, brand elements |
| `--color-success` | Custom oklch | Success states, completion |
| `--color-warning` | Custom oklch | Warning states, caution |
| `--color-error` | `var(--destructive)` | Error states, destructive actions |
| `--color-info` | Custom oklch | Informational states |
| `--color-surface` | `var(--card)` | Surface backgrounds |
| `--color-border` | `var(--border)` | Borders, dividers |

### Level 3: Domain-Specific Tokens

Specialized tokens for specific UI domains.

#### Brain Node States

These tokens define the visual language for brain node states in the Nexus and Flow Designer.

| Token | Light Mode | Dark Mode | Usage |
|-------|-----------|-----------|-------|
| `--color-brain-active` | oklch(0.734 0.188 162.5) | oklch(0.834 0.188 162.5) | Active brain nodes, animated edges |
| `--color-brain-complete` | oklch(0.623 0.188 142.5) | oklch(0.723 0.188 142.5) | Completed brains, success states |
| `--color-brain-error` | oklch(0.677 0.215 27.3) | oklch(0.727 0.215 27.3) | Error states, failed executions |
| `--color-brain-idle` | oklch(0.556 0.048 254.8) | oklch(0.656 0.048 254.8) | Idle states, inactive nodes |
| `--color-brain-blueprint` | oklch(0.556 0.048 254.8) | oklch(0.656 0.048 254.8) | Ghost/blueprint mode |

#### Nexus Canvas

Canvas backgrounds for the Nexus DAG visualization.

| Token | Light Mode | Dark Mode | Usage |
|-------|-----------|-----------|-------|
| `--nexus-canvas-bg` | oklch(0.145 0 0) | oklch(0.08 0 0) | Cooldown mode canvas |
| `--nexus-canvas-bg-default` | oklch(0.12 0 0) | oklch(0.06 0 0) | Default canvas background |

#### Spacing Scale

Consistent spacing values following a 4px base scale.

| Token | Value | Usage |
|-------|-------|-------|
| `--spacing-0` | 0 | No spacing |
| `--spacing-1` | 0.25rem (4px) | Tight spacing |
| `--spacing-2` | 0.5rem (8px) | Compact spacing |
| `--spacing-3` | 0.75rem (12px) | Comfortable spacing |
| `--spacing-4` | 1rem (16px) | Default spacing |
| `--spacing-5` | 1.25rem (20px) | Medium spacing |
| `--spacing-6` | 1.5rem (24px) | Large spacing |
| `--spacing-8` | 2rem (32px) | Extra large spacing |
| `--spacing-10` | 2.5rem (40px) | XL spacing |
| `--spacing-12` | 3rem (48px) | XXL spacing |
| `--spacing-16` | 4rem (64px) | Section spacing |
| `--spacing-20` | 5rem (80px) | Container spacing |
| `--spacing-24` | 6rem (96px) | Jumbo spacing |

#### Shadow Scale

Depth tokens for elevation and hierarchy.

| Token | Light Mode | Dark Mode | Usage |
|-------|-----------|-----------|-------|
| `--shadow-sm` | 0 1px 2px rgb(0 0 0 / 0.05) | 0 1px 2px rgb(0 0 0 / 0.3) | Subtle elevation |
| `--shadow` | 0 1px 3px rgb(0 0 0 / 0.1) | 0 1px 3px rgb(0 0 0 / 0.4) | Default elevation |
| `--shadow-md` | 0 4px 6px rgb(0 0 0 / 0.1) | 0 4px 6px rgb(0 0 0 / 0.4) | Medium elevation |
| `--shadow-lg` | 0 10px 15px rgb(0 0 0 / 0.1) | 0 10px 15px rgb(0 0 0 / 0.4) | Large elevation |
| `--shadow-xl` | 0 20px 25px rgb(0 0 0 / 0.1) | 0 20px 25px rgb(0 0 0 / 0.4) | Extra large elevation |

#### Radius Scale

Border radius tokens for consistent rounded corners.

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | calc(var(--radius) * 0.6) | Small corners (buttons, inputs) |
| `--radius-md` | calc(var(--radius) * 0.8) | Medium corners (cards) |
| `--radius-lg` | var(--radius) | Large corners (panels) |
| `--radius-xl` | calc(var(--radius) * 1.4) | Extra large corners |
| `--radius-2xl` | calc(var(--radius) * 1.8) | XXL corners |
| `--radius-3xl` | calc(var(--radius) * 2.2) | XXXL corners |
| `--radius-full` | 9999px | Fully rounded (pills, circles) |

#### Layout Variables

Application-wide layout dimensions.

| Token | Value | Usage |
|-------|-------|-------|
| `--company-rail-width` | 180px | Company rail expanded width |
| `--company-rail-width-collapsed` | 60px | Company rail collapsed width |
| `--sidebar-width` | 240px | Sidebar expanded width |
| `--sidebar-width-collapsed` | 60px | Sidebar collapsed width |
| `--layout-transition-duration` | 200ms | Layout animation duration |
| `--layout-transition-easing` | cubic-bezier(0.4, 0, 0.2, 1) | Layout animation easing |

## Usage Guidelines

### Text Colors

Use Tailwind utility classes for text colors:

```tsx
// Primary text
className="text-foreground"

// Secondary text
className="text-muted-foreground"

// Text on primary backgrounds
className="text-primary-foreground"

// Domain-specific text
className="nexus-text-active"  // Uses --color-brain-active
className="nexus-text-complete"  // Uses --color-brain-complete
className="nexus-text-error"  // Uses --color-brain-error
className="nexus-text-idle"  // Uses --color-brain-idle
```

### Background Colors

```tsx
// Primary action backgrounds
className="bg-primary"

// Subtle backgrounds
className="bg-muted"

// Main content area
className="bg-background"

// Hover states (with opacity)
className="hover:bg-muted/50"

// Domain-specific backgrounds
className="nexus-canvas-bg"  // Uses --nexus-canvas-bg-default
className="nexus-canvas-bg-cooldown"  // Uses --nexus-canvas-bg
```

### Border Colors

```tsx
// Standard borders
className="border-border"

// Emphasized borders
className="border-primary"

// Focus states
className="focus:ring-primary"

// Domain-specific borders
className="status-active-border"  // Uses --color-info
className="status-complete-border"  // Uses --color-success
className="status-error-border"  // Uses --color-error
```

### React Flow Nodes

For React Flow nodes that require inline styles:

```tsx
// Using CSS custom properties with fallbacks
style={{
  backgroundColor: 'var(--color-surface-primary, hsl(var(--color-primary) / 0.1))',
  borderColor: 'var(--color-node-brain-border, var(--primary))',
}}

// Using domain-specific tokens
style={{
  stroke: 'var(--color-brain-active, #64FFDA)',
  filter: 'drop-shadow(0 0 6px var(--color-brain-active, #64FFDA))',
}}
```

**Always provide fallback values** for inline styles to ensure graceful degradation.

## Theme Switching

### Light Mode

Activated by removing the `.dark` class from the `<html>` element:

```tsx
document.documentElement.classList.remove('dark')
```

### Dark Mode

Activated by adding the `.dark` class to the `<html>` element:

```tsx
document.documentElement.classList.add('dark')
```

All components automatically adapt without code changes. The theme toggle is handled by `ThemeProvider.tsx` and `ThemeToggle.tsx`.

## Adding New Tokens

### 1. Define Token in globals.css

Add your token to both `:root` and `.dark` selectors:

```css
:root {
  --color-your-token: oklch(0.5 0.1 200);
}

.dark {
  --color-your-token: oklch(0.6 0.1 200);
}
```

### 2. Create Semantic Alias (Optional)

For better semantic clarity:

```css
:root {
  --color-semantic-alias: var(--color-your-token);
}
```

### 3. Use in Components

Via Tailwind utility:

```tsx
className="bg-[var(--color-your-token)]"
```

Or via CSS custom property:

```tsx
style={{ color: 'var(--color-semantic-alias)' }}
```

## Token Files

| File | Purpose |
|------|---------|
| `apps/web/src/app/globals.css` | Token definitions |
| `apps/web/src/components/ThemeProvider.tsx` | Theme provider component |
| `apps/web/src/components/ThemeToggle.tsx` | Theme toggle component |

## Color Philosophy

### OKLCH Color Space

We use OKLCH for all color definitions because it:

- Provides perceptual uniformity
- Enables consistent lightness adjustments
- Supports wide gamut colors
- Offers better hue consistency than HSL

### Color Adjustments

The `oklch()` function allows for sophisticated color manipulation:

```css
/* Lighten a color while preserving chroma and hue */
background-color: oklch(from var(--color-info) c l 0.95);

/* Darken a color while preserving chroma and hue */
background-color: oklch(from var(--color-info) c l 0.15);
```

This technique is used extensively in status-based backgrounds to create consistent hover and active states.

## Accessibility

### Contrast Ratios

All text color combinations meet WCAG AA standards (4.5:1 for normal text, 3:1 for large text).

### Motion Preferences

All animations respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  .animate-shake,
  .animate-pulse {
    animation: none;
  }
}
```

### Semantic Color Pairing

Colors are always paired with icons or text labels to ensure state communication is not color-dependent:

```tsx
<span className={cn(base, 'nexus-text-complete')}>
  <CheckCircle2 className="size-3" aria-hidden="true" />
  <span>Complete</span>
</span>
```

## Related Documentation

- [Phase A2: Design Token System Implementation](../../../../../.planning/phase-A2-design-tokens/README.md)
- [Phase B1: Flow Designer Theming](../../../../../.planning/phase-B1-flow-designer/README.md)
- [Phase D1: All Screens Theme-Aware](../../../../../.planning/phase-D1-theme-aware/README.md)
- [Theme Verification Checklist](./THEME_VERIFICATION_CHECKLIST.md)

## Maintenance

When updating tokens:

1. Update both `:root` and `.dark` selectors
2. Test in both light and dark modes
3. Verify contrast ratios
4. Update this documentation
5. Run visual regression tests
