# Phase 04 Technical Decisions - 2026-03-14

## Experience Logging (04-01)

**Decision:** JSONB storage with regex + Pydantic dual defense for PII redaction

**Why:**
- JSONB preserves full-fidelity data (no lossy compression)
- Regex patterns catch structured PII (email, phone, SSN, credit card, IP)
- Pydantic SecretStr provides runtime-level defense (type-level protection)
- Dual defense ensures PII redaction even if one layer fails

**Trade-offs:**
- JSONB uses more storage than compressed formats — acceptable for 30-day retention
- Regex patterns need maintenance — PII patterns evolve, but core patterns stable
- Pydantic SecretStr not visible in logs — intended behavior for security

**Implementation:**
- `mastermind_cli/experience/models.py` - ExperienceRecord Pydantic model (112 lines)
- `mastermind_cli/experience/redaction.py` - PII redaction utilities (118 lines)
- `mastermind_cli/experience/logger.py` - Async ExperienceLogger (194 lines)
- `scripts/archive_logs.sh` - 30-day rotation to .jsonl.gz

---

## Brain Protocol (04-02)

**Decision:** Hybrid approach (BrainMessage envelope + Orchestrator-directed DAG)

**Why:**
- BrainMessage envelope provides typed communication between brains
- Orchestrator maintains topological sort authority (Phase 2 Kahn's algorithm)
- Parent outputs passed via `context.parent_outputs` to dependent brains
- Correlation ID links all messages in a flow for tracing

**Trade-offs:**
- Not pure message-passing (brains don't send directly to each other) — acceptable for deterministic orchestration
- Orchestrator is routing bottleneck — mitigated by parallel execution within waves
- Message log grows with flow size — acceptable for 30-day retention

**Implementation:**
- `mastermind_cli/types/protocol.py` - BrainMessage, BrainEnvelope, BrainOutputType (211 lines)
- `mastermind_cli/orchestrator/stateless_coordinator.py` - Enhanced with message_log, correlation_id (440 lines)
- `tests/integration/test_brain_protocol.py` - 5 tests for envelope, parent outputs, DAG order

---

## Semantic Regression (04-03)

**Decision:** sentence-transformers with brain-specific thresholds

**Why:**
- all-MiniLM-L6-v2 model (384d, fast, good quality)
- Brain-specific thresholds account for output variability (Finance: 0.98, Brand: 0.85, Default: 0.90)
- Lazy-loading model avoids startup overhead
- Graceful degradation if sentence-transformers not installed

**Trade-offs:**
- sentence-transformers requires torch (2GB+) — tests skip gracefully if not available
- Semantic similarity not perfect — human review still needed for critical changes
- Golden outputs need manual creation — one-time cost for regression protection

**Implementation:**
- `tests/utils/semantic_diff.py` - semantic_similarity(), compare_outputs() (136 lines)
- `tests/integration/test_semantic_regression.py` - 5 tests with thresholds
- `tests/snapshots/` - Golden output storage

---

## CI Pipeline (04-05)

**Decision:** 3-tier verification (typecheck → tests → semantic regression)

**Why:**
- Level 1 (mypy + ruff): Fast feedback for all PRs
- Level 2 (pytest): Catches regressions for all PRs
- Level 3 (semantic regression): Expensive (requires golden outputs), main branch only
- Trufflehog secret detection in pre-commit (commented due to build time)

**Trade-offs:**
- Trufflehog slow to install — commented out, can be enabled optionally
- Semantic regression on main only — acceptable trade-off for CI speed
- No Docker build in CI — manual verification step for production

**Implementation:**
- `.github/workflows/ci.yml` - 3 jobs (typecheck, tests, semantic)
- `.pre-commit-config.yaml` - ruff, mypy, pytest hooks
- `Dockerfile` - Multi-stage (builder + runtime), Python 3.14-slim, uv
