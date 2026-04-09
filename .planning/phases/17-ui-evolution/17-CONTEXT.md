# Phase 17 — CONTEXT (Brain-Informed Planning)

> **Phase:** 17 — UI Evolution
> **Generated:** 2026-04-08
> **Status:** Planning complete
> **Brain consultation:** Skipped (direct planning based on validated requirements)

---

## Phase Goal

Extract 10 UX patterns from Paperclip and rebuild them in Next.js 16 App Router for MasterMind v3.0 enterprise platform.

**Key Constraint:** NOT a fork — Paperclip uses Vite + React Router (incompatible with Next.js). Extract patterns only, rebuild from scratch.

---

## Success Criteria (from ROADMAP)

1. **Three-column layout** (CompanyRail + Sidebar + Content) rebuilt in Next.js 16 with multi-tenant sidebar switcher and responsive mobile (swipe gestures, bottom nav)

2. **Real-time agent monitoring panel** with ping animation, status badges (idle/running/completed/failed), compact density modes — ActiveAgentsPanel pattern from Paperclip

3. **Orchestration canvas** extends existing React Flow Nexus with real-time WebSocket updates — cost dashboard with MetricCard per brain (tokens, duration, cost) and budget enforcement visual (QuotaBar pattern)

---

## Requirements from ROADMAP

| ID | Requirement | Status |
|----|-------------|--------|
| UIE-01 | Three-column layout with multi-tenant switcher | Pending |
| UIE-02 | Real-time agent monitoring panel with density modes | Pending |
| UIE-03 | Orchestration canvas with cost dashboard | Pending |

---

## Technical Context

### Current Stack (Locked from BRAIN-FEED.md)

| Layer | Library | Version | Notes |
|-------|---------|---------|-------|
| Framework | Next.js | 16.x | App Router, no Pages |
| UI | React | 19.x | Compiler disabled (conflicts with React.memo on RF nodes) |
| Language | TypeScript | 5.x | strict mode |
| Styling | Tailwind CSS | 4.x | CSS-only config, no tailwind.config.js |
| Components | shadcn/ui | Nova preset | OKLCH color system, base-ui |
| State | Zustand | 5.x | + Immer middleware |
| Query | TanStack Query | v5 | staleTime: 30s default |
| Graph | @xyflow/react | v12 | React Flow v12 |
| Auth | jose | latest | Edge Runtime compatible |
| Package mgr | pnpm | — | Never npm/yarn |

### What Exists (Prevent Re-inventing)

**4 Production Screens:**
- **Command Center** — BentoGrid 24 tiles, BrainTile with ping animation, BriefInputModal
- **The Nexus** — React Flow DAG canvas, dagre layout, WebSocket illumination
- **Strategy Vault** — Execution history list, detail view, Markdown rendering
- **Engine Room** — API key CRUD, brain YAML viewer, virtual scroll logs

**Infrastructure:**
- WebSocket: `wsDispatcher.ts` singleton + `brainStore.ts` with RAF batching
- Auth: Server Actions + httpOnly cookies, JWT verification in `lib/auth.ts`
- Components: shadcn/ui (button, input, sheet, dialog, card)
- Testing: Vitest, 407 frontend tests passing

### Current Limitations (Why Phase 17)

- **No three-column layout** — Single-column layout only
- **No multi-tenant switcher** — Single organization only
- **No real-time agent monitoring panel** — Individual BrainTile components exist
- **No cost dashboard** — No MetricCard or QuotaBar patterns
- **No orchestration canvas with cost tracking** — React Flow exists but no cost overlay
- **No responsive mobile** — Desktop-first, no swipe gestures or bottom nav

---

## 10 UX Patterns from Paperclip (PAPERCLIP-UX-AUDIT.md)

1. **Three-Column Layout** — Left: CompanyRail (multi-tenant switcher, draggable), Center: Sidebar (nav), Right: Content area + Properties panel, Mobile: Swipe gestures, bottom nav

2. **Real-time Agent Monitoring** — ActiveAgentsPanel with ping animation, LiveRunWidget with transcript streaming, Status badges: idle/running/completed/failed, Compact density modes

3. **Company-as-Context** — Draggable company ordering via @dnd-kit, Visual status indicators per company (live agents, unread inbox), Company-specific branding/icons, Sync across tabs via localStorage

4. **Agent Configuration Form** — AgentConfigForm: Identity → Adapter → Permissions → Run Policy sections, Dirty tracking with floating save button, **IMPROVE:** Template gallery, config validation, import/export

5. **Cost Dashboard** — BillerSpendCard with hierarchical breakdown, QuotaBar visual progress (percent of allocation), MetricCard for quick stats, Provider-level cost tracking

6. **Kanban Board** — @dnd-kit for drag-and-drop, Multi-column status workflow, Compact cards with live run indicators, **IMPROVE:** Swim lanes, bulk operations

7. **Command Palette** — Cmd/Ctrl+K trigger, Radix Command dialog, Search issues, agents, pages, actions, Categorized results

8. **Run Transcript** — Multi-density: compact, normal, detailed, Raw vs Nice display modes, Streaming updates, **IMPROVE:** Search/filter, syntax highlighting, export

9. **Onboarding Wizard** — Progressive step-by-step setup, Goal-based company creation, Adapter type selection, Environment validation, **IMPROVE:** Templates, progress save/resume

10. **Org Chart** — SVG-based org chart visualization, ReportsToPicker for hierarchy, CompanyPatternIcon per entity

---

## Architecture Decisions

### Layout Architecture

**Three-Column Layout (NEW):**
```
┌─────────────┬─────────────────┬──────────────────────────┐
│ CompanyRail │    Sidebar      │       Content Area       │
│ (180px)     │    (240px)      │       (flex-fill)        │
│             │                 │                          │
│ - Draggable │ - Nav items     │ - Page content           │
│ - Status    │ - Org switcher  │ - Properties panel       │
│ - Branding  │ - Settings      │   (conditional overlay)  │
└─────────────┴─────────────────┴──────────────────────────┘
```

**Mobile (Single Column):**
- Bottom nav for main sections
- Swipe gestures to navigate
- Full-screen content with back button

### Component Architecture

**New Layout Components:**
- `CompanyRail` — Left column, draggable company switcher
- `AppSidebar` — Center column, navigation items
- `ThreeColumnLayout` — Wraps protected routes, manages layout state
- `PropertiesPanel` — Right overlay for context-specific properties

**New Feature Components:**
- `ActiveAgentsPanel` — Real-time agent monitoring with density modes
- `MetricCard` — Cost dashboard metric display
- `QuotaBar` — Budget enforcement visual
- `CommandPalette` — Cmd+K global search
- `OnboardingWizard` — Progressive setup flow

### State Management

**New Zustand Stores:**
- `layoutStore` — Layout state (columns collapsed/expanded, density mode)
- `companyStore` — Multi-tenant company context, ordering, active company
- `costStore` — Cost metrics per brain, budget enforcement

**Existing Stores (preserve):**
- `brainStore` — Brain state with RAF batching
- `wsDispatcher` — WebSocket singleton

### Performance Constraints

- **60fps at 24-brain burst** — RAF batching must be preserved
- **Zero GC pauses** — Rust WebSocket Hub handles thousands of connections
- **Compact density modes** — Reduce DOM nodes for high-density views

---

## Implementation Priority

### Wave 1: Foundation (Layout + Multi-tenant)
- Plan 17-01: Three-column layout foundation (CompanyRail + Sidebar + Content)
- Plan 17-02: Multi-tenant company switcher with localStorage sync

### Wave 2: Real-time Monitoring
- Plan 17-03: ActiveAgentsPanel with density modes + status badges
- Plan 17-04: Cost dashboard with MetricCard + QuotaBar

### Wave 3: Advanced Features
- Plan 17-05: Command palette (Cmd+K) with global search
- Plan 17-06: Onboarding wizard + responsive mobile polish

---

## Dependencies

- **Phase 16 (Observability + Real-time Hub)** — Must be complete for WebSocket infrastructure
- **Phase 15 (Rust Control Plane)** — PostgreSQL + event sourcing for cost tracking
- **Phase 13 (Vertical Slice)** — gRPC + Protobuf contracts for type-safe APIs

---

## Testing Strategy

**Unit Tests (Vitest):**
- Layout component rendering tests
- Company switcher state management tests
- Cost dashboard metric calculation tests
- Command palette search/filter tests

**Integration Tests:**
- Multi-tenant switching flow
- Real-time WebSocket updates in monitoring panel
- Command palette action execution

**E2E Tests (Playwright):**
- Full user flows (company switching → monitoring → cost tracking)
- Responsive mobile interactions (swipe gestures, bottom nav)
- Onboarding wizard completion

---

## Accessibility Requirements

- **Keyboard navigation** — All interactive elements must be keyboard-accessible
- **Screen reader support** — Proper ARIA labels on all components
- **Focus management** — Focus trap in modals, proper focus order
- **prefers-reduced-motion** — Respect system preference (fix TODO in BrainTile.tsx:159)
- **Color contrast** — OKLCH color system must meet WCAG AA standards

---

## Anti-Patterns to Avoid

- ❌ **Forking Paperclip** — Architecture mismatch (Vite vs Next.js App Router)
- ❌ **Ignoring RAF batching** — Will break 60fps at 24-brain burst
- ❌ **Breaking existing WebSocket infrastructure** — Must preserve wsDispatcher.ts
- ❌ **Hardcoded company context** — Must support multi-tenant switching
- ❌ **Desktop-only design** — Mobile responsiveness is required
- ❌ **Ignoring accessibility** -prefers-reduced-motion guard missing in current code

---

## Open Questions

1. **DnD library choice** — Paperclip uses @dnd-kit, but React Flow has built-in DnD. Should we use @dnd-kit for company rail or build custom?

2. **Cost data source** — Should cost metrics come from Rust event sourcing (activity_log) or Python API? Likely Rust for performance.

3. **Command palette scope** — What actions should it support? Navigate to screens, trigger brain runs, create companies, switch orgs?

4. **Onboarding skip flow** — Can users skip onboarding? What's the minimal setup required?

5. **Mobile bottom nav items** — Which sections should appear in mobile bottom nav? All 4 screens or subset?

---

## Next Steps

1. ✅ CONTEXT.md created — This file
2. ⏭️ Create PLAN.md files (6 plans estimated)
3. ⏭️ Execute Phase 17 via `/mm:execute-phase 17`

---

*Context created: 2026-04-08*
*Ready for GSD planning phase*
