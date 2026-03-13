# TESTING.md - Testing Patterns

**MasterMind Framework** - Testing strategy and implementation

## Testing Philosophy

**Test pyramid:**
- **E2E Tests:** Critical user flows (brief processing)
- **Integration Tests:** MCP interactions, orchestrator flows
- **Unit Tests:** Individual functions, data models

**Current state:** E2E tests established, unit tests partial

## Test Structure

```
tests/
├── test-briefs/                   # E2E test briefs (Markdown)
│   ├── README.md
│   ├── test-marketing-01-brand-awareness.md
│   ├── test-marketing-02-lead-gen.md
│   ├── test-marketing-03-ecommerce-funnel.md
│   └── test-marketing-04-retention-campaign.md
│
├── unit/                          # Unit tests (pytest)
│   ├── test_orchestrator/
│   │   ├── test_coordinator.py     # 9/9 passing
│   │   ├── test_flow_detector.py
│   │   └── test_brain_executor.py
│   └── test_interview_learning.py  # 10/10 passing
│
└── integration/                   # Integration tests (future)
    ├── test_mcp_integration.py
    └── test_notebooklm_client.py
```

## E2E Tests

### Purpose

Validate end-to-end brief processing through the orchestrator with marketing brains.

### Framework

**Custom runner:** `scripts/run_e2e_tests.py`

**Execution:**
```bash
uv run python scripts/run_e2e_tests.py
```

### Test Format

**Markdown files with structured metadata:**

```markdown
# TEST-MARKETING-XX: Test Name

> **Tipo de Test:** Full Marketing Strategy
> **Nicho:** Marketing Digital (16 cerebros M1-M16)
> **Veredicto Esperado:** APPROVE con recomendaciones
> **Cerebros Involucrados:** M1, M2, M3, M4, M9, M15, M16
> **Complejidad:** Media

---

## El Brief (Usuario)

[Brief text here]

---

## Resultados Esperados

[Expected outputs for each brain]

---

## Métricas de Éxito

| Métrica | Esperado | Mínimo Aceptable |
|---------|----------|------------------|
| Canales recomendados | 3-4 | 2+ |
| MVPs activos | M1, M2, M3, M4 | M1, M2 |
| Evaluator score | 80+ | 70+ |

---

## Anti-patrones que DEBEN ser detectados

❌ Vanity metrics
❌ Todo para todos
❌ Sin retención
```

### Current E2E Tests

| Test | Brief Type | Brains Involved | Status |
|------|------------|-----------------|--------|
| **01 - Brand Awareness** | Fitness app launch | M1, M2, M3, M4, M9, M15, M16 | ✅ PASS |
| **02 - Lead Gen** | B2B SaaS demand gen | M1, M3, M5, M6, M9, M11, M12, M13, M16 | ✅ PASS |
| **03 - Ecommerce Funnel** | Fashion CRO | M1, M2, M3, M6, M7, M8, M11, M12, M16 | ✅ PASS |
| **04 - Retention** | SaaS lifecycle | M1, M9, M10, M11, M13, M15, M16 | ✅ PASS |

### E2E Test Runner Features

- **Parallel execution:** Tests run sequentially (can be parallelized)
- **Results JSON:** Saved to `logs/e2e-results-*.json`
- **Exit codes:** 0 = all pass, 1 = any fail
- **Verbose output:** Progress per test, summary at end

## Unit Tests

### Framework

**pytest** with **pytest-cov** for coverage

**Execution:**
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=mastermind_cli --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_orchestrator/test_coordinator.py

# Verbose output
uv run pytest -v
```

### Test Patterns

#### Coordinator Tests

```python
# tests/unit/test_orchestrator/test_coordinator.py

def test_orchestrate_with_mock_mpc():
    """Test orchestration with mocked MCP calls."""
    brief = "quiero lanzar una app de fitness"

    # Mock MCP responses
    with patch('mastermind_cli.orchestrator.coordinator.MCPIntegration') as mock_mcp:
        mock_mcp.return_value.query.return_value = {
            "result": "strategy output"
        }

        result = coordinator.orchestrate(brief, use_mcp=False)

        assert result["status"] == "completed"
        assert "output" in result
```

#### Flow Detector Tests

```python
def test_flow_detector_validation_only():
    """Test validation-only flow detection."""
    brief = "es buena idea esta app?"

    flow = flow_detector.detect_flow(brief)

    assert flow == "validation_only"
```

#### Interview Learning Tests

```python
# tests/unit/test_interview_learning.py

def test_find_similar_interviews():
    """Test finding similar interviews."""
    interviews = [
        Interview(project="Test App", date="2026-03-10", brief="fitness app"),
        Interview(project="Ecommerce", date="2026-03-11", brief="online store")
    ]

    similar = interview_logger.find_similar_interviews("app de fitness", interviews)

    assert len(similar) == 1
    assert similar[0].project == "Test App"
```

### Current Unit Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| `orchestrator/coordinator` | 9 | ✅ 9/9 PASS |
| `interview_learning` | 10 | ✅ 10/10 PASS |
| `flow_detector` | 0 | ⏳ TODO |
| `brain_executor` | 0 | ⏳ TODO |
| `evaluator` | 0 | ⏳ TODO |

## Integration Tests

### Planned Tests

**MCP Integration:**
```python
# tests/integration/test_mcp_integration.py

def test_notebooklm_query_real():
    """Test real NotebookLM MCP call."""
    mcp = MCPIntegration()

    result = mcp.call_tool(
        server="notebooklm-mcp",
        tool="notebook_query",
        parameters={
            "notebook_id": "f276ccb3-...",
            "query": "What is product strategy?"
        }
    )

    assert result["status"] == "success"
    assert "content" in result
```

**Multi-brain orchestration:**
```python
def test_full_product_flow():
    """Test complete product flow through all brains."""
    brief = "quiero crear una app de viajes"

    result = coordinator.orchestrate(
        brief,
        flow="full_product",
        use_mcp=True
    )

    assert result["status"] == "completed"
    assert len(result["tasks"]) == 7  # M1 → M7
```

## Mocking Strategy

### MCP Calls

**For unit tests:** Mock `MCPIntegration` class

```python
from unittest.mock import Mock, patch

with patch('mastermind_cli.orchestrator.coordinator.MCPIntegration') as mock_mcp:
    mock_mcp.return_value.query.return_value = {
        "content": "Mocked brain output"
    }
    # Run test
```

**For integration tests:** Use real MCP (requires `nlm login`)

### Git Operations

**Mock gitpython:**

```python
with patch('git.Repo') as mock_repo:
    mock_repo.return_value.head.commit.hexsha = "abc123"
    # Run test
```

### File System

**Use tmp_path fixture:**

```python
def test_source_file_validation(tmp_path):
    """Test source file validation with temp file."""
    source_file = tmp_path / "FUENTE-001.md"
    source_file.write_text(yaml_content)

    result = validation.validate_source_file(str(source_file))

    assert result.is_valid
```

## Coverage Goals

| Module | Target | Current |
|--------|--------|---------|
| `orchestrator/coordinator` | 80% | ~60% |
| `orchestrator/flow_detector` | 80% | 0% |
| `orchestrator/brain_executor` | 80% | 0% |
| `orchestrator/evaluator` | 80% | 0% |
| `memory/interview_logger` | 80% | ~70% |
| Overall | 70% | ~40% |

## Test Data

### Fixtures

**Pytest fixtures in `conftest.py`:**

```python
@pytest.fixture
def sample_brief():
    """Sample brief for testing."""
    return "quiero crear una app de fitness"

@pytest.fixture
def mock_brain_config():
    """Mock brain configuration."""
    return {
        "id": "M1",
        "name": "Product Strategy",
        "notebook_id": "test-notebook-id"
    }
```

### Test Briefs

**Location:** `tests/test-briefs/`

**Naming:** `test-{niche}-{number}-{name}.md`

**Usage:** E2E runner extracts brief from `## El Brief (Usuario)` section

## CI/CD Integration

**Pre-commit hooks:**
- Gentleman Guardian Angel (AI review)
- YAML validation
- No automated test execution (manual for now)

**Future:**
- GitHub Actions workflow
- Run tests on PR
- Coverage reporting
- E2E tests in CI environment

## Testing Best Practices

### DO

- **Test behavior, not implementation**
- **Use descriptive test names** (`test_flow_detector_validation_only`)
- **Follow AAA pattern** (Arrange, Act, Assert)
- **Mock external dependencies** (MCP, Git)
- **Use fixtures for shared data**
- **Test error cases** (invalid input, network failures)

### DON'T

- **Don't test trivial code** (getters/setters)
- **Don't mock everything** (integration tests need real deps)
- **Don't ignore test coverage** (< 70% = add tests)
- **Don't commit with failing tests** (CI should block)

## Debugging Tests

**Verbose output:**
```bash
uv run pytest -v -s  # Show print statements
```

**Stop on first failure:**
```bash
uv run pytest -x
```

**Enter debugger on failure:**
```bash
uv run pytest --pdb
```

**Run specific test:**
```bash
uv run pytest tests/unit/test_coordinator.py::test_orchestrate_mock
```

## Test Documentation

**E2E test manual:** `docs/testing/E2E-TEST-MANUAL.md`

**Test report:** `docs/ORCHESTRATOR-TEST-REPORT.md`
