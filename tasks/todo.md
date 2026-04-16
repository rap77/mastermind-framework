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
- [ ] Create `apps/web/src/app/providers/theme-provider.tsx`
  - Read from `localStorage("mastermind-theme")`
  - Fallback to `prefers-color-scheme`
  - Toggle `.dark` class on `<html>`
  - Export ThemeContext + useTheme hook
- [ ] Create `apps/web/src/components/theme/ThemeToggle.tsx`
  - Sun/moon icons
  - Smooth icon transition
- [ ] Extend `apps/web/src/app/globals.css`
  - Add semantic token block in `:root` and `.dark`
  - `--color-primary`, `--color-success`, `--color-warning`, `--color-error`, `--color-info`
  - `--color-surface`, `--color-border`, `--spacing-*`, `--shadow-*`, `--radius-*`
- [ ] Modify `apps/web/src/app/layout.tsx`
  - Wrap with ThemeProvider
- [ ] Write 3 unit tests for ThemeProvider
- [ ] Write 1 component test for ThemeToggle

### A2: UI Redesign — Design Tokens + Base Components
- [ ] Redesign `apps/web/src/components/ui/button.tsx` with token variants
- [ ] Redesign `apps/web/src/components/ui/card.tsx` with token variants
- [ ] Redesign `apps/web/src/components/ui/input.tsx` with token variants
- [ ] Redesign `apps/web/src/components/ui/dialog.tsx` with token variants
- [ ] Create `apps/web/src/components/ui/dropdown.tsx`
- [ ] Create `apps/web/src/components/ui/tooltip.tsx`
- [ ] Create `apps/web/src/components/ui/badge.tsx` (replace StatusBadge)
- [ ] Create `apps/web/src/components/ui/toggle.tsx`
- [ ] Verify zero hardcoded hex in components
- [ ] All 628+ existing tests pass

---

## PHASE B — Visual Orchestration

### B1: Flow Designer (n8n-style)
- [ ] Create `apps/web/src/components/flow-designer/types.ts`
- [ ] Create `apps/web/src/stores/flowDesignerStore.ts`
- [ ] Create `apps/web/src/lib/flow-serializer.ts` (export/import JSON)
- [ ] Create `apps/web/src/components/flow-designer/nodes/BrainNode.tsx`
- [ ] Create `apps/web/src/components/flow-designer/nodes/GatewayNode.tsx`
- [ ] Create `apps/web/src/components/flow-designer/nodes/AdapterNode.tsx`
- [ ] Create `apps/web/src/components/flow-designer/nodes/RouterNode.tsx`
- [ ] Create `apps/web/src/components/flow-designer/nodes/ConditionNode.tsx`
- [ ] Create `apps/web/src/components/flow-designer/edges/FlowEdge.tsx`
- [ ] Create `apps/web/src/components/flow-designer/FlowPalette.tsx`
- [ ] Create `apps/web/src/components/flow-designer/FlowToolbar.tsx`
- [ ] Create `apps/web/src/components/flow-designer/FlowDesignerCanvas.tsx`
- [ ] Create `apps/web/src/app/(protected)/flow-designer/page.tsx`
- [ ] Write 10+ tests for flow-serializer
- [ ] Write 5+ tests for FlowDesignerCanvas

### B2: Simulation & Replay Engine
- [ ] Create `apps/web/src/stores/simulationStore.ts`
- [ ] Create `apps/web/src/components/simulation/ReplayControls.tsx`
- [ ] Create `apps/web/src/components/simulation/TimelineScrubber.tsx`
- [ ] Create `apps/web/src/components/simulation/EventLog.tsx`
- [ ] Create `apps/web/src/components/simulation/ErrorSummary.tsx`
- [ ] Create `apps/web/src/components/simulation/SimulationCanvas.tsx`
- [ ] Create `apps/web/src/app/(protected)/simulation/page.tsx`
- [ ] Write 8+ tests for simulationStore
- [ ] Write 5+ tests for SimulationCanvas

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
- [ ] Command Center: replace hardcoded colors with tokens
- [ ] Nexus: replace hardcoded colors with tokens
- [ ] Strategy Vault: replace hardcoded colors with tokens
- [ ] Engine Room: replace hardcoded colors with tokens
- [ ] React Flow canvas adapts to theme (Nexus + Flow Designer)
- [ ] Verify zero hardcoded hex in screen components
- [ ] All 628+ tests pass

### D2: Flow Designer ↔ Simulation Wiring
- [ ] Create `apps/web/src/lib/flow-execution-adapter.ts`
- [ ] Add "Simulate" button to FlowDesignerCanvas
- [ ] Add "Edit Flow" button to SimulationCanvas
- [ ] Handle unmapped nodes gracefully

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
