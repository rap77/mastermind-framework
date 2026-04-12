# Test Fixing Patterns - MasterMind Framework v2.0

## Context
Patterns discovered during post-v2.0.0 test fixing sessions (2026-03-15 to 2026-03-16).

## Pattern 1: Pydantic Model Attribute Access

**Problem:** Tests treating Pydantic model instances as strings.

**Symptoms:**
- AssertionError: `assert 'text' in Brief(...)`
- Type errors comparing strings to objects

**Solution:**
Access the actual attribute:
```python
# Brief is a Pydantic model with problem_statement attribute
assert "text" in result.brief.problem_statement
```

**When to apply:**
- AssertionError with Pydantic model in output
- "in" operator failing on model objects

---

## Pattern 2: Callable vs Instance for Adapters

**Problem:** Passing object instance instead of method to adapters expecting callables.

**Symptoms:**
- `TypeError: 'X' object is not callable`
- RuntimeError about non-callable objects

**Solution:**
Pass the `.execute` method, not the object:
```python
# WRONG - Instance is not callable
adapter = LegacyBrainAdapter(
    brain_executor=MockLegacyBrain(),  # Instance
    ...
)

# CORRECT - Method is callable
adapter = LegacyBrainAdapter(
    brain_executor=MockLegacyBrain().execute,  # Method
    ...
)
```

**When to apply:**
- Adapter/wrapper classes with `brain_executor` or similar parameters
- "object is not callable" errors

---

## Pattern 3: Async Function Not Awaited

**Problem:** Calling async functions without `await` keyword.

**Symptoms:**
- `TypeError: cannot unpack non-iterable coroutine object`
- "coroutine was never awaited" warnings

**Solution:**
Add `await` before async function calls:
```python
# WRONG - async function not awaited
full_key, response = create_api_key(key_data)  # Returns coroutine

# CORRECT - await the async function
full_key, response = await create_api_key(key_data)  # Returns tuple
```

**When to apply:**
- "cannot unpack non-iterable coroutine object"
- Any function call that returns `Coroutine[...]`

---

## Pattern 4: asyncio.to_thread Variable Isolation

**Problem:** `asyncio.to_thread` executes functions in separate thread pool → local variables don't persist.

**Symptoms:**
- List/variable empty despite function being called multiple times
- `assert 0 == 3` when expecting multiple calls

**Solution:**
Use thread-safe communication (files, queues, multiprocessing.Manager):
```python
# WRONG - Local variable doesn't persist across threads
call_times = []
def track_time():
    call_times.append(asyncio.get_event_loop().time())
asyncio.to_thread(mock_func, ...)  # Different thread!

# CORRECT - File I/O is thread-safe
temp_file = tempfile.NamedTemporaryFile(delete=False)
def track_time():
    with open(temp_file.name, 'a') as f:
        f.write(f"{time.time()}\n")
asyncio.to_thread(mock_func, ...)
```

**When to apply:**
- Mocking functions called via `asyncio.to_thread`
- Variables not being updated despite function execution
- Needing thread-safe cross-thread communication

---

## Pattern 5: Test Isolation Issues

**Problem:** Tests pass individually but fail when run in suite.

**Symptoms:**
- Test passes: `pytest test_file.py::test_func` ✅
- Test fails: `pytest test_file.py` ❌
- Database state pollution between tests

**Common Causes:**
1. Fixtures not cleaning up database/state
2. Global variables modified by previous tests
3. Mock patches not being undone
4. Async event loop state pollution

**Investigation Steps:**
```bash
# Run test individually
pytest tests/unit/test_logger.py::TestContextManager::test_x -v

# Run test in file
pytest tests/unit/test_logger.py -v

# Check for differences
```

**Solutions:**
- Use `yield` in fixtures for cleanup
- `autouse=True` fixtures for database reset
- Explicit `unittest.mock.patch()` context managers
- `asyncio.run()` in tests instead of reusing event loop

---

## Quick Reference

| Error Pattern | Likely Cause | Fix |
|---------------|--------------|-----|
| `assert 'x' in Brief(...)` | Treating model as string | Access `.attribute` |
| `'X' object is not callable` | Passing instance instead of method | Use `.method` |
| `cannot unpack coroutine` | Missing `await` | Add `await` |
| `assert 0 == N` (called N times) | `asyncio.to_thread` isolation | Thread-safe IPC |
| Passes alone, fails in suite | Test isolation pollution | Fix cleanup |

---

## Related Files
- `.planning/phases/04-experience-store-production/.continue-here.md` - Current session handoff
- `SESSION-2026-03-16-POST-V2.0-TEST-FIXES-COMPLETE` - Detailed session log
