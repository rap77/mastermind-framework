"""
MasterMind Framework - Authentication Module.

This module provides API key and JWT authentication for both CLI and Web UI.
"""

from .api_keys import APIKey, validate_api_key, get_current_api_key
from .jwt_handler import (
    JWTTokenData,
    TokenResponse,
    TenantValidationResult,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_tenant_access,
    get_current_user,
    validate_tenant_access,
)

__all__ = [
    # API Key Auth
    "APIKey",
    "validate_api_key",
    "get_current_api_key",
    # JWT Auth
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
