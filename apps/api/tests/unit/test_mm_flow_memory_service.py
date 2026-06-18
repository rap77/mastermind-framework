"""Tests for MM-Flow memory-service runtime wiring."""

from __future__ import annotations

import pytest

from mastermind_cli.mm_flow import cli as mm_flow_cli


def test_build_memory_service_uses_shared_runtime_builder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MM-Flow should build its memory service through the shared env builder."""
    captured: dict[str, object] = {}

    class DummyStore:
        """Store stub returned by the runtime builder."""

    def fake_build_memory_store_from_env(
        database_url: str,
        *,
        enable_vector: bool,
        enable_index: bool,
    ) -> DummyStore:
        captured["database_url"] = database_url
        captured["enable_vector"] = enable_vector
        captured["enable_index"] = enable_index
        return DummyStore()

    monkeypatch.setattr(
        "mastermind_cli.mm_flow.cli.build_memory_store_from_env",
        fake_build_memory_store_from_env,
    )

    service = mm_flow_cli._build_memory_service("postgresql://memory-db")

    assert captured == {
        "database_url": "postgresql://memory-db",
        "enable_vector": False,
        "enable_index": True,
    }
    assert service._store.__class__.__name__ == "DummyStore"  # type: ignore[attr-defined]
