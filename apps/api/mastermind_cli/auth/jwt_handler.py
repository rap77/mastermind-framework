"""
JWT Authentication Handler with Tenant Isolation.

This module provides JWT token generation and validation with multi-tenant support.
Critical security feature: JWT includes tenant memberships to prevent header spoofing.

Brain #5 Requirement: X-Tenant-ID header is spoofable without JWT claim binding.
Solution: JWT must include `tenants: []` array with user's tenant memberships.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from typing import Final

from jose import JWTError, jwt
from pydantic import BaseModel, Field
from fastapi import Depends, Header, HTTPException, status

# ===== CONSTANTS =====

_ALGORITHM: Final = "HS256"
_ACCESS_TOKEN_EXPIRE_MINUTES: Final = 30
_REFRESH_TOKEN_EXPIRE_DAYS: Final = 7

# Get JWT secret from environment (must be set in production)
_JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")

if _JWT_SECRET == "dev-secret-change-in-production":
    import warnings

    warnings.warn(
        "Using default JWT secret. Set JWT_SECRET environment variable in production!",
        stacklevel=1,
    )


# ===== MODELS =====


class JWTTokenData(BaseModel):
    """JWT payload data."""

    sub: str = Field(..., description="User ID or email")
    tenants: list[str] = Field(..., description="List of tenant IDs user can access")
    exp: datetime | None = Field(default=None, description="Expiration time")
    iat: datetime | None = Field(default=None, description="Issued at time")


class TokenResponse(BaseModel):
    """Token response from login endpoint."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int  # Seconds until expiration


class TenantValidationResult(BaseModel):
    """Result of tenant validation."""

    is_valid: bool
    tenant_id: str | None = None
    user_id: str | None = None
    error: str | None = None


# ===== JWT OPERATIONS =====


def create_access_token(
    subject: str,
    tenants: list[str],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token with tenant membership.

    Args:
        subject: User ID or email (sub claim)
        tenants: List of tenant IDs user can access
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token

    Example:
        ```python
        token = create_access_token(
            subject="user@example.com",
            tenants=["tenant-1", "tenant-2"],
            expires_delta=timedelta(minutes=30)
        )
        ```
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "sub": subject,
        "tenants": tenants,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(to_encode, _JWT_SECRET, algorithm=_ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """
    Create a JWT refresh token (long-lived).

    Args:
        subject: User ID or email

    Returns:
        Encoded JWT refresh token
    """
    expire = datetime.now(timezone.utc) + timedelta(days=_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(to_encode, _JWT_SECRET, algorithm=_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> JWTTokenData | None:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token to decode

    Returns:
        JWTTokenData if valid, None if invalid

    Raises:
        JWTError: If token is malformed or signature invalid
    """
    try:
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_ALGORITHM])

        sub = payload.get("sub")
        if not sub:
            return None

        return JWTTokenData(
            sub=sub,
            tenants=payload.get("tenants", []),
            exp=datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc),
            iat=datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.utc),
        )
    except JWTError:
        return None


def verify_tenant_access(
    token_data: JWTTokenData,
    tenant_id: str,
) -> TenantValidationResult:
    """
    Verify that the user has access to the requested tenant.

    Critical security check: Prevents X-Tenant-ID header spoofing.

    Args:
        token_data: Decoded JWT token data
        tenant_id: Tenant ID from X-Tenant-ID header

    Returns:
        TenantValidationResult with validation status

    Example:
        ```python
        token_data = decode_token(token)
        result = verify_tenant_access(token_data, "tenant-1")
        if not result.is_valid:
            raise HTTPException(403, result.error)
        ```
    """
    if not token_data.tenants:
        return TenantValidationResult(
            is_valid=False, error="Token does not contain tenant membership"
        )

    if tenant_id not in token_data.tenants:
        return TenantValidationResult(
            is_valid=False,
            error=f"Tenant access denied: User not a member of tenant '{tenant_id}'",
        )

    return TenantValidationResult(
        is_valid=True,
        tenant_id=tenant_id,
        user_id=token_data.sub,
    )


# ===== FASTAPI DEPENDENCIES =====


async def get_current_user(
    authorization: str = Header(..., description="Bearer token"),
) -> JWTTokenData:
    """
    FastAPI dependency to extract and validate JWT token from Authorization header.

    Usage:
        ```python
        @app.get("/protected")
        async def protected_endpoint(user: JWTTokenData = Depends(get_current_user)):
            return {"message": f"Hello {user.sub}"}
        ```

    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication header format. Expected: 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]
    token_data = decode_token(token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


async def validate_tenant_access(
    x_tenant_id: str = Header(..., description="Tenant ID for multi-tenancy"),
    current_user: JWTTokenData = Depends(get_current_user),
) -> TenantValidationResult:
    """
    FastAPI dependency to validate tenant access (CRITICAL for security).

    Brain #5 Requirement: X-Tenant-ID header is spoofable without JWT claim binding.
    This dependency enforces that the requested tenant_id is in the user's JWT tenants array.

    Usage:
        ```python
        @app.get("/api/companies/{id}")
        async def get_company(
            id: str,
            tenant: TenantValidationResult = Depends(validate_tenant_access)
        ):
            # Tenant is validated, safe to use tenant.tenant_id
            return await get_company_data(tenant.tenant_id, id)
        ```

    Raises:
        HTTPException: 403 if tenant access is denied
    """
    result = verify_tenant_access(current_user, x_tenant_id)

    if not result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Tenant access denied",
                "code": "TENANT_FORBIDDEN",
                "message": result.error,
            },
        )

    return result


# ===== EXPORTS =====

__all__ = [
    "JWTTokenData",
    "TokenResponse",
    "TenantValidationResult",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_tenant_access",
    "get_current_user",
    "validate_tenant_access",
]
