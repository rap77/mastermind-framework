"""
MM-Flow config loader.

Reads .planning/.mm-flow/config.yml — falls back to built-in defaults
if file is missing, raises ConfigError if file is malformed.

IMPORTANT: _DEFAULTS model IDs must be updated when Anthropic deprecates
a model version. Check https://docs.anthropic.com/en/docs/about-claude/models
and update the model strings here before models stop responding.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)

VALID_MODEL_KEYS = frozenset({"quality", "balanced", "budget"})

_DEFAULTS: dict[str, Any] = {
    "model_profiles": {
        "quality": {
            "model": "claude-opus-4-6",
            "use_when": "critical decisions, Brain #7 barrier",
        },
        "balanced": {
            "model": "claude-sonnet-4-6",
            "use_when": "standard domain brains",
        },
        "budget": {
            "model": "claude-haiku-4-5",
            "use_when": "context recovery, status checks",
        },
    },
    "brain_routing": {
        "DISCUSSION": {"brains": [1, 2, 3], "parallel": True, "barrier": [7]},
        "PLANNING": {"brains": [4, 5, 6], "parallel": True, "barrier": [7]},
        "EXECUTION_WAVE": {"brains": [7], "parallel": False, "barrier": []},
        "VERIFICATION": {
            "brains": [7],
            "parallel": False,
            "barrier": [],
            "blocking": True,
        },
    },
    "verification_gates": {
        "spec_coverage_threshold": 0.95,
        "max_gate_retries": 1,
        "escalate_on_failure": True,
    },
}


class ConfigError(Exception):
    """Raised when config.yml is malformed or contains unknown keys."""


@dataclass
class ModelProfile:
    model: str
    use_when: str


@dataclass
class BrainRoutingRule:
    brains: list[int]
    parallel: bool
    barrier: list[int] = field(default_factory=list)
    model_override: str | None = None
    blocking: bool = False


@dataclass
class MMFlowConfig:
    model_profiles: dict[str, ModelProfile]
    brain_routing: dict[str, BrainRoutingRule]
    verification_gates: dict[str, Any]


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge override into base, only overriding present keys."""
    result: dict[str, Any] = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str = ".planning/.mm-flow/config.yml") -> MMFlowConfig:
    """
    Load MM-Flow config from path.

    - missing file  → use defaults, log warning
    - malformed YAML → raise ConfigError
    - unknown model key → raise ConfigError
    """
    try:
        raw: dict[str, Any] = yaml.safe_load(Path(path).read_text()) or {}
    except FileNotFoundError:
        logger.warning("config.yml not found at %s — using defaults", path)
        raw = {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"config.yml malformado en {path}: {exc}") from exc

    # Deep merge: user overrides only the keys they provide
    data = _deep_merge(_DEFAULTS, raw)

    # Validate model profile keys
    profiles_raw: dict[str, Any] = data["model_profiles"]
    for key in profiles_raw:
        if key not in VALID_MODEL_KEYS:
            raise ConfigError(
                f"model_profiles contiene clave desconocida: '{key}'. "
                f"Válidas: {sorted(VALID_MODEL_KEYS)}"
            )

    model_profiles = {
        k: ModelProfile(model=v["model"], use_when=v.get("use_when", ""))
        for k, v in profiles_raw.items()
    }

    routing_raw: dict[str, Any] = data["brain_routing"]
    brain_routing = {
        moment: BrainRoutingRule(
            brains=v["brains"],
            parallel=v.get("parallel", True),
            barrier=v.get("barrier", []),
            model_override=v.get("model_override"),
            blocking=v.get("blocking", False),
        )
        for moment, v in routing_raw.items()
    }

    return MMFlowConfig(
        model_profiles=model_profiles,
        brain_routing=brain_routing,
        verification_gates=data["verification_gates"],
    )


# ---------------------------------------------------------------------------
# Runtime State Model (SUGGESTION #4)
# ---------------------------------------------------------------------------


class RuntimeState(BaseModel):
    """Runtime state written to runtime-state.json (C2, C4).

    Attributes:
        execution_id: UUID string matching phase_executions.id (C4).
        phase: Phase number being executed.
        current_moment: Current execution moment (e.g. EXECUTION_WAVE, COMPLETED).
        active_brain: Active brain ID; 0 means orchestrator.
        brain_state: Brain lifecycle state (ACTIVE | IDLE | BARRIER | OFFLINE).
        backend: Execution backend identifier (e.g. "claude").
        updated_at: ISO timestamp of last state update.
    """

    model_config = ConfigDict(strict=True)
    execution_id: str
    phase: int
    current_moment: str
    active_brain: int
    brain_state: str
    backend: str
    updated_at: str

    def to_json_file(self, path: Path) -> None:
        """Write runtime state atomically via temp file + rename.

        Performance: Uses Pydantic's model_dump_json() which is ~2x faster
        than json.dumps(model_dump()) because it serializes directly without
        intermediate dict conversion.

        Args:
            path: Target file path (will be created/overwritten atomically).

        Raises:
            ValueError: If path contains directory traversal components.

        The temp file + rename pattern guarantees atomicity on POSIX systems:
        - Write to temp file (path.tmp)
        - Rename temp to target (atomic operation)
        - If process crashes mid-write, target file remains intact

        Permissions are explicitly set to 0o644 (rw-r--r--) for security-sensitive
        environments, preventing accidental permission drift from umask.
        """
        # Security: Prevent path traversal attacks
        if ".." in path.parts:
            raise ValueError(
                f"Invalid path: {path}. Path must not contain '..' (path traversal)"
            )

        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = Path(str(path) + ".tmp")
        tmp.write_text(self.model_dump_json(indent=2))
        tmp.rename(path)
        # Explicit permissions for security-sensitive environments
        path.chmod(0o644)  # rw-r--r--
