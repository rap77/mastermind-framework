"""
Brain Registry - Load brain configurations from YAML.

This module loads brain configurations from YAML and provides helper
functions for querying brain data. It maintains backward compatibility
with existing code that uses BRAIN_CONFIGS directly.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional

# Config directory paths
CONFIG_DIR = Path(__file__).parent / "config"
BRAINS_CONFIG_PATH = CONFIG_DIR / "brains.yaml"


def load_brain_configs() -> Dict[int, Dict]:
    """
    Load brain configurations from YAML file.

    Returns:
        Dictionary mapping brain_id to brain config.

    Raises:
        FileNotFoundError: If brains.yaml doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    if not BRAINS_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Brain config not found: {BRAINS_CONFIG_PATH}\n"
            f"Run 'mm framework status' to verify installation."
        )

    with open(BRAINS_CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    brains = {}
    for brain in config.get("brains", []):
        brains[brain["id"]] = brain

    return brains


# Maintain backward compatibility - load brains at import time
BRAIN_CONFIGS = load_brain_configs()


def get_brain(brain_id: int) -> Optional[Dict]:
    """Get a specific brain configuration."""
    return BRAIN_CONFIGS.get(brain_id)


def list_active_brains() -> List[int]:
    """List all active brain IDs."""
    return [
        brain_id
        for brain_id, config in BRAIN_CONFIGS.items()
        if config.get("status") == "active"
    ]


def get_brain_count() -> int:
    """Get total number of registered brains."""
    return len(BRAIN_CONFIGS)


# Public notebook identifiers (legacy - for external reference)
# Safe to version control - these are configuration, not credentials.
BRAIN_REGISTRY: dict = {
    "#1": {
        "name": "Product Strategy",
        "notebook_id": "f276ccb3-0bce-4069-8b55-eae8693dbe75",
        "expertise": "What & Why - Product definition, strategy, discovery",
    },
    "#2": {
        "name": "UX Research",
        "notebook_id": "ea006ece-00a9-4d5c-91f5-012b8b712936",
        "expertise": "User Experience - Research methods, user insights",
    },
    "#3": {
        "name": "UI Design",
        "notebook_id": "8d544475-6860-4cd7-9037-8549325493dd",
        "expertise": "Visual Design - Design systems, components, patterns",
    },
    "#4": {
        "name": "Frontend",
        "notebook_id": "85e47142-0a65-41d9-9848-49b8b5d2db33",
        "expertise": "Frontend Architecture - React, Next.js, state management",
    },
    "#5": {
        "name": "Backend",
        "notebook_id": "c6befbbc-b7dd-4ad0-a677-314750684208",
        "expertise": "Backend Architecture - APIs, databases, services",
    },
    "#6": {
        "name": "QA/DevOps",
        "notebook_id": "74cd3a81-1350-4927-af14-c0c4fca41a8e",
        "expertise": "Quality & Operations - Testing, CI/CD, reliability",
    },
    "#7": {
        "name": "Growth/Data",
        "notebook_id": "d8de74d6-7028-44ed-b4d4-784d6a9256e6",
        "expertise": "Growth & Evaluation - Metrics, experimentation, optimization",
    },
}
