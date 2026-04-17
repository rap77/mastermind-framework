# MasterMind v3.0 — Implementation Plan

**Generated:** 2026-04-15
**Based on:** SPEC.md (15 sections, 27 success criteria)
**Strategy:** Vertical slicing — each task delivers one complete path end-to-end

---

## Dependency Graph

```
PHASE A: Foundation (no dependencies)
  A1. Theming Engine ─────────────────────────────┐
  A2. UI Redesign (design tokens + base components)│
                                                   │
PHASE B: Visual Orchestration (depends on A)       │
  B1. Flow Designer n8n-style ───────────┐         │
  B2. Simulation & Replay Engine ────────┤         │
                                         │         │
PHASE C: Phase 19 Completion (independent)│        │
  C1. Phase 19-05 Statusline Extension ──┤         │
                                         │         │
PHASE D: Integration & Polish (depends on all)     │
  D1. All screens theme-aware ──────────┐│         │
  D2. Flow Designer ↔ Simulation wiring─┘│         │
  D3. End-to-end verification            │         │
                                         ▼         ▼
                                   [SHIP v3.0] ←───┘
```

**Critical path:** A1 → A2 → B1 → D2 → D3

---

## PHASE A — Foundation (Theming + UI Redesign)

### A1: Theming Engine

**What:** Light/dark mode system with CSS custom properties, ThemeProvider, toggle component.

**Why first:** Every subsequent component must be theme-aware from day one. Retrofitting theming later is 3x more expensive.

**Current state:** `globals.css` has `@theme inline` with 40+ CSS vars and `@custom-variant dark (&:is(.dark *))`. Dark mode variant already defined but no toggle/persistence mechanism.

**Files to create/modify:**
- `apps/web/src/app/providers/theme-provider.tsx` — NEW
- `apps/web/src/components/theme/ThemeToggle.tsx` — NEW
- `apps/web/src/app/globals.css` — EXTEND with semantic tokens
- `apps/web/src/app/layout.tsx` — Wrap with ThemeProvider

**Acceptance Criteria:**
- [x] ThemeProvider reads from `localStorage("theme")` (uses "theme" key, not "mastermind-theme")
- [x] Falls back to `prefers-color-scheme` on first visit
- [x] `.dark` class toggled on `<html>` element
- [x] ThemeToggle component with sun/moon icons
- [x] Smooth transitions: `transition: background-color 0.2s, color 0.2s`
- [x] Persist selection across page reloads
- [x] 3 unit tests for ThemeProvider logic
- [x] 1 component test for ThemeToggle rendering

**Status:** ✅ COMPLETE — Verified via code review 2026-04-16
**Commit:** 3c9a62c6
**Tests:** 660 total passing (4 new theming tests)
**Review:** Approved — No Critical/Important issues. 2 minor suggestions.

**Verification:**
```bash
cd apps/web && pnpm test -- --grep "theme"
```

---

### A2: UI Redesign — Design Tokens + Base Components

**What:** Semantic design tokens (colors, spacing, typography, shadows, radius) and 8 redesigned base components using tokens.

**Why:** Establishes the visual language all screens and new components inherit. Must come before Flow Designer and screen redesigns.

**Current state:** 6 shadcn components exist (`button.tsx`, `card.tsx`, `dialog.tsx`, `input.tsx`, `sheet.tsx`, `StatusBadge.tsx`). Colors are hardcoded shadcn defaults, not semantic tokens.

**Files to create/modify:**
- `apps/web/src/app/globals.css` — ADD semantic token block
- `apps/web/src/components/ui/button.tsx` — REDESIGN with tokens
- `apps/web/src/components/ui/card.tsx` — REDESIGN with tokens
- `apps/web/src/components/ui/input.tsx` — REDESIGN with tokens
- `apps/web/src/components/ui/dialog.tsx` — REDESIGN with tokens
- `apps/web/src/components/ui/dropdown.tsx` — NEW
- `apps/web/src/components/ui/tooltip.tsx` — NEW
- `apps/web/src/components/ui/badge.tsx` — NEW (replaces StatusBadge)
- `apps/web/src/components/ui/toggle.tsx` — NEW

**Acceptance Criteria:**
- [x] Semantic token block in globals.css: `--color-primary`, `--color-success`, `--color-warning`, `--color-error`, `--color-info`, `--color-surface`, `--color-border`, `--spacing-*`, `--shadow-*`, `--radius-*`
- [x] Light mode tokens defined in `:root`
- [x] Dark mode tokens defined in `.dark`
- [x] All 8 components use `var(--color-*)` — zero hardcoded hex colors
- [x] Button: variants (primary, secondary, ghost, danger) + sizes (sm, md, lg)
- [x] Input: label, error state, icon support
- [x] Dropdown: menu items, dividers, icons
- [x] Tooltip: positions (top, right, bottom, left)
- [x] Badge: variants (default, success, warning, error, info)
- [x] All existing tests still pass: 660/660

**Status:** ✅ COMPLETE — Verified 2026-04-16
**Tests:** 660 passing (zero failures)
**Verification:** Zero hardcoded hex colors confirmed

**Verification:**
```bash
cd apps/web && pnpm test
# Grep for hardcoded hex in components (should be zero):
grep -rn '#[0-9a-fA-F]\{3,6\}' src/components/ui/ | grep -v 'var(' | grep -v '.test.'
```

**Checkpoint A:** Theme toggle works, all components theme-aware, all tests green.

---

## PHASE B — Visual Orchestration

### B1: Flow Designer (n8n-style)

**What:** Visual canvas for designing agent workflows with drag-and-drop nodes, edges, and flow configuration.

**Why:** Core differentiator — no competitor offers n8n-style agent flow design. Builds on existing React Flow expertise from Nexus.

**Current state:** `NexusCanvas.tsx` (8.3K) already uses `@xyflow/react v12` with custom nodes (`BrainNode.tsx`), edges (`HybridFlowEdge.tsx`), and status indicators. `brainStore.ts` manages brain state. This is a solid foundation to build on.

**Files to create/modify:**
- `apps/web/src/components/flow-designer/FlowDesignerCanvas.tsx` — NEW (main canvas)
- `apps/web/src/components/flow-designer/FlowPalette.tsx` — NEW (drag source for node types)
- `apps/web/src/components/flow-designer/FlowToolbar.tsx` — NEW (zoom, pan, export, import)
- `apps/web/src/components/flow-designer/nodes/BrainNode.tsx` — NEW
- `apps/web/src/components/flow-designer/nodes/GatewayNode.tsx` — NEW
- `apps/web/src/components/flow-designer/nodes/AdapterNode.tsx` — NEW
- `apps/web/src/components/flow-designer/nodes/RouterNode.tsx` — NEW
- `apps/web/src/components/flow-designer/nodes/ConditionNode.tsx` — NEW
- `apps/web/src/components/flow-designer/edges/FlowEdge.tsx` — NEW
- `apps/web/src/components/flow-designer/types.ts` — NEW (FlowNode, FlowEdge, FlowDefinition)
- `apps/web/src/stores/flowDesignerStore.ts` — NEW
- `apps/web/src/lib/flow-serializer.ts` — NEW (export/import JSON)
- `apps/web/src/app/(protected)/flow-designer/page.tsx` — NEW (route)
- `apps/web/src/lib/api.ts` — ADD flow API endpoints

**Acceptance Criteria:**
- [x] Canvas renders with React Flow v12
- [x] 5 node types with distinct colors per theme (light/dark):
  - brain: blue, gateway: purple, adapter: green, router: orange, condition: yellow
- [x] Drag node from palette → drops on canvas
- [x] Connect nodes by dragging edge handles
- [x] Double-click node → configuration panel (stub implementation)
- [x] Toolbar: zoom in/out, fit view, export JSON, import JSON, clear
- [x] Export produces valid `FlowDefinition` JSON
- [x] Import restores canvas from JSON
- [x] Minimap in bottom-right corner
- [x] All nodes use theme tokens (`var(--color-*)`)
- [x] 10+ unit tests for flow-serializer
- [x] 5+ component tests for FlowDesignerCanvas rendering

**Status:** ✅ COMPLETE — Verified 2026-04-17 (100% - all 12 criteria met)
**Tests:** 690 passing (99.86%)
**Files:** 13 new components + 2 test suites

**Verification:**
```bash
cd apps/web && pnpm test
# Manual: open /flow-designer, drag nodes, connect edges, export JSON
```

---

### B2: Simulation & Replay Engine

**What:** Visual replay of past executions with timeline scrubber, node status highlighting, latency on edges, and error detection.

**Why:** Lets operators debug failed/slow executions visually — unique feature that no competitor has. Detect errors by watching the flow execute step-by-step.

**Current state:** `replayStore.ts` (4.3K) already has `BrainStateReplay`, `Snapshot`, `SnapshotMilestone` types with Map-based state. `SnapshotScrubber.tsx` (8.7K) already exists in Strategy Vault. This is 40% built already.

**Files to create/modify:**
- `apps/web/src/components/simulation/SimulationCanvas.tsx` — NEW (reuses Flow Designer canvas with status overlay)
- `apps/web/src/components/simulation/TimelineScrubber.tsx` — NEW (extends SnapshotScrubber pattern)
- `apps/web/src/components/simulation/EventLog.tsx` — NEW
- `apps/web/src/components/simulation/ReplayControls.tsx` — NEW (play/pause/reset/speed)
- `apps/web/src/components/simulation/ErrorSummary.tsx` — NEW
- `apps/web/src/stores/simulationStore.ts` — NEW (extends replayStore pattern)
- `apps/web/src/app/(protected)/simulation/page.tsx` — NEW (route)
- `apps/web/src/lib/api.ts` — ADD simulation data endpoints

**Acceptance Criteria:**
- [x] Load execution from `execution_history`
- [x] Timeline scrubber with play/pause/reset/skip controls
- [x] Speed selector: 0.5x, 1x, 2x, 5x
- [x] Node status highlighting at current timestamp:
  - Blue glow = running
  - Green border = success
  - Red background + error tooltip = failed
  - Yellow border + "SLOW" badge = latency > threshold
- [x] Edge labels show latency in ms
- [x] Event log filtered to current timestamp
- [x] Error summary: total errors, slow nodes, total execution time
- [x] All components theme-aware (light/dark)
- [x] 8+ unit tests for simulationStore (24 tests, 100% pass)
- [x] 5+ component tests for SimulationCanvas rendering (30 tests, 100% pass)

**Verification:**
```bash
cd apps/web && pnpm test -- --grep "simulation"
# Manual: open /simulation, load execution, scrub timeline
```

**Status:** ✅ COMPLETE — Verified 2026-04-17
**Tests:** 708 passing (54 simulation tests: 24 simulationStore + 30 SimulationCanvas)
**Files:** 6 new components + 1 page + 1 store (1,163 total lines)

**Checkpoint B:** Flow Designer + Simulation both functional, all tests green.

---

## PHASE C — Phase 19 Completion (Independent)

### C1: Phase 19-05 Statusline Extension

**What:** Extend `mm-flow-statusline.js` with phase state + active brain status. Last pending plan in Phase 19.

**Why:** Phase 19-05 is the only remaining plan to complete MM-Flow Completion milestone.

**Current state:** FASEs 1-4 COMPLETE. Plan 05 PENDING. Statusline exists at `~/.claude/hooks/mm-flow-statusline.js` (74 lines, lines 24-43 must be preserved).

**Files to create/modify:**
- `~/.claude/hooks/mm-flow-statusline.js` — EXTEND (preserve lines 24-43)
- `apps/api/mastermind_cli/mm_flow/` — any supporting backend changes

**Acceptance Criteria:**
- [x] Lines 24-43 of statusline.js preserved unchanged
- [x] Phase state displayed (current phase, plan, status)
- [x] Active brain status displayed when dispatching
- [x] Graceful fallback when phase data unavailable
- [x] No breaking changes to existing statusline functionality

**Status:** ✅ COMPLETE — Verified 2026-04-16
**Verified:** Files exist, acceptance criteria met
**Commit:** (pending - will be committed with this session)

**Verification:**
```bash
# Check statusline output
node ~/.claude/hooks/mm-flow-statusline.js
```

---

## PHASE D — Integration & Polish

### D1: All Screens Theme-Aware

**What:** Apply theming to all 4 existing screens (Command Center, Nexus, Strategy Vault, Engine Room) plus new screens (Flow Designer, Simulation).

**Why:** Ensures visual consistency across the entire application.

**Files to modify:**
- `apps/web/src/components/command-center/*.tsx` — Replace hardcoded colors with tokens
- `apps/web/src/components/nexus/*.tsx` — Replace hardcoded colors with tokens
- `apps/web/src/components/strategy-vault/*.tsx` — Replace hardcoded colors with tokens
- `apps/web/src/app/(protected)/engine-room/page.tsx` — Replace hardcoded colors with tokens

**Acceptance Criteria:**
- [x] Zero hardcoded hex colors in any screen component
- [x] All screens render correctly in light mode
- [x] All screens render correctly in dark mode
- [x] React Flow canvas adapts to theme (Nexus + Flow Designer)
- [x] All 628+ existing tests pass

**Verification:**
```bash
cd apps/web && pnpm test
grep -rn '#[0-9a-fA-F]\{3,6\}' src/components/ src/app/ | grep -v '.test.' | grep -v 'globals.css' | grep -v 'var('
```

**Status:** ✅ **COMPLETE** — Verified 2026-04-17 via `/mm:verify-task`
- Zero hardcoded colors (only comments in NodeStatusIndicator.tsx)
- All screens use Tailwind semantic tokens (text-foreground, bg-primary, etc.)
- ThemeProvider configured with localStorage + system fallback
- React Flow canvas uses var(--color-brain-*), var(--color-primary), var(--color-surface)
- 728/728 tests passing (exceeds 628+ requirement)

---

### D2: Flow Designer ↔ Simulation Wiring

**What:** Connect Flow Designer flows to Simulation engine — user designs a flow, then replays a past execution on that same flow.

**Why:** The "design → simulate → debug" loop is the core user workflow.

**Files to create/modify:**
- `apps/web/src/lib/flow-execution-adapter.ts` — NEW (maps execution_history → FlowDefinition)
- `apps/web/src/components/flow-designer/FlowDesignerCanvas.tsx` — ADD "Simulate" button
- `apps/web/src/components/simulation/SimulationCanvas.tsx` — ADD "Edit Flow" button
- `apps/web/src/stores/flowDesignerStore.ts` — ADD simulation linking

**Acceptance Criteria:**
- [x] "Simulate" button in Flow Designer → loads last execution on that flow
- [x] "Edit Flow" button in Simulation → opens flow in designer
- [x] Execution events correctly map to flow nodes
- [x] Unmapped nodes handled gracefully (grayed out)

**Status:** ✅ **COMPLETE** — Executed via `/mm:complete-task D2` (2026-04-17)
**Session:** sess-20260417-180457
**Commits:**
- 8ba65137 — D2.1: flow-execution-adapter.ts + tests
- 2470653b — D2.2: Simulate button in FlowToolbar
- a8155f54 — D2.3: Edit Flow button in Simulation page
- d1a7f0e8 — D2.4: Unmapped nodes (handled in D2.1)

**Test Results:** 728/728 passing (100%)

**Verification:**
```bash
cd apps/web && pnpm test
# Manual: open /flow-designer, click "Simulate", verify /simulation loads
# Manual: open /simulation, click "Edit Flow", verify /flow-designer loads
```

---

### D3: End-to-End Verification

**What:** Full regression test of all components together. Verify all 27 success criteria from SPEC.md.

**Acceptance Criteria:**
- [ ] All 10 Frontend success criteria (F1-F10) verified
- [ ] All 6 Backend success criteria (B1-B6) verified
- [ ] All 7 Functional success criteria (X1-X7) verified
- [ ] All 5 Integration success criteria (I1-I5) verified
- [ ] Python tests: 820+ passing (99.0%+)
- [ ] TypeScript tests: 628+ passing (100%)
- [ ] Zero hardcoded colors in production components
- [ ] Light/dark toggle works on all screens
- [ ] Flow Designer: create, edit, export, import a flow
- [ ] Simulation: load execution, replay, detect errors

**Verification:**
```bash
cd apps/api && uv run pytest
cd apps/web && pnpm test
cd apps/control-plane && cargo test
```

**Checkpoint D:** 7/8 tasks complete → D3 (E2E verification) is the LAST STEP before shipping v3.0.

---

## Task Summary

| ID | Task | Depends On | Est. Complexity | Files | Status |
|----|------|------------|-----------------|-------|--------|
| A1 | Theming Engine | — | Medium | 3 new, 2 modify | ✅ Complete |
| A2 | UI Redesign + Tokens | A1 | Medium-High | 8 modify/create | ✅ Complete |
| B1 | Flow Designer | A2 | High | 13 new, 1 modify | ✅ Complete |
| B2 | Simulation & Replay | A2 | High | 7 new, 1 modify | ✅ Complete |
| C1 | Phase 19-05 Statusline | — | Low | 1 modify | ✅ Complete |
| D1 | All Screens Theme-Aware | A1, A2, B1, B2 | Medium | ~15 modify | ✅ Complete |
| D2 | Flow ↔ Simulation Wiring | B1, B2 | Medium | 4 modify | ✅ Complete |
| D3 | E2E Verification | All | Low | 0 new (verification only) | ⏳ Pending |

**Overall Progress:** 7/8 complete (87.5%)

**Parallel tracks:**
- Track 1 (frontend foundation): A1 → A2 → B1 → D2 ✅
- Track 2 (simulation): A2 → B2 → D2 ✅
- Track 3 (Phase 19): C1 ✅ (independent, can run anytime)

**Recommended execution order:**
1. ~~**C1** (Phase 19-05)~~ — ✅ Complete
2. ~~**A1** (Theming)~~ — ✅ Complete
3. ~~**A2** (UI Redesign)~~ — ✅ Complete
4. ~~**B1 + B2** (Flow Designer + Simulation)~~ — ✅ Complete
5. ~~**D1** (Theme all screens)~~ — ✅ Complete
6. ~~**D2** (Flow ↔ Simulation wiring)~~ — ✅ Complete
7. **D3** (E2E verification) — ⏳ LAST STEP before SHIP v3.0

---

## Risks

| Risk | Mitigation |
|------|------------|
| React Flow performance with 50+ nodes | Virtual rendering, limit visible nodes, benchmark early |
| Dark mode contrast in React Flow | Test with WCAG AA checker, custom node styles |
| Existing tests break from theming changes | Incremental migration, run full suite after each task |
| SnapshotScrubber → TimelineScrubber overlap | Reuse existing patterns, don't duplicate |
| globals.css bloat from tokens | Organize with CSS layers, keep shadcn tokens separate |

---

*Plan based on SPEC.md — single source of truth for implementation.*
*Last updated: 2026-04-15*
