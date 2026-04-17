# MasterMind v3.0 — Task List

**Generated:** 2026-04-15
**Based on:** tasks/plan.md

## Status Legend
- [ ] Pending
- [~] In Progress
- [x] Complete

---

## PHASE A — Foundation

### A1: Theming Engine
- [x] Create `apps/web/src/components/theme-provider.tsx` (location differs from plan)
  - Read from `localStorage("theme")` (note: key is "theme", not "mastermind-theme")
  - Fallback to `prefers-color-scheme`
  - Toggle `.dark` class on `<html>`
  - Export ThemeContext + useTheme hook
- [x] Create `apps/web/src/components/theme-toggle/theme-toggle.tsx` (location differs from plan)
  - Sun/moon icons
  - Smooth icon transition
- [x] Extend `apps/web/src/app/globals.css` (uses existing Tailwind 4 CSS variables)
  - Semantic tokens already exist in `@theme inline` block
  - `--color-primary`, `--color-success`, `--color-warning`, `--color-error`, `--color-info`
  - `--color-surface`, `--color-border`, `--spacing-*`, `--shadow-*`, `--radius-*`
- [x] Modify `apps/web/src/app/layout.tsx`
  - Wrap with ThemeProvider
- [x] Write 3 unit tests for ThemeProvider
- [x] Write 1 component test for ThemeToggle

### A2: UI Redesign — Design Tokens + Base Components
- [x] Add semantic token block to `apps/web/src/app/globals.css`
- [x] Redesign `apps/web/src/components/ui/button.tsx` with token variants
- [x] Redesign `apps/web/src/components/ui/card.tsx` with token variants
- [x] Redesign `apps/web/src/components/ui/input.tsx` with token variants (added label, error, icons)
- [x] Redesign `apps/web/src/components/ui/dialog.tsx` with token variants
- [x] Create `apps/web/src/components/ui/dropdown.tsx`
- [x] Create `apps/web/src/components/ui/tooltip.tsx`
- [x] Create `apps/web/src/components/ui/badge.tsx` (replaces StatusBadge)
- [x] Create `apps/web/src/components/ui/toggle.tsx`
- [x] Verify zero hardcoded hex in components
- [x] All 660 tests pass (100% success rate)

---

## PHASE B — Visual Orchestration

### B1: Flow Designer (n8n-style)
- [x] Create `apps/web/src/components/flow-designer/types.ts`
- [x] Create `apps/web/src/stores/flowDesignerStore.ts` (457 lines with Immer)
- [x] Create `apps/web/src/lib/flow-serializer.ts` (export/import JSON + validation)
- [x] Create `apps/web/src/components/flow-designer/nodes/BrainNode.tsx`
- [x] Create `apps/web/src/components/flow-designer/nodes/GatewayNode.tsx`
- [x] Create `apps/web/src/components/flow-designer/nodes/AdapterNode.tsx`
- [x] Create `apps/web/src/components/flow-designer/nodes/RouterNode.tsx`
- [x] Create `apps/web/src/components/flow-designer/nodes/ConditionNode.tsx`
- [x] Create `apps/web/src/components/flow-designer/edges/FlowEdge.tsx`
- [x] Create `apps/web/src/components/flow-designer/FlowPalette.tsx`
- [x] Create `apps/web/src/components/flow-designer/FlowToolbar.tsx`
- [x] Create `apps/web/src/components/flow-designer/FlowDesignerCanvas.tsx`
- [x] Create `apps/web/src/app/(protected)/flow-designer/page.tsx`
- [x] Write 10+ tests for flow-serializer (14 tests, all passing)
- [x] Write 5+ tests for FlowDesignerCanvas (5 tests, all passing)

### B2: Simulation & Replay Engine
- [x] Create `apps/web/src/stores/simulationStore.ts` (24 tests, ✅ 100% pass)
- [x] Create `apps/web/src/components/simulation/ReplayControls.tsx` (111 lines)
- [x] Create `apps/web/src/components/simulation/TimelineScrubber.tsx` (255 lines)
- [x] Create `apps/web/src/components/simulation/EventLog.tsx` (148 lines)
- [x] Create `apps/web/src/components/simulation/ErrorSummary.tsx` (81 lines)
- [x] Create `apps/web/src/components/simulation/SimulationCanvas.tsx` (237 lines)
- [x] Create `apps/web/src/app/(protected)/simulation/page.tsx` (280 lines)
- [x] Write 8+ tests for simulationStore (24 tests, ✅ 100% pass)
- [x] Write 5+ tests for SimulationCanvas (30 tests, ✅ 100% pass)

---

## PHASE C — Phase 19 Completion

### C1: Phase 19-05 Statusline Extension
- [x] Extend `~/.claude/hooks/mm-flow-statusline.js`
  - Preserve lines 24-43
  - Add phase state display
  - Add active brain status
- [x] Verify no breaking changes to existing statusline

---

## PHASE D — Integration & Polish

### D1: All Screens Theme-Aware
- [x] Command Center: replace hardcoded colors with tokens
- [x] Nexus: replace hardcoded colors with tokens
- [x] Strategy Vault: replace hardcoded colors with tokens
- [x] Engine Room: replace hardcoded colors with tokens
- [x] React Flow canvas adapts to theme (Nexus + Flow Designer)
- [x] Verify zero hardcoded hex in screen components
- [x] All 628+ tests pass

### D2: Flow Designer ↔ Simulation Wiring
- [x] Create `apps/web/src/lib/flow-execution-adapter.ts`
- [x] Add "Simulate" button to FlowDesignerCanvas
- [x] Add "Edit Flow" button to SimulationCanvas
- [x] Handle unmapped nodes gracefully

### D3: End-to-End Verification
- [ ] Verify 10 Frontend success criteria (F1-F10)
- [ ] Verify 6 Backend success criteria (B1-B6)
- [ ] Verify 7 Functional success criteria (X1-X7)
- [ ] Verify 5 Integration success criteria (I1-I5)
- [ ] Python: 820+ tests passing
- [ ] TypeScript: 628+ tests passing
- [ ] Manual: Flow Designer create → edit → export → import
- [ ] Manual: Simulation load → replay → detect errors
- [ ] Manual: Theme toggle light ↔ dark on all 6 screens

---

**Total: 8 tasks, ~65 subtasks**
**Critical path: A1 → A2 → B1 → D2 → D3**
