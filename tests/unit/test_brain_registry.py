"""
Unit tests for brain_registry.py
"""

import pytest
import yaml
from pathlib import Path
from mastermind_cli.brain_registry import (
    load_brain_configs,
    get_brain,
    list_active_brains,
    get_brain_count
)


def test_load_brain_configs():
    """Test that brain configs load from YAML."""
    configs = load_brain_configs()

    # Should have brains 1-8
    assert len(configs) >= 8
    assert 1 in configs
    assert 8 in configs


def test_get_brain():
    """Test getting a specific brain config."""
    brain_1 = get_brain(1)

    assert brain_1 is not None
    assert brain_1["name"] == "Product Strategy"
    assert brain_1["status"] == "active"


def test_get_brain_not_found():
    """Test getting non-existent brain returns None."""
    brain_999 = get_brain(999)

    assert brain_999 is None


def test_list_active_brains():
    """Test listing only active brains."""
    active = list_active_brains()

    # Brain #8 is active as of PRP-015
    assert 1 in active
    assert 8 in active  # Active since PRP-015


def test_get_brain_count():
    """Test getting total brain count."""
    count = get_brain_count()

    assert count >= 8  # At least brains 1-8


def test_yaml_schema_valid():
    """Test that brains.yaml follows expected schema."""
    import mastermind_cli.brain_registry as registry

    with open(registry.BRAINS_CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    # Verify structure
    assert "version" in config
    assert "brains" in config
    assert isinstance(config["brains"], list)

    # Verify each brain has required fields
    for brain in config["brains"]:
        assert "id" in brain
        assert "name" in brain
        assert "status" in brain
