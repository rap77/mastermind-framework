"""Tests for mm_flow/config_loader.py — FASE 1 Task 1.5."""

import textwrap

import pytest

from mastermind_cli.mm_flow.config_loader import ConfigError, MMFlowConfig, load_config


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
