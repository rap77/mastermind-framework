"""
API Key Authentication System for MasterMind Framework.

Supports two authentication modes:
1. CLI: Environment variable (MM_API_KEY)
2. Web UI: SQLite database with X-API-Key header

This is a simplified auth system suitable for v2.0.
Future v3.0 will add OAuth2/JWT refresh token rotation.
"""

from __future__ import annotations

import os
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Final

from pydantic import BaseModel, Field, field_validator


# ===== CONSTANTS =====

_KEY_PREFIX: Final = "mmsk_"  # MasterMind Secret Key
_KEY_LENGTH: Final = 32  # 256-bit key
_HASH_ALGORITHM: Final = "sha256"


# ===== MODELS =====

class APIKey(BaseModel):
    """
    API Key model for authentication.

    Attributes:
        key: The API key (format: mmsk_<random>)
        key_hash: SHA256 hash of the key (for storage)
        owner: Owner identifier (email or username)
        created_at: ISO timestamp of creation
        is_active: Whether the key is active
        scopes: List of allowed scopes (e.g., ["read", "write"])
    """

    key: str = Field(..., min_length=37, max_length=100)
    key_hash: str = Field(..., min_length=64, max_length=64)
    owner: str = Field(..., min_length=1, max_length=100)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_active: bool = Field(default=True)
    scopes: list[str] = Field(default_factory=list)

    @field_validator("key")
    @classmethod
    def validate_key_format(cls, v: str) -> str:
        """Validate API key format."""
        if not v.startswith(_KEY_PREFIX):
            raise ValueError(f"API key must start with '{_KEY_PREFIX}'")
        expected_length = len(_KEY_PREFIX) + _KEY_LENGTH
        if len(v) != expected_length:
            raise ValueError(f"API key must be {expected_length} characters")
        return v

    @field_validator("key_hash")
    @classmethod
    def validate_hash_format(cls, v: str) -> str:
        """Validate SHA256 hash format."""
        if len(v) != 64:  # SHA256 produces 64 hex chars
            raise ValueError("Hash must be 64 characters (SHA256)")
        # Try to validate it's hex by checking each character
        try:
            int(v, 16)
        except ValueError:
            raise ValueError("Hash must be hexadecimal (SHA256 format)")
        return v


class APIKeyCreate(BaseModel):
    """Input model for creating a new API key."""

    owner: str = Field(..., min_length=1, max_length=100)
    scopes: list[str] = Field(default=["read", "write"])


class APIKeyResponse(BaseModel):
    """Response model for API key creation (excludes the actual key)."""

    key_prefix: str = Field(..., description="First 8 chars of key for identification")
    key_hash: str
    owner: str
    created_at: str
    is_active: bool
    scopes: list[str]


# ===== KEY GENERATION =====

def generate_api_key() -> str:
    """
    Generate a new API key.

    Returns:
        API key in format: mmsk_<32_random_chars>
    """
    random_part = secrets.token_urlsafe(_KEY_LENGTH)[:_KEY_LENGTH]
    return f"{_KEY_PREFIX}{random_part}"


def hash_api_key(key: str) -> str:
    """
    Hash an API key using SHA256.

    Args:
        key: The API key to hash

    Returns:
        Hex-encoded SHA256 hash
    """
    return hashlib.sha256(key.encode()).hexdigest()


# ===== VALIDATION =====

def validate_api_key(api_key: str) -> APIKey | None:
    """
    Validate an API key against environment variable or database.

    Priority order:
    1. Environment variable MM_API_KEY (CLI usage)
    2. SQLite database (Web UI usage)

    Args:
        api_key: The API key to validate

    Returns:
        APIKey object if valid, None otherwise

    Note:
        This is a synchronous wrapper. Database calls will fail if called
        from async context. Use validate_api_key_async for async contexts.
    """
    # 1. Check environment variable (CLI mode)
    env_key = os.getenv("MM_API_KEY")
    if env_key and api_key == env_key:
        # Create APIKey from environment
        return APIKey(
            key=api_key,
            key_hash=hash_api_key(api_key),
            owner="cli-user",
            created_at=datetime.now(timezone.utc).isoformat(),
            is_active=True,
            scopes=["read", "write"],
        )

    # 2. Check SQLite database (Web UI mode) - synchronous version
    # For async contexts, use validate_api_key_async instead
    return None  # Database validation not supported in sync mode


async def validate_api_key_async(api_key: str) -> APIKey | None:
    """
    Async version of validate_api_key for database lookups.

    Args:
        api_key: The API key to validate

    Returns:
        APIKey object if valid, None otherwise
    """
    # 1. Check environment variable first (CLI mode)
    env_key = os.getenv("MM_API_KEY")
    if env_key and api_key == env_key:
        return APIKey(
            key=api_key,
            key_hash=hash_api_key(api_key),
            owner="cli-user",
            created_at=datetime.now(timezone.utc).isoformat(),
            is_active=True,
            scopes=["read", "write"],
        )

    # 2. Check SQLite database (Web UI mode)
    try:
        from mastermind_cli.state.database import get_db

        db = get_db()
        key_data = await db.get_api_key(hash_api_key(api_key))

        if key_data:
            return APIKey(**key_data)
    except Exception:
        # Database not available or error
        pass

    return None


def validate_api_key_hash(api_key_hash: str) -> APIKey | None:
    """
    Validate an API key by its hash (for database queries).

    Args:
        api_key_hash: SHA256 hash of the API key

    Returns:
        APIKey object if valid, None otherwise
    """
    try:
        from mastermind_cli.state.database import get_db

        db = get_db()
        key_data = db.get_api_key(api_key_hash)

        if key_data:
            return APIKey(**key_data)
    except Exception:
        pass

    return None


# ===== KEY MANAGEMENT =====

def create_api_key(create_data: APIKeyCreate) -> tuple[str, APIKeyResponse]:
    """
    Create a new API key and store it in the database.

    Args:
        create_data: Key creation parameters

    Returns:
        Tuple of (full_key, response_without_key)
    """
    key = generate_api_key()
    key_hash = hash_api_key(key)

    api_key = APIKey(
        key=key,
        key_hash=key_hash,
        owner=create_data.owner,
        created_at=datetime.now(timezone.utc).isoformat(),
        is_active=True,
        scopes=create_data.scopes,
    )

    # Store in database
    try:
        from mastermind_cli.state.database import get_db

        db = get_db()
        db.save_api_key(api_key.model_dump())
    except Exception:
        # Database not available - still return the key
        pass

    response = APIKeyResponse(
        key_prefix=key[:8],
        key_hash=key_hash,
        owner=api_key.owner,
        created_at=api_key.created_at,
        is_active=api_key.is_active,
        scopes=api_key.scopes,
    )

    return key, response


async def revoke_api_key(key_hash: str) -> bool:
    """
    Revoke an API key by setting is_active=False.

    Args:
        key_hash: SHA256 hash of the key to revoke

    Returns:
        True if revoked, False if not found
    """
    try:
        from mastermind_cli.state.database import get_db

        db = get_db()
        return await db.revoke_api_key(key_hash)
    except Exception:
        return False


async def list_api_keys(owner: str | None = None) -> list[APIKeyResponse]:
    """
    List all API keys, optionally filtered by owner.

    Args:
        owner: Optional owner filter

    Returns:
        List of API key responses (without actual keys)
    """
    try:
        from mastermind_cli.state.database import get_db

        db = get_db()
        keys_data = await db.list_api_keys(owner=owner)

        return [
            APIKeyResponse(
                key_prefix=data["key"][:8] if "key" in data else data["key_hash"][:8],
                key_hash=data["key_hash"],
                owner=data["owner"],
                created_at=data["created_at"],
                is_active=data["is_active"],
                scopes=data["scopes"],
            )
            for data in keys_data
        ]
    except Exception:
        return []


# ===== FASTAPI INTEGRATION =====

try:
    from fastapi import Header, HTTPException, status

    async def get_current_api_key(
        x_api_key: str = Header(..., alias="X-API-Key", description="API key for authentication"),
    ) -> APIKey:
        """
        FastAPI dependency for API key validation.

        Usage:
            @app.get("/protected")
            async def protected_endpoint(api_key: APIKey = Depends(get_current_api_key)):
                return {"message": f"Hello {api_key.owner}"}

        Raises:
            HTTPException: 401 if key is invalid
        """
        validated = validate_api_key(x_api_key)

        if not validated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        if not validated.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API key has been revoked",
            )

        return validated

    # Export for FastAPI use
    __all__ = ["APIKey", "APIKeyCreate", "APIKeyResponse", "validate_api_key", "get_current_api_key"]

except ImportError:
    # FastAPI not installed - skip dependency
    __all__ = ["APIKey", "APIKeyCreate", "APIKeyResponse", "validate_api_key"]
