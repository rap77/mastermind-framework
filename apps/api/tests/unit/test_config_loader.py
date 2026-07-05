"""Tests for mm_flow/config_loader.py — FASE 1 Task 1.5 + C2.01/C2.02 provider config."""

from pathlib import Path
import textwrap

import pytest

from mastermind_cli.mm_flow.config_loader import (
    ConfigError,
    HarnessLibraryConfig,
    MMFlowConfig,
    ModelProfile,
    ProviderConfig,
    load_config,
)


def test_missing_file_uses_defaults(tmp_path: Path) -> None:
    """A missing config file should fall back to defaults without raising."""
    config = load_config(str(tmp_path / "nonexistent.yml"))
    assert "quality" in config.model_profiles
    assert "balanced" in config.model_profiles
    assert "budget" in config.model_profiles


def test_malformed_yaml_raises_config_error(tmp_path: Path) -> None:
    """Malformed YAML should surface as a ConfigError with a parse message."""
    bad_yaml = tmp_path / "bad.yml"
    bad_yaml.write_text("key: [unclosed bracket")
    with pytest.raises(ConfigError, match="malformado"):
        load_config(str(bad_yaml))


def test_unknown_model_key_raises_config_error(tmp_path: Path) -> None:
    """Unknown model profile keys should raise a ConfigError naming the bad key."""
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


def test_partial_config_deep_merges_without_dropping_defaults(tmp_path: Path) -> None:
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


def test_empty_file_uses_defaults(tmp_path: Path) -> None:
    """An empty config file should be parsed as the default configuration."""
    empty = tmp_path / "empty.yml"
    empty.write_text("")
    config = load_config(str(empty))
    assert isinstance(config, MMFlowConfig)
    assert "quality" in config.model_profiles


def test_defaults_disable_multi_harness_library(tmp_path: Path) -> None:
    """Multi-harness library should be opt-in until project config enables it."""
    config = load_config(str(tmp_path / "nonexistent.yml"))

    assert isinstance(config.harness_library, HarnessLibraryConfig)
    assert config.harness_library.enabled is False
    assert config.harness_library.path == ".mm-flow/harness-library"
    assert config.harness_library.bundle_output_path == ".run-bundles"


def test_harness_library_config_from_file(tmp_path: Path) -> None:
    """Config file should enable and relocate the multi-harness library."""
    cfg_file = tmp_path / "harness_library.yml"
    cfg_file.write_text(
        textwrap.dedent("""
        harness_library:
          enabled: true
          path: custom/harness-library
          bundle_output_path: custom/run-bundles
    """)
    )

    config = load_config(str(cfg_file))

    assert config.harness_library.enabled is True
    assert config.harness_library.path == "custom/harness-library"
    assert config.harness_library.bundle_output_path == "custom/run-bundles"


# ---------------------------------------------------------------------------
# C2.01 — provider:model_id format tests
# ---------------------------------------------------------------------------


def test_defaults_use_provider_qualified_model_ids(tmp_path: Path) -> None:
    """C2.01: default model_profiles use provider:model_id format."""
    config = load_config(str(tmp_path / "nonexistent.yml"))
    assert config.model_profiles["quality"].model == "anthropic:claude-opus-4-6"
    assert config.model_profiles["balanced"].model == "anthropic:claude-sonnet-4-6"
    assert config.model_profiles["budget"].model == "z_ai:claude-3-7-sonnet"


def test_model_profile_provider_property() -> None:
    """C2.01: ModelProfile.provider parses provider from model string."""
    p = ModelProfile(model="anthropic:claude-opus-4-6", use_when="test")
    assert p.provider == "anthropic"

    p2 = ModelProfile(model="openrouter:anthropic/claude-opus-4", use_when="test")
    assert p2.provider == "openrouter"

    p3 = ModelProfile(model="z_ai:claude-3-7-sonnet", use_when="test")
    assert p3.provider == "z_ai"


def test_model_profile_model_id_property() -> None:
    """C2.01: ModelProfile.model_id strips the provider prefix."""
    p = ModelProfile(model="anthropic:claude-opus-4-6", use_when="test")
    assert p.model_id == "claude-opus-4-6"

    p2 = ModelProfile(model="openrouter:anthropic/claude-opus-4", use_when="test")
    assert p2.model_id == "anthropic/claude-opus-4"


def test_invalid_provider_raises_config_error(tmp_path: Path) -> None:
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


def test_openrouter_provider_accepted(tmp_path: Path) -> None:
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


# ---------------------------------------------------------------------------
# C2.02 — providers section tests
# ---------------------------------------------------------------------------


def test_defaults_include_providers_section(tmp_path: Path) -> None:
    """C2.02: default config includes three providers with env_key and base_url."""
    config = load_config(str(tmp_path / "nonexistent.yml"))
    assert "anthropic" in config.providers
    assert "openrouter" in config.providers
    assert "z_ai" in config.providers


def test_anthropic_provider_config(tmp_path: Path) -> None:
    """C2.02: anthropic provider has ANTHROPIC_API_KEY env_key and no base_url."""
    config = load_config(str(tmp_path / "nonexistent.yml"))
    p = config.providers["anthropic"]
    assert p.env_key == "ANTHROPIC_API_KEY"
    assert p.base_url is None


def test_openrouter_provider_config(tmp_path: Path) -> None:
    """C2.02: openrouter provider has OPENROUTER_API_KEY and correct base_url."""
    config = load_config(str(tmp_path / "nonexistent.yml"))
    p = config.providers["openrouter"]
    assert p.env_key == "OPENROUTER_API_KEY"
    assert p.base_url == "https://openrouter.ai/api/v1"


def test_z_ai_provider_config(tmp_path: Path) -> None:
    """C2.02: z_ai provider has ZAI_API_KEY and correct base_url."""
    config = load_config(str(tmp_path / "nonexistent.yml"))
    p = config.providers["z_ai"]
    assert p.env_key == "ZAI_API_KEY"
    assert p.base_url == "https://api.z.ai/v1"


def test_provider_config_dataclass() -> None:
    """C2.02: ProviderConfig is a plain dataclass with env_key and base_url."""
    p = ProviderConfig(env_key="MY_KEY", base_url="https://example.com")
    assert p.env_key == "MY_KEY"
    assert p.base_url == "https://example.com"

    p_none = ProviderConfig(env_key="MY_KEY", base_url=None)
    assert p_none.base_url is None


def test_providers_section_from_file(tmp_path: Path) -> None:
    """C2.02: providers section is parsed from config file."""
    cfg_file = tmp_path / "custom_providers.yml"
    cfg_file.write_text(
        textwrap.dedent("""
        providers:
          custom_prov:
            env_key: CUSTOM_API_KEY
            base_url: "https://custom.example.com/v2"
    """)
    )
    config = load_config(str(cfg_file))
    assert "custom_prov" in config.providers
    assert config.providers["custom_prov"].env_key == "CUSTOM_API_KEY"
    assert config.providers["custom_prov"].base_url == "https://custom.example.com/v2"
