"""API key management REST endpoints.

Provides show-once API key creation with mmsk_ prefix, masked listing,
and immediate soft-delete revocation via revoked_at field.

Endpoints:
    GET    /api/keys          - List active keys (masked: prefix + suffix)
    POST   /api/keys          - Create key (shows full key ONCE in response)
    DELETE /api/keys/{id}     - Revoke key (soft-delete via revoked_at)

Show-once pattern: The full key is only returned on creation. It is
never stored plaintext or re-returned. Users must save it immediately.

Key format: mmsk_ + 32 hex = 37 chars total
  - prefix (13 chars): "mmsk_" + 8 hex chars, used for O(1) DB lookup
  - suffix (4 chars): last 4 chars, for display identification

Security:
  - bcrypt hash stored (not SHA256) for strong resistance to DB leaks
  - slowapi rate limiting: 60/minute on key validation route (Brain #7 gap B)
  - Immediate revocation: revoked_at field checked before bcrypt

Requirements: ER-02
"""

import secrets
import uuid
from datetime import datetime
from typing import Optional

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from mastermind_cli.api.dependencies import get_db_path
from mastermind_cli.api.routes.auth import get_current_user_any
from mastermind_cli.state.database import DatabaseConnection

router = APIRouter()

# Rate limiter for key validation (Brain #7 gap B)
_limiter = Limiter(key_func=get_remote_address)

_KEY_PREFIX = "mmsk_"
_KEY_HEX_LENGTH = 32  # 32 hex chars = 128-bit key
_BCRYPT_ROUNDS = 12  # Standard production rounds


def _generate_key() -> str:
    """Generate a new API key with mmsk_ prefix.

    Format: mmsk_ + 32 hex chars (37 chars total)
    """
    return _KEY_PREFIX + secrets.token_hex(_KEY_HEX_LENGTH // 2)


def _hash_key(key: str) -> str:
    """bcrypt-hash a plaintext API key for storage."""
    return bcrypt.hashpw(key.encode(), bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)).decode()


def _verify_key(key: str, key_hash: str) -> bool:
    """Verify a plaintext key against its bcrypt hash."""
    try:
        return bcrypt.checkpw(key.encode(), key_hash.encode())
    except Exception:
        return False


# ===== Request/Response models =====


class CreateKeyRequest(BaseModel):
    """Request to create a new API key."""

    name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional label for the key (e.g., 'Claude API key')",
    )


class APIKeyMasked(BaseModel):
    """Masked API key for list responses.

    Full key is never re-exposed after creation.
    """

    id: str = Field(..., description="Key UUID")
    prefix: str = Field(..., description="First 13 chars (mmsk_ + 8 hex)")
    suffix: str = Field(..., description="Last 4 chars")
    name: Optional[str] = Field(None, description="User-defined label")
    created_at: str = Field(..., description="ISO timestamp")
    last_used_at: Optional[str] = Field(None, description="ISO timestamp of last use")


class CreateKeyResponse(BaseModel):
    """Response after creating a new API key.

    IMPORTANT: full_key is shown ONCE. After this response, it is
    irrecoverable. The user must save it immediately.
    """

    id: str = Field(..., description="Key UUID")
    full_key: str = Field(..., description="Full key — save immediately, shown ONCE")
    prefix: str = Field(..., description="First 13 chars for display")
    suffix: str = Field(..., description="Last 4 chars for display")
    message: str = Field(
        default="Save this key, you won't see it again",
        description="Warning message",
    )


class RevokeKeyResponse(BaseModel):
    """Response after revoking a key."""

    status: str = Field(default="revoked")
    id: str = Field(..., description="Revoked key UUID")


class APIKeyListResponse(BaseModel):
    """Response for key listing."""

    keys: list[APIKeyMasked] = Field(default_factory=list)


# ===== Endpoints =====


@router.get("", response_model=APIKeyListResponse)
async def list_keys(
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> APIKeyListResponse:
    """List active (non-revoked) API keys for the current user.

    Returns masked keys only (prefix + suffix + metadata).
    The full key is never returned after creation.

    Returns:
        APIKeyListResponse with list of APIKeyMasked
    """
    async with DatabaseConnection(db_path) as db:
        await db.create_api_keys_v2_schema()

        cursor = await db.conn.execute(
            """SELECT id, prefix, suffix, name, created_at, last_used_at
               FROM api_keys_v2
               WHERE user_id = ? AND revoked_at IS NULL
               ORDER BY created_at DESC""",
            [user_id],
        )
        rows = await cursor.fetchall()

    keys = [
        APIKeyMasked(
            id=row[0],
            prefix=row[1],
            suffix=row[2],
            name=row[3],
            created_at=str(row[4]),
            last_used_at=str(row[5]) if row[5] else None,
        )
        for row in rows
    ]

    return APIKeyListResponse(keys=keys)


@router.post("", response_model=CreateKeyResponse, status_code=201)
async def create_key(
    request_body: CreateKeyRequest,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> CreateKeyResponse:
    """Create a new API key.

    The full key is returned ONCE in this response only.
    It is never logged or re-returned. Save immediately.

    Key format: mmsk_ + 32 hex chars (37 chars total)
    prefix = first 13 chars (for display + DB lookup)
    suffix = last 4 chars (for display identification)

    Returns:
        CreateKeyResponse with full_key (one-time reveal)

    Raises:
        401: If JWT missing/invalid
    """
    full_key = _generate_key()
    key_hash = _hash_key(full_key)
    key_id = str(uuid.uuid4())
    prefix = full_key[:13]  # "mmsk_" + 8 hex
    suffix = full_key[-4:]  # last 4 hex

    async with DatabaseConnection(db_path) as db:
        await db.create_api_keys_v2_schema()

        await db.conn.execute(
            """INSERT INTO api_keys_v2
               (id, user_id, key_hash, prefix, suffix, name, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                key_id,
                user_id,
                key_hash,
                prefix,
                suffix,
                request_body.name,
                datetime.utcnow().isoformat(),
            ],
        )
        await db.conn.commit()

    return CreateKeyResponse(
        id=key_id,
        full_key=full_key,
        prefix=prefix,
        suffix=suffix,
        message="Save this key, you won't see it again",
    )


@router.delete("/{key_id}", response_model=RevokeKeyResponse)
async def revoke_key(
    key_id: str,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> RevokeKeyResponse:
    """Revoke (soft-delete) an API key immediately.

    Sets revoked_at timestamp. Key is immediately invalid for authentication.
    No grace period. No Redis cache to invalidate.

    Returns:
        RevokeKeyResponse with status="revoked"

    Raises:
        404: Key not found
        403: Key belongs to another user
        401: JWT missing/invalid
    """
    async with DatabaseConnection(db_path) as db:
        await db.create_api_keys_v2_schema()

        # Check key exists and belongs to user
        cursor = await db.conn.execute(
            "SELECT id, user_id FROM api_keys_v2 WHERE id = ? AND revoked_at IS NULL",
            [key_id],
        )
        row = await cursor.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="API key not found")

        if row[1] != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this API key")

        # Soft-delete: set revoked_at
        await db.conn.execute(
            "UPDATE api_keys_v2 SET revoked_at = ? WHERE id = ?",
            [datetime.utcnow().isoformat(), key_id],
        )
        await db.conn.commit()

    return RevokeKeyResponse(status="revoked", id=key_id)


async def validate_api_key_v2(
    raw_key: str,
    db_path: str,
) -> str | None:
    """Validate an API key and return the user_id if valid.

    Uses prefix-based lookup (O(1)) + bcrypt verification.
    Updates last_used_at as a side effect (non-blocking).

    Args:
        raw_key: The plaintext API key (mmsk_ prefixed)
        db_path: SQLite database path

    Returns:
        user_id if valid, None if invalid/revoked
    """
    if not raw_key.startswith(_KEY_PREFIX) or len(raw_key) < 13:
        return None

    prefix = raw_key[:13]

    async with DatabaseConnection(db_path) as db:
        await db.create_api_keys_v2_schema()

        # O(1) candidate lookup by prefix
        cursor = await db.conn.execute(
            """SELECT id, user_id, key_hash
               FROM api_keys_v2
               WHERE prefix = ? AND revoked_at IS NULL""",
            [prefix],
        )
        candidate = await cursor.fetchone()

        if candidate is None:
            return None

        key_id, owner_id, key_hash = candidate[0], candidate[1], candidate[2]

        # bcrypt verification (CPU-bound, ~100ms)
        if not _verify_key(raw_key, str(key_hash)):
            return None

        # Update last_used_at (non-critical, ignore failure)
        try:
            await db.conn.execute(
                "UPDATE api_keys_v2 SET last_used_at = ? WHERE id = ?",
                [datetime.utcnow().isoformat(), key_id],
            )
            await db.conn.commit()
        except Exception:
            pass

        return str(owner_id)
