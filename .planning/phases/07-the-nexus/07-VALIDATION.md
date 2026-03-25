---
phase: 07
slug: the-nexus
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-22
audited: 2026-03-25
---

# Phase 07 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest 4.1.0 + @testing-library/react 16.3.2 (frontend) / pytest (backend) |
| **Config file** | `apps/web/vitest.config.ts` |
| **Quick run command** | `cd apps/web && pnpm vitest run src/components/nexus/__tests__/ src/stores/__tests__/brainStore.test.ts` |
| **Full suite command** | `cd apps/web && pnpm vitest run` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite (web + api) must be green
- **Max feedback latency:** ~15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | BE-02 | unit (pytest) | `cd apps/api && uv run pytest tests/api/test_executions.py -k "graph" -x` | ✅ | ✅ green |
| 07-02-01 | 02 | 0 | NEX-01 | unit (Vitest) | `cd apps/web && pnpm vitest run src/components/nexus/__tests__/NexusCanvas.test.tsx` | ✅ | ✅ green |
| 07-02-02 | 02 | 1 | NEX-01 | unit (Vitest) | `cd apps/web && pnpm vitest run src/components/nexus/__tests__/layout.test.ts` | ✅ | ✅ green |
| 07-02-03 | 02 | 1 | NEX-02 | unit (Vitest) | `cd apps/web && pnpm vitest run src/components/nexus/__tests__/BrainNode.test.tsx` | ✅ | ✅ green |
| 07-02-04 | 02 | 1 | NEX-03 | unit (Vitest) | `cd apps/web && pnpm vitest run src/components/nexus/__tests__/BrainNode.test.tsx` | ✅ | ✅ green |
| 07-03-01 | 03 | 1 | NEX-02 | unit (Vitest) | `cd apps/web && pnpm vitest run src/stores/__tests__/brainStore.test.ts` | ✅ | ✅ green |
| 07-03-02 | 03 | 1 | NEX-03 | unit (Vitest) | `cd apps/web && pnpm vitest run src/components/nexus/__tests__/BrainNode.test.tsx` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `apps/web/src/components/nexus/__tests__/NexusCanvas.test.tsx` — NODE_TYPES stability, no canvas remount on state change (NEX-01)
- [x] `apps/web/src/components/nexus/__tests__/layout.test.ts` — dagre position stability, 24 node positions unchanged between renders (NEX-01)
- [x] `apps/web/src/components/nexus/__tests__/BrainNode.test.tsx` — targeted re-render on own brainId (NEX-02), nodrag/nopan classes, click without drag (NEX-03)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Ghost Architecture visual (24 dashed nodes, 20% opacity) | NEX-01 | CSS opacity + dashed border requires visual inspection | Navigate to /nexus without active task — verify 24 ghost nodes visible |
| Neon glow animation on activation | NEX-02 | CSS animation requires visual/browser inspection | Trigger a WS brain_started event — verify border glow transitions |
| Cooldown Mode visual shift | NEX-02 | Background color shift requires visual inspection | Complete a task execution — verify canvas enters read-only cooldown state |
| NodeDetailPanel renders on click | NEX-03 | shadcn Sheet interaction — visual/integration test | Click any brain node — verify right-side panel slides in with brain details |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** 2026-03-25 — gsd-nyquist-auditor
