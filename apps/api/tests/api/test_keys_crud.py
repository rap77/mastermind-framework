"""Tests for API key management endpoints (ER-02).

Tests:
- POST /api/keys: create key, show-once pattern, mmsk_ format
- GET /api/keys: list masked keys (no full key)
- DELETE /api/keys/{id}: revoke key immediately

Requirements: ER-02
"""

import pytest

from mastermind_cli.api.routes.keys import _verify_key, validate_api_key_v2
from mastermind_cli.api.routes import keys as keys_routes


@pytest.mark.asyncio
async def test_create_key_success(client, auth_headers) -> None:
    """POST /api/keys creates a key and returns full_key (one-time)."""
    response = await client.post(
        "/api/keys", headers=auth_headers, json={"name": "Test Key"}
    )
    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert "full_key" in data
    assert "prefix" in data
    assert "suffix" in data
    assert "message" in data
    assert "Save this key" in data["message"]


@pytest.mark.asyncio
async def test_create_key_format_mmsk(client, auth_headers) -> None:
    """Created key starts with mmsk_ prefix."""
    response = await client.post("/api/keys", headers=auth_headers, json={})
    assert response.status_code == 201
    data = response.json()

    assert data["full_key"].startswith("mmsk_")
    assert len(data["full_key"]) == 37  # mmsk_ (5) + 32 hex = 37


@pytest.mark.asyncio
async def test_create_key_prefix_suffix_match(client, auth_headers) -> None:
    """prefix is first 13 chars, suffix is last 4 chars of full_key."""
    response = await client.post("/api/keys", headers=auth_headers, json={})
    assert response.status_code == 201
    data = response.json()

    full_key = data["full_key"]
    assert data["prefix"] == full_key[:13]
    assert data["suffix"] == full_key[-4:]


@pytest.mark.asyncio
async def test_create_key_auth_required(client) -> None:
    """POST /api/keys requires JWT."""
    response = await client.post("/api/keys", json={})
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_keys_masked(client, auth_headers) -> None:
    """GET /api/keys returns masked keys (prefix + suffix only, no full_key)."""
    # Create a key first
    create_resp = await client.post("/api/keys", headers=auth_headers, json={})
    assert create_resp.status_code == 201
    created = create_resp.json()

    # List keys
    list_resp = await client.get("/api/keys", headers=auth_headers)
    assert list_resp.status_code == 200
    data = list_resp.json()

    assert "keys" in data
    assert len(data["keys"]) >= 1

    # Find the created key
    found = next((k for k in data["keys"] if k["id"] == created["id"]), None)
    assert found is not None
    assert found["prefix"] == created["prefix"]
    assert found["suffix"] == created["suffix"]

    # full_key must NOT be present in masked list
    for key in data["keys"]:
        assert "full_key" not in key


@pytest.mark.asyncio
async def test_list_keys_auth_required(client) -> None:
    """GET /api/keys requires JWT."""
    response = await client.get("/api/keys")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_revoke_key_success(client, auth_headers) -> None:
    """DELETE /api/keys/{id} revokes key (status=revoked, key gone from list)."""
    # Create key
    create_resp = await client.post("/api/keys", headers=auth_headers, json={})
    key_id = create_resp.json()["id"]

    # Revoke key
    revoke_resp = await client.delete(f"/api/keys/{key_id}", headers=auth_headers)
    assert revoke_resp.status_code == 200
    data = revoke_resp.json()
    assert data["status"] == "revoked"
    assert data["id"] == key_id

    # Key should no longer appear in list
    list_resp = await client.get("/api/keys", headers=auth_headers)
    keys = list_resp.json()["keys"]
    key_ids = [k["id"] for k in keys]
    assert key_id not in key_ids


@pytest.mark.asyncio
async def test_revoke_key_not_found(client, auth_headers) -> None:
    """DELETE /api/keys/{id} returns 404 for nonexistent key."""
    response = await client.delete(
        "/api/keys/nonexistent-key-id-00001", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_revoke_key_auth_required(client) -> None:
    """DELETE /api/keys/{id} requires JWT."""
    response = await client.delete("/api/keys/some-key-id")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_key_isolation_cross_user(client, auth_headers, auth_headers_b) -> None:
    """User A cannot revoke User B's key (403)."""
    # User A creates a key
    create_resp = await client.post("/api/keys", headers=auth_headers, json={})
    key_id_a = create_resp.json()["id"]

    # User B tries to revoke User A's key
    revoke_resp = await client.delete(f"/api/keys/{key_id_a}", headers=auth_headers_b)
    assert revoke_resp.status_code == 403


@pytest.mark.asyncio
async def test_create_key_with_name(client, auth_headers) -> None:
    """POST /api/keys with name stores it and returns in list."""
    response = await client.post(
        "/api/keys", headers=auth_headers, json={"name": "My Production Key"}
    )
    assert response.status_code == 201
    key_id = response.json()["id"]

    list_resp = await client.get("/api/keys", headers=auth_headers)
    keys = list_resp.json()["keys"]
    found = next((k for k in keys if k["id"] == key_id), None)
    assert found is not None
    assert found["name"] == "My Production Key"


@pytest.mark.asyncio
async def test_create_key_without_name(client, auth_headers) -> None:
    """POST /api/keys without name is valid (name is optional)."""
    response = await client.post("/api/keys", headers=auth_headers, json={})
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_list_keys_empty(client, auth_headers) -> None:
    """GET /api/keys returns empty list when no keys exist."""
    response = await client.get("/api/keys", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["keys"] == []


@pytest.mark.asyncio
async def test_revoke_key_twice_returns_404(client, auth_headers) -> None:
    """Revoking an already-revoked key returns 404."""
    # Create and revoke
    create_resp = await client.post("/api/keys", headers=auth_headers, json={})
    key_id = create_resp.json()["id"]
    await client.delete(f"/api/keys/{key_id}", headers=auth_headers)

    # Second revoke → 404 (key is gone from active list)
    second_revoke = await client.delete(f"/api/keys/{key_id}", headers=auth_headers)
    assert second_revoke.status_code == 404


@pytest.mark.asyncio
async def test_validate_api_key_v2_accepts_injected_db_factory() -> None:
    """API key validation can build its DB connection through an injected factory."""
    raw_key = "mmsk_12345678deadbeefdeadbeefdeadbeef"
    factory_calls: list[str] = []

    class _Cursor:
        async def fetchone(self):
            return ("key-id", "user-123", "stored-hash")

    class _Conn:
        def __init__(self) -> None:
            self.execute_calls: list[tuple[str, list[object]]] = []
            self.committed = False

        async def execute(self, sql: str, params=None):
            self.execute_calls.append((sql, list(params or [])))
            return _Cursor()

        async def commit(self):
            self.committed = True

    class _FakeDB:
        def __init__(self, db_path: str) -> None:
            self.db_path = db_path
            self.conn = _Conn()
            self.schema_created = False

        async def create_api_keys_v2_schema(self) -> None:
            self.schema_created = True

        async def __aenter__(self) -> "_FakeDB":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            del exc_type, exc, tb

    fake_dbs: list[_FakeDB] = []

    def _db_factory(db_path: str) -> _FakeDB:
        factory_calls.append(db_path)
        db = _FakeDB(db_path)
        fake_dbs.append(db)
        return db

    result = await validate_api_key_v2(
        raw_key=raw_key,
        db_path="keys-test.db",
        db_factory=_db_factory,
    )

    assert result is None  # bcrypt verification still fails for the fake row
    assert factory_calls == ["keys-test.db"]
    assert len(fake_dbs) == 1
    assert fake_dbs[0].schema_created is True
    assert len(fake_dbs[0].conn.execute_calls) == 1


def test_verify_key_returns_false_for_invalid_bcrypt_hash() -> None:
    """Malformed bcrypt hashes should be treated as invalid keys."""
    assert _verify_key("mmsk_12345678deadbeefdeadbeefdeadbeef", "not-a-hash") is False


@pytest.mark.asyncio
async def test_validate_api_key_v2_logs_last_used_update_failure(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Best-effort last_used_at updates should log sqlite failures."""
    import sqlite3

    raw_key = "mmsk_12345678deadbeefdeadbeefdeadbeef"
    caplog.set_level("WARNING")

    class _Cursor:
        def __init__(self) -> None:
            self._calls = 0

        async def fetchone(self):
            self._calls += 1
            if self._calls == 1:
                return ("key-id", "user-123", "stored-hash")
            return None

    class _Conn:
        async def execute(self, sql: str, params=None):
            del params
            if sql.startswith("UPDATE api_keys_v2"):
                raise sqlite3.Error("boom")
            return _Cursor()

        async def commit(self):
            return None

    class _FakeDB:
        def __init__(self, db_path: str) -> None:
            self.db_path = db_path
            self.conn = _Conn()

        async def create_api_keys_v2_schema(self) -> None:
            return None

        async def __aenter__(self) -> "_FakeDB":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            del exc_type, exc, tb

    original_verify = keys_routes._verify_key
    keys_routes._verify_key = lambda *_args, **_kwargs: True  # type: ignore[assignment]
    try:
        result = await validate_api_key_v2(
            raw_key=raw_key,
            db_path="keys-test.db",
            db_factory=lambda db_path: _FakeDB(db_path),
        )
    finally:
        keys_routes._verify_key = original_verify  # type: ignore[assignment]

    assert result == "user-123"
    assert "api key last_used_at update failed" in caplog.text
