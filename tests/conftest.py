"""
Pytest configuration and shared fixtures.

This module provides fixtures for testing parallel execution components.
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict, Any, List

from mastermind_cli.types.parallel import FlowConfig, ProviderConfig


# Paths to test configuration files
CONFIG_DIR = Path(__file__).parent.parent / "mastermind_cli" / "config"
PROVIDERS_CONFIG_PATH = CONFIG_DIR / "providers.yaml"


@pytest.fixture
def mock_flow_yaml() -> Dict[str, Any]:
    """Valid flow configuration with parallel branches.

    Structure:
    - Wave 0: brain-01, brain-02 (no dependencies)
    - Wave 1: brain-03, brain-04 (depend on wave 0)
    - Wave 2: brain-05 (depends on wave 1)
    """
    return {
        "flow_id": "test-flow",
        "nodes": {
            "brain-01": [],  # No deps (Wave 0)
            "brain-02": [],  # No deps (Wave 0)
            "brain-03": ["brain-01"],  # Dep on Wave 0 (Wave 1)
            "brain-04": ["brain-01", "brain-02"],  # Dep on Wave 0 (Wave 1)
            "brain-05": ["brain-03", "brain-04"],  # Dep on Wave 1 (Wave 2)
        }
    }


@pytest.fixture
def cyclic_flow_yaml() -> Dict[str, Any]:
    """Invalid flow configuration with a cycle (A→B→A)."""
    return {
        "flow_id": "cyclic-flow",
        "nodes": {
            "brain-A": ["brain-B"],
            "brain-B": ["brain-A"]
        }
    }


@pytest.fixture
def linear_flow_yaml() -> Dict[str, Any]:
    """Simple linear flow (A→B→C→D)."""
    return {
        "flow_id": "linear-flow",
        "nodes": {
            "brain-A": [],
            "brain-B": ["brain-A"],
            "brain-C": ["brain-B"],
            "brain-D": ["brain-C"]
        }
    }


@pytest.fixture
def diamond_flow_yaml() -> Dict[str, Any]:
    """Diamond pattern flow (A→B, A→C, B→D, C→D)."""
    return {
        "flow_id": "diamond-flow",
        "nodes": {
            "brain-A": [],
            "brain-B": ["brain-A"],
            "brain-C": ["brain-A"],
            "brain-D": ["brain-B", "brain-C"]
        }
    }


@pytest.fixture
def empty_flow_yaml() -> Dict[str, Any]:
    """Empty flow with no brains."""
    return {
        "flow_id": "empty-flow",
        "nodes": {}
    }


@pytest.fixture
def provider_configs() -> List[ProviderConfig]:
    """Load provider configurations from providers.yaml."""
    if not PROVIDERS_CONFIG_PATH.exists():
        pytest.skip(f"Providers config not found: {PROVIDERS_CONFIG_PATH}")

    with open(PROVIDERS_CONFIG_PATH) as f:
        data = yaml.safe_load(f)

    return [ProviderConfig(**provider) for provider in data["providers"]]


@pytest.fixture
def notebooklm_provider() -> ProviderConfig:
    """Get NotebookLM provider configuration."""
    return ProviderConfig(
        name="notebooklm",
        max_concurrent_calls=2,
        retry_attempts=3,
        backoff_base=1.0
    )


@pytest.fixture
def claude_provider() -> ProviderConfig:
    """Get Claude provider configuration."""
    return ProviderConfig(
        name="claude",
        max_concurrent_calls=10,
        retry_attempts=3,
        backoff_base=1.0
    )
