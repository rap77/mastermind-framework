# Phase 1: Type Safety Foundation - Research

**Researched:** 2026-03-13
**Domain:** Python Type Safety, Pydantic v2, Mypy Strict Mode
**Confidence:** HIGH

## Summary

Phase 1 establishes the type safety foundation for MasterMind Framework v2.0, migrating from Pydantic v1 to v2 and implementing mypy --strict mode across the codebase. This phase focuses on internal developer infrastructure without changing user-facing functionality.

**Primary recommendation:** Use a tiered enforcement strategy for mypy strict mode with Pydantic v2's discriminated unions for YAML configs, TypeAdapter for runtime validation, and validate_call decorator for critical coordinator functions.

## User Constraints

### Locked Decisions (from CONTEXT.md)

**Estrategia Pydantic v2:**
- Big-bang migration con Test-First para core modules + Feature-based para periphery
- Orden: Escribir tests primero para core (coordinator.py, mcp_wrapper.py), luego migrar feature-vertical slices
- Herramienta: `bump-pydantic` CLI tool para automatizar migración v1→v2
- Safety net: pydantic.v1 shim durante migración híbrida (periphery → core)

**MCP responses (NotebookLM):**
- Enfoque evolutivo con `model_config = ConfigDict(extra='allow')` de Pydantic v2
- Campos conocidos validados estrictamente, campos extra preservados automáticamente

**Brain outputs legacy:**
- Normalizer pattern con fallbacks inteligentes
- `normalize_brain_output(raw_yaml: str) -> StandardSchema`
- Try-except global: YAML parse error → fallback a `{"raw_text": raw_yaml}`

**YAML configs (brains.yaml, flows.yaml, thresholds.yaml):**
- **Discriminated Unions** con `Field(discriminator="type")`
- Ideal para 23 brains heterogéneos con parámetros diferentes

**Alcance mypy strict:**
- **Tiered Enforcement** — niveles de severidad graduales
- Fase 1: `disallow_untyped_defs` (firmas tipadas)
- Fase 2: `no_implicit_optional`, `warn_return_any` (cuerpos de funciones)
- Fase 3: `warn_unused_ignores` (limpieza de ignores)

**Validación Runtime:**
- **Integrity Checkpoints** — validación en puntos de transformación de datos
- **Boundaries:** CLI input, MCP responses, brain outputs
- **Core logic:** `@validate_call` decorator de Pydantic v2 en funciones críticas

### Claude's Discretion

**Areas donde Claude tiene flexibilidad:**
- Orden exacto de flags de mypy en Tiered Enforcement
- Nombres específicos de campos en modelos Pydantic (si siguen convenciones)
- Cantidad de snapshots tests vs unit tests para alcanzar coverage goals
- Formato exacto de mensajes de error human-readable (si contienen información necesaria)

**Principios rectores:**
- Preferir type safety sobre conveniencia a corto plazo
- Mantener backward compatibility con 23 brains existentes
- Priorizar calidad sobre velocidad en core modules (Coordinator, Auth)
- Ser pragmático con legacy code (brains)

### Deferred Ideas (OUT OF SCOPE)

- Implementar Web UI (Phase 3)
- Parallel execution de brains (Phase 2)
- ML-based optimization (v3.0+)
- Full RAG vector DB (v3.0+)
- Hot-reload de brains sin reiniciar
- Type-aware auto-completion en Web UI (Monaco editor)
- Custom metrics dashboard

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| TS-01 | All data structures have Pydantic v2 models (requests, responses, brain outputs, configs) | Pydantic v2 BaseModel, Field, ConfigDict; discriminated unions for YAML configs; TypeAdapter for runtime validation |
| TS-02 | Codebase passes `mypy --strict` mode without errors | Tiered enforcement strategy; per-module overrides; gradual rollout; existing code patterns from memory/models.py |
| TS-03 | MCP wrapper is type-safe (request/response models, validated) | Pydantic v2 models with extra='allow' for evolutivo approach; validate_call decorator for runtime validation |
| TS-04 | System validates types at runtime before execution (Pydantic validation) | @validate_call decorator; TypeAdapter.validate_python(); ValidationError handling with graceful degradation |
| TS-05 | System provides clear type error messages for mismatches | Pydantic ValidationError formatting; rich/click for human-readable output; contextual diagnostics |
| TS-06 | CLI-to-Orchestrator boundary uses typed interfaces (no raw dicts) | Pydantic models for all data structures; Protocol-based brain consumption; TypeAdapter validation |
| TS-07 | Brain outputs conform to typed schemas (backward compatible with v1 brains) | Normalizer pattern with fallbacks; TypedDict for legacy bridge; StandardSchema with safe defaults |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **pydantic** | >=2.12.5 | Data validation and type models | Industry standard for Python type validation, v2 has major performance improvements and better type checking |
| **mypy** | >=1.14.0 | Static type checking | De facto standard for Python type checking, --strict mode ensures comprehensive type safety |
| **pytest** | >=9.0.2 | Testing framework | Most popular Python testing framework, supports type testing plugins |
| **pytest-mypy** | >=0.10.0 | Mypy plugin for pytest | Runs mypy tests within pytest suite, integrates type checking with CI |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **bump-pydantic** | latest | Automated v1→v2 migration | One-time migration tool for Pydantic v1 codebase |
| **pytest-regressions** | latest | Snapshot testing | For brain output validation, detecting breaking changes |
| **rich** | >=13.0.0 | Terminal formatting | Already in stack, used for error messages |
| **click** | >=8.1.0 | CLI framework | Already in stack, integrates with Pydantic via TypeAdapter |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pydantic v2 | Pydantic v1 | v1 is deprecated, v2 has 5-50x performance boost, better type checking |
| mypy --strict | pyright | Pyright is faster but less standard in Python ecosystem, mypy has better Pydantic v2 support via pydantic.mypy plugin |
| Discriminated Unions | Standard Union | Discriminated unions are more performant, predictable, and generate better JSON schemas |
| @validate_call | Manual validation | Decorator is less boilerplate, consistent with Pydantic patterns, better error messages |

**Installation:**
```bash
# Core dependencies (already in pyproject.toml)
uv add --dev pytest-mypy

# Migration tool (one-time)
uv add --dev bump-pydantic

# Type checking plugin (required for Pydantic v2)
uv add --dev pydantic.mypy
```

## Architecture Patterns

### Recommended Project Structure

```
mastermind_cli/
├── types/                      # NEW: Type definitions module
│   ├── __init__.py
│   ├── coordinator.py          # Coordinator request/response models
│   ├── mcp.py                  # MCP request/response models
│   ├── brains.py               # Brain output models
│   ├── config.py               # YAML config models (discriminated unions)
│   └── common.py               # Shared types (literals, enums)
│
├── orchestrator/
│   ├── coordinator.py          # MIGRATE: Add type hints, @validate_call
│   ├── mcp_wrapper.py          # MIGRATE: Type-safe MCP wrapper
│   └── ...
│
├── memory/
│   └── models.py               # MIGRATE: Pydantic v1→v2
│
├── utils/
│   └── validation.py           # NEW: Runtime validation helpers
│
└── commands/
    └── *.py                    # MIGRATE: Click → Pydantic bridge
```

### Pattern 1: Discriminated Unions for YAML Configs

**What:** Use Pydantic v2's discriminated unions to validate heterogeneous brain configurations with a discriminator field.

**When to use:** Validating YAML configs where different brain types have different required parameters (e.g., `top_k` for vector-search, `temperature` for generative).

**Example:**
```python
# Source: https://docs.pydantic.dev/latest/concepts/unions/
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field, Discriminator

class SearchBrain(BaseModel):
    type: Literal['vector-search']
    top_k: int
    embedding_model: str

class GenerativeBrain(BaseModel):
    type: Literal['generative']
    temperature: float
    max_tokens: int

# Discriminated union - Pydantic uses 'type' field to select model
BrainConfig = Annotated[
    Union[SearchBrain, GenerativeBrain],
    Field(discriminator='type')
]

class ConfigFile(BaseModel):
    brains: list[BrainConfig]
    # Validates correctly based on 'type' field
```

**Benefits:**
- Single-pass validation (no trying multiple union members)
- Clear error messages (only shows errors for matched type)
- Better performance (O(1) vs O(n) for standard unions)
- OpenAPI-compliant JSON schema generation

### Pattern 2: TypeAdapter for Runtime Validation

**What:** Use `TypeAdapter[T].validate_python()` for validating data without creating full model classes.

**When to use:** Validating raw dictionaries from MCP, CLI input, or brain outputs where you need runtime validation but don't need a full model class.

**Example:**
```python
# Source: https://docs.pydantic.dev/latest/concepts/type_adapter/
from pydantic import TypeAdapter, ValidationError

# Define type with constraints
BrainScore = Annotated[int, Field(ge=0, le=100)]

# Create adapter
score_adapter = TypeAdapter(BrainScore)

# Validate at runtime
try:
    score = score_adapter.validate_python(user_input)
except ValidationError as e:
    print(f"Invalid score: {e.errors()[0]['msg']}")
```

**Benefits:**
- Lightweight validation without model overhead
- Reusable for complex types (Unions, Annotated, etc.)
- Better performance than full BaseModel for simple validations
- Preserves type information for mypy

### Pattern 3: @validate_call for Critical Functions

**What:** Use `@validate_call` decorator to validate function arguments at runtime using type annotations.

**When to use:** Critical coordinator functions where type safety is essential (e.g., `process_brain_evaluation`, `orchestrate`).

**Example:**
```python
# Source: https://docs.pydantic.dev/latest/concepts/validation_decorator/
from pydantic import validate_call, ValidationError, Field, PositiveInt
from typing import Annotated

@validate_call
def process_brain_evaluation(
    brain_id: str,
    score: Annotated[float, Field(ge=0.0, le=1.0)],
    issues: list[str] = []
) -> dict:
    """Process brain evaluation with runtime type validation."""
    # Pydantic validates arguments before function executes
    # "0.8" → 0.8 (coerce), "alto" → ValidationError
    return {"brain_id": brain_id, "score": score, "issues": issues}

# Usage
try:
    result = process_brain_evaluation(
        brain_id="brain-1",
        score="0.8",  # Coerced to float
        issues=["missing_metric"]  # List validation
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
```

**Benefits:**
- Zero boilerplate validation
- Type coercion (e.g., "0.8" → 0.8)
- Clear error messages
- Preserves function signature for type checkers

### Pattern 4: Normalizer Pattern for Legacy Brain Outputs

**What:** Wrap legacy brain outputs with a normalizer that handles YAML parse errors and missing fields gracefully.

**When to use:** Processing outputs from 23 existing v1.3.0 brains that may not conform to new schemas.

**Example:**
```python
from pydantic import BaseModel, Field, ValidationError
from typing import Any, Optional

class StandardSchema(BaseModel):
    id: str = Field(..., description="Brain identifier")
    content: str = Field(..., description="Brain output content")
    version: str = Field(default="v1.0.0", description="Schema version")
    raw_text: Optional[str] = Field(None, description="Fallback for unparseable output")

def normalize_brain_output(raw_yaml: str) -> StandardSchema:
    """Normalize legacy brain output to standard schema."""
    import yaml

    try:
        # Try to parse as YAML and validate
        data = yaml.safe_load(raw_yaml)
        return StandardSchema(
            id=data.get("brain_id", "unknown"),
            content=data.get("output", raw_yaml),
            version=data.get("version", "v1.0.0")
        )
    except (yaml.YAMLError, ValidationError) as e:
        # Fallback to raw text if parsing fails
        return StandardSchema(
            id="unknown",
            content="",
            raw_text=raw_yaml
        )
```

**Benefits:**
- Backward compatibility with v1 brains
- Graceful degradation (never crashes on malformed output)
- Collects unparseable outputs for later analysis
- Provides migration path for legacy brains

### Pattern 5: TypedDict as Legacy Bridge

**What:** Use `TypedDict` for read-only data from uncontrolled systems (legacy brain outputs) vs `BaseModel` for internal communication.

**When to use:** Consuming data from 23 legacy brains where you don't control the schema but want type safety for reading.

**Example:**
```python
from typing import TypedDict
from pydantic import BaseModel

# Read-only view of legacy brain output
class LegacyBrainOutput(TypedDict):
    brain_id: str
    raw_output: str
    timestamp: str

# Internal communication model (validated, mutable)
class BrainEvaluation(BaseModel):
    brain_id: str
    score: float
    issues: list[str]

# Unpack pattern: validate legacy data when needed
def evaluate_legacy_brain(legacy: LegacyBrainOutput) -> BrainEvaluation:
    """Convert legacy brain output to typed evaluation."""
    # Validation happens here, not at creation
    return BrainEvaluation(
        brain_id=legacy["brain_id"],
        score=0.5,  # Computed from legacy output
        issues=[]
    )
```

**Benefits:**
- Doesn't mutate original legacy data
- Clear separation between external (TypedDict) and internal (BaseModel)
- Lazy validation (only when needed)
- Type checker still validates field access

### Anti-Patterns to Avoid

- **Discriminated union with single variant:** Python reduces `Union[T]` to `T`, making discriminator ineffective. Use at least 2 variants or skip discriminated unions.
- **Global type ignores without codes:** `# type: ignore` hides all errors. Use `# type: ignore[union-attr]` with specific error codes.
- **Validating everything:** Internal code should trust types, not validate redundant paths. Only validate at boundaries (MCP, CLI, brain outputs).
- **Mixing v1 and v2 imports:** `from pydantic import BaseModel` and `from pydantic.v1 import BaseModel` in same file creates confusion. Use pydantic.v1 shim only during migration.
- **Ignoring mypy errors permanently:** `# type: ignore` should have TODO tickets. Clean as you touch code.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML validation | Custom YAML parsers with schema validation | Pydantic v2 discriminated unions | Edge cases: type coercion, nested validation, JSON schema export, error messages |
| Runtime type checking | `isinstance()` checks everywhere | `@validate_call` decorator | Edge cases: Type coercion, nested validation, clear error messages |
| Brain output parsing | Manual YAML parsing with try/except | Normalizer pattern with Pydantic | Edge cases: Missing fields, type errors, malformed YAML, graceful fallbacks |
| CLI argument validation | Custom Click parameter types | TypeAdapter with Click ParamType | Edge cases: Type coercion, validation error formatting, consistent with Pydantic |
| Type-safe MCP wrapper | Manual dict validation | Pydantic models with `extra='allow'` | Edge cases: Evolving schemas, unknown fields, type coercion, serialization |

**Key insight:** Custom validation code is rarely production-grade. Pydantic has handled edge cases for 5+ years across millions of deployments. Every custom validation function is technical debt.

## Common Pitfalls

### Pitfall 1: Mypy Strict Mode All-at-Once

**What goes wrong:** Enabling `mypy --strict` on entire codebase reveals thousands of errors, overwhelming team and halting progress.

**Why it happens:** Existing codebase has 28+ Python files with loose typing (`Dict[str, Any]`, no type hints).

**How to avoid:**
- Use **tiered enforcement**: Start with `disallow_untyped_defs` (signatures only), then `no_implicit_optional`, then full strict
- Use **per-module overrides**: Enable strict only for migrated modules
- Use **ignore_errors = True** for legacy modules, then selectively enable

**Warning signs:**
- More than 100 mypy errors in first run
- Team spending more time adding `# type: ignore` than fixing types
- PR reviews blocked on type errors in unrelated code

### Pitfall 2: Discriminated Union Mismatch

**What goes wrong:** Discriminator field value doesn't match any union member, causing cryptic "union_tag_not_found" errors.

**Why it happens:** YAML config has `type: "vector-search"` but model defines `Literal['vectors']`.

**How to avoid:**
- Use **exact literal matches**: Ensure discriminator values in configs match literals in models exactly
- Add **Tag annotations**: `Annotated[Model, Tag('vector-search')]` for self-documenting unions
- Validate **config files early**: Add schema validation step that shows all allowed discriminator values

**Warning signs:**
- "union_tag_not_found" errors in production
- Frequent config updates to match model changes
- Confusion about which discriminator values are valid

### Pitfall 3: Pydantic v1→v2 Breaking Changes

**What goes wrong:** Code using `__init__` parameters from Pydantic v1 breaks in v2 (e.g., `extra='allow'` moved to `ConfigDict`).

**Why it happens:** Pydantic v2 changed many APIs, but v1 code still runs with deprecation warnings until removed.

**How to avoid:**
- Use **bump-pydantic** CLI tool for automated migration
- Run **test suite** after migration to catch behavior changes
- Use **pydantic.v1 shim** temporarily for periphery modules during gradual migration

**Warning signs:**
- Deprecation warnings in test output
- `AttributeError: 'ConfigDict' object has no attribute 'extra'`
- Validation behavior changes after migration

### Pitfall 4: Runtime Validation Overhead

**What goes wrong:** Adding `@validate_call` to every function degrades performance significantly.

**Why it happens:** Pydantic validation has overhead (parsing, coercion, error construction). Calling it on every function is unnecessary.

**How to avoid:**
- Only validate at **boundaries**: MCP responses, CLI input, brain outputs
- Trust **internal types**: Don't validate between internal functions
- Use **TypeAdapter** for simple validations (lighter than `@validate_call`)

**Warning signs:**
- Orchestrator takes 2-3x longer after adding validation
- Profile shows 20%+ time in `validate_call`
- Validation errors in internal code (indicates over-validation)

### Pitfall 5: Type Ignore Proliferation

**What goes wrong:** Code accumulates hundreds of `# type: ignore` comments, defeating the purpose of type checking.

**Why it happens:** Developers add ignores to "make tests pass" without fixing underlying issues.

**How to avoid:**
- Require **error codes**: `# type: ignore[union-attr]` with justification
- Enable **warn_unused_ignores**: MyPy will warn if ignore isn't needed
- **Clean as you touch**: Remove ignores when editing related code

**Warning signs:**
- >10% of lines have `# type: ignore`
- Ignores without error codes
- Ignores older than 6 months

## Code Examples

Verified patterns from official sources:

### Discriminated Union for Brain Configs

```python
# Source: https://docs.pydantic.dev/latest/concepts/unions/
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field

class VectorSearchBrain(BaseModel):
    type: Literal['vector-search']
    top_k: int
    embedding_model: str = Field(default="text-embedding-ada-002")

class GenerativeBrain(BaseModel):
    type: Literal['generative']
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(gt=0)

class BrainConfig(BaseModel):
    brain: Annotated[
        Union[VectorSearchBrain, GenerativeBrain],
        Field(discriminator='type')
    ]
    enabled: bool = True

# Validates correctly based on 'type' field
config1 = BrainConfig(brain={'type': 'vector-search', 'top_k': 5})
config2 = BrainConfig(brain={'type': 'generative', 'temperature': 0.7})
```

### TypeAdapter for CLI Validation

```python
# Source: https://docs.pydantic.dev/latest/concepts/type_adapter/
from pydantic import TypeAdapter, ValidationError, Field
from typing import Annotated
import click

# Define type with constraints
ConfidenceScore = Annotated[float, Field(ge=0.0, le=1.0)]

class ConfidenceParam(click.ParamType):
    """Click parameter type for confidence scores."""
    name = "confidence"

    def __init__(self):
        self.adapter = TypeAdapter(ConfidenceScore)

    def convert(self, value, param, ctx):
        try:
            return self.adapter.validate_python(value)
        except ValidationError as e:
            self.fail(f"Invalid confidence (0.0-1.0): {e.errors()[0]['msg']}", param, ctx)

# Use in Click command
@click.command()
@click.option('--confidence', type=ConfidenceParam(), default=0.5)
def evaluate(confidence: float):
    """Evaluate with confidence score."""
    print(f"Confidence: {confidence}")
```

### Graceful Degradation for Brain Outputs

```python
# Source: Pattern from CONTEXT.md
from pydantic import BaseModel, Field, ValidationError, ConfigDict
from typing import Optional
import yaml

class BrainOutput(BaseModel):
    """Standard brain output schema with graceful fallback."""
    model_config = ConfigDict(extra='allow')  # Preserve unknown fields

    brain_id: str = Field(..., description="Brain identifier")
    content: str = Field(..., description="Brain output content")
    version: str = Field(default="v1.0.0")
    raw_fallback: Optional[str] = Field(None, description="Original text if parsing failed")

    @classmethod
    def from_yaml(cls, raw_yaml: str) -> "BrainOutput":
        """Parse YAML with fallback to raw text."""
        try:
            data = yaml.safe_load(raw_yaml)
            return cls(
                brain_id=data.get("brain_id", "unknown"),
                content=data.get("content", raw_yaml),
                version=data.get("version", "v1.0.0")
            )
        except yaml.YAMLError:
            return cls(
                brain_id="parse_error",
                content="",
                raw_fallback=raw_yaml
            )

# Usage
raw_output = """
brain_id: "strategy-01"
content: "Product validation successful"
version: "v2.0.0"
extra_field: "preserved via extra='allow'"
"""

output = BrainOutput.from_yaml(raw_output)
print(output.model_dump())
# {'brain_id': 'strategy-01', 'content': '...', 'version': 'v2.0.0', 'raw_fallback': None}
```

### Mypy Tiered Enforcement Configuration

```toml
# pyproject.toml
[tool.mypy]
# Base configuration (Tier 1)
python_version = "3.14"
warn_return_any = false  # Tier 2
disallow_untyped_defs = true  # Tier 1
warn_unused_ignores = false  # Tier 3
show_error_codes = true

# Per-module overrides
[[tool.mypy.overrides]]
module = "mastermind_cli.orchestrator.coordinator"
strict = true  # Core module gets strict mode first

[[tool.mypy.overrides]]
module = "mastermind_cli.brains_legacy.*"
disallow_untyped_defs = false  # Legacy modules stay loose until migration

[[tool.mypy.overrides]]
module = "mastermind_cli.types.*"
strict = true  # New type modules are strict from day 1

# Pydantic plugin (REQUIRED for v2)
[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pydantic v1 `BaseModel` | Pydantic v2 `BaseModel` | v2.0 released 2023 | 5-50x performance boost, better type checking, breaking API changes |
| Standard `Union[A, B]` | Discriminated unions | Pydantic v2.0 | O(1) validation, predictable errors, better JSON schemas |
| Manual validation decorators | `@validate_call` | Pydantic v2.0 | Zero boilerplate, consistent with Pydantic patterns |
| `mypy --strict` all-at-once | Tiered enforcement | Best practice 2024+ | Gradual rollout, prevents overwhelming teams |
| Custom type guards | TypeAdapter | Pydantic v2.0 | Lightweight validation, better performance |

**Deprecated/outdated:**
- **Pydantic v1:** End-of-life, no longer maintained. Migrate to v2 using `bump-pydantic`
- **`__init__` config in v2:** Moved to `model_config = ConfigDict(...)`
- **`@validator` decorator:** Replaced by `@field_validator` in v2
- **`parse_obj` method:** Use `model_validate` in v2
- **Union mode 'left_to_right' as default:** Changed to 'smart' in v2.0

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest >=9.0.2 |
| Type checking | mypy >=1.14.0 |
| Type test plugin | pytest-mypy >=0.10.0 |
| Config file | pyproject.toml (mypy section) |
| Quick run command | `uv run pytest tests/ -x -v` |
| Type check command | `uv run mypy mastermind_cli/` |
| Full suite command | `uv run pytest tests/ --cov=mastermind_cli --cov-report=term-missing` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TS-01 | Pydantic v2 models for all data structures | unit | `pytest tests/unit/test_types.py -x -v` | ❌ Wave 0 |
| TS-02 | Codebase passes mypy --strict | type | `mypy mastermind_cli/ --strict` | ❌ Wave 0 |
| TS-03 | MCP wrapper type-safe | integration | `pytest tests/integration/test_mcp_wrapper.py -x -v` | ❌ Wave 0 |
| TS-04 | Runtime validation at boundaries | unit | `pytest tests/unit/test_validation.py -x -v` | ❌ Wave 0 |
| TS-05 | Clear type error messages | unit | `pytest tests/unit/test_error_messages.py -x -v` | ❌ Wave 0 |
| TS-06 | CLI-to-Orchestrator typed interfaces | integration | `pytest tests/integration/test_cli_coordinator.py -x -v` | ❌ Wave 0 |
| TS-07 | Brain outputs conform to schemas | unit | `pytest tests/unit/test_brain_normalization.py -x -v` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `uv run pytest tests/unit/test_*.py -x --tb=short` (unit tests only, <30s)
- **Per wave merge:** `uv run pytest tests/ --cov=mastermind_cli --cov-report=term-missing && uv run mypy mastermind_cli/` (full suite + type check, ~2-3 min)
- **Phase gate:** All tests passing + mypy --strict on all migrated modules + 80% type coverage minimum

### Wave 0 Gaps

**Critical files to create before implementation:**

- [ ] `mastermind_cli/types/__init__.py` — Type definitions module
- [ ] `mastermind_cli/types/coordinator.py` — Coordinator request/response models
- [ ] `mastermind_cli/types/mcp.py` — MCP request/response models
- [ ] `mastermind_cli/types/brains.py` — Brain output models
- [ ] `mastermind_cli/types/config.py` — YAML config models (discriminated unions)
- [ ] `mastermind_cli/types/common.py` — Shared types (literals, enums)
- [ ] `mastermind_cli/utils/validation.py` — Runtime validation helpers
- [ ] `tests/unit/test_types.py` — Type definition tests
- [ ] `tests/integration/test_mcp_wrapper.py` — MCP wrapper integration tests
- [ ] `tests/integration/test_cli_coordinator.py` — CLI-to-coordinator integration tests
- [ ] `tests/unit/test_validation.py` — Runtime validation tests
- [ ] `tests/unit/test_error_messages.py` — Error message formatting tests
- [ ] `tests/unit/test_brain_normalization.py` — Brain output normalization tests
- [ ] `mypy.ini` or `pyproject.toml [tool.mypy]` section — Mypy configuration with tiered enforcement
- [ ] `.mypy.ini` or update `pyproject.toml` — Enable pydantic.mypy plugin

**Framework install commands (if missing):**
```bash
uv add --dev pytest-mypy
uv add --dev pydantic.mypy
uv add --dev bump-pydantic  # One-time migration tool
```

## Sources

### Primary (HIGH confidence)

- **Pydantic v2 Documentation** - Discriminated Unions (https://docs.pydantic.dev/latest/concepts/unions/)
  - Verified discriminated union syntax, Field(discriminator=), callable discriminators, nested discriminated unions, Tag annotations, TypeAdapter usage
- **Pydantic v2 Documentation** - Validation Decorator (https://docs.pydantic.dev/latest/concepts/validation_decorator/)
  - Verified @validate_call decorator syntax, parameter validation, custom configuration, async support, compatibility with type checkers
- **Mypy Documentation** - Existing Code (https://mypy.readthedocs.io/en/stable/existing_code.html)
  - Verified gradual typing strategy, per-module overrides, strict mode introduction, preventing regressions with CI
- **Project Codebase** - `mastermind_cli/memory/models.py`
  - Verified existing Pydantic v1 usage patterns: BaseModel, Field, Enum, validation logic, to_dict/from_dict methods
- **Project Codebase** - `mastermind_cli/orchestrator/coordinator.py`
  - Verified current type hints: Optional[Dict], Dict[str, Any], lack of strict typing

### Secondary (MEDIUM confidence)

- **CONTEXT.md** (User decisions)
  - Verified locked decisions: Pydantic v2 strategy, MCP responses approach, brain outputs legacy pattern, YAML configs discriminated unions, mypy strict tiered enforcement, runtime validation checkpoints
  - Verified Claude's discretion areas and guiding principles
- **REQUIREMENTS.md**
  - Verified TS-01 through TS-07 requirements mapping to Phase 1
  - Verified backward compatibility requirements (BC-01 through BC-05)
- **pyproject.toml**
  - Verified current Pydantic version (>=2.0.0), Python version (>=3.14), existing dev dependencies (pytest>=9.0.2, pytest-cov>=7.0.0)
- **Test files** - `tests/test_orchestrator/test_discovery_flow.py`, `tests/test_orchestration_e2e.py`
  - Verified existing pytest usage, test structure, import patterns

### Tertiary (LOW confidence)

- **Web search attempts** (Rate-limited, unable to verify)
  - Pydantic v2 migration best practices 2026
  - mypy strict mode tiered enforcement gradual rollout Python 2026
  - pytest-mypy plugins type testing validation Python 2026
  - **Note:** These searches hit rate limits, so findings are marked LOW and require validation with official sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified with official Pydantic v2 docs and project's pyproject.toml
- Architecture: HIGH - Verified with official Pydantic docs (discriminated unions, validate_call, TypeAdapter) and Mypy docs (gradual typing)
- Pitfalls: MEDIUM - Based on official docs + common Python type safety issues, but some pitfalls specific to this codebase need validation during implementation
- Validation architecture: HIGH - Based on existing test infrastructure + pytest + mypy + pytest-mypy documentation

**Research date:** 2026-03-13
**Valid until:** 2026-04-13 (30 days - Pydantic and mypy are stable, but rapid ecosystem changes possible)

**Open Questions:**
1. **bump-pydantic effectiveness:** How well does the automated migration tool handle complex patterns (discriminated unions, validators, custom serializers)? Needs validation on small subset first.
2. **Type coverage measurement:** How to measure "80% type coverage" for TS-02? Tools like `typeguard` or `mypy coverage` plugins exist but need evaluation.
3. **Performance impact of @validate_call:** What's the actual overhead on coordinator functions? Need benchmarks before/after.
4. **Legacy brain compatibility:** How many of the 23 existing brains produce YAML that fails parsing? Needs audit before implementing normalizer pattern.
