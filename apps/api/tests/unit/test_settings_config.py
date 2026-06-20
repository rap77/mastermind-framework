"""Tests for centralized runtime settings."""

from __future__ import annotations

import pytest

from mastermind_cli.api.config import load_settings


def test_settings_accepts_jwt_secret_legacy_alias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """JWT secret should load from the legacy JWT_SECRET env var."""
    monkeypatch.delenv("MM_SECRET_KEY", raising=False)
    monkeypatch.setenv("JWT_SECRET", "legacy-secret")

    settings = load_settings()

    assert settings.jwt_secret.get_secret_value() == "legacy-secret"


def test_settings_accepts_mm_secret_key_alias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """JWT secret should also load from the newer MM_SECRET_KEY env var."""
    monkeypatch.setenv("MM_SECRET_KEY", "primary-secret")
    monkeypatch.setenv("JWT_SECRET", "legacy-secret")

    settings = load_settings()

    assert settings.jwt_secret.get_secret_value() == "primary-secret"


def test_settings_loads_channel_and_smtp_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SMTP and channel credentials should be parsed through BaseSettings."""
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USERNAME", "bot@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "smtp-secret")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "12345")
    monkeypatch.setenv("WHATSAPP_ACCESS_TOKEN", "wa-secret")
    monkeypatch.setenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "ig-biz-1")
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "ig-secret")

    settings = load_settings()

    assert settings.smtp_host == "smtp.example.com"
    assert settings.smtp_port == 587
    assert settings.smtp_password is not None
    assert settings.smtp_password.get_secret_value() == "smtp-secret"
    assert settings.whatsapp_phone_number_id == "12345"
    assert settings.whatsapp_access_token is not None
    assert settings.whatsapp_access_token.get_secret_value() == "wa-secret"
    assert settings.instagram_business_account_id == "ig-biz-1"
    assert settings.instagram_access_token is not None
    assert settings.instagram_access_token.get_secret_value() == "ig-secret"
