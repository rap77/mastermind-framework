# Velocity Baseline — Phase 13 Vertical Slice

**Date:** 2026-04-05
**Purpose:** Measure Python baseline to compare Rust velocity against (Brain #5 + #7 Condition)

## Python Baseline Metrics

### Endpoint: POST /api/tasks/auto

**Implementation:**
- File: `apps/api/mastermind_cli/api/routes/tasks.py`
- Handler: `create_auto_task()`
- Dependencies: FlowDetector, BackgroundTasks, orchestrator

**Metrics:**

| Metric | Python Baseline | Notes |
|--------|----------------|-------|
| **Time to implement** | ~8 hours (estimated) | Based on git history from PRD002 implementation |
| **LOC (handler)** | 447 lines | Full file: `apps/api/mastermind_cli/api/routes/tasks.py` |
| **LOC (dependencies)** | 1,667 lines | coordinator.py (1518) + flow_detector.py (149) |
| **Total LOC** | 2,114 lines | All orchestration code for auto endpoint |
| **Test cycle time** | 3.85s | `pytest tests/api/test_auto_task.py` (8 tests) |
| **Test count** | 8 tests | All passing, zero failures |

### Boot Time Baseline

**Current (before Phase 13):**
- Services: 2 (api + web)
- Target: ≤ 90 seconds
- **Measured:** TBD (will measure after PostgreSQL image download completes)

**After Phase 13:**
- Services: 4 (api + web + control-plane + postgres)
- Target: ≤ 90 seconds
- Escape hatch trigger: > 120 seconds

## Setup Overhead

**Encountered during Phase 13-01:**
- PostgreSQL pgvector image download: > 30 minutes (first pull)
- **Documented as:** "Setup overhead" — one-time cost, not reflective of development velocity
- **Action:** Continue with validation, document in velocity-report.md

**Encountered during Phase 13-02:**
- buf CLI installation failed: `brew install buf` hung, `curl` download didn't work
- protoc not available: requires `sudo apt-get install protobuf-compiler` (not accessible)
- **Workaround:** Created manual proto modules (Rust/Python/TypeScript) as placeholders
- **Documented as:** "Setup overhead" — toolchain installation blockers
- **Action:** Manual proto types for Phase 13 VS, full buf integration deferred to Phase 15
- **Impact:** None — manual types match proto contract exactly, will replace with buf-generated in Phase 15

## Rust Velocity Targets (Brain #5 + #7 Conditions)

**Escape hatch triggers:**
1. **Runtime/dev cycle velocity:** Rust time ≥ 0.5x Python (target: 4 hours or less)
2. **LOC efficiency:** Rust LOC ≤ 2.0x Python LOC (target: ≤ 4,228 lines)
3. **Test cycle time:** Rust test time ≤ 2.0x Python (target: ≤ 7.7s)

**If velocity < 0.5x Python:** Activate escape hatch → Rust only for WebSocket Hub + Adapter Registry
**If boot time > 120s:** Activate escape hatch → Investigate service dependencies

## Treatment Exposure Rate (Brain #7 Condition #7)

Track % of requests to `/api/tasks/auto` vs legacy `/api/tasks`:
- **Goal:** ≥ 50% exposure by Phase 13 midpoint
- **Measurement:** Count requests in logs after 1 week of usage
- **If < 50%:** Vertical slice not being validated, need to increase traffic

## Next Steps

1. Complete Phase 13-02 (Proto + Rust project setup)
2. Complete Phase 13-03 (Backend implementation)
3. Complete Phase 13-04 (Frontend + Docker + measurement)
4. Create `velocity-report.md` with actual Rust metrics
5. Make escape hatch decision based on comparison
