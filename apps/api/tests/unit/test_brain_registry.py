"""
Unit tests for brain_registry.py
"""

import yaml
from mastermind_cli.brain_registry import (
    load_brain_configs,
    get_brain,
    list_active_brains,
    get_brain_count,
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


def test_get_all_brains_paginated():
    """Test that get_all_brains returns paginated response."""
    from mastermind_cli.brain_registry import get_all_brains

    result = get_all_brains(page=1, page_size=24, user_id="test-user")

    # Should have pagination metadata
    assert "brains" in result
    assert "total" in result
    assert "page" in result
    assert "page_size" in result

    # Should return all current brains by default
    assert result["total"] >= 8  # At least brains 1-8
    assert len(result["brains"]) <= 24  # Respects page_size


def test_get_all_brains_default_page_size():
    """Test that default page_size=24 returns all current brains."""
    from mastermind_cli.brain_registry import get_all_brains

    result = get_all_brains(page=1, user_id="test-user")

    # Should use default page_size=24
    assert result["page_size"] == 24
    assert len(result["brains"]) >= 8  # At least brains 1-8


def test_get_all_brains_brain_metadata():
    """Test that each brain has required metadata fields."""
    from mastermind_cli.brain_registry import get_all_brains

    result = get_all_brains(page=1, page_size=24, user_id="test-user")

    # Check first brain has all required fields
    if len(result["brains"]) > 0:
        brain = result["brains"][0]
        assert "id" in brain
        assert "name" in brain
        assert "niche" in brain
        assert "status" in brain
        assert "uptime" in brain
        assert "last_called_at" in brain


def test_get_all_brains_niche_values():
    """Test that niche is one of: master, software, marketing."""
    from mastermind_cli.brain_registry import get_all_brains

    result = get_all_brains(page=1, page_size=24, user_id="test-user")

    valid_niches = ["software-development", "marketing-digital", "universal"]
    for brain in result["brains"]:
        assert brain["niche"] in valid_niches


def test_get_all_brains_status_values():
    """Test that status is one of: idle, active, error, complete."""
    from mastermind_cli.brain_registry import get_all_brains

    result = get_all_brains(page=1, page_size=24, user_id="test-user")

    valid_statuses = ["idle", "active", "error", "complete"]
    for brain in result["brains"]:
        assert brain["status"] in valid_statuses


def test_get_all_brains_pagination_logic():
    """Test that page_size=10 with page=1 returns first 10 brains."""
    from mastermind_cli.brain_registry import get_all_brains

    result = get_all_brains(page=1, page_size=10, user_id="test-user")

    # Should return first 10 brains
    assert len(result["brains"]) <= 10
    assert result["page"] == 1
    assert result["page_size"] == 10
    assert result["total"] >= 8  # Total should reflect all brains
