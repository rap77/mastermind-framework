"""
Integration test for backend-switch-handler.py CLI — C2.19

Verifies complete-task-handler.py use case:
- At startup, with BACKEND-SWITCH-REQUIRED.json present:
  → ACTIVE_BACKEND changes to next provider
  → BACKEND-SWITCH-REQUIRED.json deleted
"""

import json
from pathlib import Path


HANDLER = Path(__file__).parent / "backend-switch-handler.py"


class TestBackendSwitchCLI:
    """C2.19: backend-switch-handler.py CLI integration."""

    def test_cli_applies_switch_and_deletes_signal(self, tmp_path, monkeypatch):
        """C2.19: handler called with switch file → ACTIVE_BACKEND changes + file deleted."""
        switch_file = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
        active_file = tmp_path / "ACTIVE-BACKEND.json"

        # Write the switch signal
        signal = {
            "current_backend": "z_ai",
            "next_backend": "openrouter",
            "reason": "token_depletion",
            "timestamp": "2026-05-13T10:00:00Z",
        }
        switch_file.write_text(json.dumps(signal))

        # Import and use the module directly (not subprocess to avoid path issues)
        import importlib.util

        spec = importlib.util.spec_from_file_location("backend_switch_handler", HANDLER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # Patch paths to use tmp_path
        mod.BACKEND_SWITCH_REQUIRED_PATH = switch_file
        mod.ACTIVE_BACKEND_PATH = active_file
        mod._PLANNING_DIR = tmp_path

        # Apply the switch (simulates what complete-task-handler.py calls at startup)
        switched = mod.check_and_apply_switch()

        # C2.19 assertions
        assert switched is True, "Should have applied switch"
        assert not switch_file.exists(), "Signal file should be deleted"
        assert active_file.exists(), "ACTIVE-BACKEND.json should be written"

        data = json.loads(active_file.read_text())
        assert (
            data["active_backend"] == "openrouter"
        ), "Active backend should switch to openrouter"

    def test_cli_no_switch_file_no_change(self, tmp_path):
        """C2.19: no switch file → active backend unchanged."""
        active_file = tmp_path / "ACTIVE-BACKEND.json"
        active_file.write_text(json.dumps({"active_backend": "claude"}))

        import importlib.util

        spec = importlib.util.spec_from_file_location("backend_switch_handler", HANDLER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.BACKEND_SWITCH_REQUIRED_PATH = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
        mod.ACTIVE_BACKEND_PATH = active_file
        mod._PLANNING_DIR = tmp_path

        switched = mod.check_and_apply_switch()

        assert switched is False
        # Active backend unchanged
        data = json.loads(active_file.read_text())
        assert data["active_backend"] == "claude"

    def test_repeated_calls_idempotent_without_switch_file(self, tmp_path):
        """C2.19: multiple calls without switch file → ACTIVE-BACKEND.json stable."""
        import importlib.util

        spec = importlib.util.spec_from_file_location("backend_switch_handler", HANDLER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.BACKEND_SWITCH_REQUIRED_PATH = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
        mod.ACTIVE_BACKEND_PATH = tmp_path / "ACTIVE-BACKEND.json"
        mod._PLANNING_DIR = tmp_path

        # First call creates ACTIVE-BACKEND.json
        mod.check_and_apply_switch()
        data1 = json.loads((tmp_path / "ACTIVE-BACKEND.json").read_text())

        # Second call — same backend
        mod.check_and_apply_switch()
        data2 = json.loads((tmp_path / "ACTIVE-BACKEND.json").read_text())

        assert data1["active_backend"] == data2["active_backend"] == "claude"
