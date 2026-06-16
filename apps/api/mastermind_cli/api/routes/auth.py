"""Authentication routes with JWT and refresh token rotation.

This module provides endpoints for:
- Login (returns access_token + refresh_token)
- Refresh (with token rotation - new refresh_token each time)
- API key management (create, list, revoke)

Requirements: UI-02, UI-03, UI-07
"""

import os
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from mastermind_cli.api.dependencies import get_db_path
from mastermind_cli.types.auth import (
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    verify_password,
    hash_token,
)
from mastermind_cli.state.database import DatabaseConnection

# Router configuration
router = APIRouter()

# Security schemes
jwt_scheme = HTTPBearer()
api_key_scheme = HTTPBearer()


async def get_auth_db(
    db_path: str = Depends(get_db_path),
) -> AsyncIterator[DatabaseConnection]:
    """Yield an auth database connection for route handlers."""
    async with DatabaseConnection(db_path) as db:
        yield db


def _int_env(name: str, default: int) -> int:
    """Read an integer environment variable with fallback."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError:
        return default


def _jwt_secret() -> str:
    """Return the configured JWT secret."""
    secret = os.getenv("MM_SECRET_KEY") or os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("MM_SECRET_KEY or JWT_SECRET must be set")
    return str(secret)


def _jwt_algorithm() -> str:
    """Return the configured JWT algorithm."""
    return str(os.getenv("MM_JWT_ALGORITHM", "HS256"))


def create_access_token(user_id: str) -> str:
    """Create JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=_int_env("MM_ACCESS_TOKEN_EXPIRY_MINUTES", 30)
    )
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "access",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=_jwt_algorithm())


def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(
        hours=_int_env("MM_REFRESH_TOKEN_EXPIRY_HOURS", 24)
    )
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=_jwt_algorithm())


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(jwt_scheme),
) -> str:
    """Extract user_id from JWT access token."""
    try:
        payload = jwt.decode(
            credentials.credentials, _jwt_secret(), algorithms=[_jwt_algorithm()]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        request.state.user_id = user_id
        return str(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user_from_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(api_key_scheme),
    db_path: str = Depends(get_db_path),
) -> str:
    """Extract user_id from API key."""
    token = credentials.credentials
    if not token.startswith("mmsk_"):
        raise HTTPException(status_code=401, detail="Invalid API key format")

    from mastermind_cli.api.routes.keys import validate_api_key_v2

    user_id = await validate_api_key_v2(token, db_path)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    request.state.user_id = user_id
    return user_id


async def get_current_user_any(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(jwt_scheme),
    db_path: str = Depends(get_db_path),
) -> str:
    """Extract user_id from JWT or API key (flexible auth)."""
    token = credentials.credentials

    # Try JWT first
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[_jwt_algorithm()])
        if payload.get("type") == "access":
            user_id = str(payload.get("sub"))
            request.state.user_id = user_id
            return user_id
    except JWTError:
        pass

    # Try new bcrypt API key (mmsk_ prefix — api_keys_v2 table)
    if token.startswith("mmsk_"):
        from mastermind_cli.api.routes.keys import validate_api_key_v2

        mmsk_user_id = await validate_api_key_v2(token, db_path)
        if mmsk_user_id is not None:
            request.state.user_id = mmsk_user_id
            return mmsk_user_id

    raise HTTPException(status_code=401, detail="Invalid authentication")


# ===== Endpoints =====


@router.post("/login")
async def login(
    request: LoginRequest,
    db: DatabaseConnection = Depends(get_auth_db),
) -> JSONResponse:
    """Authenticate user and return JWT tokens.

    Validates credentials, creates session with refresh_token_hash,
    and returns access_token (30min) + refresh_token (24h).

    Cookies: Sets httpOnly cookies for access_token and refresh_token.
    """
    # Look up user by username
    cursor = await db.conn.execute(
        "SELECT id, password_hash FROM users WHERE username = ?",
        [request.username],
    )
    user = await cursor.fetchone()

    if user is None or not verify_password(request.password, user[1]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_id = user[0]

    # Generate tokens
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    # Create session with refresh_token_hash (for rotation)
    session_id = str(uuid.uuid4())
    await db.conn.execute(
        """INSERT INTO sessions (id, user_id, refresh_token_hash, created_at, expires_at)
           VALUES (?, ?, ?, ?, ?)""",
        [
            session_id,
            user_id,
            hash_token(refresh_token),
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
            + timedelta(hours=_int_env("MM_REFRESH_TOKEN_EXPIRY_HOURS", 24)),
        ],
    )
    await db.conn.commit()

    # Create response with JSONResponse
    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )

    # Build Response and set cookies individually
    response = JSONResponse(content=token_response.model_dump())

    # Set httpOnly cookies (browser sends them automatically)
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=_int_env("MM_ACCESS_TOKEN_EXPIRY_MINUTES", 30) * 60,
    )

    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=_int_env("MM_REFRESH_TOKEN_EXPIRY_HOURS", 24) * 3600,
    )

    return response


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshRequest,
    db: DatabaseConnection = Depends(get_auth_db),
) -> TokenResponse:
    """Exchange refresh token for new tokens WITH ROTATION.

    CRITICAL: Old refresh_token is deleted from database (revoked).
    Each refresh issues a completely NEW refresh token.
    Replay attacks fail because old token hash no longer exists.
    """
    try:
        payload = jwt.decode(
            request.refresh_token, _jwt_secret(), algorithms=[_jwt_algorithm()]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Look up session by refresh_token_hash
    cursor = await db.conn.execute(
        "SELECT id, rotation_count FROM sessions WHERE user_id = ? AND refresh_token_hash = ?",
        [user_id, hash_token(request.refresh_token)],
    )
    session = await cursor.fetchone()

    if session is None:
        raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")

    session_id, rotation_count = session

    # ROTATION: Delete old session (revoke old refresh_token)
    await db.conn.execute("DELETE FROM sessions WHERE id = ?", [session_id])

    # Generate NEW refresh token (invalidate old one)
    new_refresh_token = create_refresh_token(user_id)
    new_session_id = str(uuid.uuid4())

    # Create new session
    await db.conn.execute(
        """INSERT INTO sessions (id, user_id, refresh_token_hash, created_at, expires_at, rotation_count)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [
            new_session_id,
            user_id,
            hash_token(new_refresh_token),
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
            + timedelta(hours=_int_env("MM_REFRESH_TOKEN_EXPIRY_HOURS", 24)),
            rotation_count + 1,
        ],
    )
    await db.conn.commit()

    # Return new access token AND new refresh token
    new_access_token = create_access_token(user_id)
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


@router.post("/logout")
async def logout(
    user_id: str = Depends(get_current_user_any),
    db: DatabaseConnection = Depends(get_auth_db),
) -> dict[str, str]:
    """Revoke refresh token (logout)."""
    # Note: In production, accept refresh_token in request body to revoke specific session
    # For now, revoke all sessions for user
    await db.conn.execute("DELETE FROM sessions WHERE user_id = ?", [user_id])
    await db.conn.commit()

    return {"message": "Logged out"}


@router.get("/verify")
async def verify_token_endpoint(
    request: Request,
) -> dict[str, object]:
    """Verify JWT token from httpOnly cookie.

    Reads access_token from cookie and verifies it using python-jose.
    Returns validation result and user_id if valid.

    This avoids library incompatibility between python-jose (backend) and jose (frontend).
    Frontend should call this endpoint instead of verifying JWT locally.
    """
    # Read token from httpOnly cookie
    token = request.cookies.get("access_token")
    if not token:
        return {"valid": False, "user_id": None}

    # Verify token using same library that generated it (python-jose)
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[_jwt_algorithm()])
        user_id = payload.get("sub")
        if user_id is None:
            return {"valid": False, "user_id": None}
        return {"valid": True, "user_id": user_id}
    except JWTError:
        return {"valid": False, "user_id": None}
