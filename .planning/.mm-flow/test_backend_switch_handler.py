"""
Tests for backend-switch-handler.py — C2.14 + C2.15

Verifies:
- C2.14: BACKEND-SWITCH-REQUIRED.json triggers ACTIVE_BACKEND update + file deletion
- C2.15: ACTIVE-BACKEND.json is written with active backend as source of truth
"""

import json
from pathlib import Path


# We need to mock the path constants before importing the module
# so tests use tmp_path instead of real .planning/ dir.


def _load_handler(monkeypatch, tmp_path):
    """Import backend-switch-handler with patched paths."""
    handler_path = Path(__file__).parent / "backend-switch-handler.py"

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "backend_switch_handler", handler_path
    )
    mod = importlib.util.module_from_spec(spec)

    # Patch module-level path constants after import
    spec.loader.exec_module(mod)
    mod.BACKEND_SWITCH_REQUIRED_PATH = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
    mod.ACTIVE_BACKEND_PATH = tmp_path / "ACTIVE-BACKEND.json"
    mod._PLANNING_DIR = tmp_path
    return mod


class TestReadActiveBackend:
    """C2.15: read_active_backend defaults to 'claude' if file missing."""

    def test_defaults_to_claude_if_missing(self, monkeypatch, tmp_path):
        mod = _load_handler(monkeypatch, tmp_path)
        assert mod.read_active_backend() == "claude"

    def test_reads_from_active_backend_json(self, monkeypatch, tmp_path):
        mod = _load_handler(monkeypatch, tmp_path)
        (tmp_path / "ACTIVE-BACKEND.json").write_text(
            json.dumps({"active_backend": "openrouter"})
        )
        assert mod.read_active_backend() == "openrouter"


class TestWriteActiveBackend:
    """C2.15: write_active_backend writes ACTIVE-BACKEND.json."""

    def test_writes_active_backend_json(self, monkeypatch, tmp_path):
        mod = _load_handler(monkeypatch, tmp_path)
        mod.write_active_backend("z_ai", "initial_setup")

        data = json.loads((tmp_path / "ACTIVE-BACKEND.json").read_text())
        assert data["active_backend"] == "z_ai"
        assert data["reason"] == "initial_setup"
        assert "updated_at" in data

    def test_overwrites_existing_file(self, monkeypatch, tmp_path):
        mod = _load_handler(monkeypatch, tmp_path)
        (tmp_path / "ACTIVE-BACKEND.json").write_text(
            json.dumps({"active_backend": "claude"})
        )
        mod.write_active_backend("openrouter", "switch")

        data = json.loads((tmp_path / "ACTIVE-BACKEND.json").read_text())
        assert data["active_backend"] == "openrouter"


class TestGetNextBackend:
    """C2.14: get_next_backend returns next in priority order z_ai→openrouter→claude."""

    def test_z_ai_next_is_openrouter(self, monkeypatch, tmp_path):
        mod = _load_handler(monkeypatch, tmp_path)
        assert mod.get_next_backend("z_ai") == "openrouter"

    def test_openrouter_next_is_claude(self, monkeypatch, tmp_path):
        mod = _load_handler(monkeypatch, tmp_path)
        assert mod.get_next_backend("openrouter") == "claude"

    def test_claude_has_no_next(self, monkeypatch, tmp_path):
        mod = _load_handler(monkeypatch, tmp_path)
        assert mod.get_next_backend("claude") is None

    def test_unknown_backend_returns_none(self, monkeypatch, tmp_path):
        mod = _load_handler(monkeypatch, tmp_path)
        assert mod.get_next_backend("unknown_provider") is None


class TestCheckAndApplySwitch:
    """C2.14: check_and_apply_switch handles BACKEND-SWITCH-REQUIRED.json."""

    def test_no_switch_file_returns_false(self, monkeypatch, tmp_path):
        mod = _load_handler(monkeypatch, tmp_path)
        result = mod.check_and_apply_switch()
        assert result is False

    def test_switch_applied_updates_active_backend(self, monkeypatch, tmp_path):
        """C2.14: switch file present → ACTIVE-BACKEND.json updated."""
        mod = _load_handler(monkeypatch, tmp_path)
        signal = {
            "current_backend": "z_ai",
            "next_backend": "openrouter",
            "reason": "token_depletion",
            "timestamp": "2026-05-13T10:00:00Z",
        }
        (tmp_path / "BACKEND-SWITCH-REQUIRED.json").write_text(json.dumps(signal))

        result = mod.check_and_apply_switch()

        assert result is True
        data = json.loads((tmp_path / "ACTIVE-BACKEND.json").read_text())
        assert data["active_backend"] == "openrouter"

    def test_switch_deletes_signal_file(self, monkeypatch, tmp_path):
        """C2.14: signal file is deleted after switch."""
        mod = _load_handler(monkeypatch, tmp_path)
        signal = {
            "current_backend": "z_ai",
            "next_backend": "openrouter",
            "reason": "token_depletion",
            "timestamp": "2026-05-13T10:00:00Z",
        }
        switch_file = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
        switch_file.write_text(json.dumps(signal))

        mod.check_and_apply_switch()

        assert not switch_file.exists(), "Signal file should be deleted after switch"

    def test_no_switch_file_creates_active_backend_json(self, monkeypatch, tmp_path):
        """C2.15: ACTIVE-BACKEND.json created if missing even without switch."""
        mod = _load_handler(monkeypatch, tmp_path)
        assert not (tmp_path / "ACTIVE-BACKEND.json").exists()

        mod.check_and_apply_switch()

        assert (tmp_path / "ACTIVE-BACKEND.json").exists()

    def test_switch_without_next_backend_in_file_uses_priority(
        self, monkeypatch, tmp_path
    ):
        """C2.14: if next_backend absent in signal, use priority order."""
        mod = _load_handler(monkeypatch, tmp_path)
        signal = {
            "current_backend": "openrouter",
            # no next_backend field
            "reason": "token_depletion",
        }
        (tmp_path / "BACKEND-SWITCH-REQUIRED.json").write_text(json.dumps(signal))

        mod.check_and_apply_switch()

        data = json.loads((tmp_path / "ACTIVE-BACKEND.json").read_text())
        assert data["active_backend"] == "claude"
