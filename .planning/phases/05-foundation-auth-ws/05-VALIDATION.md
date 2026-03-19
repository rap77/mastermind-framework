---
phase: 5
slug: foundation-auth-ws
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest (ESM-native, faster than Jest for Next.js 16) |
| **Config file** | `vitest.config.ts` (Wave 0) |
| **Quick run command** | `pnpm test --run` |
| **Full suite command** | `pnpm test --run --coverage` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pnpm tsc --noEmit && pnpm test --run`
- **After every plan wave:** Run `pnpm build && pnpm test --run --coverage`
- **Before `/gsd:verify-work`:** Full suite must be green + `pnpm build` clean
- **Max feedback latency:** 45 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | FND-01 | smoke | `pnpm build` exits 0 | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | FND-01 | smoke | Visual check: React Flow handles/edges render | ❌ W0 | ⬜ pending |
| 05-01-03 | 01 | 1 | FND-01 | smoke | Visual check: Magic UI @keyframes animate | ❌ W0 | ⬜ pending |
| 05-02-01 | 02 | 2 | FND-02 | unit | `pnpm test -- loginAction` valid credentials | ❌ W0 | ⬜ pending |
| 05-02-02 | 02 | 2 | FND-02 | unit | `pnpm test -- loginAction` invalid credentials | ❌ W0 | ⬜ pending |
| 05-02-03 | 02 | 2 | FND-03 | unit | `pnpm test -- proxy` redirects unauthenticated | ❌ W0 | ⬜ pending |
| 05-02-04 | 02 | 2 | FND-03 | unit | `pnpm test -- AuthGuardLayout` invalid JWT | ❌ W0 | ⬜ pending |
| 05-02-05 | 02 | 2 | FND-04 | integration | `pnpm test -- cors` against live API | ❌ W0 | ⬜ pending |
| 05-03-01 | 03 | 3 | SB-01 | unit | `pnpm test -- generate-types` outputs api.ts | ❌ W0 | ⬜ pending |
| 05-03-02 | 03 | 3 | SB-01 | type-check | `pnpm tsc --noEmit` catches drift | ❌ W0 | ⬜ pending |
| 05-03-03 | 03 | 3 | WS-01 | unit | `pnpm test -- wsStore` connect no-op if same taskId | ❌ W0 | ⬜ pending |
| 05-03-04 | 03 | 3 | WS-01 | integration | `pnpm test -- wsStore` survives navigation | ❌ W0 | ⬜ pending |
| 05-03-05 | 03 | 3 | WS-02 | unit | `pnpm test -- brainStore` RAF drains 24 events | ❌ W0 | ⬜ pending |
| 05-03-06 | 03 | 3 | WS-03 | unit | `pnpm test -- useBrainState` selector isolation | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `apps/web/vitest.config.ts` — test runner config
- [ ] `apps/web/src/stores/__tests__/wsStore.test.ts` — WS-01 coverage
- [ ] `apps/web/src/stores/__tests__/brainStore.test.ts` — WS-02, WS-03 coverage
- [ ] `apps/web/src/app/__tests__/proxy.test.ts` — FND-03 coverage
- [ ] `apps/web/src/app/__tests__/loginAction.test.ts` — FND-02 coverage
- [ ] `apps/web/scripts/__tests__/generate-types.test.ts` — SB-01 coverage
- [ ] Framework install: `pnpm add -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/jest-dom`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| React Flow CSS renders handles and edges | FND-01 | Visual output requires human judgment | After Plan 05-01, build a 2-node ReactFlow graph, verify handles visible and edges render in `npm run build` output (not just dev mode) |
| Magic UI @keyframes animations | FND-01 | Animation smoothness requires visual verification | After Plan 05-01, install one Magic UI component (e.g., BentoGrid), verify CSS animations play smoothly in browser |
| CORS with httpOnly cookies | FND-04 | Browser CORS enforcement is external to frontend | After Plan 05-02, login from localhost:3000, verify DevTools shows cookie set and no CORS errors |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (15 test files to create)
- [ ] No watch-mode flags (all use `--run`)
- [ ] Feedback latency < 45s (estimated)
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 complete

**Approval:** pending
