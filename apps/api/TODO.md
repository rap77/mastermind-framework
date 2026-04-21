# MasterMind - Fix & Suggestion Queue

## CRITICAL FIXES (blocking issues)

### ✅ Fix 1: Mypy module resolution error - FIXED
- **File:** `main.py:1`
- **Issue:** `Source file found twice under different module names: "worker.worker_pb2" and "mastermind.worker.worker_pb2"`
- **Impact:** Was blocking type checking with mypy entirely
- **Solution applied:**
  1. ✅ Created `mastermind/__init__.py` to establish proper module structure
  2. ✅ Added type stubs: `types-protobuf` and `types-grpcio`
  3. ✅ Updated `pyproject.toml` to exclude test files from mypy checking
- **Status:** ✅ FIXED - mypy now runs successfully

## WARNINGS (non-blocking)

### Warning 1: Cold start fallback in template extraction
- **File:** `mastermind_cli/experience/template_extractor.py`
- **Issue:** UserWarning emitted when system has zero templates after 50 sessions, threshold lowers to 2.0
- **Code location:** Around line 100-110 in `_extract_template_from_session()`
- **Impact:** Non-blocking runtime warning, indicates cold start mode activated
- **Action:** Monitor in production, consider adding telemetry for cold start events

### Warning 2: Test suite shows no runtime warnings
- **Status:** ✅ GOOD - No RuntimeWarning or UserWarning in test output
- **Note:** Previous concern about unawaited coroutine not present in current test run

## COVERAGE GAPS

### High Priority (0% coverage - critical business logic)

#### File: `mastermind_cli/commands/evaluation.py` (9.4K, 0%)
- **Priority:** HIGH
- **Reason:** Evaluation commands are part of core CLI functionality
- **Risk:** No test coverage for evaluation logic
- **Recommended tests:**
  - Test evaluation command execution
  - Test error handling
  - Test output formatting

#### File: `mastermind_cli/commands/framework.py` (4.3K, 0%)
- **Priority:** HIGH
- **Reason:** Framework management commands
- **Risk:** No validation of framework operations
- **Recommended tests:**
  - Test framework listing/installation
  - Test framework configuration
  - Test error cases

#### File: `mastermind_cli/orchestrator/event_emitter.py` (5.3K, 0%)
- **Priority:** HIGH
- **Reason:** Event emission is critical for observability and integrations
- **Risk:** No validation of event emission logic
- **Recommended tests:**
  - Test event emission
  - Test event formatting
  - Test error handling

### Medium Priority (0% coverage - supporting infrastructure)

#### Directory: `mastermind_cli/observability/` (3 files, 0%)
- **Files:**
  - `logging.py` (6 lines, 0%)
  - `tracer.py` (7 lines, 0%)
  - `__init__.py` (3 lines, 0%)
- **Priority:** MEDIUM
- **Reason:** Observability infrastructure important for production monitoring
- **Note:** These are small files, likely straightforward to test

### Low Priority (0% coverage - utils/types)

#### Files with minimal code:
- `mastermind_cli/utils/` (3 files, 0%) - git.py, yaml.py, validation.py
- `mastermind_cli/types/auth.py` (35 lines, 0%)
- `mastermind_cli/types/protocol.py` (37 lines, 0%)

## TYPE/LINTER ISSUES

### ✅ Fix 1: Mypy configuration - FIXED
- **Status:** ✅ FIXED - Now running successfully
- **Changes:**
  - Created `mastermind/__init__.py`
  - Added `types-protobuf` and `types-grpcio` to dev dependencies
  - Added `exclude = ["tests/", ".venv/"]` to mypy config

### Issue 2: Type annotation gaps (73 errors remaining)
- **Status:** 🔄 IN PROGRESS - 31 errors fixed, 73 remaining
- **Total errors:** 104 → 73 type errors across 8 files (31 errors resolved!)
- **Priority:** MEDIUM - Code works but needs type safety
- **Progress:**
  - ✅ Phase 1: Quick wins (main.py, services/channel_router.py, scripts/cleanup_interviews.py) - ALREADY FIXED
  - ✅ Phase 2: Medium priority router files - FIXED (18 errors resolved)
    - routers/audit.py (3 errors) - UUID type mismatch, len() on Iterable
    - routers/email.py (4 errors) - Missing type params, tuple unpacking
    - routers/instagram.py (5 errors) - Missing type params, added Any import
    - routers/whatsapp.py (4 errors) - Missing type params, added Any import
    - routers/channel_router.py (2 errors) - Implicit Optional issues
  - ✅ Phase 3: Added tests for evaluation.py - DONE (10 tests, all passing)
  - ⏳ Phase 4: High priority type errors (services/engram_sync.py - 20 errors) - PENDING

#### High priority type errors (>10 errors per file):

**File: `services/engram_sync.py` (20 errors)**
- Missing return type annotations (3 occurrences)
- Incompatible type assignments: `None` to non-optional types (6)
- Operations on `object` type instead of proper types (11)
- **Example:** Line 300-426 - List operations on `object` instead of `list`

**File: `routers/audit.py` (4 errors)**
- UUID type mismatch at line 705
- `len()` called on `Iterable[Row]` instead of `Sized` at lines 1437, 1440
- **Fix:** Cast to `list()` before `len()` or use proper type

**File: `scripts/escanear_proyecto.py` (10 errors)**
- Missing type parameters for generic types (`dict`, `list`)
- Collection operations on immutable types
- **Fix:** Add type annotations: `dict[str, Any]`, `list[str]`

**File: `scripts/escanear_proyecto_serena.py` (12 errors)**
- Same issues as `escanear_proyecto.py`
- **Fix:** Batch type annotation update needed

**File: `mastermind/worker/worker_pb2_grpc.py` (11 errors)**
- Generated gRPC code has no type annotations
- Module attribute errors for generated classes
- **Fix:** Add `# type: ignore` or regenerate with types

#### Medium priority type errors:

**Files with 3-5 errors:**
- `routers/email.py` (4 errors) - Missing type params
- `routers/instagram.py` (5 errors) - Missing type params
- `scripts/run_e2e_tests.py` (7 errors) - Return types + dict types
- `routers/channel_router.py` (4 errors) - Implicit Optional issues
- `routers/whatsapp.py` (5 errors) - Missing type params

**Quick wins (1-2 errors each):**
- `main.py` (2 errors) - Add `-> None` to `main()` function
- `services/channel_router.py` (2 errors) - Add return type
- `scripts/cleanup_interviews.py` (2 errors) - Add return type
- `routers/audit.py` single errors - UUID handling

### Issue 3: Ruff linter - All checks passed
- **Status:** ✅ NO ISSUES
- **Result:** `All checks passed!`
- **Note:** Codebase follows ruff standards perfectly

## COVERAGE SUMMARY

### Current Stats:
- **Total Coverage:** 4% (6177/6411 lines missing)
- **Files with 100% coverage:** 12 files
- **Files with 0% coverage:** 54 files

### Files with partial coverage (good progress):
- `mastermind_cli/state/database.py` - 19% (largest partially covered file)
- `mastermind_cli/types/brains.py` - 64%
- `mastermind_cli/types/interfaces.py` - 95%
- `mastermind_cli/types/parallel.py` - 44%

### Recommendation:
Focus on testing core business logic first:
1. Commands (evaluation, framework)
2. Orchestrator (event_emitter, coordinator, evaluator)
3. State management (database, repositories)
4. Experience tracking (template_extractor, logger)

## ACTION PLAN

### ✅ Immediate (today):
1. ✅ Create TODO.md (this file)
2. ✅ Fix mypy module resolution (add `__init__.py` or config)
3. ✅ Re-run mypy after fix to identify type issues
4. ✅ Fix quick wins (main.py, services/channel_router.py, scripts/cleanup_interviews.py)

### Short term (this week):
5. 🧪 Add tests for `evaluation.py` (HIGH impact, low effort - 9.4K file)
6. 🧪 Add tests for `framework.py` (HIGH impact, low effort - 4.3K file)
7. 🧪 Add tests for `event_emitter.py` (HIGH impact, medium effort - 5.3K file)
8. 🔧 Fix medium priority type errors (routers/audit.py, email.py, instagram.py, whatsapp.py)

### Medium term (next sprint):
9. 🧪 Add tests for `observability/` directory (3 small files)
10. 🧪 Improve coverage for `state/database.py` (19% → 50%+ target)
11. 🧪 Add tests for `orchestrator/` core modules
12. 🔧 Fix high priority type errors (services/engram_sync.py - 20 errors)

### Long term (ongoing):
13. 📈 Target 80%+ coverage for business logic
14. 🔍 Maintain 100% coverage for utilities and types
15. 📝 Add tests for all new code (TDD approach)

## NOTES

- Test suite passes: 854 tests, 0 failures
- Ruff linter: All checks passed
- No TODO/FIXME/XXX/HACK comments found in codebase
- No critical runtime warnings detected
- Coverage script: `uv run pytest --cov=mastermind_cli --cov-report=term-missing`
