---
phase: 1
slug: type-safety-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-13
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest >=9.0.2 |
| **Config file** | pyproject.toml |
| **Quick run command** | `uv run pytest tests/unit/test_types.py -x -v` |
| **Full suite command** | `uv run pytest tests/ --cov=mastermind_cli --cov-report=term-missing && uv run mypy mastermind_cli/` |
| **Estimated runtime** | ~120-180 seconds (full suite + type check) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/unit/test_*.py -x --tb=short` (unit tests only, <30s)
- **After every plan wave:** Run `uv run pytest tests/ --cov=mastermind_cli --cov-report=term-missing && uv run mypy mastermind_cli/` (full suite + type check, ~2-3 min)
- **Before `/gsd:verify-work`:** Full suite must be green + mypy --strict on all migrated modules
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | TS-01 | unit | `pytest tests/unit/test_types.py -x -v` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | TS-01 | unit | `pytest tests/unit/test_types.py -x -v` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | TS-01 | unit | `pytest tests/unit/test_types.py -x -v` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 2 | TS-02 | type | `mypy mastermind_cli/types/ --strict` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 2 | TS-02 | type | `mypy mastermind_cli/orchestrator/coordinator.py --strict` | ❌ W0 | ⬜ pending |
| 01-02-03 | 02 | 2 | TS-02 | type | `mypy mastermind_cli/ --strict` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 3 | TS-03 | integration | `pytest tests/integration/test_mcp_wrapper.py -x -v` | ❌ W0 | ⬜ pending |
| 01-03-02 | 03 | 3 | TS-04 | unit | `pytest tests/unit/test_validation.py -x -v` | ❌ W0 | ⬜ pending |
| 01-03-03 | 03 | 3 | TS-05 | unit | `pytest tests/unit/test_error_messages.py -x -v` | ❌ W0 | ⬜ pending |
| 01-03-04 | 03 | 3 | TS-06 | integration | `pytest tests/integration/test_cli_coordinator.py -x -v` | ❌ W0 | ⬜ pending |
| 01-03-05 | 03 | 3 | TS-07 | unit | `pytest tests/unit/test_brain_normalization.py -x -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

**Critical files to create before implementation:**

- [ ] `mastermind_cli/types/__init__.py` — Type definitions module
- [ ] `mastermind_cli/types/coordinator.py` — Coordinator request/response models
- [ ] `mastermind_cli/types/mcp.py` — MCP request/response models
- [ ] `mastermind_cli/types/brains.py` — Brain output models
- [ ] `mastermind_cli/types/config.py` — YAML config models (discriminated unions)
- [ ] `mastermind_cli/types/common.py` — Shared types (literals, enums)
- [ ] `mastermind_cli/utils/validation.py` — Runtime validation helpers
- [ ] `tests/unit/test_types.py` — Type definition tests (TS-01)
- [ ] `tests/integration/test_mcp_wrapper.py` — MCP wrapper integration tests (TS-03)
- [ ] `tests/integration/test_cli_coordinator.py` — CLI-to-coordinator integration tests (TS-06)
- [ ] `tests/unit/test_validation.py` — Runtime validation tests (TS-04)
- [ ] `tests/unit/test_error_messages.py` — Error message formatting tests (TS-05)
- [ ] `tests/unit/test_brain_normalization.py` — Brain output normalization tests (TS-07)
- [ ] `pyproject.toml [tool.mypy]` section — Mypy configuration with tiered enforcement
- [ ] `pyproject.toml [tool.pydantic-mypy]` section — Enable pydantic.mypy plugin

**Framework install commands (if missing):**
```bash
uv add --dev pytest-mypy
uv add --dev pydantic.mypy
uv add --dev bump-pydantic  # One-time migration tool
```

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Type error message clarity | TS-05 | Human judgment required | 1. Trigger type error in CLI. 2. Verify error message shows exact location (file:line) and mismatch. 3. Verify Rust-style contextual diagnostics. |
| Legacy brain compatibility | TS-07 | Requires testing with real brain outputs | 1. Test with 5-10 existing v1.3.0 brains. 2. Verify outputs normalize correctly. 3. Verify malformed YAML falls back gracefully. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 180s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
