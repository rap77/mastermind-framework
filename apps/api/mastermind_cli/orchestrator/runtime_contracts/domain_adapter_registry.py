"""Deterministic exact-match registry for domain delivery adapters."""

from __future__ import annotations

from dataclasses import dataclass

from .domain_delivery_adapter import DomainDeliveryAdapter


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be empty")


@dataclass(frozen=True, slots=True)
class AdapterResolution:
    """Explainable result of one explicit domain and mode selection."""

    adapter: DomainDeliveryAdapter
    domain: str
    mode: str
    required_capability_ids: tuple[str, ...]
    rationale: tuple[str, ...]


class DomainAdapterRegistry:
    """Validate an active adapter inventory and resolve exact requests."""

    def __init__(self, adapters: tuple[DomainDeliveryAdapter, ...]) -> None:
        """Register an unambiguous set of immutable adapter declarations."""
        identities = tuple(adapter.versioned_id for adapter in adapters)
        duplicate_identities = sorted(
            identity for identity in set(identities) if identities.count(identity) > 1
        )
        if duplicate_identities:
            raise ValueError(
                "Duplicate domain delivery adapter identity: "
                + ", ".join(duplicate_identities)
            )

        adapters_by_match: dict[tuple[str, str], list[DomainDeliveryAdapter]] = {}
        for adapter in adapters:
            for domain in adapter.supported_domains:
                for mode in adapter.supported_modes:
                    adapters_by_match.setdefault((domain, mode), []).append(adapter)
        for (domain, mode), matches in sorted(adapters_by_match.items()):
            if len(matches) > 1:
                matched_ids = ", ".join(
                    sorted(adapter.versioned_id for adapter in matches)
                )
                raise ValueError(
                    "Ambiguous domain delivery adapter match for "
                    f"{domain}/{mode}: {matched_ids}"
                )

        self._adapters_by_match = {
            match: matches[0] for match, matches in adapters_by_match.items()
        }

    def resolve(
        self,
        *,
        domain: str,
        mode: str,
        required_capability_ids: frozenset[str],
    ) -> AdapterResolution:
        """Resolve an exact adapter and fail if required capabilities are absent."""
        _require_text(domain, "domain")
        _require_text(mode, "mode")
        adapter = self._adapters_by_match.get((domain, mode))
        if adapter is None:
            raise ValueError(
                f"No domain delivery adapter matches domain '{domain}' "
                f"and delivery mode '{mode}'"
            )

        available_capability_ids = {
            capability.capability_id for capability in adapter.producer_capabilities
        }
        missing_capability_ids = tuple(
            sorted(required_capability_ids - available_capability_ids)
        )
        if missing_capability_ids:
            raise ValueError(
                f"Adapter '{adapter.versioned_id}' is missing required capabilities: "
                + ", ".join(missing_capability_ids)
            )

        required_ids = tuple(sorted(required_capability_ids))
        capability_rationale = ", ".join(required_ids) if required_ids else "none"
        return AdapterResolution(
            adapter=adapter,
            domain=domain,
            mode=mode,
            required_capability_ids=required_ids,
            rationale=(
                f"exact domain match: {domain}",
                f"exact delivery mode match: {mode}",
                f"required capabilities satisfied: {capability_rationale}",
                f"selected adapter: {adapter.versioned_id}",
            ),
        )
