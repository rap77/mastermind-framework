# Mypy Type Safety Fixing Patterns

**Context:** Phase 04 code review - fixing all 259 mypy strict errors across codebase
**Session:** 2026-03-15 - 117/259 errors fixed (45% reduction)

## Common Mypy Error Patterns and Fixes

### 1. Generic Type Parameters (Most Common - ~60% of errors)
**Error:** `Missing type parameters for generic type "Dict"`
**Fix:** `Dict` → `dict[str, Any]`

```python
# Before
from typing import Dict
def foo(data: Dict) -> Dict:
    return {}

# After
from typing import Any
def foo(data: dict[str, Any]) -> dict[str, Any]:
    return {}
```

**Affected types:**
- `Dict` → `dict[str, Any]` or `dict[int, dict[str, Any]]`
- `List` → `list[str]` or `list[Any]`
- `dict` → `dict[str, Any]` (when using lowercase)

### 2. Missing Return Type Annotations (~20% of errors)
**Error:** `Function is missing a return type annotation`
**Fix:** Add `-> None` or proper return type

```python
# Before
@click.group()
def framework():
    pass

# After
@click.group()
def framework() -> None:
    pass
```

**Common cases:**
- Click commands: `-> None`
- Async void functions: `async def foo() -> None:`
- Class methods: `def method(self) -> ReturnType:`

### 3. Implicit Optional (~10% of errors)
**Error:** `Incompatible default for argument "x" (default has type "None", argument has type "str")`
**Fix:** Add `Optional` type hint

```python
# Before
def __init__(self, skills_dir: str = None):

# After
def __init__(self, skills_dir: Optional[str] = None) -> None:
```

### 4. Variable Type Annotations (~5% of errors)
**Error:** `Need type annotation for "var" (hint: "var: dict[<type>, <type>] = ...")`
**Fix:** Add type annotation to variable declaration

```python
# Before
results = {}
context_types = {}
verdict_counts = {}

# After
results: dict[str, Any] = {}
context_types: dict[str, int] = {}
verdict_counts: dict[str, int] = {}
```

### 5. Variable Shadowing (~2% of errors)
**Error:** Type confusion when variable name reused
**Fix:** Rename inner variable to avoid shadowing

```python
# Before - causes type confusion
sources = list(sources_dir.glob("*.md"))  # list[Path]
for brain in brains_data:
    sources = brain["sources"]  # int - shadows outer variable!
    if sources > 0:  # Error: can't compare list[Path] to int
        ...

# After - clear variable names
source_files = list(sources_dir.glob("*.md"))  # list[Path]
for brain in brains_data:
    source_count = brain["sources"]  # int - distinct name
    if source_count > 0:  # Works correctly
        ...
```

### 6. Lambda Function Type Hints (~1% of errors)
**Error:** `Argument "key" to "max" has incompatible type overloaded function`
**Fix:** Use explicit lambda with type hints

```python
# Before
return max(flow_scores, key=flow_scores.get)

# After
return max(flow_scores.keys(), key=lambda k: flow_scores[k])
```

### 7. Returning Any from Function (~2% of errors)
**Error:** `Returning Any from function declared to return "dict[str, Any]`
**Fix:** Add type assertion or proper typing

```python
# Before
def _load_yaml(self, filename: str) -> Dict:
    return yaml.safe_load(filepath)  # Returns Any

# After
def _load_yaml(self, filename: str) -> dict[str, Any]:
    parsed: dict[str, Any] = yaml.safe_load(filepath)
    return parsed
```

## Batch Fixing Strategy

### High-Volume Fixes (sed + Edit)
1. Replace all `Dict` with `dict[str, Any]`
2. Add `-> None` to all click commands
3. Add type annotations to empty dicts: `{} → dict[str, Any] = {}`

### Manual Fixes (Careful with each)
1. Optional type hints (need to check if None is valid)
2. Return type annotations (need to determine correct type)
3. Variable shadowing (need to understand context)
4. Complex type assertions (need to verify runtime behavior)

## Import Organization

**When using `Any`:**
```python
from typing import Any, Dict, List, Optional  # Add Any when needed
```

**Common mistake:** Forgetting to add `Any` to imports after using it in type hints.

## Pre-commit Hook Considerations

**Problem:** Pre-commit mypy runs on ENTIRE codebase (64 files), not just staged files
**Solution:** Fix all errors before committing, or adjust hook to only check staged files

**Files modified in this session:** 25+ files across:
- orchestrator/ (9 files)
- commands/ (5 files)
- memory/ (3 files)
- state/ (2 files)
- types/ (2 files)
- compatibility/ (1 file)
- utils/ (1 file)
- tests/ (3 files)

## Progress Tracking

**Start:** 259 mypy errors
**End:** 142 mypy errors
**Fixed:** 117 errors (45% reduction)
**Rate:** ~117 errors per session
**Remaining:** 142 errors in more complex files (mcp_wrapper.py, task_executor.py, memory/logger.py, etc.)
