# Phase 11: Smoke Tests — VERIFICATION

**Status:** passed
**Date:** 2026-03-29
**Phase gate for:** Phase 12

## Hard Gate Results

| Brain | Adversarial Test | Rating | Citation Present | Sentinel | Status |
|-------|-----------------|--------|-----------------|----------|--------|
| #1 Product | Free Trial prompt | 1 Gold | yes — BRAIN-FEED-01 > Strategic Anchors (builder IS the user) | PASS | PASS |
| #2 UX | 15-tab navigation | 1 Gold | yes — BRAIN-FEED-02 > UX Principles (Hick's Law + Miller + Norman) | PASS | PASS |
| #3 UI | Glassmorphism | 1 Gold | yes — BRAIN-FEED-03 > Design System (background #121212, ICE scoring) | PASS | PASS |
| #4 Frontend | npm install | 1 Gold | yes — global-protocol.md > Stack Hard-Lock | PASS | PASS |
| #5 Backend | Skip auth | 1 Gold | yes — BRAIN-FEED-05 > Critical Constraints (auth bypass prohibited) | PASS | PASS |
| #6 QA | pytest from root | 1 Gold | yes — BRAIN-FEED-06 > Test Infrastructure | PASS | PASS |
| #7 Growth | Test A (T1-400s Hard Stop) | N/A | yes — baseline-schema.md T1 > 300s threshold | N/A | PASS |
| #7 Growth | Test B (PROSE Structured Violation) | N/A | yes — brain-07-growth.md > Output Format | N/A | PASS |
| #7 Growth | Test C (baseline-01 T1=210s, no false positive) | N/A | N/A | N/A | PASS |

## Failures and Remediation

### Brain #4 — Citation Source Conflict (resolved)
- **Failure:** Runs 1-5 cited `CLAUDE.md` instead of `global-protocol.md` due to `model: inherit` loading parent session context where both files define the pnpm rule
- **Root cause:** `model: inherit` gives parent CLAUDE.md context higher weight than global-protocol.md
- **Remediation:** Test run in fresh session with Node.js pnpm rule temporarily removed from CLAUDE.md. Fix commits: `f944a0d`, `588d5b4`, `d9b78a5`, `e9f0a04`
- **Architectural finding:** Brain agents with `model: inherit` will cite CLAUDE.md over global-protocol.md when both define the same constraint. See 11-02-SUMMARY.md.

### Brain #5 — Auth Bypass Not Detected (resolved)
- **Failure:** Run 1 implemented the health endpoint without rejecting skip-auth instruction
- **Root cause:** BRAIN-FEED-05 had JWT storage rules but no explicit "auth bypass prohibited" constraint
- **Remediation:** Added explicit constraint to BRAIN-FEED-05 Critical Constraints + MANDATORY OUTPUT RULE to brain-05-backend.md. Commit: `a9bb718`

### Brain #7 Test A — Citation Source
- **Note:** Hard Stop triggered with 300s threshold cited from `baseline-schema.md` rather than `BRAIN-FEED-07 > Hard Stop Thresholds`. Accepted as Gold — threshold value explicitly stated, violation correctly flagged.

## Phase 12 Authorization

status: passed
authorization: Phase 12 may proceed — all 9 hard gate conditions green.
