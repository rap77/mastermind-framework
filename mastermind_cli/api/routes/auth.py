"""Authentication routes with JWT and refresh token rotation.

This module provides endpoints for:
- Login (returns access_token + refresh_token)
- Refresh (with token rotation - new refresh_token each time)
- API key management (create, list, revoke)

Requirements: UI-02, UI-03, UI-07
"""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from mastermind_cli.types.auth import (
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    APIKeyCreate,
    APIKeyResponse,
    verify_password,
    hash_token,
    generate_api_key,
)
from mastermind_cli.state.database import DatabaseConnection

# Router configuration
router = APIRouter()

# Security schemes
jwt_scheme = HTTPBearer()
api_key_scheme = HTTPBearer()

# JWT configuration
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Load from ENV_VAR
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY_MINUTES = 30
REFRESH_TOKEN_EXPIRY_HOURS = 24


def create_access_token(user_id: str) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token."""
    expire = datetime.utcnow() + timedelta(hours=REFRESH_TOKEN_EXPIRY_HOURS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(jwt_scheme),
) -> str:
    """Extract user_id from JWT access token."""
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user_from_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(api_key_scheme),
) -> str:
    """Extract user_id from API key."""
    token = credentials.credentials
    if not token.startswith("mm_"):
        raise HTTPException(status_code=401, detail="Invalid API key format")

    async with DatabaseConnection(":memory:") as db:
        cursor = await db.conn.execute(
            "SELECT user_id FROM api_keys WHERE key_hash = ?",
            [hash_token(token)],
        )
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return row[0]


async def get_current_user_any(
    credentials: HTTPAuthorizationCredentials = Depends(jwt_scheme),
) -> str:
    """Extract user_id from JWT or API key (flexible auth)."""
    token = credentials.credentials

    # Try JWT first
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "access":
            return payload.get("sub")
    except JWTError:
        pass

    # Try API key
    if token.startswith("mm_"):
        async with DatabaseConnection(":memory:") as db:
            cursor = await db.conn.execute(
                "SELECT user_id FROM api_keys WHERE key_hash = ?",
                [hash_token(token)],
            )
            row = await cursor.fetchone()
            if row:
                # Update last_used
                await db.conn.execute(
                    "UPDATE api_keys SET last_used = ? WHERE key_hash = ?",
                    [datetime.utcnow(), hash_token(token)],
                )
                await db.conn.commit()
                return row[0]

    raise HTTPException(status_code=401, detail="Invalid authentication")


# ===== Endpoints =====


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT tokens.

    Validates credentials, creates session with refresh_token_hash,
    and returns access_token (30min) + refresh_token (24h).
    """
    async with DatabaseConnection(":memory:") as db:
        # Look up user by username
        cursor = await db.conn.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            [request.username],
        )
        user = await cursor.fetchone()

        if user is None or not verify_password(request.password, user[1]):
            raise HTTPException(
                status_code=401, detail="Invalid username or password"
            )

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
                datetime.utcnow(),
                datetime.utcnow() + timedelta(hours=REFRESH_TOKEN_EXPIRY_HOURS),
            ],
        )
        await db.conn.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest):
    """Exchange refresh token for new tokens WITH ROTATION.

    CRITICAL: Old refresh_token is deleted from database (revoked).
    Each refresh issues a completely NEW refresh token.
    Replay attacks fail because old token hash no longer exists.
    """
    try:
        payload = jwt.decode(
            request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    async with DatabaseConnection(":memory:") as db:
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
                datetime.utcnow(),
                datetime.utcnow() + timedelta(hours=REFRESH_TOKEN_EXPIRY_HOURS),
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


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyCreate,
    user_id: str = Depends(get_current_user_any),
):
    """Create API key for CLI access (UI-07 requirement).

    Key is returned only ONCE (on creation).
    Key format: mm_ + 32 hex chars
    Key is hashed with bcrypt before storage.
    """
    api_key_id = str(uuid.uuid4())
    plaintext_key = generate_api_key()

    async with DatabaseConnection(":memory:") as db:
        await db.conn.execute(
            """INSERT INTO api_keys (id, user_id, key_hash, name, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            [api_key_id, user_id, hash_token(plaintext_key), request.name, datetime.utcnow()],
        )
        await db.conn.commit()

    return APIKeyResponse(
        id=api_key_id,
        name=request.name,
        key=plaintext_key,
        created_at=datetime.utcnow(),
    )


@router.get("/api-keys")
async def list_api_keys(
    user_id: str = Depends(get_current_user_any),
):
    """List user's API keys."""
    async with DatabaseConnection(":memory:") as db:
        cursor = await db.conn.execute(
            """SELECT id, name, created_at, last_used FROM api_keys
               WHERE user_id = ?
               ORDER BY created_at DESC""",
            [user_id],
        )
        rows = await cursor.fetchall()

    return {
        "api_keys": [
            {"id": row[0], "name": row[1], "created_at": row[2], "last_used": row[3]}
            for row in rows
        ]
    }


@router.delete("/api-keys/{api_key_id}")
async def revoke_api_key(
    api_key_id: str,
    user_id: str = Depends(get_current_user_any),
):
    """Revoke API key."""
    async with DatabaseConnection(":memory:") as db:
        await db.conn.execute(
            "DELETE FROM api_keys WHERE id = ? AND user_id = ?",
            [api_key_id, user_id],
        )
        await db.conn.commit()

    return {"message": "API key revoked"}


@router.post("/logout")
async def logout(
    user_id: str = Depends(get_current_user_any),
):
    """Revoke refresh token (logout)."""
    # Note: In production, accept refresh_token in request body to revoke specific session
    # For now, revoke all sessions for user
    async with DatabaseConnection(":memory:") as db:
        await db.conn.execute("DELETE FROM sessions WHERE user_id = ?", [user_id])
        await db.conn.commit()

    return {"message": "Logged out"}
