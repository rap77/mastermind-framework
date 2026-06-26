"""Evidence registry service for canonical documents and source deltas."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import asyncpg

from .evidence_registry_repository import EvidenceRegistryRepository

SOURCE_TYPES = {"repo", "url", "book", "doc", "product", "system", "interview"}
VERSION_STATES = {"current", "superseded", "archived", "deprecated", "retracted"}
DELTA_TYPES = {"functional", "structural", "data", "nfr", "decision"}
DELTA_DECISIONS = {"adopted", "adapted", "rejected", "deprecated", "superseded"}


class EvidenceRegistryService:
    """Manage the versioned evidence registry used by canonical workflows."""

    def __init__(self, registry_path: Path) -> None:
        """Initialize the service with an explicit registry path."""
        self._registry_path = registry_path

    @property
    def registry_path(self) -> Path:
        """Return the registry file path."""
        return self._registry_path

    def load_registry(self) -> dict[str, Any]:
        """Load the registry, returning an empty shape when the file is missing."""
        if not self._registry_path.exists():
            return {"version": 1, "sources": [], "versions": [], "deltas": []}
        try:
            data = json.loads(self._registry_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise ValueError(f"Failed to read evidence registry: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("Evidence registry must be a JSON object.")
        for key in ("sources", "versions", "deltas"):
            if not isinstance(data.get(key), list):
                raise ValueError(
                    f"Evidence registry must contain top-level '{key}' list."
                )
        return data

    def write_registry(self, data: dict[str, Any]) -> None:
        """Persist the registry to disk."""
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._registry_path.write_text(
            json.dumps(data, indent=2) + "\n",
            encoding="utf-8",
        )

    def register_version(
        self,
        *,
        source_type: str,
        name: str,
        uri: str,
        version_ref: str,
        version_hash: str,
        summary: str,
        source_id: str | None = None,
        version_id: str | None = None,
        state: str = "current",
        confidence: float = 0.7,
        coverage: float = 0.7,
        critical_gaps: int = 0,
        important_gaps: int = 0,
        optional_gaps: int = 0,
        contradictions: int = 0,
        user_answers_complete: bool = False,
    ) -> dict[str, Any]:
        """Register a new evidence version and supersede the prior one when needed."""
        self._validate_source_type(source_type)
        self._validate_version_state(state)
        data = self.load_registry()
        version_id = version_id or self._next_version_id(data)
        versions = data["versions"]
        if any(
            entry.get("id") == version_id
            for entry in versions
            if isinstance(entry, dict)
        ):
            raise ValueError(f"Version ID already exists: {version_id}")

        previous_version = self._latest_version_for_source(data, source_id)
        now = self._utc_now()
        entry: dict[str, Any] = {
            "id": version_id,
            "source_id": source_id,
            "source_type": source_type,
            "name": name,
            "uri": uri,
            "version_ref": version_ref,
            "version_hash": version_hash,
            "summary": summary,
            "state": state,
            "confidence": self._clamp(confidence, 0.0, 1.0),
            "coverage": self._clamp(coverage, 0.0, 1.0),
            "critical_gaps": critical_gaps,
            "important_gaps": important_gaps,
            "optional_gaps": optional_gaps,
            "contradictions": contradictions,
            "user_answers_complete": user_answers_complete,
            "created_at_utc": now,
            "updated_at_utc": now,
        }
        versions.append(entry)

        if source_id and not any(
            source.get("source_id") == source_id
            for source in data["sources"]
            if isinstance(source, dict)
        ):
            data["sources"].append(
                {
                    "source_id": source_id,
                    "source_type": source_type,
                    "name": name,
                    "uri": uri,
                    "created_at_utc": now,
                    "updated_at_utc": now,
                }
            )

        delta: dict[str, Any] | None = None
        if (
            previous_version is not None
            and previous_version.get("version_hash") != version_hash
        ):
            previous_version["state"] = "superseded"
            previous_version["updated_at_utc"] = now
            delta = self.record_delta(
                data,
                from_version_id=str(previous_version.get("id")),
                to_version_id=version_id,
                delta_type="decision",
                summary="Auto-recorded canonical source update",
                impact="medium",
                risk="low",
                decision="superseded",
                source_id=source_id,
            )

        self.write_registry(data)
        return {
            "registry_path": str(self._registry_path),
            "version": entry,
            "delta": delta,
        }

    def list_versions(self) -> dict[str, Any]:
        """Return all known evidence versions."""
        data = self.load_registry()
        return {
            "registry_path": str(self._registry_path),
            "versions": data.get("versions", []),
        }

    def list_deltas(
        self,
        *,
        source_id: str | None = None,
        delta_type: str | None = None,
        decision: str | None = None,
    ) -> dict[str, Any]:
        """Return evidence deltas filtered by source, type, or decision."""
        if delta_type is not None:
            self._validate_delta_type(delta_type)
        if decision is not None:
            self._validate_delta_decision(decision)
        data = self.load_registry()
        deltas = [
            entry
            for entry in data.get("deltas", [])
            if isinstance(entry, dict)
            and (source_id is None or entry.get("source_id") == source_id)
            and (delta_type is None or entry.get("delta_type") == delta_type)
            and (decision is None or entry.get("decision") == decision)
        ]
        return {
            "registry_path": str(self._registry_path),
            "deltas": deltas,
        }

    def record_delta(
        self,
        data: dict[str, Any],
        *,
        from_version_id: str,
        to_version_id: str,
        delta_type: str,
        summary: str,
        impact: str,
        risk: str,
        decision: str,
        source_id: str | None,
    ) -> dict[str, Any]:
        """Append a delta row to a loaded registry payload."""
        self._validate_delta_type(delta_type)
        self._validate_delta_decision(decision)
        delta = {
            "id": self._next_delta_id(data),
            "from_version_id": from_version_id,
            "to_version_id": to_version_id,
            "delta_type": delta_type,
            "summary": summary,
            "impact": impact,
            "risk": risk,
            "decision": decision,
            "source_id": source_id,
            "created_at_utc": self._utc_now(),
        }
        data["deltas"].append(delta)
        return delta

    def record_explicit_delta(
        self,
        *,
        from_version_id: str,
        to_version_id: str,
        delta_type: str,
        summary: str,
        impact: str = "medium",
        risk: str = "medium",
        decision: str = "adapted",
    ) -> dict[str, Any]:
        """Create and persist a delta between two registered versions."""
        self._validate_delta_type(delta_type)
        self._validate_delta_decision(decision)
        data = self.load_registry()
        from_version = self._find_version(data, from_version_id)
        to_version = self._find_version(data, to_version_id)
        if from_version is None or to_version is None:
            raise ValueError("Both version IDs must exist before recording a delta.")

        delta = self.record_delta(
            data,
            from_version_id=from_version_id,
            to_version_id=to_version_id,
            delta_type=delta_type,
            summary=summary,
            impact=impact,
            risk=risk,
            decision=decision,
            source_id=(
                to_version.get("source_id") or from_version.get("source_id") or None
            ),
        )
        self.write_registry(data)
        return {"registry_path": str(self._registry_path), "delta": delta}

    def readiness(self, version_id: str) -> dict[str, Any]:
        """Return the deterministic readiness verdict for one version."""
        data = self.load_registry()
        version = self._find_version(data, version_id)
        if version is None:
            raise ValueError(f"Unknown version ID: {version_id}")
        return {
            "version_id": version_id,
            "registry_path": str(self._registry_path),
            "readiness": self.calculate_readiness(version),
        }

    async def sync_to_postgres(
        self,
        database_url: str,
        *,
        registry_key: str = "default",
    ) -> dict[str, object]:
        """Sync the current registry snapshot into PostgreSQL."""
        data = self.load_registry()
        conn = await asyncpg.connect(database_url)
        try:
            repo = EvidenceRegistryRepository(conn)
            counts = await repo.sync_snapshot(
                registry_key=registry_key,
                sources=data.get("sources", []),
                versions=data.get("versions", []),
                deltas=data.get("deltas", []),
            )
            return {
                "registry_path": str(self._registry_path),
                "registry_key": registry_key,
                "synced": {
                    "sources": counts.sources,
                    "versions": counts.versions,
                    "deltas": counts.deltas,
                },
            }
        finally:
            await conn.close()

    @staticmethod
    def calculate_readiness(entry: Mapping[str, Any]) -> dict[str, Any]:
        """Compute a readiness verdict from registry metadata."""
        confidence = float(entry.get("confidence") or 0.0)
        coverage = float(entry.get("coverage") or 0.0)
        critical_gaps = int(entry.get("critical_gaps") or 0)
        contradictions = int(entry.get("contradictions") or 0)
        user_answers_complete = bool(entry.get("user_answers_complete"))

        if contradictions > 0:
            verdict = "blocked"
            reason = "contradictions_present"
        elif critical_gaps > 0:
            verdict = "not_ready"
            reason = "critical_gaps_open"
        elif not user_answers_complete and coverage < 0.8:
            verdict = "blocked"
            reason = "missing_user_answers"
        elif confidence >= 0.8 and coverage >= 0.8:
            verdict = "ready"
            reason = "high_confidence_high_coverage"
        elif confidence >= 0.7 and coverage >= 0.7:
            verdict = "conditionally_ready"
            reason = "good_enough_with_caution"
        else:
            verdict = "not_ready"
            reason = "insufficient_confidence_or_coverage"

        return {
            "verdict": verdict,
            "reason": reason,
            "confidence": confidence,
            "coverage": coverage,
            "critical_gaps": critical_gaps,
            "contradictions": contradictions,
            "user_answers_complete": user_answers_complete,
        }

    def _latest_version_for_source(
        self,
        data: dict[str, Any],
        source_id: str | None,
    ) -> dict[str, Any] | None:
        """Return the latest version for a source when one exists."""
        if source_id is None:
            return None
        return next(
            (
                entry
                for entry in reversed(data.get("versions", []))
                if isinstance(entry, dict) and entry.get("source_id") == source_id
            ),
            None,
        )

    def _find_version(
        self,
        data: dict[str, Any],
        version_id: str,
    ) -> dict[str, Any] | None:
        """Look up a version by identifier."""
        return next(
            (
                entry
                for entry in data.get("versions", [])
                if isinstance(entry, dict) and entry.get("id") == version_id
            ),
            None,
        )

    def _next_version_id(self, data: dict[str, Any]) -> str:
        """Generate the next sequential evidence version ID."""
        max_value = 0
        for entry in data.get("versions", []):
            version_id = entry.get("id", "")
            if not isinstance(version_id, str) or not version_id.startswith("ev-"):
                continue
            suffix = version_id.removeprefix("ev-")
            if suffix.isdigit():
                max_value = max(max_value, int(suffix))
        return f"ev-{max_value + 1:04d}"

    def _next_delta_id(self, data: dict[str, Any]) -> str:
        """Generate the next sequential evidence delta ID."""
        max_value = 0
        for entry in data.get("deltas", []):
            delta_id = entry.get("id", "")
            if not isinstance(delta_id, str) or not delta_id.startswith("ed-"):
                continue
            suffix = delta_id.removeprefix("ed-")
            if suffix.isdigit():
                max_value = max(max_value, int(suffix))
        return f"ed-{max_value + 1:04d}"

    def _clamp(self, value: float, minimum: float, maximum: float) -> float:
        """Clamp a numeric value to the given range."""
        return max(minimum, min(maximum, value))

    def _validate_source_type(self, source_type: str) -> None:
        """Validate supported source types."""
        if source_type not in SOURCE_TYPES:
            raise ValueError(f"Unsupported source type: {source_type}")

    def _validate_version_state(self, state: str) -> None:
        """Validate supported version states."""
        if state not in VERSION_STATES:
            raise ValueError(f"Unsupported version state: {state}")

    def _validate_delta_type(self, delta_type: str) -> None:
        """Validate supported delta types."""
        if delta_type not in DELTA_TYPES:
            raise ValueError(f"Unsupported delta type: {delta_type}")

    def _validate_delta_decision(self, decision: str) -> None:
        """Validate supported delta decisions."""
        if decision not in DELTA_DECISIONS:
            raise ValueError(f"Unsupported delta decision: {decision}")

    def _utc_now(self) -> str:
        """Return the current UTC time as an ISO8601 string."""
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
