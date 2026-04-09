# Brain #3 (UI Design) — Phase 17 Consultation

> **Phase:** 17 — UI Evolution
> **Date:** 2026-04-08
> **Expertise:** Component architecture, design systems, atomic design, OKLCH color system, 5-state components, accessibility (WCAG 2.1 AA)

---

## Verified Insights

**From existing codebase + BRAIN-FEED-03:**
- shadcn/ui (Nova preset) already installed — button, input, sheet, dialog, card available
- OKLCH color system implemented in globals.css — WCAG 2.1 AA compliant
- 5-state system defined in BRAIN-FEED-03 — Default, Hover, Active, Disabled, Error/Loading
- Dark mode: #121212 background (NEVER #000000 → OLED smearing)
- Motion max: 300ms for transitions (>300ms = "heavy" feel)
- React Compiler DISABLED — conflicts with React.memo on React Flow nodes
- Missing shadcn components: `tabs`, `progress` (need `pnpm dlx shadcn add tabs progress`)
- Grid system: 12-column + 4/8px spacing scale (defined in BRAIN-FEED-03)
- Typography scale: math-based ratio 1.25 (defined in BRAIN-FEED-03)

---

## Component Architecture

### UIE-01 (Three-Column Layout)

**Component Hierarchy (Atomic Design):**
```
Template: ThreeColumnLayout
  ├─ Organism: CompanyRail (left column)
  │   ├─ Molecule: CompanyTile (repeated)
  │   │   ├─ Atom: CompanyIcon
  │   │   ├─ Atom: CompanyName
  │   │   └─ Atom: StatusBadge
  │   └─ Molecule: AddCompanyButton
  ├─ Organism: AppSidebar (center column)
  │   ├─ Molecule: NavItem (repeated)
  │   │   ├─ Atom: NavIcon
  │   │   └─ Atom: NavLabel
  │   └─ Molecule: CollapseButton
  └─ Template: ContentArea (right column)
      ├─ Organism: PropertiesPanel (conditional overlay)
      └─ Atom: PageContent (children)
```

**Component Specifications:**

#### 1. ThreeColumnLayout (Template)
```tsx
// apps/web/src/components/layout/ThreeColumnLayout.tsx
"use client"

interface Props {
  children: ReactNode
  showPropertiesPanel?: boolean
}

// Layout: CSS Grid with 3 columns
// Desktop: grid-cols-[auto_1fr] → [CompanyRail Sidebar Content]
// Mobile: grid-cols-1 → single column
```

**5-State System:**
- **Default:** All columns expanded (180px + 240px + auto)
- **Hover:** Hover effects on CompanyRail/Sidebar items (not on layout itself)
- **Active:** N/A (layout is structural, not interactive)
- **Disabled:** N/A (layout always interactive)
- **Error/Loading:** Skeleton loading state for each column

**CSS Variables (globals.css):**
```css
:root {
  --company-rail-width: 180px;
  --company-rail-width-collapsed: 60px;
  --sidebar-width: 240px;
  --sidebar-width-collapsed: 60px;
  --transition-duration: 200ms; /* Max for usability, not "animation" */
}

@media (max-width: 768px) {
  :root {
    --company-rail-width: 0px; /* Hidden on mobile */
    --sidebar-width: 0px; /* Hidden on mobile */
  }
}
```

#### 2. CompanyRail (Organism)
```tsx
// apps/web/src/components/layout/CompanyRail.tsx
"use client"

interface Company {
  id: string
  name: string
  icon: string
  liveAgents: number
  unreadCount: number
}

interface Props {
  companies: Company[]
  activeCompanyId: string
  onSelectCompany: (id: string) => void
}

// Fixed width: var(--company-rail-width)
// Collapsed width: var(--company-rail-width-collapsed)
// Drag handle for future reordering (Plan 02)
```

**5-State System:**
- **Default:** Gray background, border-right
- **Hover:** Darker background (tonal elevation +1)
- **Active:** Selected company highlighted with border-left
- **Disabled:** N/A (companies always selectable)
- **Error/Loading:** Skeleton state while loading companies

**Tonal Elevation (dark mode):**
```css
/* globals.css */
--elevation-0: rgba(255, 255, 255, 0.00); /* Surface */
--elevation-1: rgba(255, 255, 255, 0.05); /* Hover */
--elevation-2: rgba(255, 255, 255, 0.10); /* Active/Focus */
--elevation-3: rgba(255, 255, 255, 0.15); /* Modal/Sheet */
```

#### 3. AppSidebar (Organism)
```tsx
// apps/web/src/components/layout/AppSidebar.tsx
"use client"

interface NavItem {
  id: string
  label: string
  icon: LucideIcon
  href: string
}

interface Props {
  items: NavItem[]
  activePath: string
}

// Fixed width: var(--sidebar-width)
// Collapsed width: var(--sidebar-width-collapsed)
// Active state highlighting via usePathname()
```

**5-State System:**
- **Default:** Transparent background, border-right
- **Hover:** Tonal elevation +1, icon color shift
- **Active:** Selected item highlighted with bg-muted
- **Disabled:** N/A (nav items always accessible)
- **Error/Loading:** N/A (nav items don't have error state)

#### 4. PropertiesPanel (Organism)
```tsx
// apps/web/src/components/layout/PropertiesPanel.tsx
"use client"

interface Props {
  isOpen: boolean
  onClose: () => void
  children: ReactNode
}

// Conditional overlay on right side
// Width: 320px (desktop), full-width (mobile)
// Uses shadcn Sheet component (already installed)
```

**5-State System:**
- **Default:** Closed (hidden)
- **Hover:** N/A (panel is modal, not hoverable)
- **Active:** Open (visible)
- **Disabled:** N/A (panel always interactive when open)
- **Error/Loading:** Skeleton state while loading content

---

### UIE-02 (Real-time Agent Monitoring)

**Component Hierarchy:**
```
Organism: ActiveAgentsPanel
  ├─ Molecule: DensityModeSelector (compact/normal/detailed)
  ├─ Organism: CompactView (grid, 24 brains)
  │   └─ Molecule: BrainCard (repeated)
  │       ├─ Atom: BrainName
  │       ├─ Atom: StatusBadge
  │       └─ Atom: PingAnimation
  ├─ Organism: NormalView (cards, 12 brains)
  │   └─ Molecule: BrainCard (expanded)
  │       ├─ Atom: BrainName
  │       ├─ Atom: StatusBadge
  │       ├─ Atom: LastResult
  │       └─ Atom: Duration
  └─ Organism: DetailedView (single brain)
      └─ Molecule: BrainDetailView
          ├─ Atom: Transcript
          ├─ Atom: CostBreakdown
          └─ Atom: Metrics
```

**Component Specifications:**

#### 1. ActiveAgentsPanel (Organism)
```tsx
// apps/web/src/components/monitoring/ActiveAgentsPanel.tsx
"use client"

type DensityMode = 'compact' | 'normal' | 'detailed'

interface Props {
  brains: Brain[]
  densityMode: DensityMode
  onDensityChange: (mode: DensityMode) => void
}

// Layout: Grid with responsive columns
// Compact: 4-6 columns (desktop), 2 columns (mobile)
// Normal: 2-3 columns (desktop), 1 column (mobile)
// Detailed: 1 column (full-screen or modal)
```

#### 2. StatusBadge (Atom)
```tsx
// apps/web/src/components/ui/StatusBadge.tsx
"use client"

type BrainStatus = 'idle' | 'running' | 'completed' | 'failed' | 'routing'

interface Props {
  status: BrainStatus
}

// 5-State System:
// - Default: Gray (idle)
// - Hover: N/A (status is read-only)
// - Active: N/A (status is read-only)
// - Disabled: N/A (status always visible)
// - Error/Loading: Each status has its own visual

// Color semantics (OKLCH):
const statusColors = {
  idle: 'oklch(var(--color-muted-foreground))',      // Gray
  running: 'oklch(var(--color-primary))',             // Blue
  completed: 'oklch(var(--color-success))',           // Green
  failed: 'oklch(var(--color-error))',                // Red
  routing: 'oklch(var(--color-warning))',             // Amber
}
```

**WCAG 2.1 AA Compliance:**
- Icon + text label (triple redundancy for 8% daltonism users)
- Contrast ratio ≥ 4.5:1 (OKLCH auto-complies)
- `aria-label` for screen readers

#### 3. PingAnimation (Atom)
```tsx
// apps/web/src/components/ui/PingAnimation.tsx
"use client"

interface Props {
  isActive: boolean
}

// Reuse animate-ping from BrainTile.tsx line 65
// Timing: 1000ms (1 second) → matches existing implementation
// Easing: ease-out (physically inspired)
// Accessibility: @media (prefers-reduced-motion: reduce) disables animation
```

**Animation Specs:**
```css
/* globals.css */
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
  .animate-ping {
    animation: none;
  }
}
```

---

### UIE-03 (Cost Dashboard)

**Component Hierarchy:**
```
Organism: CostDashboard
  ├─ Molecule: QuotaBar (progress visualization)
  ├─ Molecule: MetricCard (repeated)
  │   ├─ Atom: MetricLabel
  │   ├─ Atom: MetricValue
  │   └─ Atom: MetricTrend
  └─ Molecule: CostBreakdown
      └─ Atom: CostItem (repeated)
          ├─ Atom: CostLabel
          └─ Atom: CostValue
```

**Component Specifications:**

#### 1. MetricCard (Molecule)
```tsx
// apps/web/src/components/cost/MetricCard.tsx
"use client"

interface Props {
  label: string
  value: string | number
  trend?: 'up' | 'down' | 'neutral'
  unit?: string
}

// 5-State System:
// - Default: Surface background, border
// - Hover: Tonal elevation +1
// - Active: N/A (metric is read-only)
// - Disabled: N/A (metric always visible)
// - Error/Loading: Skeleton state while loading

// Size: 200px width × 120px height (compact card)
// Layout: Flex column (label → value → trend)
```

**5-State Implementation:**
```tsx
const cardVariants = {
  default: "bg-[var(--color-surface)] border-[var(--color-outline)]",
  hover: "bg-[var(--color-surface-hover)] shadow-sm",
  active: "", // N/A
  disabled: "", // N/A
  loading: "animate-pulse bg-[var(--color-muted)]",
}
```

#### 2. QuotaBar (Molecule)
```tsx
// apps/web/src/components/cost/QuotaBar.tsx
"use client"

interface Props {
  current: number
  total: number
  threshold?: number // Warning threshold (default: 0.8 = 80%)
}

// 5-State System:
// - Default: Green gradient (within budget)
// - Hover: Show tooltip with exact values
// - Active: N/A (progress is read-only)
// - Disabled: N/A (progress always visible)
// - Error: Red gradient (over budget)

// Visual: Horizontal bar with color gradient
// Height: 8px (compact), 16px (detailed)
// Border radius: 4px (pill shape)
```

**Color Semantics:**
```css
/* globals.css */
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

---

## 5-State System

**Application to All Components:**

| Component | Default | Hover | Active | Disabled | Error/Loading |
|-----------|---------|-------|--------|----------|---------------|
| **ThreeColumnLayout** | Expanded | N/A | N/A | N/A | Skeleton |
| **CompanyRail** | Gray bg | Elev+1 | Selected | N/A | Skeleton |
| **AppSidebar** | Transparent | Elev+1 | Highlight | N/A | N/A |
| **PropertiesPanel** | Closed | N/A | Open | N/A | Skeleton |
| **ActiveAgentsPanel** | Grid | N/A | N/A | N/A | Skeleton |
| **StatusBadge** | Gray | N/A | N/A | N/A | Each status |
| **PingAnimation** | Hidden | N/A | Ping | N/A | N/A |
| **MetricCard** | Surface | Elev+1 | N/A | N/A | Skeleton |
| **QuotaBar** | Green | Tooltip | N/A | N/A | Red |

**Tonal Elevation Implementation:**
```css
/* globals.css */
.elevation-0 { background: var(--elevation-0); }
.elevation-1 { background: var(--elevation-1); }
.elevation-2 { background: var(--elevation-2); }
.elevation-3 { background: var(--elevation-3); }
```

---

## Animation Specs

**Approved Animations (with timing + easing):**

| Animation | Purpose | Duration | Easing | Accessibility |
|-----------|---------|----------|--------|---------------|
| **Ping** | Orientation (status updates) | 1000ms | cubic-bezier(0,0,0.2,1) | @media prefers-reduced-motion |
| **Status badge transition** | Feedback (state change) | 200ms | ease-out | @media prefers-reduced-motion |
| **QuotaBar fill** | Feedback (progress) | 300ms | ease-in-out | @media prefers-reduced-motion |
| **Panel slide-in** | Orientation (PropertiesPanel) | 250ms | ease-out | @media prefers-reduced-motion |

**Rejected Animations:**
- Layout collapse/expand (ICE Score 6.7 < 15) — Use instant CSS transition
- Company rail reordering (ICE Score 8 < 15) — Use instant move

**Animation Invariants:**
- NEVER linear easing — always physically inspired
- Max duration: 300ms (>300ms = "heavy" feel)
- Always respect `prefers-reduced-motion`

---

## Anti-patterns to Avoid

### UI Violations (AC-09 placeholder-only labels):
```tsx
// ❌ WRONG (AC-09 violation)
<Input placeholder="Company name" />

// ✅ CORRECT
<Label>Company name</Label>
<Input />
```

### UI Violations (color-only states):
```tsx
// ❌ WRONG (8% daltonism users can't distinguish)
<div className={status === 'error' ? 'bg-red-500' : 'bg-green-500'} />

// ✅ CORRECT (triple redundancy)
<div className={status === 'error' ? 'bg-red-500' : 'bg-green-500'}>
  {status === 'error' && <AlertCircle aria-label="Error" />}
  <span>{status === 'error' ? 'Failed' : 'Success'}</span>
</div>
```

### UI Violations (hardcoded hex values):
```css
/* ❌ WRONG */
.brain-card { background: #1e1e1e; }

/* ✅ CORRECT */
.brain-card { background: oklch(var(--color-surface)); }
```

### UI Violations (wrong background color):
```css
/* ❌ WRONG (OLED smearing) */
body { background: #000000; }

/* ✅ CORRECT */
body { background: #121212; }
```

---

## Accessibility Checklist

**WCAG 2.1 AA Requirements:**

### Perceivable:
- ✅ Color contrast ≥ 4.5:1 (OKLCH auto-complies)
- ✅ Icon + text label for all status indicators (8% daltonism)
- ✅ No color-only information (triple redundancy)

### Operable:
- ✅ Keyboard navigation (Tab/Enter for all interactive elements)
- ✅ Focus-visible ring with 3:1 contrast minimum
- ✅ No keyboard traps (modals have focus trap)

### Understandable:
- ✅ Consistent navigation (same 4 items across desktop/mobile)
- ✅ Clear labels (no placeholder-only labels)
- ✅ Error messages explain what went wrong + how to fix

### Robust:
- ✅ ARIA labels for screen readers
- ✅ Semantic HTML (nav, main, aside, header)
- ✅ Role attributes for custom components

**Specific Component Checks:**
- [ ] CompanyRail — aria-label="Company switcher"
- [ ] AppSidebar — aria-label="Main navigation"
- [ ] StatusBadge — aria-label="Brain status: {status}"
- [ ] MetricCard — aria-label="{label}: {value}"
- [ ] QuotaBar — role="progressbar", aria-valuenow={current}, aria-valuemax={total}

---

## Open Questions Answered

### Q1: DnD library — @dnd-kit for company rail or custom?

**Answer:** USE @dnd-kit (don't build custom)

**Rationale:**
1. **Proven library** — Paperclip uses @dnd-kit, battle-tested
2. **Accessibility built-in** — Keyboard drag-drop, screen reader support
3. **Performance optimized** — Uses React refs, not context (avoids re-renders)
4. **TypeScript support** — Full type safety
5. **Maintenance burden** — Custom DnD = ongoing maintenance cost

**Implementation:**
```bash
pnpm add @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
```

**Component:**
```tsx
// apps/web/src/components/layout/CompanyRail.tsx
import { DndContext, closestCenter } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';

// Wrap CompanyTile list with DndContext
// Use SortableContext for vertical list sorting
// Handle onDragEnd to update company order in layoutStore
```

**Performance Consideration:**
- Use `useSensor(PointerSensor)` for mouse drag-drop
- Use `useSensor(KeyboardSensor)` for keyboard drag-drop (accessibility)
- Debounce localStorage updates during drag (don't write on every pixel)

### Q5: Mobile bottom nav — Which sections to include?

**Answer:** 4 items (matching Brain #2 UX response):

1. **Command Center** — Icon: Target (🎯)
2. **The Nexus** — Icon: Network (🕸️)
3. **Strategy Vault** — Icon: Scroll (📜)
4. **Engine Room** — Icon: Settings (⚙️)

**Component:**
```tsx
// apps/web/src/components/layout/MobileBottomNav.tsx
"use client"

import { usePathname } from 'next/navigation'

const navItems = [
  { id: 'command-center', label: 'Center', icon: Target, href: '/command-center' },
  { id: 'nexus', label: 'Nexus', icon: Network, href: '/nexus' },
  { id: 'vault', label: 'Vault', icon: Scroll, href: '/vault' },
  { id: 'engine-room', label: 'Engine', icon: Settings, href: '/engine-room' },
]

// Render bottom nav with 4 items
// Active item highlighted with bg-muted
// Touch targets: 44x44px minimum (WCAG 2.1 AA)
// Fixed position: bottom-0 left-0 right-0
```

**5-State System:**
- **Default:** Transparent background, border-top
- **Hover:** Tonal elevation +1 (on tap)
- **Active:** Selected item highlighted with bg-muted
- **Disabled:** N/A (all items always accessible)
- **Error/Loading:** N/A (nav items don't have error state)

---

## Summary

**Key Decisions:**
1. **Three-column layout:** CSS Grid with 3 columns, responsive breakpoints
2. **5-state system:** Applied to ALL interactive components
3. **Dark mode:** #121212 background (NEVER #000000)
4. **DnD library:** @dnd-kit (not custom)
5. **Mobile bottom nav:** 4 items (matches desktop navigation)
6. **Animation max:** 300ms (platform feels "heavy" beyond this)
7. **Accessibility:** WCAG 2.1 AA compliance (color contrast, ARIA labels, keyboard nav)

**Next Steps:**
- Brain #4 (Frontend) — State management + WebSocket integration
- Brain #6 (QA) — Testing strategy + performance SLOs

---

*Brain #3 consultation complete — 2026-04-08*
