# Session 2026-03-17 — Test Stubs COMPLETE

## Commits
- `dc38c1e` - test(api): implement 48 test stubs + fix 2 real failures — 467 passing
- `dfc8c3f` - wip: post-v2.0 test stubs complete (continue-here updated)

## Final State
**Suite: 467 passed, 0 failed, 8 skipped** (was: 422/48/5)
**11 commits pending push to GitHub** (e54c51e → dfc8c3f)

## What Was Done

### Files Created
- `tests/api/conftest.py` — fixtures: db_path, app, client (async), sync_client, auth_headers, auth_headers_b, valid_jwt, valid_refresh_token

### Test Files Implemented (48 stubs → real tests)
| File | Tests | Notes |
|------|-------|-------|
| `tests/api/test_app.py` | 3 | health check, routes registered, CORS |
| `tests/api/test_auth.py` | 9 | login, refresh rotation (1.1s sleep), api keys, logout |
| `tests/api/test_executions.py` | 8 | CRUD + 3 skip (export=frontend-only) |
| `tests/api/test_sessions.py` | 5 | isolation, concurrent, persistence |
| `tests/api/test_audit.py` | 4 | log created, structure, no GETs, query |
| `tests/api/test_websocket.py` | 8 | connect, invalid, broadcast, throttle, multi, disconnect |
| `tests/perf/test_db_queries.py` | 4 | latency benchmarks |
| `tests/perf/test_websocket_perf.py` | 4 | broadcast benchmarks |

### Production Fixes (dc38c1e)
- `mastermind_cli/state/database.py` — added `user_id TEXT` column to executions table
- `mastermind_cli/api/routes/tasks.py` — WHERE user_id = ? in list/get/cancel/graph endpoints; get_task_state now injects db_path

### Real Failure Fixes
- `test_parse_follow_up_basic`: `question=` → `_question=` (function signature uses leading underscore)
- `test_web_auth_with_database`: `create_api_key` doesn't call `connect()` — fixed by passing pre-connected instance via `patch("mastermind_cli.state.database.get_db", return_value=connected_db)`

## Key Patterns Learned

### conftest.py pattern for FastAPI + SQLite
```python
@pytest.fixture
def db_path(tmp_path):
    asyncio.run(setup_schema_and_users(str(tmp_path / "test.db")))
    return str(tmp_path / "test.db")

@pytest.fixture
def app(db_path):
    application = create_app(db_path)
    application.dependency_overrides[get_db_path] = lambda: db_path
    return application
```

### JWT rotation timing issue
JWT tokens use second-resolution `exp`. Same-second tokens are identical → rotation check fails.
Fix: `await asyncio.sleep(1.1)` before first refresh in rotation tests.

### Patching local imports
`create_api_key` does `from mastermind_cli.state.database import get_db` inside function body.
Patch: `patch("mastermind_cli.state.database.get_db", return_value=connected_db)` — this works because Python looks up `get_db` in the module dict at import time, which is the patched Mock.

### token_type case
Auth endpoint returns `token_type="Bearer"` (capital B). Use `.lower() == "bearer"` in assertions.

### WebSocket tests use sync_client
`TestClient` from starlette supports WebSocket context managers. Use `with sync_client.websocket_connect(url):` (no `as ws` to avoid F841).

## Next Session
- `git push origin master` — push 11 commits
- Consider: v2.1 planning, milestone closure, or next feature
