"""Persistence helpers for governance evidence."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import AuditEvent, PolicyVerdict


class JsonLinesAuditWriter:
    """Append governance events as one JSON object per line."""

    _REDACTED_TOKEN = "[REDACTED]"

    def __init__(self, path: Path) -> None:
        """Store the destination path."""
        self._path = path

    def append(self, event: AuditEvent) -> str:
        """Append a redacted event and return its durable reference."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = self._serialize(event)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")
        return event.event_id

    def _serialize(self, event: AuditEvent) -> dict[str, object]:
        """Convert an audit event to a JSON-serializable payload."""
        payload = asdict(event)
        snapshot = payload["intention_snapshot"]
        if isinstance(snapshot, dict):
            targets = snapshot.get("targets", [])
            if isinstance(targets, list):
                snapshot["targets"] = [
                    self._redact_target(target) for target in targets
                ]
        verdict = payload.get("verdict")
        if isinstance(verdict, PolicyVerdict):
            payload["verdict"] = verdict.value
        return payload

    def _redact_target(self, target: object) -> object:
        """Redact obvious secret targets before persistence."""
        if not isinstance(target, str):
            return target
        lowered = target.lower()
        if any(
            marker in lowered for marker in (".env", "secret", "credential", "token")
        ):
            return self._REDACTED_TOKEN
        return target
