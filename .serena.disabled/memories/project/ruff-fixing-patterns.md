# Ruff Linting Fix Patterns - Systematic Debugging Results

**Session:** 2026-03-15
**Total Errors Fixed:** 36
**Methodology:** Systematic Debugging (4-phase process)

## Error Types and Solutions

### F841 - Local variable assigned but never used (18 cases)

**Root Cause:**
Variables assigned but return value never used. Common in tests where only side effects matter.

**Pattern 1: Testing side effects**
```python
# Before (F841)
results = await coordinator.execute_flow(brief, brain_ids)
assert len(coordinator.message_log) == 3

# After
await coordinator.execute_flow(brief, brain_ids)
assert len(coordinator.message_log) == 3
```

**Pattern 2: Performance measurement**
```python
# Before (F841)
task = await repo.create(task_id="task-perf-001", brain_id="brain-01")
start = time.perf_counter()
retrieved = await repo.get_task_status(task_id="task-perf-001")

# After
_ = await repo.create(task_id="task-perf-001", brain_id="brain-01")
start = time.perf_counter()
retrieved = await repo.get_task_status(task_id="task-perf-001")
```

**Pattern 3: Dead code**
```python
# Before (F841)
call_count = {"before": 0, "after": 0}  # Never used
execution_order = []

# After
execution_order = []  # Removed unused variable
```

**Solution Strategy:**
- Remove assignment if result is never used
- Use `_` if intentionally discarding
- Remove dead code variables

### F401 - Imported but unused (7 cases)

**Root Cause:**
Imports for availability checking in tests. Valid pattern, not actual errors.

**Pattern: Module availability test**
```python
# Before (F401)
try:
    from fastapi import Header
    from mastermind_cli.auth.api_keys import get_current_api_key
except ImportError:
    pytest.skip("FastAPI not installed")

# After (with noqa)
try:
    from fastapi import Header  # noqa: F401
    from mastermind_cli.auth.api_keys import get_current_api_key  # noqa: F401
except ImportError:
    pytest.skip("FastAPI not installed")
```

**Pattern: Import verification**
```python
# Before (F401)
def test_module_is_importable_without_errors():
    try:
        import mastermind_cli.types
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import: {e}")

# After (with noqa)
def test_module_is_importable_without_errors():
    try:
        import mastermind_cli.types  # noqa: F401
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import: {e}")
```

**Solution Strategy:**
- Add `# noqa: F401` to intentional test imports
- Don't refactor - this is a valid testing pattern

### F811 - Redefinition while unused (1 case)

**Root Cause:**
Copy-paste error creating duplicate function definitions.

**Pattern: Duplicate test function**
```python
# Before (F811)
def test_normalize_brain_7_output_partial(self):
    # First definition - complete with all asserts
    ...

def test_normalize_brain_7_output_partial(self):  # Duplicate!
    # Second definition - incomplete, missing asserts
    ...

# After - Remove duplicate
def test_normalize_brain_7_output_partial(self):
    # Only one definition remains
    ...
```

**Solution Strategy:**
- Identify which definition is complete/correct
- Remove the duplicate definition
- Verify no functionality is lost

### E402 - Module level import not at top (7 cases)

**Root Cause:**
sys.path manipulation before module imports. Necessary pattern in some scripts.

**Pattern: sys.path manipulation**
```python
# Before (E402)
import sys
import os

MASTERMIND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{MASTERMIND_ROOT}/tools/mastermind-cli")

from mastermind_cli.orchestrator import Coordinator, OutputFormatter

# After (with noqa)
import sys
import os

MASTERMIND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{MASTERMIND_ROOT}/tools/mastermind-cli")

from mastermind_cli.orchestrator import Coordinator, OutputFormatter  # noqa: E402
```

**Solution Strategy:**
- Add `# noqa: E402` to imports after sys.path manipulation
- Don't restructure - the pattern is intentional

### E712 - Comparisons to True/False (2 cases)

**Root Cause:**
Explicit boolean comparisons when implicit is preferred.

**Pattern: True comparison**
```python
# Before (E712)
assert client.is_brain_available(1) == True

# After
assert client.is_brain_available(1)
```

**Pattern: False comparison**
```python
# Before (E712)
assert client.is_brain_available(99) == False

# After
assert not client.is_brain_available(99)
```

**Solution Strategy:**
- Use `if x:` instead of `if x == True:`
- Use `if not x:` instead of `if x == False:`
- More Pythonic and cleaner

## Systematic Debugging Process Applied

### Phase 1: Root Cause Investigation
- Read error messages carefully
- Reproduced consistently with `ruff check`
- Identified patterns across files

### Phase 2: Pattern Analysis
- Found working examples in codebase
- Compared similar code patterns
- Understood intent behind each error

### Phase 3: Hypothesis
- Formed hypothesis: "These are intentional patterns, not bugs"
- Tested minimally with targeted fixes
- Verified each fix individually

### Phase 4: Implementation
- Applied fix to one file at a time
- Verified with `ruff check <file>`
- Confirmed no regressions

## Verification Commands

```bash
# Check specific error types
uv run ruff check tests/ --output-format=text | grep F841

# Check specific files
uv run ruff check path/to/file.py

# Full verification
uv run ruff check tests/ tools/ scripts/
```

## Time Taken

- Phase 1 (tests/): ~30 minutes for 22 errors
- Phase 2 (tools/): ~20 minutes for 14 errors
- **Total: ~50 minutes for 36 errors** (~1.4 min/error)

## Success Metrics

- ✅ 0 errors remaining
- ✅ All pre-commit hooks passing
- ✅ Commit successful (31714b7)
- ✅ No regressions introduced
