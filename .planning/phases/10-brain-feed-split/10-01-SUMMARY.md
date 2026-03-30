---
phase: 10-brain-feed-split
plan: "01"
subsystem: brain-feed-architecture
tags: [verification-scripts, domain-feeds, engineering-niche, sync-pointers, conservation-law]
dependency_graph:
  requires: []
  provides: [verify_feed_conservation.py, verify_feed_paths.py, verify_global_purity.py, BRAIN-FEED-04-frontend.md, BRAIN-FEED-05-backend.md, BRAIN-FEED-06-qa.md]
  affects: [phase-10-02, phase-10-03, phase-11-smoke-tests]
tech_stack:
  added: []
  patterns: [conservation-law-with-known-deletions, migration-mode-flag, sync-pointer-format, critical-constraints-guardrail-first]
key_files:
  created:
    - .planning/verify_feed_conservation.py
    - .planning/verify_feed_paths.py
    - .planning/verify_global_purity.py
    - .planning/BRAIN-FEED-04-frontend.md
    - .planning/BRAIN-FEED-05-backend.md
    - .planning/BRAIN-FEED-06-qa.md
  modified: []
decisions:
  - "verify_feed_conservation.py needs --strict flag: migration mode allows global+domain duplicates (expected until Plan 10-03 purges global); strict mode enforces zero duplicates post-cleanup"
  - "verify_feed_paths.py exits 1 through Plan 10-01: only 4 of 7 feeds exist (BRAIN-FEED-01 + 04/05/06); 02/03/07 created in Plan 10-02"
  - "BRAIN-FEED-04 anti-patterns includes ICE ≥ 15 (frontend animation policy) — correctly owned by Frontend, not global"
metrics:
  duration: "3 minutes"
  completed_date: "2026-03-29"
  tasks_completed: 3
  files_created: 6
---

# Phase 10 Plan 01: Engineering Niche Domain Feeds + Verification Safety Net Summary

Wave 0 verification safety net (3 Python scripts) + Engineering Niche domain feeds for Brains #4/5/6 with SYNC pointer cross-references and conservation law enforcement.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create 3 verification scripts (Wave 0) | 0618573 | verify_feed_conservation.py, verify_feed_paths.py, verify_global_purity.py |
| 2 | Create Engineering Niche domain feeds (#4/#5/#6) | 77c88de | BRAIN-FEED-04-frontend.md, BRAIN-FEED-05-backend.md, BRAIN-FEED-06-qa.md |
| 3 | Engineering Niche smoke test | auto-approved | — (checkpoint:human-verify, auto_advance=true) |

## What Was Built

### Verification Safety Net (3 scripts)

**verify_feed_conservation.py** — Conservation law assertion with KNOWN_DELETIONS=2.
- Migration mode (default): allows entries in both global and domain feeds — expected until Plan 10-03 purges global
- Strict mode (`--strict`): enforces zero duplicates — for Plan 10-03+ verification
- Set equality: `original - KNOWN_DELETIONS == union(domain + global)` — no entries lost in migration

**verify_feed_paths.py** — Path existence check.
- Scans all `.claude/agents/mm/**/*.md` for `BRAIN-FEED-\d{2}-[\w-]+\.md` references
- Asserts every referenced file exists on disk — catches silent empty-context failures

**verify_global_purity.py** — Domain vocabulary linter.
- Word-boundary matching (`\bZustand\b`, `\bpytest\b`, etc.) — prevents false positives in Stack table
- Table row skip (`line.startswith("|")`) — Stack table exemption
- Silent pass / verbose fail — CI-friendly output

### Engineering Niche Domain Feeds

**BRAIN-FEED-04-frontend.md** (4 sections + SYNC block):
- State & Rendering Engine: Zustand Map, useBrainState(id), RAF batching, 4 Active Constraints
- React Flow Internals: NODE_TYPES/EDGE_TYPES module-level, dagre once, @layer base CSS
- Performance & Quality Radar: Phase 05/06 learnings, animation policy (opacity+transform ONLY locked)
- Anti-patterns (Frontend): 6 entries copied verbatim from BRAIN-FEED.md
- 4 SYNC pointers: BF-05-001 (WS token handoff), BF-05-002 (httpOnly cookie), BF-05-003 (Zod contracts), BF-05-004 (error shape)

**BRAIN-FEED-05-backend.md** (Critical Constraints FIRST):
- Critical Constraints (Non-Negotiable): uv only, apps/api pytest, httpOnly JWT, WS handoff
- Auth & Security: 4 verbatim bullets from BRAIN-FEED.md
- API Design: pagination, TanStack Query, selectinload (required pattern), IDOR protection
- 1 SYNC pointer: BF-06-001 (pytest infrastructure → Brain #6)

**BRAIN-FEED-06-qa.md** (3 sections):
- Test Infrastructure: pytest from apps/api/, Vitest over Jest, WS_SLOS guardrails
- Baseline Anchors: delta_velocity=4 adversarial signal, 575+407 test suite baseline
- Anti-patterns (QA): root pytest fix

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] verify_feed_conservation.py incorrectly failed during migration phase**
- **Found during:** Task 2 verification
- **Issue:** Script checked `all_domain & global_entries` and exited 1 on any overlap. During Plans 10-01/10-02, entries intentionally exist in both global and domain feeds — cleanup happens in Plan 10-03.
- **Fix:** Added `--strict` flag. Default mode (migration) prints INFO for duplicates but exits 0. Strict mode enforces zero duplicates for post-Plan 10-03 use.
- **Files modified:** `.planning/verify_feed_conservation.py`
- **Commit:** 77c88de (included in Task 2 commit)

## Verification Results

```
Conservation: OK: 50 original entries. 45 in domain feeds, 50 in global. KNOWN_DELETIONS=2. Conservation law holds.
SYNC markers in feed-04: 4/4 — [BF-05-001, BF-05-002, BF-05-003, BF-05-004]
Feed-05 first section: ## Critical Constraints (Non-Negotiable)
Feed-06 has pytest: True
Feed-06 has Vitest: True
```

Note: verify_feed_paths.py exits 1 (MISSING: BRAIN-FEED-02, 03, 07) — expected, those are Plan 10-02 scope. Will pass after Plan 10-02 completes.
Note: verify_global_purity.py exits 1 — expected until Plan 10-03 cleans global feed.

## Self-Check: PASSED

Files exist:
- .planning/verify_feed_conservation.py — FOUND
- .planning/verify_feed_paths.py — FOUND
- .planning/verify_global_purity.py — FOUND
- .planning/BRAIN-FEED-04-frontend.md — FOUND
- .planning/BRAIN-FEED-05-backend.md — FOUND
- .planning/BRAIN-FEED-06-qa.md — FOUND

Commits:
- 0618573 (Wave 0 verification scripts) — FOUND
- 77c88de (Engineering domain feeds) — FOUND
