# Phase 4: Experience Store & Production - Research

**Researched:** 2026-03-14
**Source:** CONTEXT.md decisions + codebase analysis

## RESEARCH COMPLETE ✅

---

## Technical Investigation

### ExperienceRecord Schema Design

**SQLite JSONB pattern** (aiosqlite supports JSON operations):
```sql
CREATE TABLE experience_records (
    id TEXT PRIMARY KEY,
    brain_id TEXT NOT NULL,
    input_hash TEXT NOT NULL,  -- SHA256 of input_json for deduplication
    output_json JSONB NOT NULL,
    timestamp TEXT NOT NULL,  -- ISO 8601
    duration_ms INTEGER NOT NULL,
    status TEXT NOT NULL,  -- success, failure, timeout
    embedding_stub BLOB,  -- NULL placeholder for v3.0 pgvector migration
    parent_brain_id TEXT,  -- lineage: which brain called this one
    trace_context_id TEXT,  -- lineage: correlation across flow
    custom_metadata JSONB  -- extensible: brain-specific metrics
);
CREATE INDEX idx_experience_brain_timestamp ON experience_records(brain_id, timestamp DESC);
CREATE INDEX idx_experience_trace ON experience_records(trace_context_id);
```

**PII Redaction Strategy:**
```python
import re
from pydantic import SecretStr

PII_PATTERNS = [
    (r'sk-[a-zA-Z0-9]{20,}', '[REDACTED_SECRET]'),  # API keys
    (r'mmsk_[a-zA-Z0-9]{20,}', '[REDACTED_SECRET]'),  # MultiOn keys
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]'),
    (r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]'),  # SSN pattern
]

def redact_pii(text: str) -> str:
    for pattern, replacement in PII_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text

# Pydantic SecretStr auto-redaction
class SecretInput(BaseModel):
    api_key: SecretStr
    # .model_dump(exclude_defaults=True) auto-redacts SecretStr
```

**Archive Rotation (cron script):**
```bash
# /usr/local/bin/mm-archive-logs.sh
sqlite3 mastermind.db ".dump experience_records" | \
  gzip > /archive/mm-logs-$(date +%Y%m%d).jsonl.gz
sqlite3 mastermind.db "DELETE FROM experience_records WHERE timestamp < datetime('now', '-30 days')"
```

---

### Brain-to-Brain Protocol Patterns

**Message Envelope (simple transport):**
```python
@dataclass
class BrainMessage:
    from_brain: str
    to_brain: str
    payload: BrainInput
    correlation_id: str
    transport_metadata: dict = field(default_factory=dict)  # latency, retries
```

**Internal Content (YAML-based from ROADMAP):**
```yaml
from: brain-software-01-product-strategy
to: brain-software-03-ux-research
type: output
content:
  summary: "Product strategy validated"
  detail: "..."
task_id: "task_123"
version: "1.0.0"
```

**Orchestrator-directed DAG (topological sort):**
```python
from mastermind_cli.orchestrator.dependency_resolver import resolve_dependencies

# Already implemented in Phase 2
flow_config = FlowConfig(brains=[...])
dag = resolve_dependencies(flow_config)  # Kahn's algorithm
# Execute in topological order: independent brains in parallel
```

---

### Semantic Similarity Testing

**sentence-transformers for regression detection:**
```python
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

model = SentenceTransformer('all-MiniLM-L6-v2')  # 384d, fast

def semantic_similarity(golden: str, actual: str) -> float:
    emb1 = model.encode(golden)
    emb2 = model.encode(actual)
    return 1 - cosine(emb1, emb2)  # 0.0 = different, 1.0 = identical

# Thresholds per brain type
THRESHOLDS = {
    "product_strategy": 0.90,  # creative allows variance
    "finance": 0.98,  # precision required
    "brand": 0.85,  # highly subjective
}
```

**Golden outputs storage:**
```
tests/snapshots/
  brain-01-product-strategy/
    brief-001.yaml.golden
    brief-002.yaml.golden
```

---

### CI Pipeline with uv

**GitHub Actions pattern (.github/workflows/ci.yml):**
```yaml
name: CI
on: pull_request
jobs:
  level1-typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv run mypy --strict mastermind_cli/
      - run: uv run ruff check .

  level2-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv run pytest tests/

  level3-semantic:  # Only on main/release tags
    if: github.ref == 'refs/heads/master'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv run pytest tests/integration/test_semantic_regression.py
```

**Pre-commit local shield (.pre-commit-config.yaml):**
```yaml
repos:
  - repo: https://github.com/trufflesecurity/trufflehog
    hooks:
      - id: trufflehog
        args: [--only-verified]
  - repo: local
    hooks:
      - id: ruff
        name: ruff
        entry: uv run ruff check --fix .
        language: system
```

---

## Implementation Patterns

### Integration Points Identified

**Experience Logging:**
- New module: `mastermind_cli/experience/logger.py` (200 LOC est.)
- Integration: `stateless_coordinator.py` calls logger after each brain execution
- Archive script: `scripts/archive_logs.sh` (cron job)

**Brain-to-Brain:**
- Enhance: `stateless_coordinator.py` to pass parent outputs to dependent brains
- New type: `mastermind_cli/types/protocol.py` with `BrainMessage`, `BrainEnvelope`
- Optional: `mastermind_cli/events/` for Event-Bus (deferred to v3.0)

**Backward Compatibility:**
- Test suite: `tests/integration/test_backward_compat.py` (23 brains × 5 briefs = 115 tests)
- Utility: `tests/utils/semantic_diff.py` (similarity scoring)
- Snapshots: `tests/snapshots/` (golden outputs)

**CI Pipeline:**
- Workflow: `.github/workflows/ci.yml` (3 levels: typecheck, tests, semantic)
- Pre-commit: `.pre-commit-config.yaml` (trufflehog local shield)
- Dockerfile: For containerized deployment

---

## Validation Architecture (Nyquist Dimension 8)

**How will we KNOW Phase 4 is complete?**

### Automated Verification Gates

1. **ExperienceRecord persistence tests**
   - ✅ Record saved to SQLite with all fields
   - ✅ PII redaction regex catches test secrets
   - ✅ JSONB queries work on custom_metadata
   - ✅ Archive script creates .jsonl.gz and deletes old records

2. **Brain-to-Brain protocol tests**
   - ✅ Message envelope serializes/deserializes
   - ✅ Orchestrator passes parent outputs to children
   - ✅ DAG execution respects dependencies (topological order)

3. **Semantic regression tests**
   - ✅ Golden outputs stored in tests/snapshots/
   - ✅ Similarity score > threshold for each brain type
   - ✅ CI fails on semantic degradation (< 90%)

4. **Backward compatibility suite**
   - ✅ All 23 brains execute with v1.3.0 CLI commands
   - ✅ v1.3.0 flows load without modification
   - ✅ E2E tests pass (software + marketing niches)

5. **CI Pipeline verification**
   - ✅ Level 1 (mypy + ruff) passes on all PRs
   - ✅ Level 2 (unit tests) passes on all PRs
   - ✅ Level 3 (semantic) runs on main only
   - ✅ Pre-commit hook blocks secrets from committing

### Manual Verification Checklist

1. **Experience logging works**
   - [ ] Run `mm orchestrate` and verify records in SQLite
   - [ ] Check PII redaction: input API key → [REDACTED_SECRET] in DB
   - [ ] Run archive script and verify .jsonl.gz created

2. **Brain-to-brain communication**
   - [ ] Execute multi-brain flow (Brain #1 → #3 → #7)
   - [ ] Verify outputs cascade correctly
   - [ ] Check Dashboard shows real-time updates

3. **Backward compatibility**
   - [ ] Run `mm install brain` for software dev brains
   - [ ] Run `mm source add` for legacy workflows
   - [ ] Verify v1.3.0 commands work unchanged

4. **CI/CD pipeline**
   - [ ] Create PR and verify GitHub Actions run
   - [ ] Test pre-commit hook with fake secret
   - [ ] Deploy Docker container to test registry

---

## Technical Feasibility: ✅ CONFIRMED

All 5 plans are technically feasible with existing patterns:

| Plan | Feasibility | Key Risk | Mitigation |
|------|-------------|----------|------------|
| 04-01 (ExperienceRecord) | ✅ High | JSONB performance | SQLite JSONB sufficient for <10k records/day |
| 04-02 (Brain protocol) | ✅ High | Orchestrator complexity | Reuse Phase 2 DAG resolver |
| 04-03 (Backward compat) | ⚠️ Medium | 23 brains = test burden | Hybrid: core automated, rest manual quarterly |
| 04-04 (E2E tests) | ✅ High | Flaky tests | Use tearest fixtures, isolate DB per test |
| 04-05 (CI pipeline) | ✅ High | Token cost (Level 3) | Only run semantic on main, not PRs |

---

## Deferred Ideas (Out of Scope)

- **Full RAG vector database** → v3.0+ (PostgreSQL + pgvector/qdrant)
- **Machine learning training pipeline** → v3.0+ (LoRA fine-tuning on experience logs)
- **Multi-tenant SaaS** → v3.0+ (single-tenant only for now)
- **Event-Bus implementation** → Optional enhancement (Hybrid Pulse sufficient)

---

*Research complete: 2026-03-14*
*Phase: 04-experience-store-production*
