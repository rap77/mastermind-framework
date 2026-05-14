"""Tests for mm_flow/config_loader.py — FASE 1 Task 1.5 + C2.01 provider format."""

import textwrap

import pytest

from mastermind_cli.mm_flow.config_loader import (
    ConfigError,
    MMFlowConfig,
    ModelProfile,
    load_config,
)


def test_missing_file_uses_defaults(tmp_path):
    config = load_config(str(tmp_path / "nonexistent.yml"))
    assert "quality" in config.model_profiles
    assert "balanced" in config.model_profiles
    assert "budget" in config.model_profiles


def test_malformed_yaml_raises_config_error(tmp_path):
    bad_yaml = tmp_path / "bad.yml"
    bad_yaml.write_text("key: [unclosed bracket")
    with pytest.raises(ConfigError, match="malformado"):
        load_config(str(bad_yaml))


def test_unknown_model_key_raises_config_error(tmp_path):
    bad_config = tmp_path / "unknown_key.yml"
    bad_config.write_text(
        textwrap.dedent("""
        model_profiles:
          premium:
            model: some-model
            use_when: testing
    """)
    )
    with pytest.raises(ConfigError, match="clave desconocida"):
        load_config(str(bad_config))


def test_partial_config_deep_merges_without_dropping_defaults(tmp_path):
    """Brain #7 Condition A: partial override must not drop other profile keys."""
    partial = tmp_path / "partial.yml"
    partial.write_text(
        textwrap.dedent("""
        model_profiles:
          quality:
            model: claude-opus-4-6-custom
    """)
    )
    config = load_config(str(partial))
    # quality was overridden
    assert config.model_profiles["quality"].model == "claude-opus-4-6-custom"
    # balanced and budget must still be present (deep merge, not shallow)
    assert "balanced" in config.model_profiles
    assert "budget" in config.model_profiles


def test_empty_file_uses_defaults(tmp_path):
    empty = tmp_path / "empty.yml"
    empty.write_text("")
    config = load_config(str(empty))
    assert isinstance(config, MMFlowConfig)
    assert "quality" in config.model_profiles


# ---------------------------------------------------------------------------
# C2.01 — provider:model_id format tests
# ---------------------------------------------------------------------------


def test_defaults_use_provider_qualified_model_ids(tmp_path):
    """C2.01: default model_profiles use provider:model_id format."""
    config = load_config(str(tmp_path / "nonexistent.yml"))
    assert config.model_profiles["quality"].model == "anthropic:claude-opus-4-6"
    assert config.model_profiles["balanced"].model == "anthropic:claude-sonnet-4-6"
    assert config.model_profiles["budget"].model == "z_ai:claude-3-7-sonnet"


def test_model_profile_provider_property():
    """C2.01: ModelProfile.provider parses provider from model string."""
    p = ModelProfile(model="anthropic:claude-opus-4-6", use_when="test")
    assert p.provider == "anthropic"

    p2 = ModelProfile(model="openrouter:anthropic/claude-opus-4", use_when="test")
    assert p2.provider == "openrouter"

    p3 = ModelProfile(model="z_ai:claude-3-7-sonnet", use_when="test")
    assert p3.provider == "z_ai"


def test_model_profile_model_id_property():
    """C2.01: ModelProfile.model_id strips the provider prefix."""
    p = ModelProfile(model="anthropic:claude-opus-4-6", use_when="test")
    assert p.model_id == "claude-opus-4-6"

    p2 = ModelProfile(model="openrouter:anthropic/claude-opus-4", use_when="test")
    assert p2.model_id == "anthropic/claude-opus-4"


def test_invalid_provider_raises_config_error(tmp_path):
    """C2.01: unknown provider prefix raises ConfigError."""
    bad = tmp_path / "bad_provider.yml"
    bad.write_text(
        textwrap.dedent("""
        model_profiles:
          quality:
            model: "unknown_provider:some-model"
    """)
    )
    with pytest.raises(ConfigError, match="proveedor desconocido"):
        load_config(str(bad))


def test_openrouter_provider_accepted(tmp_path):
    """C2.01: openrouter is a valid provider."""
    cfg_file = tmp_path / "openrouter.yml"
    cfg_file.write_text(
        textwrap.dedent("""
        model_profiles:
          quality:
            model: "openrouter:anthropic/claude-opus-4"
    """)
    )
    config = load_config(str(cfg_file))
    assert config.model_profiles["quality"].provider == "openrouter"
    assert config.model_profiles["quality"].model_id == "anthropic/claude-opus-4"
