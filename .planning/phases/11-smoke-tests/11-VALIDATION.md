---
phase: 11
slug: smoke-tests
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-29
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual execution + Sentinel Script (bash) + git diff |
| **Config file** | `tests/smoke/verify_feed_isolation.sh` (Wave 0 creates it) |
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
| 11-01-01 | 01 | 0 | AGT-04 | scaffold | `test -f tests/smoke/verify_feed_isolation.sh` | ❌ W0 | ⬜ pending |
| 11-01-02 | 01 | 0 | AGT-04 | scaffold | `test -f tests/baselines/agent-run-SYNTHETIC-T1-400s.md` | ❌ W0 | ⬜ pending |
| 11-01-03 | 01 | 0 | AGT-04 | scaffold | `test -f tests/baselines/agent-run-SYNTHETIC-PROSE.md` | ❌ W0 | ⬜ pending |
| 11-02-01 | 02 | 1 | AGT-04 | manual | Sentinel Script → PASS for brain-04-frontend | ❌ W0 | ⬜ pending |
| 11-02-02 | 02 | 1 | AGT-04 | manual | Sentinel Script → PASS for brain-05-backend | ❌ W0 | ⬜ pending |
| 11-02-03 | 02 | 1 | AGT-04 | manual | Sentinel Script → PASS for brain-06-qa | ❌ W0 | ⬜ pending |
| 11-03-01 | 03 | 2 | AGT-04 | manual | Sentinel Script → PASS for brain-01-product | ❌ W0 | ⬜ pending |
| 11-03-02 | 03 | 2 | AGT-04 | manual | Sentinel Script → PASS for brain-02-ux | ❌ W0 | ⬜ pending |
| 11-03-03 | 03 | 2 | AGT-04 | manual | Sentinel Script → PASS for brain-03-ui | ❌ W0 | ⬜ pending |
| 11-04-01 | 04 | 3 | AGT-04 | manual | Brain #7 Test A: Hard Stop cited from BRAIN-FEED-07 | N/A | ⬜ pending |
| 11-04-02 | 04 | 3 | AGT-04 | manual | Brain #7 Test B: Structured Output Violation rejected | N/A | ⬜ pending |
| 11-04-03 | 04 | 4 | AGT-04 | scaffold | `test -f .planning/phases/11-smoke-tests/11-VERIFICATION.md` | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/smoke/` directory created
- [ ] `tests/smoke/verify_feed_isolation.sh` — Sentinel Script (covers AGT-04 feed isolation)
- [ ] `tests/baselines/agent-run-SYNTHETIC-T1-400s.md` — Brain #7 Test A (T1=400s Hard Stop)
- [ ] `tests/baselines/agent-run-SYNTHETIC-PROSE.md` — Brain #7 Test B (Structured Output Violation)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Brain reads both feeds (global + domain) | AGT-04 | Agent output inspection — no automated way to verify MCP reads | Look for `[IMPLEMENTED REALITY]` block in agent output showing feed contents loaded |
| Adversarial rejection with Oracle Pattern citation | AGT-04 | Human judgment: file name + section name present? | Check rejection output for `Source: <file> > <section>` pattern |
| Brain #7 Hard Stop at T1=400s | AGT-04 | Brain #7 agent dispatch is manual | Dispatch with SYNTHETIC-T1-400s.md in scope. Verify output cites `BRAIN-FEED-07 > Hard Stop Thresholds: T1 > 300s` |
| Brain #7 Structured Output Violation | AGT-04 | Brain #7 agent dispatch is manual | Dispatch with SYNTHETIC-PROSE.md. Verify output cites `global-protocol.md > Output Format` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency: per-agent (Sentinel runs immediately after each dispatch)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
