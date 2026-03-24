---
phase: 08-strategy-vault-engine-room
plan: 04
subsystem: ui
tags: [zustand, tanstack-query, react, typescript, focus-mode, api-keys, engine-room]

# Dependency graph
requires:
  - phase: 08-strategy-vault-engine-room
    plan: 01
    provides: "POST /api/keys, GET /api/keys, DELETE /api/keys/{id} backend endpoints"
  - phase: 08-strategy-vault-engine-room
    plan: 03
    provides: "Engine Room page with LiveLogPanel + tabbed layout (Config tab was placeholder)"
  - phase: 06-command-center
    provides: "CommandCenterWrapper + BriefInputModal with Server Action createTask"
  - phase: 07-the-nexus
    provides: "NexusCanvas + BrainNode React Flow graph"
provides:
  - "OrchestratorStore: Zustand store tracking task state (idle/running/complete/error) and Focus Mode computed state"
  - "FocusModeBadge: floating escape hatch button for Focus Mode ([F]/[Esc] keyboard shortcuts)"
  - "NexusPage: client layout wrapper — sidebar collapses + canvas expands on Focus Mode"
  - "BrainNode: idle tiles dim to 30% opacity during Focus Mode"
  - "APIKeyManager: tabbed container for API key CRUD (Create Key | My Keys)"
  - "KeyCreateDialog: show-once pattern — full key displayed once, copy-to-clipboard, security warning"
  - "KeyListTable: masked keys table (prefix...suffix) with revoke confirm dialog"
  - "Engine Room Config tab: wired to APIKeyManager (replaced placeholder)"
affects: [08-05-integration-tests, v2.2-brain-agents]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "OrchestratorStore: Zustand store without Immer (simple object, no Maps) — isFocusMode computed inline in each action"
    - "Focus Mode escape hatch: userOverride flag — user can exit without killing running task"
    - "CSS-only layout transitions: w-0/w-[250px] + opacity-0/opacity-100 + pointer-events-none (no framer-motion)"
    - "Show-once security: createdKey held in component state only, cleared on dialog close, never cached/logged"
    - "KeyListTable revoke: confirm dialog via separate Dialog component (not AlertDialog — not in shadcn install)"
    - "formatRelativeTime: exported helper for relative timestamps (sec/min/hour/day/month/year)"

key-files:
  created:
    - "apps/web/src/stores/orchestratorStore.ts"
    - "apps/web/src/stores/__tests__/orchestratorStore.test.ts"
    - "apps/web/src/components/shared/FocusModeBadge.tsx"
    - "apps/web/src/components/shared/__tests__/FocusModeBadge.test.tsx"
    - "apps/web/src/components/nexus/NexusPage.tsx"
    - "apps/web/src/components/nexus/__tests__/NexusPage.test.tsx"
    - "apps/web/src/components/engine-room/APIKeyManager.tsx"
    - "apps/web/src/components/engine-room/KeyCreateDialog.tsx"
    - "apps/web/src/components/engine-room/KeyListTable.tsx"
    - "apps/web/src/components/engine-room/__tests__/APIKeyManager.test.tsx"
    - "apps/web/src/components/engine-room/__tests__/KeyCreateDialog.test.tsx"
    - "apps/web/src/components/engine-room/__tests__/KeyListTable.test.tsx"
  modified:
    - "apps/web/src/components/command-center/CommandCenterWrapper.tsx"
    - "apps/web/src/components/nexus/BrainNode.tsx"
    - "apps/web/src/app/(protected)/engine-room/page.tsx"

key-decisions:
  - "framer-motion replaced with CSS transitions: framer-motion not installed in project — w-0/opacity-0 transitions achieve same layout shift effect without dependency"
  - "OrchestratorStore without Immer: state is simple scalars (no Maps/Sets), Immer overhead not needed"
  - "BriefInputModal contract preserved: startTask() added to CommandCenterWrapper (not BriefInputModal) — 8 existing tests unbroken"
  - "NexusPage.tsx as separate layout component: server page.tsx is async Server Component — layout concerns belong in client wrapper"
  - "Tabs implemented without shadcn/ui Tabs component: Tabs not in installed shadcn components — raw ARIA button tabs used instead"
  - "Dialog used for revoke confirmation (not AlertDialog): AlertDialog not in installed shadcn components — Dialog with custom content achieves same UX"

patterns-established:
  - "Focus Mode state machine: userOverride flag decouples task state from user preference — no re-trapping on Esc"
  - "Layout collapse pattern: w-0 + opacity-0 + pointer-events-none = fully hidden but DOM-present sidebar"
  - "Show-once key pattern: createdKey in React state, cleared on handleClose — never reaches localStorage/sessionStorage"

requirements-completed: [UX-01, ER-02]

# Metrics
duration: 26min
completed: 2026-03-24
---

# Phase 08 Plan 04: Focus Mode + API Key Management Summary

**Zustand OrchestratorStore for task/Focus Mode state machine, floating FocusModeBadge with keyboard shortcuts, NexusPage layout collapse on Focus Mode, and complete API key CRUD (show-once create, masked list, revoke with confirm) wired into Engine Room Configuration tab**

## Performance

- **Duration:** 26 min
- **Started:** 2026-03-24T10:53:15Z
- **Completed:** 2026-03-24T11:18:25Z
- **Tasks:** 7 (Tasks 1-7)
- **Files modified:** 15 (12 created, 3 modified)

## Accomplishments

- OrchestratorStore tracks task lifecycle with computed `isFocusMode = state === 'running' && !userOverride`
- Focus Mode auto-activates on task start, sidebar collapses smoothly via CSS transitions, FocusModeBadge provides [F]/[Esc] escape hatch
- API key CRUD complete: show-once creation, masked display (prefix...suffix), revoke with confirmation dialog
- Engine Room Config tab wired to APIKeyManager (replaces placeholder from 08-03)
- 321 total tests passing (40 test files), net +57 tests added this plan

## Task Commits

1. **Task 1: OrchestratorStore** - `e21fe41` (feat)
2. **Task 2: Wire BriefInputModal to OrchestratorStore** - `e7990c0` (feat)
3. **Task 3: FocusModeBadge** - `f27cf98` (feat)
4. **Task 4: NexusPage Focus Mode layout + BrainNode dimming** - `34c67e5` (feat)
5-7. **Tasks 5-7: APIKeyManager + KeyCreateDialog + KeyListTable** - `4846396` (feat)

## Files Created/Modified

- `apps/web/src/stores/orchestratorStore.ts` — Zustand store: task state + Focus Mode computed property
- `apps/web/src/stores/__tests__/orchestratorStore.test.ts` — 21 tests: all state transitions, edge cases
- `apps/web/src/components/shared/FocusModeBadge.tsx` — Floating exit button, [F]/[Esc] keyboard listeners
- `apps/web/src/components/shared/__tests__/FocusModeBadge.test.tsx` — 13 tests: visibility, keyboard, position
- `apps/web/src/components/nexus/NexusPage.tsx` — Client layout wrapper with sidebar/panel collapse logic
- `apps/web/src/components/nexus/__tests__/NexusPage.test.tsx` — 12 tests: Focus Mode layout behavior
- `apps/web/src/components/nexus/BrainNode.tsx` — Added idle tile dimming (opacity-30) in Focus Mode
- `apps/web/src/components/command-center/CommandCenterWrapper.tsx` — Added `startTask()` call after WS connect
- `apps/web/src/components/engine-room/APIKeyManager.tsx` — Tabbed container, TanStack Query, error/loading states
- `apps/web/src/components/engine-room/KeyCreateDialog.tsx` — Show-once dialog, copy-to-clipboard, security warning
- `apps/web/src/components/engine-room/KeyListTable.tsx` — Masked key table, formatRelativeTime, revoke confirm dialog
- `apps/web/src/app/(protected)/engine-room/page.tsx` — Config tab wired to APIKeyManager

## Decisions Made

- `framer-motion` replaced with CSS transitions: library not installed, Tailwind transition classes achieve equivalent visual result
- `OrchestratorStore` uses plain Zustand (no Immer): state is scalars only, no Maps/Sets
- `BriefInputModal` callback contract preserved: `startTask()` wired in `CommandCenterWrapper` to avoid breaking 8 existing tests
- `NexusPage.tsx` created as separate client component: server `page.tsx` is async Server Component and can't hold client layout state
- Raw ARIA tabs used instead of shadcn/ui `Tabs`: Tabs component not in project's shadcn install set

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] framer-motion not installed in project**
- **Found during:** Task 3 (FocusModeBadge)
- **Issue:** Plan referenced `motion.button` and `AnimatePresence` from framer-motion, but library is not in `package.json`
- **Fix:** Replaced with native `<button>` and conditional render using `if (!isFocusMode) return null` — CSS `transition-colors` provides animation
- **Files modified:** `FocusModeBadge.tsx` (no framer-motion import)
- **Verification:** 13 tests pass, no import errors
- **Committed in:** `f27cf98` (Task 3 commit)

**2. [Rule 3 - Blocking] shadcn/ui Tabs component not installed**
- **Found during:** Task 5 (APIKeyManager)
- **Issue:** Plan used `<Tabs>`, `<TabsList>`, `<TabsTrigger>`, `<TabsContent>` from shadcn/ui, none present in `apps/web/src/components/ui/`
- **Fix:** Implemented accessible tab navigation using native HTML `<button>` elements with `role="tab"`, `aria-selected`, `aria-controls` — ARIA pattern equivalent
- **Files modified:** `APIKeyManager.tsx`
- **Verification:** 12 tests pass including tab switching behavior
- **Committed in:** `4846396` (Task 5-7 commit)

**3. [Rule 3 - Blocking] shadcn/ui AlertDialog component not installed**
- **Found during:** Task 7 (KeyListTable)
- **Issue:** Plan used `<AlertDialog>` for revoke confirmation, not in project's shadcn install
- **Fix:** Used existing `<Dialog>` component with custom content (Cancel + destructive Revoke buttons)
- **Files modified:** `KeyListTable.tsx`
- **Verification:** 15 tests pass including revoke confirm dialog flow
- **Committed in:** `4846396` (Task 5-7 commit)

---

**Total deviations:** 3 auto-fixed (all Rule 3 — Blocking: missing dependencies)
**Impact on plan:** All fixes maintain functional equivalence. No scope change. CSS transitions are visually equivalent to framer-motion for this use case. ARIA tab pattern matches accessibility requirements.

## Issues Encountered

- Test "multiple elements" error for text matching in KeyCreateDialog and KeyListTable: text appeared both in trigger button/table and in dialog — fixed by targeting unique dialog-specific text (`/cannot be retrieved later/i`, `/will be immediately revoked/i`)

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Wave 3 (08-04) complete: Focus Mode + API key management UI done
- Wave 0-3 all complete: Backend (08-01), Strategy Vault (08-02), Engine Room logs (08-03), Focus Mode + API keys (08-04)
- Ready for Wave 4: 08-05 integration tests
- Requirements UX-01 and ER-02 fully addressed

## Self-Check: PASSED

All created files verified present. All 5 task commits verified in git history.

---
*Phase: 08-strategy-vault-engine-room*
*Completed: 2026-03-24*
