---
phase: 11-smoke-tests
plan: "01"
subsystem: testing
tags: [smoke-tests, feed-isolation, sentinel-script, brain-7, synthetic-baselines, bash, git]

# Dependency graph
requires:
  - phase: 10-brain-feed-split
    provides: domain BRAIN-FEED files that Sentinel Script monitors for isolation violations
  - phase: 09-baselines-agent-authoring
    provides: baseline-schema.md and baseline-01 reference structure used by synthetic files

provides:
  - Sentinel Script (tests/smoke/verify_feed_isolation.sh) — git stash/diff feed isolation verifier
  - SYNTHETIC-T1-400s baseline — Brain #7 Test A: Hard Stop detection for T1 > 300s
  - SYNTHETIC-PROSE baseline — Brain #7 Test B: Structured Output Violation detection

affects: [11-02, 11-03, 11-04, phase-12-parallel-dispatch]

# Tech tracking
tech-stack:
  added: [bash scripts, git stash protocol]
  patterns: [Sentinel Script pattern for agent containment verification, synthetic baseline pattern for Brain #7 regression testing]

key-files:
  created:
    - tests/smoke/verify_feed_isolation.sh
    - tests/baselines/agent-run-SYNTHETIC-T1-400s.md
    - tests/baselines/agent-run-SYNTHETIC-PROSE.md
  modified: []

key-decisions:
  - "Sentinel Script uses git stash (not branch) for pre/post diff comparison — WSL2-safe per RESEARCH.md Pitfall 4"
  - "Global BRAIN-FEED.md check uses anchored regex (^\.planning/BRAIN-FEED\.md$) to avoid false matches on domain feeds"
  - "No-feed-modified outcome is a PASS, not a FAIL — adversarial agents correctly refusing to write produce no diff"
  - "Synthetic baselines use real context_id and plausible content so Brain #7 processes schema fields rather than dismissing as test data"

patterns-established:
  - "Sentinel Script pattern: git stash → human dispatch → git diff → validate → git stash pop"
  - "Synthetic baseline pattern: schema-compliant YAML + real-looking content + exactly ONE anomaly per file"

requirements-completed: [AGT-04]

# Metrics
duration: 2min
completed: "2026-03-29"
---

# Phase 11 Plan 01: Wave 0 Scaffolding Summary

**Sentinel Script (git stash/diff feed isolation verifier) + 2 synthetic Brain #7 test baselines created with exactly one anomaly each**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-29T16:29:19Z
- **Completed:** 2026-03-29T16:31:38Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Created `tests/smoke/verify_feed_isolation.sh` — the Sentinel Script implementing the locked protocol: pre-flight check → git stash → human dispatch → git diff → global feed anchored check → unexpected files check → git stash pop, with 4 exit codes (0/1/2/3)
- Created `agent-run-SYNTHETIC-T1-400s.md` — schema-compliant Brain #4 baseline with T1=400s as the sole anomaly (exceeds 300s profitability threshold), for Brain #7 Hard Stop detection test
- Created `agent-run-SYNTHETIC-PROSE.md` — schema-compliant Brain #2 baseline with unstructured prose replacing structured sections as the sole anomaly, for Brain #7 Structured Output Violation detection test

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Sentinel Script + tests/smoke/ directory** - `555ed2c` (feat)
2. **Task 2: Create synthetic baseline files for Brain #7 tests** - `e6c46f7` (feat)

**Plan metadata:** (docs commit — see below)

## Files Created/Modified

- `tests/smoke/verify_feed_isolation.sh` — Sentinel Script, executable, 87 lines, implements 4-step git stash/diff protocol with 4 exit codes
- `tests/baselines/agent-run-SYNTHETIC-T1-400s.md` — Test A for Brain #7: T1=400s anomaly detection
- `tests/baselines/agent-run-SYNTHETIC-PROSE.md` — Test B for Brain #7: unstructured prose anomaly detection

## Decisions Made

- Used anchored regex `^\.planning/BRAIN-FEED\.md$` for global feed check — substring match would incorrectly flag domain feeds like `BRAIN-FEED-04-frontend.md`
- Synthetic baselines use the real `context_id` from existing baselines (`bcfb93803e7ca5ca1c6b99c554fd190c77196f5a`) to ensure schema field comparisons work correctly
- Prose anomaly in SYNTHETIC-PROSE is written as one long run-on paragraph (~200 words, no section headers, no bullets) — Brain #7 must detect absence of structural markers, not just bad content

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Wave 0 scaffolding is complete — Plans 02 and 03 can now use `verify_feed_isolation.sh` to verify feed isolation during real brain dispatches
- Plan 04 has both synthetic inputs ready for Brain #7 Hard Stop and Structured Output Violation tests
- `tests/smoke/` directory established as the smoke test home for all Phase 11 verification scripts

---
*Phase: 11-smoke-tests*
*Completed: 2026-03-29*
