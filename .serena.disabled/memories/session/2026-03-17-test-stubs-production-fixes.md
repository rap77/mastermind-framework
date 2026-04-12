# Session 2026-03-17 — Test Stubs: Production Fixes (Part 1)

## Commit
`6e93428` - wip: production fixes for 48 test stubs - get_db_path injection, hash_token SHA256, audit middleware

## Decision
User chose **Opción A**: implement all 48 failing test stubs (38 api/ + 8 perf/ + 2 real failures).

## What Was Done

### Production Bugs Found & Fixed (6 files)

| File | Fix |
|------|-----|
| `mastermind_cli/api/dependencies.py` | NEW — shared `get_db_path()` for all routes |
| `mastermind_cli/types/auth.py` | `hash_token` bcrypt → SHA256 (bcrypt has random salt per call, DB lookup by equality never worked) |
| `mastermind_cli/api/routes/auth.py` | Full rewrite: injects `get_db_path` + sets `request.state.user_id` in all auth deps |
| `mastermind_cli/api/routes/tasks.py` | Import `get_db_path` from dependencies (was defined locally) |
| `mastermind_cli/api/websocket.py` | Injects `get_db_path` in WebSocket endpoint |
| `mastermind_cli/api/app.py` | Audit middleware: reads `user_id` AFTER `call_next` (was before — always None) |

### Root Cause Analysis

1. **hash_token bug**: `bcrypt.gensalt()` generates new salt each call → `WHERE key_hash = ?` with `hash_token(token)` NEVER matches stored hash. Fix: SHA256.
2. **`:memory:` per-request**: Each `DatabaseConnection(":memory:")` creates separate in-memory DB. Login session → different DB than Refresh → always 401. Fix: `get_db_path` dependency.
3. **Audit middleware timing**: `user_id = getattr(request.state, "user_id", None)` ran BEFORE `call_next`, but auth deps set it INSIDE `call_next`. Fix: move read after.
4. **Local get_db_path in tasks.py**: One override in tests couldn't cover auth routes. Fix: shared `dependencies.py`.

## What's Pending (next session)

1. Add `user_id` column to `executions` table in `database.py` + filter in tasks.py endpoints
2. Create `tests/api/conftest.py` with fixtures
3. Write all 8 test files (test_app, test_auth, test_executions, test_sessions, test_audit, test_websocket, perf/test_db_queries, perf/test_websocket_perf)
4. Fix `test_parse_follow_up_basic`: change `question=` → `_question=` (1 line)
5. Fix `test_web_auth_with_database`: patch `mastermind_cli.auth.api_keys.get_db` to use connected tmp DB

## Key Test Patterns (for next session)

### conftest.py structure
```python
TEST_USER_ID = "test-user-id-001"
TEST_PASSWORD_HASH = bcrypt.hashpw("testpass123".encode(), bcrypt.gensalt(rounds=4)).decode()

@pytest.fixture
def db_path(tmp_path):  # SYNC fixture using asyncio.run()
    asyncio.run(setup_with_schema_and_user(path))
    return path

@pytest.fixture
def app(db_path):  # SYNC — overrides get_db_path
    application = create_app(db_path)
    application.dependency_overrides[get_db_path] = lambda: db_path
    return application

@pytest_asyncio.fixture
async def client(app):  # ASYNC — for API tests
    async with AsyncClient(transport=ASGITransport(app=app), ...) as c: yield c

@pytest.fixture
def sync_client(app):  # SYNC — for WebSocket tests
    return TestClient(app)
```

### Import for override
```python
from mastermind_cli.api.dependencies import get_db_path
```
This covers ALL routes (auth, tasks, websocket) with one override.

## Current Test State
- Full suite (excluding e2e): **422 passed, 48 failed, 5 skipped**
- 9 commits not yet pushed to GitHub
- `.continue-here.md` checkpoint updated with full implementation plan
