---
phase: 12
slug: parallel-dispatch-command-update
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-30
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (backend) |
| **Config file** | `apps/api/pytest.ini` |
| **Quick run command** | `cd apps/api && uv run pytest tests/brain_agents/ -x -q` |
| **Full suite command** | `cd apps/api && uv run pytest -x -q` |
| **Estimated runtime** | ~45 seconds (brain_agents subset) / ~120s full |

---

## Sampling Rate

- **After every task commit:** Run `cd apps/api && uv run pytest tests/brain_agents/ -x -q`
- **After every plan wave:** Run `cd apps/api && uv run pytest -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 45 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 12-W0-01 | 00 | 0 | DISP-01 | script | `bash apps/api/scripts/verify_feed_isolation.sh` | ❌ W0 | ⬜ pending |
| 12-W0-02 | 00 | 0 | DISP-01 | unit | `cd apps/api && uv run pytest tests/brain_agents/test_parallel_dispatch.py -x -q` | ❌ W0 | ⬜ pending |
| 12-01-01 | 01 | 1 | DISP-01 | manual | Invoke `mm:brain-context` → observe simultaneous agent execution in UI | ✅ | ⬜ pending |
| 12-01-02 | 01 | 1 | DISP-01 | script | `bash apps/api/scripts/verify_feed_isolation.sh --check barrier-order` | ✅ after W0 | ⬜ pending |
| 12-01-03 | 01 | 1 | DISP-01 | script | `bash apps/api/scripts/verify_feed_isolation.sh --check crosstalk` | ✅ after W0 | ⬜ pending |
| 12-02-01 | 02 | 1 | DISP-02 | unit | `cd apps/api && uv run pytest tests/brain_agents/test_sync_injection.py -x -q` | ❌ W0 | ⬜ pending |
| 12-02-02 | 02 | 1 | DISP-02 | manual | SYNC characterization: break BF-05 → verify Brain #4 cites injected fragment | ✅ | ⬜ pending |
| 12-03-01 | 03 | 2 | DISP-01 | manual | Brain #7 barrier: verify Brain #7 receives domain outputs, not empty context | ✅ | ⬜ pending |
| 12-04-01 | 04 | 2 | DISP-01 | grep | `grep -r "mcp__notebooklm" .claude/skills/mm/ && echo FAIL || echo PASS` | ✅ | ⬜ pending |
| 12-04-02 | 04 | 2 | DISP-02 | grep | `grep -c "Task(" .claude/skills/mm/brain-context/moment-2.md` | ✅ | ⬜ pending |
| 12-05-01 | 05 | 3 | DISP-01 | unit | `cd apps/api && uv run pytest tests/brain_agents/test_sentinel.py -x -q` | ✅ | ⬜ pending |
| 12-05-02 | 05 | 3 | DISP-01 | manual | T1 timing: invoke full parallel dispatch → measure wall time < 120s | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/brain_agents/test_parallel_dispatch.py` — stubs for DISP-01 parallel dispatch verification
- [ ] `tests/brain_agents/test_sync_injection.py` — stubs for DISP-02 SYNC cross-talk isolation
- [ ] `apps/api/scripts/verify_feed_isolation.sh` extended with `--check barrier-order` and `--check crosstalk` flags (the script exists, needs 2 new checks)

*Note: Existing pytest infrastructure covers all other phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Simultaneous agent execution in Claude Code UI | DISP-01 | Observable only in UI — no API to inspect dispatch timing | Invoke `mm:brain-context Momento 2`, observe multiple agents launch in single orchestrator message |
| Brain #7 receives domain outputs as context | DISP-01 | Behavioral — depends on Claude Code Agent tool runtime | Invoke full flow, inspect Brain #7 prompt includes domain agent return values |
| T1 wall-clock timing < 120s | DISP-01 | Clock-based — requires real execution | Time `mm:brain-context Momento 2` end-to-end with stopwatch |
| SYNC characterization: BF-05 break → Brain #4 cites fragment | DISP-02 | Requires deliberate feed mutation and manual inspection | Temporarily edit BF-05-WS-AUTH section, invoke Brain #4, verify citation |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 45s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
