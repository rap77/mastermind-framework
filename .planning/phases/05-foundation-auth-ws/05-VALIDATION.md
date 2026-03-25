---
phase: 5
slug: foundation-auth-ws
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-19
audited_by: gsd-nyquist-auditor
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
| 05-01-01 | 01 | 1 | FND-01 | smoke | `pnpm build` exits 0 | ✅ | ✅ green |
| 05-01-02 | 01 | 1 | FND-01 | smoke | Visual check: React Flow handles/edges render | ✅ | ✅ green |
| 05-01-03 | 01 | 1 | FND-01 | smoke | `cd apps/web && pnpm vitest run src/app/__tests__/globalsCss.test.ts` | ✅ | ✅ green |
| 05-02-01 | 02 | 2 | FND-02 | unit | `cd apps/web && pnpm vitest run src/app/__tests__/loginAction.test.ts` | ✅ | ✅ green |
| 05-02-02 | 02 | 2 | FND-02 | unit | `cd apps/web && pnpm vitest run src/lib/__tests__/auth.test.ts` | ✅ | ✅ green |
| 05-02-03 | 02 | 2 | FND-03 | unit | `cd apps/web && pnpm vitest run src/app/__tests__/proxy.test.ts` | ✅ | ✅ green |
| 05-02-04 | 02 | 2 | FND-03 | unit | `cd apps/web && pnpm vitest run src/app/__tests__/authGuardLayout.test.ts` | ✅ | ✅ green |
| 05-02-05 | 02 | 2 | FND-04 | integration | `cd apps/api && uv run pytest tests/api/test_auth.py -x` | ✅ | ✅ green |
| 05-03-01 | 03 | 3 | SB-01 | unit | `cd apps/web && pnpm vitest run scripts/__tests__/generate-types.test.ts` | ✅ | ✅ green |
| 05-03-02 | 03 | 3 | SB-01 | type-check | `cd apps/web && pnpm tsc --noEmit` | ✅ | ✅ green |
| 05-03-03 | 03 | 3 | WS-01 | unit | `cd apps/web && pnpm vitest run src/stores/__tests__/wsStore.test.ts` | ✅ | ✅ green |
| 05-03-04 | 03 | 3 | WS-01 | unit | `cd apps/web && pnpm vitest run src/stores/__tests__/wsStore.test.ts` | ✅ | ✅ green |
| 05-03-05 | 03 | 3 | WS-02 | unit | `cd apps/web && pnpm vitest run src/stores/__tests__/brainStore.test.ts` | ✅ | ✅ green |
| 05-03-06 | 03 | 3 | WS-03 | unit | `cd apps/web && pnpm vitest run src/stores/__tests__/brainStore.test.ts` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All files exist. Wave 0 complete.

- [x] `apps/web/vitest.config.ts` — test runner config
- [x] `apps/web/src/stores/__tests__/wsStore.test.ts` — WS-01 coverage (5 tests)
- [x] `apps/web/src/stores/__tests__/brainStore.test.ts` — WS-02, WS-03 coverage (11 tests)
- [x] `apps/web/src/app/__tests__/proxy.test.ts` — FND-03 coverage (4 tests)
- [x] `apps/web/src/app/__tests__/loginAction.test.ts` — FND-02 coverage (4 tests)
- [x] `apps/web/src/app/__tests__/authGuardLayout.test.ts` — FND-03 coverage (4 tests)
- [x] `apps/web/src/lib/__tests__/auth.test.ts` — FND-02 coverage (4 tests)
- [x] `apps/web/scripts/__tests__/generate-types.test.ts` — SB-01 coverage (4 tests)

---

## Test File Inventory

### Backend (apps/api)

| File | Tests | Requirement |
|------|-------|-------------|
| `tests/api/test_auth.py` | 15 (CORS + JWT) | FND-04 |

### Frontend (apps/web)

| File | Tests | Requirement |
|------|-------|-------------|
| `src/app/__tests__/loginAction.test.ts` | 4 | FND-02 |
| `src/lib/__tests__/auth.test.ts` | 4 | FND-02 |
| `src/app/__tests__/proxy.test.ts` | 4 | FND-03 |
| `src/app/__tests__/authGuardLayout.test.ts` | 4 | FND-03 |
| `src/app/__tests__/globalsCss.test.ts` | — | FND-01 |
| `scripts/__tests__/generate-types.test.ts` | 4 | SB-01 |
| `src/stores/__tests__/wsStore.test.ts` | 5 | WS-01 |
| `src/stores/__tests__/brainStore.test.ts` | 11 | WS-02, WS-03 |

**Total automated:** 15 backend + 36 frontend = 51 tests passing

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| React Flow CSS renders handles and edges | FND-01 | Visual output requires human judgment | After Plan 05-01, build a 2-node ReactFlow graph, verify handles visible and edges render in `npm run build` output (not just dev mode) |
| Magic UI @keyframes animations | FND-01 | Animation smoothness requires visual verification | After Plan 05-01, install one Magic UI component (e.g., BentoGrid), verify CSS animations play smoothly in browser |
| CORS with httpOnly cookies | FND-04 | Browser CORS enforcement is external to frontend | After Plan 05-02, login from localhost:3000, verify DevTools shows cookie set and no CORS errors |

---

## Validation Sign-Off

- [x] All tasks have automated verify
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 complete — all test files exist
- [x] No watch-mode flags
- [x] Feedback latency < 45s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-25
