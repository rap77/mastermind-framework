"""Immutable, versioned declarations for domain delivery adapters."""

from __future__ import annotations

from dataclasses import dataclass


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be empty")


def _require_entries(values: tuple[str, ...], label: str) -> None:
    if not values:
        raise ValueError(f"{label} must not be empty")
    if any(not value.strip() for value in values):
        raise ValueError(f"{label} entries must not be empty")


def _require_unique(values: tuple[str, ...], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")


@dataclass(frozen=True, slots=True)
class AdapterContractRef:
    """Exact identity and version of an adapter-owned external contract."""

    contract_id: str
    version: str

    def __post_init__(self) -> None:
        _require_text(self.contract_id, "contract_id")
        _require_text(self.version, "version")

    @property
    def versioned_id(self) -> str:
        """Return the canonical versioned contract reference."""
        return f"{self.contract_id}@{self.version}"


def _require_ref_entries(values: tuple[AdapterContractRef, ...], label: str) -> None:
    if not values:
        raise ValueError(f"{label} must not be empty")
    _require_unique(tuple(value.versioned_id for value in values), label)


@dataclass(frozen=True, slots=True)
class StageVocabularyMapping:
    """Versioned mapping from a core concern to adapter-owned vocabulary."""

    concern: str
    domain_stage: str
    version: str

    def __post_init__(self) -> None:
        _require_text(self.concern, "concern")
        _require_text(self.domain_stage, "domain_stage")
        _require_text(self.version, "version")


@dataclass(frozen=True, slots=True)
class ArtifactContract:
    """Versioned artifact type and its adapter-declared owner role."""

    artifact_type: str
    owner_role: str
    version: str

    def __post_init__(self) -> None:
        _require_text(self.artifact_type, "artifact_type")
        _require_text(self.owner_role, "owner_role")
        _require_text(self.version, "version")


@dataclass(frozen=True, slots=True)
class ProducerCapability:
    """Versioned producer capability and the artifact types it may create."""

    capability_id: str
    version: str
    produced_artifact_types: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(self.capability_id, "capability_id")
        _require_text(self.version, "version")
        _require_entries(self.produced_artifact_types, "produced_artifact_types")
        _require_unique(self.produced_artifact_types, "produced_artifact_types")


@dataclass(frozen=True, slots=True)
class VerificationStrategy:
    """Versioned strategy applicable to declared adapter artifact types."""

    strategy_id: str
    version: str
    artifact_types: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(self.strategy_id, "strategy_id")
        _require_text(self.version, "version")
        _require_entries(self.artifact_types, "artifact_types")
        _require_unique(self.artifact_types, "artifact_types")


@dataclass(frozen=True, slots=True)
class AdapterExtensionMetadata:
    """Typed, versioned adapter extension data outside universal core fields."""

    schema_id: str
    schema_version: str
    entries: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        _require_text(self.schema_id, "schema_id")
        _require_text(self.schema_version, "schema_version")
        keys = tuple(key for key, _ in self.entries)
        if any(not key.strip() or not value.strip() for key, value in self.entries):
            raise ValueError("extension entries must contain non-empty keys and values")
        _require_unique(keys, "extension entry keys")


@dataclass(frozen=True, slots=True)
class DomainDeliveryAdapter:
    """Complete adapter contract consumed by the domain-agnostic runtime."""

    adapter_id: str
    version: str
    supported_domains: tuple[str, ...]
    supported_modes: tuple[str, ...]
    decomposition_rule_refs: tuple[AdapterContractRef, ...]
    stage_mappings: tuple[StageVocabularyMapping, ...]
    artifact_contracts: tuple[ArtifactContract, ...]
    producer_capabilities: tuple[ProducerCapability, ...]
    verification_strategies: tuple[VerificationStrategy, ...]
    integration_semantics_ref: AdapterContractRef
    policy_pack_refs: tuple[AdapterContractRef, ...]
    required_approval_refs: tuple[AdapterContractRef, ...]
    security_overlay_ref: AdapterContractRef
    persistence_projection_refs: tuple[AdapterContractRef, ...]
    extensions: tuple[AdapterExtensionMetadata, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.adapter_id, "adapter_id")
        _require_text(self.version, "version")
        for text_label, text_values in (
            ("supported_domains", self.supported_domains),
            ("supported_modes", self.supported_modes),
        ):
            _require_entries(text_values, text_label)
            _require_unique(text_values, text_label)
        for ref_label, ref_values in (
            ("decomposition_rule_refs", self.decomposition_rule_refs),
            ("policy_pack_refs", self.policy_pack_refs),
            ("required_approval_refs", self.required_approval_refs),
            ("persistence_projection_refs", self.persistence_projection_refs),
        ):
            _require_ref_entries(ref_values, ref_label)

        stage_concerns = tuple(mapping.concern for mapping in self.stage_mappings)
        artifact_types = tuple(
            contract.artifact_type for contract in self.artifact_contracts
        )
        capability_ids = tuple(
            capability.capability_id for capability in self.producer_capabilities
        )
        strategy_ids = tuple(
            strategy.strategy_id for strategy in self.verification_strategies
        )
        extension_schemas = tuple(extension.schema_id for extension in self.extensions)
        for values, label in (
            (stage_concerns, "stage mapping concerns"),
            (artifact_types, "artifact contract types"),
            (capability_ids, "producer capability IDs"),
            (strategy_ids, "verification strategy IDs"),
        ):
            _require_entries(values, label)
            _require_unique(values, label)
        _require_unique(extension_schemas, "extension schema IDs")

        declared_artifacts = set(artifact_types)
        producer_artifacts = {
            artifact_type
            for capability in self.producer_capabilities
            for artifact_type in capability.produced_artifact_types
        }
        if undeclared := sorted(producer_artifacts - declared_artifacts):
            raise ValueError(
                "Producer capabilities reference undeclared artifact types: "
                + ", ".join(undeclared)
            )
        verification_artifacts = {
            artifact_type
            for strategy in self.verification_strategies
            for artifact_type in strategy.artifact_types
        }
        if undeclared := sorted(verification_artifacts - declared_artifacts):
            raise ValueError(
                "Verification strategies reference undeclared artifact types: "
                + ", ".join(undeclared)
            )

    @property
    def versioned_id(self) -> str:
        """Return the stable adapter identity including its declaration version."""
        return f"{self.adapter_id}@{self.version}"
