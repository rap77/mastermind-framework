# Session: Post-v2.0.0 Test Fixes - 2026-03-16

## Summary
Productive session fixing 4 integration tests and identifying key patterns for async/test issues in the MasterMind Framework v2.0.

## Test Results
- **Before:** 158 failed, 326 passed (67% pass rate)
- **After:** 4 specific tests fixed, 326 passing baseline maintained
- **Commit:** `a8d95ec` - fix(tests): resolve integration test failures with async/await and mock fixes

## Tests Fixed

1. **test_concurrent_executions_no_crosstalk**
   - Issue: `result.brief` treated as string, but it's a Brief object
   - Fix: Changed to `result.brief.problem_statement`
   - Pattern: Pydantic models have attributes, not string values

2. **test_legacy_brain_adapter_creates_isolated_context**
   - Issue: `'MockLegacyBrain' object is not callable`
   - Fix: Changed `brain_executor=MockLegacyBrain()` to `brain_executor=MockLegacyBrain().execute`
   - Pattern: LegacyBrainAdapter expects callable (method), not instance

3. **test_web_auth_with_database**
   - Issue: `TypeError: cannot unpack non-iterable coroutine object`
   - Fix: Added `await` to `create_api_key()` call
   - Pattern: Async functions must be awaited before unpacking results

4. **test_exponential_backoff_with_jitter**
   - Issue: `call_times` empty despite 3 mock invocations
   - Root cause: `asyncio.to_thread` executes in separate threads → locals don't persist
   - Fix: Used thread-safe file-based call counting (`tempfile.NamedTemporaryFile`)
   - Pattern: `asyncio.to_thread` breaks normal variable sharing between threads

## Key Patterns Discovered

### Pattern 1: Pydantic Model Access
```python
# WRONG - treating model as string
assert "text" in result.brief

# CORRECT - access model attribute
assert "text" in result.brief.problem_statement
```

### Pattern 2: Callable vs Instance
```python
# WRONG - passing instance
adapter = LegacyBrainAdapter(
    brain_executor=MockLegacyBrain(),  # Instance, not callable
    ...
)

# CORRECT - passing method (callable)
adapter = LegacyBrainAdapter(
    brain_executor=MockLegacyBrain().execute,  # Callable
    ...
)
```

### Pattern 3: asyncio.to_thread Threading
```python
# WRONG - variables don't persist across threads
call_times = []
def track_time():
    call_times.append(...)  # Different thread, different list
asyncio.to_thread(mock_func, ...)  # Executes in thread pool

# CORRECT - use thread-safe communication
temp_file = tempfile.NamedTemporaryFile(delete=False)
def track_time():
    with open(temp_file.name, 'a') as f:
        f.write(f"{time.time()}\n")  # File I/O is thread-safe
```

## Remaining Work
- ~120 tests still failing
- Main issue: Logger test isolation (pass individually, fail in suite)
- 4 E2E multi-user tests with auth issues (401 Unauthorized)
- 39 API stub tests (intentional, not bugs)

## Files Modified
- `tests/integration/test_pure_function_arch.py` - 3 fixes
- `tests/unit/test_task_executor.py` - 1 fix (thread-safe counting)

## Commits
- `a8d95ec` - Main fixes
- `5090eff` - WIP handoff

## Next Session Priorities
1. Logger test isolation investigation (blocks many other tests)
2. E2E multi-user auth fixes
3. Push to GitHub (7 commits ready)

## Handoff Location
`.planning/phases/04-experience-store-production/.continue-here.md`
