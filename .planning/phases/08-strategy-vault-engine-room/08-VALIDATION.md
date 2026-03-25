---
phase: 8
slug: strategy-vault-engine-room
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-25
audited_by: gsd-nyquist-auditor
---

# Phase 08 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (backend)** | pytest 7.x + pytest-asyncio |
| **Framework (frontend)** | vitest 4.x + React Testing Library |
| **Backend config** | `apps/api/pyproject.toml` |
| **Frontend config** | `apps/web/vitest.config.ts` |
| **Backend quick run** | `cd apps/api && uv run pytest tests/api/test_executions_list.py tests/api/test_executions_detail.py tests/unit/test_auth_api_keys.py tests/api/test_graph_subgraph.py -v` |
| **Frontend quick run** | `cd apps/web && pnpm vitest run src/components/strategy-vault/__tests__/ src/components/engine-room/__tests__/ src/stores/__tests__/orchestratorStore.test.ts` |
| **Full backend suite** | `cd apps/api && uv run pytest -v` |
| **Full frontend suite** | `cd apps/web && pnpm vitest run` |
| **Estimated runtime** | ~8s backend, ~5s frontend |

---

## Sampling Rate

- **After every task commit:** Run quick run commands above
- **After every plan wave:** Run full suite commands
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | SV-01 | unit | `cd apps/api && uv run pytest tests/api/test_executions_list.py -x` | ✅ | ✅ green |
| 08-01-02 | 01 | 1 | SV-02 | unit | `cd apps/api && uv run pytest tests/api/test_executions_detail.py -x` | ✅ | ✅ green |
| 08-01-03 | 01 | 1 | SV-02 | unit | `cd apps/api && uv run pytest tests/api/test_graph_subgraph.py -x` | ✅ | ✅ green |
| 08-01-04 | 01 | 1 | ER-02 | unit | `cd apps/api && uv run pytest tests/unit/test_auth_api_keys.py -x` | ✅ | ✅ green |
| 08-01-05 | 01 | 1 | SV-01 | unit | `cd apps/api && uv run pytest tests/api/test_execution_writer.py -x` | ✅ | ✅ green |
| 08-02-01 | 02 | 2 | SV-01 | unit | `cd apps/web && pnpm vitest run src/components/strategy-vault/__tests__/ExecutionList.test.tsx` | ✅ | ✅ green |
| 08-02-02 | 02 | 2 | SV-02 | unit | `cd apps/web && pnpm vitest run src/components/strategy-vault/__tests__/ExecutionDetail.test.tsx` | ✅ | ✅ green |
| 08-02-03 | 02 | 2 | SV-02 | unit | `cd apps/web && pnpm vitest run src/components/strategy-vault/__tests__/SmartMarkdown.test.tsx` | ✅ | ✅ green |
| 08-02-04 | 02 | 2 | SV-02 | unit | `cd apps/web && pnpm vitest run src/components/strategy-vault/__tests__/SnapshotScrubber.test.tsx` | ✅ | ✅ green |
| 08-03-01 | 03 | 3 | ER-01 | unit | `cd apps/web && pnpm vitest run src/components/engine-room/__tests__/LiveLogPanel.test.tsx` | ✅ | ✅ green |
| 08-03-02 | 03 | 3 | ER-01 | unit | `cd apps/web && pnpm vitest run src/components/engine-room/__tests__/FilterBar.test.tsx` | ✅ | ✅ green |
| 08-03-03 | 03 | 3 | ER-01 | unit | `cd apps/web && pnpm vitest run src/components/engine-room/__tests__/LogBadge.test.tsx` | ✅ | ✅ green |
| 08-03-04 | 03 | 3 | ER-01 | unit | `cd apps/web && pnpm vitest run src/stores/__tests__/logFilterStore.test.ts` | ✅ | ✅ green |
| 08-04-01 | 04 | 4 | ER-02 | unit | `cd apps/web && pnpm vitest run src/components/engine-room/__tests__/APIKeyManager.test.tsx` | ✅ | ✅ green |
| 08-04-02 | 04 | 4 | ER-02 | unit | `cd apps/web && pnpm vitest run src/components/engine-room/__tests__/KeyCreateDialog.test.tsx` | ✅ | ✅ green |
| 08-04-03 | 04 | 4 | ER-02 | unit | `cd apps/web && pnpm vitest run src/components/engine-room/__tests__/KeyListTable.test.tsx` | ✅ | ✅ green |
| 08-04-04 | 04 | 4 | ER-02 | integration | `cd apps/web && pnpm vitest run src/__tests__/APIKeyManager.test.tsx` | ✅ | ✅ green |
| 08-04-05 | 04 | 4 | ER-03 | unit | `cd apps/web && pnpm vitest run src/components/engine-room/__tests__/BrainYAMLViewer.test.tsx` | ✅ | ✅ green |
| 08-04-06 | 04 | 4 | UX-01 | integration | `cd apps/web && pnpm vitest run src/__tests__/FocusMode.e2e.test.tsx` | ✅ | ✅ green |
| 08-04-07 | 04 | 4 | UX-01 | unit | `cd apps/web && pnpm vitest run src/stores/__tests__/orchestratorStore.test.ts` | ✅ | ✅ green |
| 08-05-01 | 05 | 5 | ALL | integration | `cd apps/web && pnpm vitest run src/__tests__/phases/Phase08Integration.test.tsx` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All files exist. Wave 0 complete.

- [x] `apps/api/tests/api/test_executions_list.py` — SV-01 paginated list
- [x] `apps/api/tests/api/test_executions_detail.py` — SV-02 detail view
- [x] `apps/api/tests/api/test_executions_models.py` — SV-01/SV-02 models
- [x] `apps/api/tests/api/test_execution_writer.py` — SV-01 concurrency
- [x] `apps/api/tests/api/test_graph_subgraph.py` — SV-02 graph sub-graph
- [x] `apps/api/tests/unit/test_auth_api_keys.py` — ER-02 API keys CRUD
- [x] `apps/web/src/components/strategy-vault/__tests__/ExecutionList.test.tsx` — SV-01
- [x] `apps/web/src/components/strategy-vault/__tests__/ExecutionDetail.test.tsx` — SV-02
- [x] `apps/web/src/components/strategy-vault/__tests__/SmartMarkdown.test.tsx` — SV-02
- [x] `apps/web/src/components/strategy-vault/__tests__/SnapshotScrubber.test.tsx` — SV-02
- [x] `apps/web/src/components/engine-room/__tests__/LiveLogPanel.test.tsx` — ER-01
- [x] `apps/web/src/components/engine-room/__tests__/FilterBar.test.tsx` — ER-01
- [x] `apps/web/src/components/engine-room/__tests__/LogBadge.test.tsx` — ER-01
- [x] `apps/web/src/stores/__tests__/logFilterStore.test.ts` — ER-01
- [x] `apps/web/src/components/engine-room/__tests__/APIKeyManager.test.tsx` — ER-02
- [x] `apps/web/src/components/engine-room/__tests__/KeyCreateDialog.test.tsx` — ER-02
- [x] `apps/web/src/components/engine-room/__tests__/KeyListTable.test.tsx` — ER-02
- [x] `apps/web/src/__tests__/APIKeyManager.test.tsx` — ER-02 integration
- [x] `apps/web/src/components/engine-room/__tests__/BrainYAMLViewer.test.tsx` — ER-03
- [x] `apps/web/src/__tests__/FocusMode.e2e.test.tsx` — UX-01
- [x] `apps/web/src/stores/__tests__/orchestratorStore.test.ts` — UX-01
- [x] `apps/web/src/__tests__/phases/Phase08Integration.test.tsx` — all requirements

---

## Test File Inventory

### Backend (apps/api)

| File | Tests | Requirement |
|------|-------|-------------|
| `tests/api/test_executions.py` | 13 | SV-01/SV-02 |
| `tests/api/test_executions_list.py` | 9 | SV-01 |
| `tests/api/test_executions_detail.py` | 6 | SV-02 |
| `tests/api/test_executions_models.py` | 20 | SV-01/SV-02 |
| `tests/api/test_execution_writer.py` | 7 | SV-01 concurrency |
| `tests/api/test_graph_subgraph.py` | 19 | SV-02 graph |
| `tests/unit/test_auth_api_keys.py` | 16 | ER-02 |

### Frontend (apps/web)

| File | Tests | Requirement |
|------|-------|-------------|
| `src/components/strategy-vault/__tests__/ExecutionList.test.tsx` | 13 | SV-01 |
| `src/components/strategy-vault/__tests__/ExecutionDetail.test.tsx` | 13 | SV-02 |
| `src/components/strategy-vault/__tests__/SmartMarkdown.test.tsx` | 13 | SV-02 |
| `src/components/strategy-vault/__tests__/SnapshotScrubber.test.tsx` | 13 | SV-02 |
| `src/components/engine-room/__tests__/LiveLogPanel.test.tsx` | 13 | ER-01 |
| `src/components/engine-room/__tests__/FilterBar.test.tsx` | 13 | ER-01 |
| `src/components/engine-room/__tests__/LogBadge.test.tsx` | 9 | ER-01 |
| `src/stores/__tests__/logFilterStore.test.ts` | — | ER-01 |
| `src/components/engine-room/__tests__/APIKeyManager.test.tsx` | 7 | ER-02 |
| `src/components/engine-room/__tests__/KeyCreateDialog.test.tsx` | 11 | ER-02 |
| `src/components/engine-room/__tests__/KeyListTable.test.tsx` | 14 | ER-02 |
| `src/__tests__/APIKeyManager.test.tsx` | 26 | ER-02 integration |
| `src/components/engine-room/__tests__/BrainYAMLViewer.test.tsx` | 13 | ER-03 |
| `src/__tests__/FocusMode.e2e.test.tsx` | 23 | UX-01 |
| `src/stores/__tests__/orchestratorStore.test.ts` | — | UX-01 |
| `src/__tests__/phases/Phase08Integration.test.tsx` | 37 | all requirements |

**Total automated:** 90 backend + 218 frontend = 308 tests passing

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Strategy Vault Markdown renders in real browser | SV-02 | react-syntax-highlighter theme verification requires visual | Open /strategy-vault/{id}, verify code blocks render with VS Code Dark theme |
| Focus Mode visual dimming of idle brains | UX-01 | CSS opacity transitions require visual judgment | Trigger task, verify non-active brain tiles dim after 2s idle |
| SnapshotScrubber timeline sync | SV-02 | Video-like scrubbing requires browser interaction | Open execution detail, drag scrubber, verify log panel jumps to matching timestamp |

---

## Requirement Coverage Summary

| Requirement | Description | Tests | Status |
|-------------|-------------|-------|--------|
| SV-01 | Execution history list, paginated, JWT-protected | 48 (backend + frontend) | ✅ green |
| SV-02 | Execution detail with Markdown, graph, scrubber | 98 (backend + frontend) | ✅ green |
| ER-01 | Live structured logs, virtual scroll, level filter | 49 frontend | ✅ green |
| ER-02 | API key CRUD (create show-once, list masked, revoke) | 71 (backend + frontend) | ✅ green |
| ER-03 | Brain YAML retrieval + viewer | 13 frontend | ✅ green |
| UX-01 | Focus Mode auto-activate, sidebar collapse, Esc exit | 60 frontend | ✅ green |

**Total automated:** 90 backend + 218 frontend = 308 tests passing

---

## Validation Sign-Off

- [x] All tasks have automated verify
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 complete — all test files exist
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-25
