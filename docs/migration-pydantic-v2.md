# Pydantic v2 Migration - Phase 1

**Date:** 2026-03-13
**Plan:** 01-02 (Type Safety Foundation)
**Status:** Complete

## Migrated Modules

- `mastermind_cli/memory/models.py` - Evaluation data models
- `mastermind_cli/orchestrator/coordinator.py` - Main orchestration coordinator
- `mastermind_cli/orchestrator/mcp_wrapper.py` - MCP integration wrapper
- `mastermind_cli/types/` - Type definition modules (created in 01-01)

## Changes Made

### v1 → v2 Syntax

#### Imports
```python
# Before (v1):
from typing import List, Optional, Dict
from datetime import datetime

# After (v2):
from datetime import datetime, timezone
from typing import Any
```

#### Type Annotations
```python
# Before (v1):
Optional[str] → str | None
List[str] → list[str]
Dict[str, Any] → dict[str, Any]
Optional[Dict] → dict[str, Any] | None
```

#### Model Definitions
```python
# Before (v1):
class EvaluationEntry(BaseModel):
    evaluation_id: Optional[str] = Field(None, description="...")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="...")
    brains_involved: List[int] = Field(default_factory=list, description="...")

# After (v2):
class EvaluationEntry(BaseModel):
    evaluation_id: str | None = Field(None, description="...")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="...")
    brains_involved: list[int] = Field(default_factory=list, description="...")
```

### Type Hints Added

#### coordinator.py
- All 20+ methods now have complete type hints
- Return type annotations: `-> dict[str, Any]`, `-> str`, `-> None`
- Parameter types: `brief: str`, `flow: str | None`, `dry_run: bool`
- Local variables: `by_category: dict[str, list[dict[str, Any]]]`, `evaluations: dict[str, Any]`

#### mcp_wrapper.py
- All static and class methods have type hints
- Return types: `-> dict[str, Any]`, `-> str`, `-> list[dict[str, Any]]`
- Parameters: `brain_id: int`, `query: str`, `source_ids: list[str] | None`
- Import type models: `from mastermind_cli.types import MCPRequest, MCPResponse`

#### memory/models.py
- All models use v2 union syntax
- Type hints on `to_dict()` and `from_dict()` methods
- Use `model_validate()` for nested object validation
- Proper type casting with `dict[str, Any]` for YAML deserialization

## Breaking Changes

**None** - All existing APIs preserved for backward compatibility.

## Backward Compatibility

### API Methods Preserved
- `EvaluationEntry.to_dict()` - Still works, returns `dict[str, object]`
- `EvaluationEntry.from_dict()` - Still works, accepts `dict[str, Any]`
- `Coordinator.orchestrate()` - Signature unchanged (only added type hints)
- `MCPWrapper.create_notebook_query_spec()` - Signature unchanged

### Test Coverage
All existing tests pass:
- `tests/unit/test_memory_models.py` - 9/9 tests passing
- `tests/unit/test_coordinator_types.py` - 8/8 tests passing
- `tests/unit/test_mcp_wrapper_types.py` - 14/14 tests passing

**Total: 31/31 tests passing**

## mypy Configuration

### Tiered Enforcement (Phase 1)
```toml
[tool.mypy]
python_version = "3.14"
disallow_untyped_defs = true  # Tier 1 - require type hints on function signatures
warn_return_any = false  # Tier 2 - enable in next phase
warn_unused_ignores = false  # Tier 3 - enable in final phase
show_error_codes = true
```

### Per-Module Overrides
```toml
[[tool.mypy.overrides]]
module = "mastermind_cli.types.*"
strict = true  # New type modules are strict from day 1

[[tool.mypy.overrides]]
module = "mastermind_cli.memory.models"
strict = true  # Migrated in this plan

[[tool.mypy.overrides]]
module = "mastermind_cli.orchestrator.coordinator"
strict = true  # Migrated in this plan

[[tool.mypy.overrides]]
module = "mastermind_cli.orchestrator.mcp_wrapper"
strict = true  # Migrated in this plan

[[tool.mypy.overrides]]
module = "mastermind_cli.brains_legacy.*"
disallow_untyped_defs = false  # Legacy brains stay loose until later
```

### Pydantic v2 Plugin
```toml
[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

## Verification Results

### mypy Strict Mode
```bash
$ uv run mypy mastermind_cli/types/ mastermind_cli/memory/models.py \
  mastermind_cli/orchestrator/coordinator.py \
  mastermind_cli/orchestrator/mcp_wrapper.py --strict

Success: no issues found in 9 source files
```

### Type Safety Coverage
- **Types module:** 6 files, 0 errors
- **Memory models:** 1 file, 0 errors
- **Coordinator:** 1 file, 0 errors
- **MCP wrapper:** 1 file, 0 errors
- **Total:** 9 files migrated, 100% pass rate

## Known Limitations

### Out of Scope (Future Phases)
- `mastermind_cli/commands/` - CLI commands not yet migrated
- `mastermind_cli/brains_legacy/` - Legacy brains remain loose
- `mastermind_cli/orchestrator/plan_generator.py` - Untyped `__init__` (type: ignore added)
- `mastermind_cli/memory/storage.py` - datetime.utcnow() deprecation (future fix)

### Type Ignores
- `coordinator.py:37` - `PlanGenerator` untyped call (legitimate, out of scope)

## Migration Statistics

- **Files migrated:** 4 modules
- **Total lines changed:** ~500 lines
- **Type hints added:** 50+ method signatures
- **Tests created:** 31 new tests
- **mypy errors fixed:** 20+ type errors
- **Breaking changes:** 0

## Next Steps

### Phase 2: Full Strict Mode
- Enable `warn_return_any` Tier 2
- Migrate `mastermind_cli/commands/` modules
- Add `@validate_call` decorators to critical functions
- Enable `warn_unused_ignores` Tier 3

### Phase 3: Complete Coverage
- Migrate `mastermind_cli/brains_legacy/` modules
- Fix all remaining `# type: ignore` comments
- Achieve 100% mypy strict coverage across entire codebase

## References

- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [Python Type Hints PEP 484](https://www.python.org/dev/peps/pep-0484/)
- `.planning/phases/01-type-safety-foundation/01-CONTEXT.md`
