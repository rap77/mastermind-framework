# Phase 17 — CONTEXT (Brain-Informed Planning)

> **Phase:** 17 — UI Evolution
> **Generated:** 2026-04-08
> **Status:** Ready for planning
> **Brain consultation:** COMPLETE — 4 domain brains + 1 evaluator consulted

---

## Phase Goal

Extract 10 UX patterns from Paperclip and rebuild them in Next.js 16 App Router for MasterMind v3.0 enterprise platform.

**Key Constraint:** NOT a fork — Paperclip uses Vite + React Router (incompatible with Next.js). Extract patterns only, rebuild from scratch.

---

## Brain-Informed Success Criteria

From 17-BRAIN-OUTPUTS.md + Brain #7 evaluation (88/100 score):

1. **Three-column layout** (UIE-01) — CompanyRail + Sidebar + Content with multi-tenant switcher, responsive mobile (swipe gestures, bottom nav), **88/100 feasibility**

2. **Real-time agent monitoring** (UIE-02) — ActiveAgentsPanel with density modes (compact/normal/detailed), ping animation (ICE 20), status badges, **85/100 feasibility**

3. **Cost dashboard** (UIE-03) — MetricCard + QuotaBar patterns, Rust event sourcing data, WebSocket updates, **92/100 feasibility**

**Overall Phase 17 Success Probability:** 90%

---

## Requirements from ROADMAP

| ID | Requirement | Status | Feasibility |
|----|-------------|--------|-------------|
| UIE-01 | Three-column layout with multi-tenant switcher | Pending | 95% |
| UIE-02 | Real-time agent monitoring panel with density modes | Pending | 85% |
| UIE-03 | Orchestration canvas with cost dashboard | Pending | 92% |

---

## Technical Context (Brain-Informed)

### Stack (Locked from BRAIN-FEED files)

| Layer | Library | Version | Notes |
|-------|---------|---------|-------|
| Framework | Next.js | 16.x | App Router, no Pages |
| UI | React | 19.x | Compiler DISABLED (conflicts with React.memo on RF nodes) |
| Language | TypeScript | 5.x | strict mode |
| Styling | Tailwind CSS | 4.x | CSS-only config, no tailwind.config.js |
| Components | shadcn/ui | Nova preset | OKLCH color system, base-ui |
| State | Zustand | 5.x | + Immer middleware |
| Query | TanStack Query | v5 | staleTime: 30s default |
| Graph | @xyflow/react | v12 | React Flow v12 |
| Drag-drop | @dnd-kit | latest | NEW for Phase 17 (company rail reordering) |
| Auth | jose | latest | Edge Runtime compatible |
| Package mgr | pnpm | — | Never npm/yarn |

### New State Management (Phase 17)

**3 Zustand Stores:**
1. **layoutStore** — Layout state (companyRailCollapsed, sidebarCollapsed, densityMode)
2. **brainStore (extended)** — Existing + monitoring state (filteredBrains, densityMode)
3. **costStore** — Cost metrics (totalCost, budgetRemaining, costPerBrain, projectedOverage)

**WebSocket Integration (NEW):**
- `agent_status_update` — Real-time brain status changes
- `brain_cost_update` — Real-time cost metric updates

### What Exists (Prevent Re-inventing)

**4 Production Screens:**
- Command Center — BentoGrid 24 tiles, BrainTile ping animation
- The Nexus — React Flow DAG, WebSocket illumination
- Strategy Vault — Execution history, Markdown rendering
- Engine Room — API keys, brain YAML viewer

**Infrastructure:**
- WebSocket: wsDispatcher.ts singleton + brainStore RAF batching
- Auth: Server Actions + httpOnly cookies + JWT
- Components: shadcn/ui (button, input, sheet, dialog, card)
- Testing: Vitest (407 tests), pytest (631 tests)

---

## Architecture Decisions (Brain-Validated)

### Layout Architecture (Brain #2 UX + Brain #3 UI)

**Three-Column Layout (NEW):**
```
┌─────────────┬─────────────────┬──────────────────────────┐
│ CompanyRail │    Sidebar      │       Content Area       │
│ (180px)     │    (240px)      │       (flex-fill)        │
│             │                 │                          │
│ PURPOSE:    │ PURPOSE:        │ PURPOSE:                 │
│ Multi-tenant │ Navigation      │ Page content +           │
│ context      │ (4 screens)     │ Properties panel         │
│             │                 │                          │
│ CHUNKS:     │ CHUNKS:         │ CHUNKS:                  │
│ - Company   │ - Command       │ - Dynamic (varies)       │
│   list      │   Center (1)    │ - Progressive disclosure │
│   (max 7)   │ - Nexus (1)     │ - Miller's Law: 7±2      │
│ - Add btn   │ - Vault (1)     │                          │
│             │ - Engine (1)    │                          │
└─────────────┴─────────────────┴──────────────────────────┘
```

**Mobile (Single Column):**
- Bottom nav: 4 items (Command Center, Nexus, Vault, Engine Room)
- Swipe gestures: Horizontal swipe to switch screens
- Full-screen content: Back button for navigation depth

**ICE Score for layout transitions:** 6.7 (BELOW 15 threshold) → Instant CSS transition (200ms max)

### Component Architecture (Brain #3 UI)

**New Layout Components:**
- `CompanyRail` — Left column, @dnd-kit reordering, max 7 companies
- `AppSidebar` — Center column, 4 nav items, active state highlighting
- `ThreeColumnLayout` — Wraps protected routes, CSS Grid layout
- `PropertiesPanel` — Right overlay, Sheet component (conditional)

**New Feature Components:**
- `ActiveAgentsPanel` — Real-time monitoring, density modes (compact/normal/detailed)
- `StatusBadge` — 5-state system (idle/running/completed/failed/routing)
- `PingAnimation` — Reuse BrainTile ping (ICE 20, APPROVED)
- `MetricCard` — Cost dashboard molecule (atomic design)
- `QuotaBar` — Budget progress visualization (color gradient)

### State Management (Brain #4 Frontend)

**layoutStore:**
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
```

**costStore:**
```typescript
interface CostMetrics {
  totalCost: number
  budgetRemaining: number
  budgetTotal: number
  costPerBrain: Map<string, number>
  projectedOverage: boolean
}
```

**Performance Invariants (CRITICAL):**
- RAF batching preserved (60fps at 24-brain burst)
- Targeted selectors (useLayoutStore((s) => s.companyRailCollapsed))
- WS updates touch only `data` prop (never positions, never topology)

### Design System (Brain #3 UI)

**5-State System (ALL interactive components):**
- Default — Base state
- Hover — Tonal elevation +1
- Active — Selected/focused
- Disabled — Grayed out, non-interactive
- Error/Loading — Skeleton or error state

**Color Semantics (OKLCH):**
```css
--color-quota-success: oklch(0.65 0.15 150); /* Green */
--color-quota-warning: oklch(0.70 0.12 80);  /* Amber */
--color-quota-error: oklch(0.65 0.15 25);    /* Red */

--elevation-0: rgba(255, 255, 255, 0.00); /* Surface */
--elevation-1: rgba(255, 255, 255, 0.05); /* Hover */
--elevation-2: rgba(255, 255, 255, 0.10); /* Active */
--elevation-3: rgba(255, 255, 255, 0.15); /* Modal */
```

**Typography Scale:**
- Ratio: 1.25 (math-based)
- Levels: h1 (48px), h2 (38px), h3 (31px), body (16px), small (13px)

**Animation Specs:**
| Animation | Purpose | Duration | Easing |
|-----------|---------|----------|--------|
| Ping | Orientation | 1000ms | cubic-bezier(0,0,0.2,1) |
| Status badge | Feedback | 200ms | ease-out |
| QuotaBar fill | Feedback | 300ms | ease-in-out |
| Panel slide-in | Orientation | 250ms | ease-out |

---

## 10 UX Patterns from Paperclip (Priority Order)

### Wave 1: Foundation (Plans 17-01, 17-02)
1. ✅ **Three-Column Layout** — CompanyRail + Sidebar + Content + Properties panel
3. ✅ **Company-as-Context** — Draggable ordering (@dnd-kit), status indicators, localStorage sync

### Wave 2: Real-time Monitoring (Plans 17-03, 17-04)
2. ✅ **Real-time Agent Monitoring** — ActiveAgentsPanel, ping animation, density modes
5. ✅ **Cost Dashboard** — MetricCard, QuotaBar, Rust event sourcing

### Wave 3: Advanced Features (Plans 17-05, 17-06)
7. ✅ **Command Palette** — Cmd+K, global search, 4 categories
9. ✅ **Onboarding Wizard** — Progressive setup, 5-step flow, skip allowed

### Deferred (Phase 18+):
4. Agent Configuration Form — Dirty tracking, template gallery
6. Kanban Board — @dnd-kit drag-drop, multi-column workflow
8. Run Transcript — Multi-density, streaming updates
10. Org Chart — SVG-based, ReportsToPicker

---

## Implementation Priority

### Wave 1: Foundation (Plans 17-01, 17-02)
- Plan 17-01: Three-column layout foundation (CompanyRail + Sidebar + Content)
- Plan 17-02: Multi-tenant company switcher with @dnd-kit reordering

### Wave 2: Real-time Monitoring (Plans 17-03, 17-04)
- Plan 17-03: ActiveAgentsPanel with density modes + status badges
- Plan 17-04: Cost dashboard with MetricCard + QuotaBar

### Wave 3: Advanced Features (Plans 17-05, 17-06)
- Plan 17-05: Command palette (Cmd+K) with global search
- Plan 17-06: Onboarding wizard + responsive mobile polish

---

## Testing Strategy (Brain #6 QA)

### Test Coverage Targets:
- **Frontend (Vitest):** +50 tests (457 total, baseline 407)
- **Backend (pytest):** +10 tests (641 total, baseline 631)
- **E2E (Playwright):** +5 tests (baseline 0, new for Phase 17)

### Performance SLOs:
| Metric | Target | Measurement |
|--------|--------|-------------|
| 24-brain burst render | 60fps (16.67ms) | RAF batching |
| Time-to-first-render | < 100ms | Performance API |
| Layout state persistence | < 10ms | localStorage |
| Cost metrics fetch | < 200ms P99 | API response time |

### Testing Layers:
1. **Unit Tests** — Component rendering, store logic
2. **Integration Tests** — WebSocket events, responsive breakpoints
3. **Visual Regression** — Screenshot comparison (Playwright)
4. **Performance Tests** — 24-brain burst, RAF validation
5. **E2E Tests** — Full user flows (mobile + desktop)

---

## Accessibility Requirements (Brain #3 UI)

- ✅ Keyboard navigation — All interactive elements keyboard-accessible
- ✅ Screen reader support — ARIA labels on all components
- ✅ Focus management — Focus trap in modals, proper focus order
- ✅ prefers-reduced-motion — Respect system preference
- ✅ Color contrast — OKLCH auto-complies (WCAG 2.1 AA)
- ✅ Touch targets — 44x44px minimum (mobile)
- ✅ Triple redundancy — Icon + text + color for status indicators

---

## Anti-patterns to Avoid (Brain-Validated)

- ❌ **Forking Paperclip** — Architecture mismatch (Vite vs Next.js)
- ❌ **Ignoring RAF batching** — Will break 60fps at 24-brain burst
- ❌ **Breaking WebSocket infrastructure** — Must preserve wsDispatcher.ts
- ❌ **Hardcoded company context** — Must support multi-tenant switching
- ❌ **Desktop-only design** — Mobile responsiveness required
- ❌ **Ignoring accessibility** — WCAG 2.1 AA compliance mandatory
- ❌ **Inline NODE_TYPES** — Always module level (React Flow constraint)
- ❌ **useStore() cascade** — Use targeted selectors (Zustand pattern)
- ❌ **#000000 background** — Use #121212 (OLED smearing)
- ❌ **Motion > 300ms** — Platform feels "heavy" beyond this

---

## Open Questions (ALL RESOLVED)

| Question | Answer | Confidence | Brain Source |
|----------|--------|------------|--------------|
| Q1: DnD library? | @dnd-kit (not custom) | HIGH (95%) | Brain #3 UI, Brain #4 Frontend |
| Q2: Cost data source? | Rust event sourcing (activity_log) | HIGH (90%) | Brain #4 Frontend |
| Q3: Command palette scope? | 4 categories (navigation, brains, companies, settings) | MEDIUM (75%) | Brain #4 Frontend |
| Q4: Onboarding skip? | YES, with trade-offs (5min minimal vs 15min full) | HIGH (85%) | Brain #2 UX |
| Q5: Mobile bottom nav? | 4 items (Command Center, Nexus, Vault, Engine Room) | HIGH (90%) | Brain #2 UX, Brain #3 UI |

---

## Dependencies

- ✅ **Phase 16 (Observability + Real-time Hub)** — COMPLETE (Ghost Mode replay, WebSocket Hub)
- ✅ **Phase 15 (Rust Control Plane)** — COMPLETE (PostgreSQL, event sourcing)
- ✅ **Phase 13 (Vertical Slice)** — COMPLETE (gRPC + Protobuf contracts)

---

## Risks and Mitigations (Brain #7 Assessment)

### High Risks (require mitigation):
1. **WebSocket scalability (24-brain burst)** — Load test with 24 simultaneous events
2. **Mobile responsiveness (desktop-first legacy)** — Mobile-first testing with device farm

### Medium Risks (monitor but don't block):
1. **Performance regression (new stores)** — React DevTools profiling
2. **Visual regression (layout changes)** — Screenshot baseline before implementation

### Low Risks (accept and document):
1. **Accessibility compliance (WCAG 2.1 AA)** — Screen reader testing before release

---

## Conditions for Approval (Brain #7)

1. **Mobile testing plan** — Specify device farm strategy before execution
2. **RAF validation** — Measure 60fps at 24-brain burst during implementation
3. **Visual baseline** — Establish screenshot baseline before layout changes
4. **Accessibility audit** — Verify WCAG 2.1 AA with screen reader before release

---

## Next Steps

1. ✅ **CONTEXT.md updated** — This file (brain-informed decisions)
2. ✅ **BRAIN-OUTPUTS.md created** — 4 domain brains + 1 evaluator
3. ⏭️ **Invoke `/mm:plan-phase 17`** — Create 6 PLAN.md files with GSD skill
4. ⏭️ **Execute Phase 17** — `/mm:execute-phase 17`

---

**Context updated:** 2026-04-08
**Brain consultation:** COMPLETE (4 domain brains + 1 evaluator)
**Readiness:** APPROVED WITH CONDITIONS (88/100 score)
**Next action:** `/mm:plan-phase 17`
