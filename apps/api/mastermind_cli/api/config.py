"""Configuration for MasterMind API.

Uses environment variables for sensitive configuration.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    postgres_dsn: str = "postgresql://postgres@localhost:5433/mastermind_bd"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1

    # Costs
    cost_metrics_enabled: bool = True

    # Legacy/new shared auth secret
    jwt_secret: SecretStr = Field(
        default=SecretStr("dev-secret"),
        validation_alias=AliasChoices("MM_SECRET_KEY", "JWT_SECRET"),
    )

    # SMTP
    smtp_host: str | None = None
    smtp_port: int = 25
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None

    # WhatsApp
    whatsapp_phone_number_id: str | None = None
    whatsapp_access_token: SecretStr | None = None

    # Instagram
    instagram_business_account_id: str | None = None
    instagram_access_token: SecretStr | None = None


def load_settings() -> Settings:
    """Return a fresh settings instance from the current environment."""
    return Settings()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return load_settings()
