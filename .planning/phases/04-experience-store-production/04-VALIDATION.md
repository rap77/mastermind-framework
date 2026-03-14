---
phase: 04
slug: experience-store-production
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-14
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + aiosqlite |
| **Config file** | `pyproject.toml` (existing from Phase 1-3) |
| **Quick run command** | `uv run pytest tests/unit/ -v -k "not integration"` |
| **Full suite command** | `uv run pytest tests/ -v --cov=mastermind_cli` |
| **Estimated runtime** | ~45 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/unit/ -v -k "new_module"`
- **After every plan wave:** Run `uv run pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | ARCH-01 | unit | `uv run pytest tests/experience/test_schema.py` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | ARCH-01 | unit | `uv run pytest tests/experience/test_redaction.py` | ❌ W0 | ⬜ pending |
| 04-01-03 | 01 | 1 | ARCH-01 | unit | `uv run pytest tests/experience/test_archive.py` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 1 | ARCH-02 | unit | `uv run pytest tests/protocol/test_envelope.py` | ❌ W0 | ⬜ pending |
| 04-02-02 | 02 | 1 | ARCH-02 | integration | `uv run pytest tests/integration/test_brain_protocol.py` | ❌ W0 | ⬜ pending |
| 04-03-01 | 03 | 2 | BC-01, BC-02 | integration | `uv run pytest tests/integration/test_backward_compat.py` | ❌ W0 | ⬜ pending |
| 04-03-02 | 03 | 2 | BC-03 | integration | `uv run pytest tests/integration/test_semantic_regression.py` | ❌ W0 | ⬜ pending |
| 04-04-01 | 04 | 2 | TEST-01, TEST-02 | e2e | `uv run pytest tests/e2e/test_multi_user.py` | ✅ existing | ⬜ pending |
| 04-04-02 | 04 | 2 | TEST-03 | e2e | `uv run pytest tests/e2e/test_mcp_integration.py` | ✅ existing | ⬜ pending |
| 04-05-01 | 05 | 3 | TEST-04 | contract | `uv run pytest .github/workflows/ci.yml` (dry-run) | ❌ W0 | ⬜ pending |
| 04-05-02 | 05 | 3 | TEST-05 | contract | `uv run pre-commit run --all-files` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/experience/__init__.py` — experience module tests
- [ ] `tests/experience/test_schema.py` — ExperienceRecord schema stubs
- [ ] `tests/experience/test_redaction.py` — PII redaction stubs
- [ ] `tests/experience/test_archive.py` — archive rotation stubs
- [ ] `tests/protocol/__init__.py` — brain-to-brain protocol tests
- [ ] `tests/protocol/test_envelope.py` — BrainMessage envelope stubs
- [ ] `tests/integration/test_backward_compat.py` — 23 brains × 5 briefs stubs
- [ ] `tests/integration/test_semantic_regression.py` — semantic similarity stubs
- [ ] `tests/utils/semantic_diff.py` — sentence-transformers utility
- [ ] `scripts/archive_logs.sh` — archive rotation script
- [ ] `.github/workflows/ci.yml` — GitHub Actions CI pipeline
- [ ] `.pre-commit-config.yaml` — pre-commit hooks (trufflehog)
- [ ] `Dockerfile` — container image for deployment

*Existing infrastructure from Phases 1-3: pytest, aiosqlite, Pydantic, SQLite database*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| PII redaction in DB | ARCH-01 | Visual verification of redaction format | 1. Run `mm orchestrate` with test brief containing API key. 2. Query SQLite: `SELECT * FROM experience_records LIMIT 1`. 3. Verify `[REDACTED_SECRET]` in output_json. |
| Archive rotation | ARCH-01 | File system verification | 1. Run `scripts/archive_logs.sh`. 2. Verify `/archive/mm-logs-YYYYMMDD.jsonl.gz` exists. 3. Verify records deleted from DB: `SELECT COUNT(*) FROM experience_records WHERE timestamp < datetime('now', '-30 days')`. |
| Brain cascade | ARCH-02 | Multi-brain orchestration | 1. Run flow with Brain #1 → #3 → #7. 2. Verify outputs cascade correctly. 3. Check Dashboard shows real-time updates. |
| v1.3.0 CLI compatibility | BC-01 | Legacy command validation | 1. Run `mm brain status` (v1.3.0 command). 2. Run `mm source list`. 3. Verify all commands work unchanged. |
| Pre-commit secret block | TEST-05 | Git hook interaction | 1. Add fake API key to file. 2. Run `git commit`. 3. Verify commit blocked with trufflehog error. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
