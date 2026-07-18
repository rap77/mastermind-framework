"""Domain security overlay declarations with fail-closed source resolution."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

from .models import SecurityControl, SecurityOverlay

SecuritySourceEscalationReason = Literal[
    "missing", "stale", "contradictory", "jurisdiction"
]


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be empty")


@dataclass(frozen=True, slots=True)
class SecuritySourceRef:
    """Exact identity of a source required by a domain overlay."""

    source_id: str
    version: str

    def __post_init__(self) -> None:
        _require_text(self.source_id, "source_id")
        _require_text(self.version, "version")

    @property
    def versioned_id(self) -> str:
        """Return the canonical source identifier retained by controls."""
        return f"{self.source_id}@{self.version}"


@dataclass(frozen=True, slots=True)
class SecuritySource:
    """Versioned source metadata; never contains raw evidence or legal analysis."""

    source_id: str
    version: str
    authority: str
    jurisdiction: str
    effective_date: date
    review_by: date
    superseded: bool = False
    contradicts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.source_id, "source_id")
        _require_text(self.version, "version")
        _require_text(self.authority, "authority")
        _require_text(self.jurisdiction, "jurisdiction")
        if self.review_by < self.effective_date:
            raise ValueError("review_by must not precede effective_date")
        if any(not reference.strip() for reference in self.contradicts):
            raise ValueError("contradicts must contain non-empty source references")

    @property
    def ref(self) -> SecuritySourceRef:
        """Return the exact source reference represented by this metadata."""
        return SecuritySourceRef(self.source_id, self.version)


@dataclass(frozen=True, slots=True)
class DomainOverlayDeclaration:
    """Adapter-owned domain overlay and its exact source dependencies."""

    domain: str
    overlay: SecurityOverlay
    source_refs: tuple[SecuritySourceRef, ...]

    def __post_init__(self) -> None:
        _require_text(self.domain, "domain")
        if self.overlay.scope != "domain" or self.overlay.domain != self.domain:
            raise ValueError("domain declaration overlay must match its domain")
        if not self.source_refs:
            raise ValueError("domain declaration requires at least one source")
        versioned_refs = tuple(ref.versioned_id for ref in self.source_refs)
        if len(versioned_refs) != len(set(versioned_refs)):
            raise ValueError("domain declaration source references must be unique")
        control_sources = {control.source_version for control in self.overlay.controls}
        if not control_sources.issubset(versioned_refs):
            raise ValueError("overlay controls must reference declared sources")


@dataclass(frozen=True, slots=True)
class ResolvedDomainOverlay:
    """Domain overlay plus the exact source and jurisdiction resolution context."""

    overlay: SecurityOverlay
    jurisdiction: str
    sources: tuple[SecuritySource, ...]


class SecuritySourceEscalation(RuntimeError):
    """Typed fail-closed signal for unusable domain security sources."""

    def __init__(
        self,
        *,
        reason: SecuritySourceEscalationReason,
        domain: str,
        jurisdiction: str,
        source_refs: tuple[str, ...],
    ) -> None:
        """Create an escalation without embedding raw evidence or source content."""
        self.reason = reason
        self.domain = domain
        self.jurisdiction = jurisdiction
        self.source_refs = source_refs
        references = ", ".join(source_refs) if source_refs else "none"
        super().__init__(
            f"Security source escalation ({reason}) for domain '{domain}' "
            f"in jurisdiction '{jurisdiction}'; sources: {references}"
        )


class DomainOverlayRegistry:
    """Resolve adapter declarations only when all exact sources are usable."""

    def __init__(
        self,
        declarations: tuple[DomainOverlayDeclaration, ...] | None = None,
        sources: tuple[SecuritySource, ...] | None = None,
    ) -> None:
        """Initialize with caller-owned declarations or the minimal defaults."""
        self._declarations = declarations or _default_declarations()
        self._sources = sources if sources is not None else _default_sources()
        domains = tuple(declaration.domain for declaration in self._declarations)
        if len(domains) != len(set(domains)):
            raise ValueError("domain overlay declarations must have unique domains")
        source_keys = tuple(source.ref for source in self._sources)
        if len(source_keys) != len(set(source_keys)):
            raise ValueError("security sources must have unique identity and version")

    def resolve(
        self,
        *,
        domain: str,
        jurisdiction: str,
        as_of: date,
    ) -> ResolvedDomainOverlay:
        """Resolve one domain overlay or raise a typed source escalation."""
        _require_text(domain, "domain")
        _require_text(jurisdiction, "jurisdiction")
        declaration = next(
            (
                candidate
                for candidate in self._declarations
                if candidate.domain == domain
            ),
            None,
        )
        if declaration is None:
            raise ValueError(f"Unsupported security overlay domain: {domain}")

        source_by_ref = {source.ref: source for source in self._sources}
        requested_refs = tuple(ref.versioned_id for ref in declaration.source_refs)
        missing = tuple(
            ref for ref in declaration.source_refs if ref not in source_by_ref
        )
        if missing:
            raise SecuritySourceEscalation(
                reason="missing",
                domain=domain,
                jurisdiction=jurisdiction,
                source_refs=tuple(ref.versioned_id for ref in missing),
            )

        resolved = tuple(source_by_ref[ref] for ref in declaration.source_refs)
        if any(
            source.jurisdiction not in {"GLOBAL", jurisdiction} for source in resolved
        ):
            raise SecuritySourceEscalation(
                reason="jurisdiction",
                domain=domain,
                jurisdiction=jurisdiction,
                source_refs=requested_refs,
            )
        if any(
            source.superseded
            or as_of < source.effective_date
            or as_of > source.review_by
            for source in resolved
        ):
            raise SecuritySourceEscalation(
                reason="stale",
                domain=domain,
                jurisdiction=jurisdiction,
                source_refs=requested_refs,
            )
        if any(source.contradicts for source in resolved):
            raise SecuritySourceEscalation(
                reason="contradictory",
                domain=domain,
                jurisdiction=jurisdiction,
                source_refs=requested_refs,
            )
        return ResolvedDomainOverlay(
            overlay=declaration.overlay,
            jurisdiction=jurisdiction,
            sources=resolved,
        )


def _overlay(
    domain: str,
    source_ref: SecuritySourceRef,
    control_ids: tuple[str, ...],
) -> SecurityOverlay:
    return SecurityOverlay(
        overlay_id=f"{domain}-security",
        version="1.0.0",
        scope="domain",
        domain=domain,
        controls=tuple(
            SecurityControl(
                control_id=control_id,
                enforcement="required",
                source_version=source_ref.versioned_id,
            )
            for control_id in control_ids
        ),
    )


def _default_declarations() -> tuple[DomainOverlayDeclaration, ...]:
    definitions = (
        (
            "software",
            SecuritySourceRef("MM-SEC-SOFTWARE", "2026.1"),
            (
                "software-authentication-authorization",
                "software-input-validation",
                "software-supply-chain",
            ),
        ),
        (
            "marketing",
            SecuritySourceRef("MM-SEC-MARKETING", "2026.1"),
            (
                "marketing-consent-tracking",
                "marketing-customer-data",
                "marketing-third-party-scripts",
            ),
        ),
        (
            "finance",
            SecuritySourceRef("MM-SEC-FINANCE", "2026.1"),
            (
                "finance-transaction-authorization",
                "finance-segregation-of-duties",
                "finance-ledger-integrity",
            ),
        ),
    )
    return tuple(
        DomainOverlayDeclaration(
            domain=domain,
            overlay=_overlay(domain, source_ref, control_ids),
            source_refs=(source_ref,),
        )
        for domain, source_ref, control_ids in definitions
    )


def _default_sources() -> tuple[SecuritySource, ...]:
    return tuple(
        SecuritySource(
            source_id=f"MM-SEC-{domain.upper()}",
            version="2026.1",
            authority="MasterMind canonical security assurance plane",
            jurisdiction="GLOBAL",
            effective_date=date(2026, 7, 1),
            review_by=date(2027, 7, 1),
        )
        for domain in ("software", "marketing", "finance")
    )
