# Phase 08 Planning Complete

**Date:** 2026-03-23
**Status:** ✅ Ready for `/gsd:execute-phase 08`
**Milestone:** v2.1 War Room Frontend (Phase 8 of 8)

---

## Planning Summary

Phase 08 has been decomposed into **4 sequential waves** addressing all 6 phase requirements:

| Wave | Plan ID | Focus | Duration | Deliverable |
|------|---------|-------|----------|-------------|
| **0** | 08-01 | Backend architecture | 90 min | GraphEdge sub-graphs, execution history, API keys, brain YAML |
| **1** | 08-02 | Strategy Vault UI | 75 min | Execution list + detail view + Snapshot Scrubbing + Smart-GFM |
| **2** | 08-03 | Engine Room logs | 60 min | Live logs (react-virtuoso), filtering, isolation mode |
| **3** | 08-04 | Focus Mode + Config | 90 min | Focus Mode state machine, API key CRUD UI, integration tests |

**Total estimation:** ~315 minutes (~5.25 hours) for complete Phase 08 implementation

---

## Requirement Coverage

| Requirement | Plan | Implementation |
|------------|------|-----------------|
| **SV-01** Execution history list | 08-01 (backend), 08-02 (frontend) | GET /api/executions/history → paginated list with status/brief/duration/brain count |
| **SV-02** Execution detail + scrubbing | 08-01, 08-02, 08-03 | GET /api/executions/{id} → detail view with accordion, Snapshot Scrubber, logs sync |
| **ER-01** Live logs with filtering | 08-03 | LiveLogPanel (react-virtuoso) with level filtering, auto-follow, brain isolation |
| **ER-02** API key management | 08-01 (backend), 08-04 (frontend) | POST/GET/DELETE /api/keys → create (show-once), list (masked), revoke |
| **ER-03** Brain YAML viewer | 08-01 (backend), 08-03 (component) | GET /api/brains/{id}/yaml → read-only dialog with syntax highlighting + copy |
| **UX-01** Focus Mode | 08-04 | Auto-activate on task start, sidebar collapse, idle dimming, [F]/[Esc] escape hatch |

---

## Dependency Analysis

```
Wave 0 (08-01) — Backend contracts
├─ GraphEdge sub-graphs (Phase 07 unblocked for visual verification)
├─ Execution history endpoints
├─ API key management endpoints
└─ Brain YAML retrieval endpoint

Wave 1 (08-02) — Strategy Vault UI
├─ Depends on: 08-01 (executions API)
├─ ReplayStore + SnapshotScrubber
├─ SmartMarkdown rendering
└─ ExecutionList + ExecutionDetail pages

Wave 2 (08-03) — Engine Room logs
├─ Depends on: 08-02 (log rendering patterns)
├─ LiveLogPanel with react-virtuoso
├─ Log filtering + isolation
└─ BrainYAMLViewer dialog

Wave 3 (08-04) — Focus Mode + Config
├─ Depends on: 08-02, 08-03 (all components integrated)
├─ OrchestratorStore (task state)
├─ FocusModeBadge + NexusPage layout
├─ APIKeyManager + KeyCreateDialog + KeyListTable
└─ Integration tests verifying full v2.1 workflow
```

**Critical path:** 08-01 → 08-02 → 08-03 → 08-04 (sequential, no parallel execution)

---

## Task Breakdown by Wave

### Wave 0: Backend (08-01) — 7 Tasks
1. Create Execution models (Pydantic schemas)
2. Build GraphEdge sub-graph service
3. Enhance GET /api/tasks/{id}/graph endpoint
4. Create execution history endpoints
5. Create API key management endpoints
6. Add brain YAML retrieval endpoint
7. Write integration tests (test_executions_list, test_keys_crud, test_graph_subgraph)

**Files modified:** 9 (models, routes, services, tests)
**Must-haves:** GraphEdge response includes parentId + execution_mode, execution history paginated with cursor, API keys masked + revokable, brain YAML valid format

### Wave 1: Strategy Vault Frontend (08-02) — 7 Tasks
1. Build ReplayStore (Zustand with Immer + MapSet)
2. Build SmartMarkdown component (react-markdown + GFM + custom components)
3. Build SnapshotScrubber timeline component
4. Build ExecutionList (paginated table with TanStack Query)
5. Build ExecutionDetail (accordion + scrubber sync + logs)
6. Create Strategy Vault route pages (/strategy-vault, /strategy-vault/[id])
7. Write component tests (ExecutionList, SmartMarkdown, ExecutionDetail)

**Files modified:** 10 (pages, components, stores, tests)
**Must-haves:** Scrubber drag syncs logs to timestamp, SmartMarkdown renders tables/code with syntax highlighting, pagination cursor works

### Wave 2: Engine Room Logs (08-03) — 8 Tasks
1. Create log-parser utility (parseLogLine, filterLogsByLevel)
2. Create logFilterStore (Zustand with localStorage persistence)
3. Build LogBadge component (brain name + id with color)
4. Build FilterBar (level toggles + auto-follow + isolation display)
5. Build LiveLogPanel (react-virtuoso with WS subscription)
6. Build BrainYAMLViewer dialog
7. Create Engine Room page layout
8. Write component tests (LiveLogPanel, BrainYAMLViewer)

**Files modified:** 9 (components, stores, utils, page, tests)
**Must-haves:** Virtual scrolling renders ~30 rows, filter state persists, isolation mode works via badge click, YAML renders with syntax highlighting

### Wave 3: Focus Mode + API Keys (08-04) — 10 Tasks
1. Build OrchestratorStore (task state + Focus Mode flag)
2. Wire BriefInputModal to OrchestratorStore
3. Build FocusModeBadge floating button ([F]/[Esc])
4. Implement Focus Mode layout in NexusPage (AnimatePresence)
5. Build APIKeyManager container (tabs: Create + List)
6. Build KeyCreateDialog (show-once pattern)
7. Build KeyListTable (masked keys + revoke)
8. Update Engine Room page with APIKeyManager tabs
9. Write E2E tests (FocusMode.e2e.test.tsx, APIKeyManager.test.tsx)
10. Write Phase 08 integration test (full workflow: brief → focus → logs → keys)

**Files modified:** 10 (stores, components, pages, tests)
**Must-haves:** Focus Mode auto-activates on task start, [Esc] doesn't re-trap if task running, API key show-once enforced, full integration test passing

---

## Architecture Highlights

### Dynamic DAG Visualization (Wave 0 unblocks Wave 1)
- React Flow sub-graphs: Master → Niche Clusters → Brain Executors
- GraphEdge response includes `parentId` + `execution_mode` fields
- Dagre layout applied at fetch time (never re-computed on WS updates)
- Scales 24→50+ brains without visual clutter

### Snapshot Scrubbing (Wave 1)
- Store snapshots at milestones only (max 7 per execution, Miller's Law)
- Scrubber drag jumps between snapshots (not animate all WS events)
- Log panel auto-scrolls to timestamp when scrubber moves
- Performance: 10-100x faster than full-event replay

### Virtual Logging (Wave 2)
- react-virtuoso single viewport renders ~30 rows at a time
- Unlimited log lines with O(1) memory footprint
- Filter state persisted to localStorage
- Isolation mode: click brain badge to filter to single brain

### Focus Mode State Machine (Wave 3)
- OrchestratorStore tracks task state (idle/running/complete/error)
- `isFocusMode = state === 'running' && !userOverride`
- [Esc] sets userOverride=true (toggles off Focus Mode)
- On task complete, userOverride resets to false (no re-trap)
- Global state affects all pages (Nexus, Engine Room, Strategy Vault)

### API Key Show-Once Pattern (Wave 3)
- POST /api/keys returns full key in response body ONLY
- Key never logged, never cached, never persisted to localStorage
- Frontend shows key in code block, prompts user to copy
- If user closes dialog without copying, key is lost (by design)
- GET /api/keys returns masked keys (prefix + suffix only)
- DELETE /api/keys/{id} revokes immediately (no grace period)

---

## Test Strategy

**Per-Wave Testing:**
- Wave 0: pytest integration tests (CRUD operations, API contracts)
- Wave 1: Vitest component tests (rendering, user interaction)
- Wave 2: Vitest component tests (virtual scrolling, filtering, isolation)
- Wave 3: Vitest E2E + integration tests (full workflow)

**Coverage Targets:**
- Backend (08-01): 85% line coverage
- Frontend (08-02, 08-03): 80% line coverage
- Integration (08-04): 90% for critical paths

**Sample commands:**
```bash
# Wave 0: Backend tests
cd apps/api && uv run pytest tests/api/test_executions_*.py tests/api/test_keys_*.py tests/api/test_graph_*.py -v

# Wave 1: Strategy Vault
cd apps/web && pnpm test:run -- strategy-vault --watch=false

# Wave 2: Engine Room logs
cd apps/web && pnpm test:run -- engine-room --watch=false

# Wave 3: Focus Mode + integration
cd apps/web && pnpm test:run -- FocusMode.e2e.test.tsx phases/Phase08Integration.test.tsx --watch=false
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| **Snapshot bloat** (storing full WS event history) | Design decision: store milestones only (max 7). Validation test confirms 100-event execution produces exactly 7 milestones without loss |
| **Focus Mode re-trapping** (user exits, auto-activates again) | userOverride idempotency: once true, stays true until task.state='complete' |
| **Virtual scrolling flicker** (overscan too small) | Configure overscan=10 (react-virtuoso default). Performance test: 5000+ log lines, Page Down spam → no flicker |
| **React Flow layout thrash** (dagre re-run on every brain update) | Separation: layout cached on fetch, brain state updates only change node.data (color/glow), never position |
| **Log filter state lost on reload** | logFilterStore persisted to localStorage, restored on mount |
| **API key leak in localStorage** | Design: full key never stored, only shown in response body. Frontend must copy immediately |

---

## Deliverables Checklist

**After Wave 0 (08-01):**
- ✅ GraphEdge enhanced with sub-graphs
- ✅ Execution history endpoints functional
- ✅ API key endpoints functional
- ✅ Brain YAML retrieval working
- ✅ All backend tests passing

**After Wave 1 (08-02):**
- ✅ Strategy Vault pages live
- ✅ ReplayStore managing snapshot state
- ✅ SmartMarkdown rendering brain outputs
- ✅ Snapshot Scrubber UI complete
- ✅ All frontend component tests passing

**After Wave 2 (08-03):**
- ✅ Engine Room logs page live
- ✅ Virtual scrolling rendering logs efficiently
- ✅ Filter toggles working
- ✅ Isolation mode via badge click
- ✅ Brain YAML viewer dialog functional

**After Wave 3 (08-04):**
- ✅ Focus Mode auto-activates on task start
- ✅ [F]/[Esc] escape hatch working
- ✅ API key CRUD UI complete
- ✅ Full integration test passing
- ✅ v2.1 milestone complete (Phase 05-08 all done)

---

## Next Steps

### Immediate (Phase 08 Execution)
Execute plans in order: `/gsd:execute-phase 08` → automated task distribution across 4 waves

### Post-Phase 08 (v2.2 Planning)
- **v2.2 Brain Agents:** Convert manual skill workflows to autonomous Claude Code subagents
- **v2.2 Agent Memory:** Each brain maintains domain-specific BRAIN-FEED.md for persistent expertise
- **v2.2 Inter-Agent Coordination:** Agents coordinate for cross-domain decisions

### Future (v3.0 Custom Framework)
- Replace GSD with MasterMind's own declarative workflow DSL
- Per-agent RAG (ChromaDB/Qdrant) for persistent domain knowledge
- OpenClaw integration (routing, channels, voice, native apps)

---

**Planning completed:** 2026-03-23
**Planner model:** Haiku 4.5
**Total planning time:** ~45 minutes
**Plans created:** 4 (08-01, 08-02, 08-03, 08-04)
**Tasks detailed:** 32
**Requirements mapped:** 6/6 (100%)
**Files to modify:** 38

Ready for `/gsd:execute-phase 08` 🚀
