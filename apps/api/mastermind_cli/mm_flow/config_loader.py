"""
MM-Flow config loader.

Reads .planning/.mm-flow/config.yml — falls back to built-in defaults
if file is missing, raises ConfigError if file is malformed.

IMPORTANT: _DEFAULTS model IDs must be updated when Anthropic deprecates
a model version. Check https://docs.anthropic.com/en/docs/about-claude/models
and update the model strings here before models stop responding.

Model format: "provider:model_id" — e.g. "anthropic:claude-opus-4-6".
Supported providers: anthropic, openrouter, z_ai.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)

VALID_MODEL_KEYS = frozenset({"quality", "balanced", "budget"})
VALID_PROVIDERS = frozenset({"anthropic", "openrouter", "z_ai"})

_DEFAULTS: dict[str, Any] = {
    "model_profiles": {
        "quality": {
            "model": "anthropic:claude-opus-4-6",
            "use_when": "critical decisions, Brain #7 barrier",
        },
        "balanced": {
            "model": "anthropic:claude-sonnet-4-6",
            "use_when": "standard domain brains",
        },
        "budget": {
            "model": "z_ai:claude-3-7-sonnet",
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
    "providers": {
        "anthropic": {
            "env_key": "ANTHROPIC_API_KEY",
            "base_url": None,
        },
        "openrouter": {
            "env_key": "OPENROUTER_API_KEY",
            "base_url": "https://openrouter.ai/api/v1",
        },
        "z_ai": {
            "env_key": "ZAI_API_KEY",
            "base_url": "https://api.z.ai/v1",
        },
    },
    "harness_library": {
        "enabled": False,
        "path": ".mm-flow/harness-library",
        "bundle_output_path": ".run-bundles",
    },
}


class ConfigError(Exception):
    """Raised when config.yml is malformed or contains unknown keys."""


@dataclass
class ModelProfile:
    """Model profile with provider-qualified model identifier.

    Attributes:
        model: Provider-qualified model string in format "provider:model_id".
               Example: "anthropic:claude-opus-4-6", "z_ai:claude-3-7-sonnet".
        use_when: Human-readable description of when to use this profile.
        provider: Parsed provider name (e.g. "anthropic", "openrouter", "z_ai").
        model_id: Parsed model identifier without provider prefix.
    """

    model: str
    use_when: str

    @property
    def provider(self) -> str:
        """Return the provider portion of the model string."""
        return self.model.split(":")[0] if ":" in self.model else "anthropic"

    @property
    def model_id(self) -> str:
        """Return the model_id portion without provider prefix."""
        return self.model.split(":", 1)[1] if ":" in self.model else self.model


@dataclass
class BrainRoutingRule:
    brains: list[int]
    parallel: bool
    barrier: list[int] = field(default_factory=list)
    model_override: str | None = None
    blocking: bool = False


@dataclass
class ProviderConfig:
    """Configuration for a single AI provider.

    Attributes:
        env_key: Environment variable name holding the API key for this provider.
                 Example: "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "ZAI_API_KEY".
        base_url: Base URL for the provider API; None means use the SDK default.
    """

    env_key: str
    base_url: str | None


@dataclass
class HarnessLibraryConfig:
    """Configuration for optional Agent Harness library composition."""

    enabled: bool
    path: str
    bundle_output_path: str


@dataclass
class MMFlowConfig:
    model_profiles: dict[str, ModelProfile]
    brain_routing: dict[str, BrainRoutingRule]
    verification_gates: dict[str, Any]
    providers: dict[str, ProviderConfig] = field(default_factory=dict)
    harness_library: HarnessLibraryConfig = field(
        default_factory=lambda: HarnessLibraryConfig(
            enabled=False,
            path=".mm-flow/harness-library",
            bundle_output_path=".run-bundles",
        )
    )


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

    model_profiles: dict[str, ModelProfile] = {}
    for k, v in profiles_raw.items():
        model_str: str = v["model"]
        profile = ModelProfile(model=model_str, use_when=v.get("use_when", ""))
        if ":" in model_str and profile.provider not in VALID_PROVIDERS:
            raise ConfigError(
                f"model_profiles['{k}'].model tiene proveedor desconocido: '{profile.provider}'. "
                f"Válidos: {sorted(VALID_PROVIDERS)}"
            )
        model_profiles[k] = profile

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

    # Parse providers section
    providers_raw: dict[str, Any] = data.get("providers", {})
    providers: dict[str, ProviderConfig] = {
        name: ProviderConfig(
            env_key=v["env_key"],
            base_url=v.get("base_url"),
        )
        for name, v in providers_raw.items()
    }

    harness_library_raw: dict[str, Any] = data["harness_library"]
    harness_library = HarnessLibraryConfig(
        enabled=bool(harness_library_raw.get("enabled", False)),
        path=str(harness_library_raw.get("path", ".mm-flow/harness-library")),
        bundle_output_path=str(
            harness_library_raw.get("bundle_output_path", ".run-bundles")
        ),
    )

    return MMFlowConfig(
        model_profiles=model_profiles,
        brain_routing=brain_routing,
        verification_gates=data["verification_gates"],
        providers=providers,
        harness_library=harness_library,
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
