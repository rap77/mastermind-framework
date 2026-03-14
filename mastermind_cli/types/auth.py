"""Authentication types for FastAPI JWT and API key authentication.

This module defines Pydantic models for user authentication, session management,
and API key handling.

Requirements: UI-02, UI-03, UI-07
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import bcrypt


class User(BaseModel):
    """User account information."""
    id: str
    username: str
    password_hash: str
    created_at: datetime


class LoginRequest(BaseModel):
    """Login request payload."""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)


class TokenResponse(BaseModel):
    """JWT token response with refresh token (rotation)."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(default=1800, description="Access token expiry in seconds (30 min)")


class RefreshRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class Session(BaseModel):
    """User session for refresh token management."""
    id: str
    user_id: str
    refresh_token_hash: str
    created_at: datetime
    expires_at: datetime
    rotation_count: int = 0


class APIKey(BaseModel):
    """API key for CLI access (UI-07 requirement)."""
    id: str
    user_id: str
    key_hash: str
    name: str
    created_at: datetime
    last_used: Optional[datetime] = None


class APIKeyCreate(BaseModel):
    """API key creation request."""
    name: str = Field(..., min_length=1, max_length=100)


class APIKeyResponse(BaseModel):
    """API key creation response (key shown only once)."""
    id: str
    name: str
    key: str = Field(..., description="Plaintext API key (mm_ + 32 hex chars)")
    created_at: datetime


class AuditLog(BaseModel):
    """Audit log entry for all mutations (UI-07 requirement)."""
    id: str
    user_id: str
    endpoint: str
    method: str
    request_hash: str = Field(..., description="SHA256 prefix of request body")
    response_status: int
    timestamp: datetime


def hash_password(password: str) -> str:
    """Hash password with bcrypt (salt=12 rounds)."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def hash_token(token: str) -> str:
    """Hash API key or refresh token for storage (bcrypt)."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(token.encode('utf-8'), salt).decode('utf-8')


def generate_api_key() -> str:
    """Generate secure API key with format: mm_ + 32 hex chars."""
    import secrets
    random_bytes = secrets.token_bytes(16)
    hex_part = random_bytes.hex()
    return f"mm_{hex_part}"
