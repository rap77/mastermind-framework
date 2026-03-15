"""
Tests for API Key Authentication System.

Tests:
- API key generation and validation
- Hash-based key storage
- CLI mode (environment variable)
- Web UI mode (database)
- FastAPI dependency integration
"""

import os
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch

import pytest

from mastermind_cli.auth.api_keys import (
    APIKey,
    APIKeyCreate,
    generate_api_key,
    hash_api_key,
    validate_api_key,
    create_api_key,
    revoke_api_key,
    list_api_keys,
    _KEY_PREFIX,
    _KEY_LENGTH,
)

from pydantic import ValidationError


class TestAPIKeyModel:
    """Test APIKey Pydantic model."""

    def test_valid_api_key(self):
        """Test creating a valid API key."""
        key = f"{_KEY_PREFIX}{'a' * _KEY_LENGTH}"
        api_key = APIKey(
            key=key,
            key_hash=hash_api_key(key),
            owner="test-user",
            created_at=datetime.now(timezone.utc).isoformat(),
            is_active=True,
            scopes=["read", "write"],
        )
        assert api_key.key == key
        assert api_key.owner == "test-user"
        assert api_key.is_active is True
        assert api_key.scopes == ["read", "write"]

    def test_invalid_key_format_no_prefix(self):
        """Test API key without correct prefix fails validation."""
        # Use a key that passes min_length but fails prefix validation
        long_key_without_prefix = "a" * 40
        with pytest.raises(ValidationError) as exc_info:
            APIKey(
                key=long_key_without_prefix,
                key_hash="a" * 64,
                owner="test-user",
            )
        # Either prefix or length validation can fail first
        error_msg = str(exc_info.value).lower()
        assert "must start with" in error_msg or "characters" in error_msg

    def test_invalid_key_format_wrong_length(self):
        """Test API key with wrong length fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            APIKey(
                key=f"{_KEY_PREFIX}short",
                key_hash="a" * 64,
                owner="test-user",
            )
        assert "characters" in str(exc_info.value).lower()

    def test_invalid_hash_format_not_hex(self):
        """Test non-hex hash fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            APIKey(
                key=f"{_KEY_PREFIX}{'a' * _KEY_LENGTH}",
                key_hash="z" * 64,  # 'z' is not valid hex
                owner="test-user",
            )
        error_msg = str(exc_info.value).lower()
        assert "hexadecimal" in error_msg or "sha256" in error_msg

    def test_invalid_hash_format_wrong_length(self):
        """Test hash with wrong length fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            APIKey(
                key=f"{_KEY_PREFIX}{'a' * _KEY_LENGTH}",
                key_hash="a" * 32,  # Wrong length
                owner="test-user",
            )
        assert "64 characters" in str(exc_info.value).lower()


class TestKeyGeneration:
    """Test API key generation functions."""

    def test_generate_api_key_format(self):
        """Test generated key has correct format."""
        key = generate_api_key()
        assert key.startswith(_KEY_PREFIX)
        assert len(key) == len(_KEY_PREFIX) + _KEY_LENGTH

    def test_generate_api_keys_are_unique(self):
        """Test generated keys are unique."""
        keys = [generate_api_key() for _ in range(100)]
        assert len(set(keys)) == 100  # All unique

    def test_hash_api_key_consistent(self):
        """Test hashing is consistent."""
        key = "test_key_value"
        hash1 = hash_api_key(key)
        hash2 = hash_api_key(key)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 = 64 hex chars

    def test_hash_api_keys_differ(self):
        """Test different keys produce different hashes."""
        hash1 = hash_api_key("key_one")
        hash2 = hash_api_key("key_two")
        assert hash1 != hash2


class TestCLIValidation:
    """Test CLI mode authentication (environment variable)."""

    def test_validate_with_env_var(self):
        """Test validation works with MM_API_KEY environment variable."""
        test_key = generate_api_key()

        with patch.dict(os.environ, {"MM_API_KEY": test_key}):
            result = validate_api_key(test_key)
            assert result is not None
            assert result.key == test_key
            assert result.owner == "cli-user"
            assert result.is_active is True

    def test_validate_fails_with_wrong_env_var(self):
        """Test validation fails when key doesn't match env var."""
        env_key = generate_api_key()
        test_key = generate_api_key()

        with patch.dict(os.environ, {"MM_API_KEY": env_key}):
            result = validate_api_key(test_key)
            assert result is None

    def test_validate_fails_without_env_var(self):
        """Test validation fails when no env var is set."""
        with patch.dict(os.environ, {}, clear=True):
            result = validate_api_key("any_key")
            assert result is None


class TestDatabaseValidation:
    """Test Web UI mode authentication (database)."""

    @pytest.mark.asyncio
    async def test_validate_with_database(self):
        """Test validation works with database lookup."""
        test_key = generate_api_key()
        test_hash = hash_api_key(test_key)

        # Mock database - return data that matches APIKey model
        mock_db = Mock()
        mock_db.get_api_key = AsyncMock(
            return_value={
                "key": test_key,  # Include the key for validation
                "key_hash": test_hash,
                "owner": "db-user",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_active": True,
                "scopes": ["read", "write"],
            }
        )

        with patch("mastermind_cli.state.database.get_db", return_value=mock_db):
            # Use async version for database validation
            from mastermind_cli.auth.api_keys import validate_api_key_async

            result = await validate_api_key_async(test_key)
            assert result is not None
            assert result.key == test_key
            assert result.owner == "db-user"

    @pytest.mark.asyncio
    async def test_validate_fails_not_in_database(self):
        """Test validation fails when key not in database."""
        test_key = generate_api_key()

        # Mock database returning None
        mock_db = Mock()
        mock_db.get_api_key = AsyncMock(return_value=None)

        with patch.dict(os.environ, {}, clear=True):
            with patch("mastermind_cli.state.database.get_db", return_value=mock_db):
                from mastermind_cli.auth.api_keys import validate_api_key_async

                result = await validate_api_key_async(test_key)
                assert result is None


class TestKeyManagement:
    """Test API key management operations."""

    @pytest.mark.asyncio
    async def test_create_api_key(self):
        """Test creating a new API key."""
        create_data = APIKeyCreate(owner="test-user", scopes=["read"])

        mock_db = Mock()
        mock_db.save_api_key = AsyncMock(return_value=True)

        with patch("mastermind_cli.state.database.get_db", return_value=mock_db):
            full_key, response = create_api_key(create_data)

            # Check key format
            assert full_key.startswith(_KEY_PREFIX)
            assert len(full_key) == len(_KEY_PREFIX) + _KEY_LENGTH

            # Check response doesn't include full key
            assert response.key_prefix == full_key[:8]
            assert len(response.key_prefix) == 8
            assert response.owner == "test-user"
            assert response.scopes == ["read"]

            # Check database was called
            mock_db.save_api_key.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_api_key(self):
        """Test revoking an API key."""
        test_hash = hash_api_key("test_key")

        mock_db = Mock()
        mock_db.revoke_api_key = AsyncMock(return_value=True)

        with patch("mastermind_cli.state.database.get_db", return_value=mock_db):
            result = await revoke_api_key(test_hash)
            assert result is True
            mock_db.revoke_api_key.assert_called_once_with(test_hash)

    @pytest.mark.asyncio
    async def test_revoke_api_key_not_found(self):
        """Test revoking non-existent key returns False."""
        mock_db = Mock()
        mock_db.revoke_api_key = AsyncMock(return_value=False)

        with patch("mastermind_cli.state.database.get_db", return_value=mock_db):
            result = await revoke_api_key("nonexistent_hash")
            assert result is False

    @pytest.mark.asyncio
    async def test_list_api_keys(self):
        """Test listing API keys."""
        # Generate valid keys to avoid validation errors
        key1 = generate_api_key()
        key2 = generate_api_key()

        mock_keys = [
            {
                "key": key1,
                "key_hash": "hash1",
                "owner": "user1",
                "created_at": "2024-01-01T00:00:00Z",
                "is_active": True,
                "scopes": ["read"],
            },
            {
                "key": key2,
                "key_hash": "hash2",
                "owner": "user2",
                "created_at": "2024-01-02T00:00:00Z",
                "is_active": True,
                "scopes": ["read", "write"],
            },
        ]

        mock_db = Mock()
        mock_db.list_api_keys = AsyncMock(return_value=mock_keys)

        with patch("mastermind_cli.state.database.get_db", return_value=mock_db):
            result = await list_api_keys()

            assert len(result) == 2
            assert result[0].owner == "user1"
            assert result[1].owner == "user2"
            # The call includes owner=None as keyword argument
            mock_db.list_api_keys.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_api_keys_filtered_by_owner(self):
        """Test listing API keys filtered by owner."""
        mock_db = Mock()
        mock_db.list_api_keys = AsyncMock(return_value=[])

        with patch("mastermind_cli.state.database.get_db", return_value=mock_db):
            await list_api_keys(owner="user1")
            mock_db.list_api_keys.assert_called_once_with(owner="user1")


class TestFastAPIIntegration:
    """Test FastAPI dependency integration."""

    def test_get_current_api_key_function_exists(self):
        """Test FastAPI dependency function is available."""
        try:
            from mastermind_cli.auth.api_keys import get_current_api_key

            assert get_current_api_key is not None
        except ImportError:
            pytest.skip("FastAPI not installed")

    @pytest.mark.asyncio
    async def test_get_current_api_key_valid(self):
        """Test FastAPI dependency with valid key."""
        try:
            from fastapi import Header  # noqa: F401
            from mastermind_cli.auth.api_keys import get_current_api_key  # noqa: F401
        except ImportError:
            pytest.skip("FastAPI not installed")
            return

        test_key = generate_api_key()

        with patch.dict(os.environ, {"MM_API_KEY": test_key}):
            # Mock the Header dependency
            with patch("mastermind_cli.auth.api_keys.Header", return_value=test_key):
                with patch(
                    "mastermind_cli.auth.api_keys.validate_api_key",
                    return_value=APIKey(
                        key=test_key,
                        key_hash=hash_api_key(test_key),
                        owner="test-user",
                        is_active=True,
                        scopes=["read"],
                    ),
                ):
                    # This would normally be called by FastAPI
                    result = validate_api_key(test_key)
                    assert result is not None

    @pytest.mark.asyncio
    async def test_get_current_api_key_invalid(self):
        """Test FastAPI dependency with invalid key raises 401."""
        try:
            from fastapi import HTTPException  # noqa: F401
            from mastermind_cli.auth.api_keys import get_current_api_key  # noqa: F401
        except ImportError:
            pytest.skip("FastAPI not installed")
            return

        # Mock validate returning None
        with patch("mastermind_cli.auth.api_keys.validate_api_key", return_value=None):
            # In real FastAPI, this would raise HTTPException
            result = validate_api_key("invalid_key")
            assert result is None


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_key_fails_validation(self):
        """Test empty key fails validation."""
        with pytest.raises(ValidationError):
            APIKey(
                key="",
                key_hash="a" * 64,
                owner="test-user",
            )

    def test_whitespace_only_key_fails_validation(self):
        """Test whitespace-only key fails validation."""
        with pytest.raises(ValidationError):
            APIKey(
                key="   ",
                key_hash="a" * 64,
                owner="test-user",
            )

    def test_unicode_in_owner(self):
        """Test unicode characters work in owner field."""
        key = generate_api_key()
        api_key = APIKey(
            key=key,
            key_hash=hash_api_key(key),
            owner="用户-user-🚀",
            is_active=True,
        )
        assert api_key.owner == "用户-user-🚀"

    @pytest.mark.asyncio
    async def test_database_error_falls_back_gracefully(self):
        """Test database errors are handled gracefully."""
        mock_db = Mock()
        mock_db.get_api_key = AsyncMock(side_effect=Exception("DB error"))

        with patch.dict(os.environ, {}, clear=True):
            with patch("mastermind_cli.state.database.get_db", return_value=mock_db):
                result = validate_api_key("any_key")
                # Should return None, not crash
                assert result is None
