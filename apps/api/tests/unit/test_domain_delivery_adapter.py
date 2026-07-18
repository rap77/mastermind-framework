"""Conformance and resolution tests for domain delivery adapters."""

from dataclasses import FrozenInstanceError, replace

import pytest

from mastermind_cli.orchestrator.runtime_contracts import (
    AdapterContractRef,
    AdapterExtensionMetadata,
    AdapterResolution,
    ArtifactContract,
    DomainAdapterRegistry,
    DomainDeliveryAdapter,
    ProducerCapability,
    StageVocabularyMapping,
    VerificationStrategy,
)


def _adapter(
    *,
    adapter_id: str = "knowledge-delivery",
    version: str = "1.2.0",
    domains: tuple[str, ...] = ("knowledge-management",),
    modes: tuple[str, ...] = ("document-production",),
    capabilities: tuple[ProducerCapability, ...] | None = None,
    verification_strategies: tuple[VerificationStrategy, ...] | None = None,
) -> DomainDeliveryAdapter:
    return DomainDeliveryAdapter(
        adapter_id=adapter_id,
        version=version,
        supported_domains=domains,
        supported_modes=modes,
        decomposition_rule_refs=(
            AdapterContractRef("decomposition:knowledge-unit", "1"),
        ),
        stage_mappings=(
            StageVocabularyMapping(
                concern="production",
                domain_stage="drafting",
                version="1",
            ),
        ),
        artifact_contracts=(
            ArtifactContract(
                artifact_type="publication",
                owner_role="domain-producer",
                version="1",
            ),
        ),
        producer_capabilities=capabilities
        or (
            ProducerCapability(
                capability_id="publication-producer",
                version="2",
                produced_artifact_types=("publication",),
            ),
        ),
        verification_strategies=verification_strategies
        or (
            VerificationStrategy(
                strategy_id="publication-review",
                version="1",
                artifact_types=("publication",),
            ),
        ),
        integration_semantics_ref=AdapterContractRef(
            "integration:publication-set", "1"
        ),
        policy_pack_refs=(AdapterContractRef("policy:publication-quality", "1"),),
        required_approval_refs=(AdapterContractRef("approval:publication-owner", "1"),),
        security_overlay_ref=AdapterContractRef("security:knowledge-management", "1"),
        persistence_projection_refs=(
            AdapterContractRef("projection:publication-lineage", "1"),
        ),
        extensions=(
            AdapterExtensionMetadata(
                schema_id="knowledge.publication-metadata",
                schema_version="1",
                entries=(("audience", "internal"),),
            ),
        ),
    )


def test_adapter_declaration_is_immutable_versioned_and_typed() -> None:
    """Domain metadata should extend the contract without mutating core models."""
    adapter = _adapter()

    assert adapter.versioned_id == "knowledge-delivery@1.2.0"
    assert adapter.security_overlay_ref.versioned_id == (
        "security:knowledge-management@1"
    )
    assert adapter.stage_mappings[0].domain_stage == "drafting"
    assert adapter.extensions[0].entries == (("audience", "internal"),)

    with pytest.raises(FrozenInstanceError):
        adapter.version = "2.0.0"  # type: ignore[misc]


def test_adapter_allows_no_domain_extension_metadata() -> None:
    """Typed extensions should remain optional when core fields are sufficient."""
    adapter = replace(_adapter(), extensions=())

    assert adapter.extensions == ()


def test_registry_resolves_explicit_domain_and_mode_with_rationale() -> None:
    """Exact selection should return stable identity and explain its evidence."""
    expected = _adapter()
    unrelated = _adapter(
        adapter_id="event-delivery",
        domains=("event-management",),
        modes=("event-production",),
    )

    first = DomainAdapterRegistry((unrelated, expected)).resolve(
        domain="knowledge-management",
        mode="document-production",
        required_capability_ids=frozenset({"publication-producer"}),
    )
    second = DomainAdapterRegistry((expected, unrelated)).resolve(
        domain="knowledge-management",
        mode="document-production",
        required_capability_ids=frozenset({"publication-producer"}),
    )

    assert isinstance(first, AdapterResolution)
    assert first == second
    assert first.adapter == expected
    assert first.rationale == (
        "exact domain match: knowledge-management",
        "exact delivery mode match: document-production",
        "required capabilities satisfied: publication-producer",
        "selected adapter: knowledge-delivery@1.2.0",
    )


def test_registry_rejects_missing_required_capabilities_loudly() -> None:
    """Selection must block rather than silently substitute a producer."""
    registry = DomainAdapterRegistry((_adapter(),))

    with pytest.raises(
        ValueError,
        match=(
            "Adapter 'knowledge-delivery@1.2.0' is missing required "
            "capabilities: localization-producer"
        ),
    ):
        registry.resolve(
            domain="knowledge-management",
            mode="document-production",
            required_capability_ids=frozenset({"localization-producer"}),
        )


def test_registry_rejects_duplicate_adapter_identity() -> None:
    """An adapter identity and version may be registered only once."""
    adapter = _adapter()

    with pytest.raises(
        ValueError,
        match="Duplicate domain delivery adapter identity: knowledge-delivery@1.2.0",
    ):
        DomainAdapterRegistry((adapter, adapter))


def test_registry_rejects_ambiguous_exact_domain_mode_match() -> None:
    """The active inventory must not rely on registration order for selection."""
    first = _adapter()
    second = _adapter(adapter_id="alternate-delivery")

    with pytest.raises(
        ValueError,
        match=(
            "Ambiguous domain delivery adapter match for "
            "knowledge-management/document-production: "
            "alternate-delivery@1.2.0, knowledge-delivery@1.2.0"
        ),
    ):
        DomainAdapterRegistry((first, second))


def test_registry_rejects_unsupported_explicit_domain_mode() -> None:
    """Inference is not a fallback when the requested pair has no exact match."""
    registry = DomainAdapterRegistry((_adapter(),))

    with pytest.raises(
        ValueError,
        match=(
            "No domain delivery adapter matches domain 'finance' "
            "and delivery mode 'report-production'"
        ),
    ):
        registry.resolve(
            domain="finance",
            mode="report-production",
            required_capability_ids=frozenset(),
        )


@pytest.mark.parametrize(
    ("capabilities", "strategies", "message"),
    [
        (
            (
                ProducerCapability(
                    capability_id="unknown-producer",
                    version="1",
                    produced_artifact_types=("undeclared-artifact",),
                ),
            ),
            None,
            "Producer capabilities reference undeclared artifact types",
        ),
        (
            None,
            (
                VerificationStrategy(
                    strategy_id="unknown-verifier",
                    version="1",
                    artifact_types=("undeclared-artifact",),
                ),
            ),
            "Verification strategies reference undeclared artifact types",
        ),
    ],
)
def test_adapter_rejects_artifact_contract_drift(
    capabilities: tuple[ProducerCapability, ...] | None,
    strategies: tuple[VerificationStrategy, ...] | None,
    message: str,
) -> None:
    """Adapter-owned producers and verifiers must honor declared artifacts."""
    with pytest.raises(ValueError, match=message):
        _adapter(capabilities=capabilities, verification_strategies=strategies)
