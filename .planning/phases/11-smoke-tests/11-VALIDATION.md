---
phase: 11
slug: smoke-tests
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-29
audited: 2026-03-29
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual execution + Sentinel Script (bash) + git diff |
| **Config file** | `tests/smoke/verify_feed_isolation.sh` |
| **Quick run command** | `bash tests/smoke/verify_feed_isolation.sh <brain-id> <expected-feed>` |
| **Full suite command** | Sentinel Script × 6 dispatches + Brain #7 × 2 synthetic tests + verify_feed_*.py |
| **Estimated runtime** | ~90 minutes (manual observation + agent dispatch time) |

---

## Sampling Rate

- **After every agent dispatch:** Run Sentinel Script immediately
- **After every wave:** Run `cd .planning && uv run python3 verify_feed_conservation.py && uv run python3 verify_feed_paths.py && uv run python3 verify_global_purity.py`
- **Before `/gsd:verify-work`:** VERIFICATION.md must exist with `status: passed`
- **Max feedback latency:** Per-agent (not per-task)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 0 | AGT-04 | scaffold | `test -f tests/smoke/verify_feed_isolation.sh` | ✅ | ✅ green |
| 11-01-02 | 01 | 0 | AGT-04 | scaffold | `test -f tests/baselines/agent-run-SYNTHETIC-T1-400s.md` | ✅ | ✅ green |
| 11-01-03 | 01 | 0 | AGT-04 | scaffold | `test -f tests/baselines/agent-run-SYNTHETIC-PROSE.md` | ✅ | ✅ green |
| 11-02-01 | 02 | 1 | AGT-04 | manual | Sentinel Script → PASS for brain-04-frontend | ✅ | ✅ green |
| 11-02-02 | 02 | 1 | AGT-04 | manual | Sentinel Script → PASS for brain-05-backend | ✅ | ✅ green |
| 11-02-03 | 02 | 1 | AGT-04 | manual | Sentinel Script → PASS for brain-06-qa | ✅ | ✅ green |
| 11-03-01 | 03 | 2 | AGT-04 | manual | Sentinel Script → PASS for brain-01-product | ✅ | ✅ green |
| 11-03-02 | 03 | 2 | AGT-04 | manual | Sentinel Script → PASS for brain-02-ux | ✅ | ✅ green |
| 11-03-03 | 03 | 2 | AGT-04 | manual | Sentinel Script → PASS for brain-03-ui | ✅ | ✅ green |
| 11-04-01 | 04 | 3 | AGT-04 | manual | Brain #7 Test A: Hard Stop cited from BRAIN-FEED-07 | N/A | ✅ green |
| 11-04-02 | 04 | 3 | AGT-04 | manual | Brain #7 Test B: Structured Output Violation rejected | N/A | ✅ green |
| 11-04-03 | 04 | 4 | AGT-04 | scaffold | `test -f .planning/phases/11-smoke-tests/11-VERIFICATION.md` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/smoke/` directory created
- [x] `tests/smoke/verify_feed_isolation.sh` — Sentinel Script (covers AGT-04 feed isolation)
- [x] `tests/baselines/agent-run-SYNTHETIC-T1-400s.md` — Brain #7 Test A (T1=400s Hard Stop)
- [x] `tests/baselines/agent-run-SYNTHETIC-PROSE.md` — Brain #7 Test B (Structured Output Violation)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Status |
|----------|-------------|------------|--------|
| Brain reads both feeds (global + domain) | AGT-04 | Agent output inspection — no automated way to verify MCP reads | ✅ Confirmed via VERIFICATION.md |
| Adversarial rejection with Oracle Pattern citation | AGT-04 | Human judgment: `Source: <file> > <section>` pattern present | ✅ All 6 brains: Rating 1 Gold |
| Brain #7 Hard Stop at T1=400s | AGT-04 | Brain #7 agent dispatch is manual | ✅ Test A PASS — threshold cited |
| Brain #7 Structured Output Violation | AGT-04 | Brain #7 agent dispatch is manual | ✅ Test B PASS — violation rejected |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency: per-agent (Sentinel runs immediately after each dispatch)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** ✅ APPROVED — 2026-03-29

---

## Validation Audit 2026-03-29

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 12 (status updated from pending → green) |
| Escalated | 0 |

*Audit note: VALIDATION.md created pre-execution with all statuses as pending. All 12 tasks verified green post-execution: 4 automated file-existence checks pass, 8 manual tasks confirmed via 11-VERIFICATION.md (status: passed, all 9 gates green).*
