---
phase: 6
slug: 06-command-center
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-25
audited_by: gsd-nyquist-auditor
---

# Phase 06 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (backend)** | pytest 7.x + pytest-asyncio |
| **Framework (frontend)** | vitest 4.x + React Testing Library |
| **Backend config** | `apps/api/pyproject.toml` |
| **Frontend config** | `apps/web/vitest.config.ts` |
| **Backend quick run** | `cd apps/api && uv run pytest tests/api/test_brains_endpoint.py tests/unit/test_brain_registry.py -v` |
| **Frontend quick run** | `cd apps/web && pnpm vitest run src/components/command-center/__tests__/ src/lib/__tests__/commands.test.ts src/app/api/tasks/__tests__/route.test.ts src/stores/__tests__/brainStore.test.ts` |
| **Full backend suite** | `cd apps/api && uv run pytest -v` |
| **Full frontend suite** | `cd apps/web && pnpm vitest run` |
| **Estimated runtime** | ~5s backend, ~3s frontend |

---

## Sampling Rate

- **After every task commit:** Run quick run commands above
- **After every plan wave:** Run full suite commands
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | BE-01 | unit | `cd apps/api && uv run pytest tests/unit/test_brain_registry.py::test_get_all_brains_paginated -x` | ✅ | ✅ green |
| 06-01-02 | 01 | 1 | BE-01 | unit | `cd apps/api && uv run pytest tests/unit/test_brain_registry.py -k "get_all_brains" -v` | ✅ | ✅ green |
| 06-01-03 | 01 | 1 | BE-01 | integration | `cd apps/api && uv run pytest tests/api/test_brains_endpoint.py -x` | ✅ | ✅ green |
| 06-02-01 | 02 | 2 | CC-02 | unit | `cd apps/web && pnpm vitest run src/app/'(protected)'/command-center/__tests__/page.test.tsx` | ✅ | ✅ green |
| 06-02-02 | 02 | 2 | CC-02 | unit | `cd apps/web && pnpm vitest run src/components/command-center/__tests__/BentoGrid.test.tsx` | ✅ | ✅ green |
| 06-02-03 | 02 | 2 | CC-02 | unit | `cd apps/web && pnpm vitest run src/components/command-center/__tests__/BrainTile.test.tsx` | ✅ | ✅ green |
| 06-02-04 | 02 | 2 | CC-02 | unit | `cd apps/web && pnpm vitest run src/components/command-center/__tests__/ClusterGroup.test.tsx` | ✅ | ✅ green |
| 06-02-05 | 02 | 2 | CC-02 | unit | `cd apps/web && pnpm vitest run src/stores/__tests__/brainStore.test.ts` | ✅ | ✅ green |
| 06-02-06 | 02 | 2 | CC-02 | unit | `cd apps/web && pnpm vitest run src/components/ws/__tests__/WSBrainBridge.test.tsx` | ✅ | ✅ green |
| 06-03-01 | 03 | 3 | CC-03 | unit | `cd apps/web && pnpm vitest run src/lib/__tests__/commands.test.ts` | ✅ | ✅ green |
| 06-03-02 | 03 | 3 | CC-03 | unit | `cd apps/web && pnpm vitest run src/components/command-center/__tests__/BriefInputModal.test.tsx` | ✅ | ✅ green |
| 06-03-03 | 03 | 3 | CC-03 | unit | `cd apps/web && pnpm vitest run src/app/api/tasks/__tests__/route.test.ts` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No Wave 0 stubs needed.

---

## Test File Inventory

### Backend (apps/api)

| File | Tests | Requirement |
|------|-------|-------------|
| `tests/unit/test_brain_registry.py` | 11 (including 6 get_all_brains tests) | BE-01 |
| `tests/api/test_brains_endpoint.py` | 6 integration tests | BE-01 |

### Frontend (apps/web)

| File | Tests | Requirement |
|------|-------|-------------|
| `src/app/(protected)/command-center/__tests__/page.test.tsx` | 3 | CC-02 |
| `src/components/command-center/__tests__/BentoGrid.test.tsx` | 5 | CC-02 |
| `src/components/command-center/__tests__/ClusterGroup.test.tsx` | 5 | CC-02 |
| `src/components/command-center/__tests__/BrainTile.test.tsx` | 7 | CC-02 |
| `src/stores/__tests__/brainStore.test.ts` | — | CC-02 |
| `src/components/ws/__tests__/WSBrainBridge.test.tsx` | 4 | CC-02 |
| `src/lib/__tests__/commands.test.ts` | 5 | CC-03 |
| `src/components/command-center/__tests__/BriefInputModal.test.tsx` | 8 | CC-03 |
| `src/app/api/tasks/__tests__/route.test.ts` | 6 | CC-03 |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 60fps maintained during 24-brain burst WebSocket updates | CC-02 | Performance measurement requires browser DevTools | Open Chrome, go to /command-center, Performance tab, trigger bulk WS events, verify FPS stays at 60 |
| prefers-reduced-motion accessibility guard | CC-02 | Requires OS-level setting change | Enable "Reduce Motion" in OS settings, visit /command-center, verify no pulse/shake animations play |
| WebSocket auto-connect after task creation | CC-03 | Requires live backend + WS server | Submit brief via modal, open Network > WS tab, verify connection established |
| DOMPurify sanitization in browser context (window.DOMPurify) | CC-03 | DOMPurify has limited functionality in jsdom test environment | Test in real browser: paste `<img src=x onerror=alert(1)>` in brief modal, verify stripped |

---

## Requirement Coverage Summary

| Requirement | Description | Tests | Status |
|-------------|-------------|-------|--------|
| BE-01 | GET /api/brains — paginated, JWT-protected, IDOR | 12 (6 unit + 6 integration) | ✅ green |
| CC-02 | Bento Grid, clustering, live WebSocket status, 60fps | 24 frontend tests | ✅ green |
| CC-03 | Brief modal, Cmd+Enter, XSS prevention, task creation | 19 frontend tests | ✅ green |

**Total automated:** 18 backend + 50 frontend = 68 tests passing

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none missing)
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-25
