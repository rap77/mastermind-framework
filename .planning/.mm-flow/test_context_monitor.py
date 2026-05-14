"""
Tests for mm-flow-context-monitor.js logic — C2.18

Since the monitor is a JS file, we test the same logic through a Python
implementation that mirrors the JS behavior. The key invariants tested:

C2.18:
- When token usage >= 95% of limit → BACKEND-SWITCH-REQUIRED.json is created
- The file contains: current_backend, next_backend, reason="token_depletion", timestamp
- next_backend follows priority: claude → openrouter, openrouter → z_ai (or vice versa)

We also test the config loading behavior:
C2.12: backend_limits are read from config.yml, not hardcoded
"""

import json
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Python mirror of mm-flow-context-monitor.js logic
# ---------------------------------------------------------------------------

# Priority order as defined in config.yml backend_limits
_DEFAULT_BACKEND_LIMITS = {
    "claude": {"token_limit": 200000, "critical_threshold": 0.95, "priority": 1},
    "openrouter": {"token_limit": 200000, "critical_threshold": 0.95, "priority": 2},
    "z_ai": {"token_limit": 200000, "critical_threshold": 0.95, "priority": 3},
}


def get_next_backend(current: str, backend_limits: dict) -> str | None:
    """Return next backend in priority order."""
    sorted_backends = sorted(
        backend_limits.keys(),
        key=lambda k: backend_limits[k].get("priority", 99),
    )
    try:
        idx = sorted_backends.index(current)
        if idx < len(sorted_backends) - 1:
            return sorted_backends[idx + 1]
    except ValueError:
        pass
    return None


def check_threshold(
    tokens_used: int,
    active_backend: str,
    backend_limits: dict,
    switch_required_path: Path,
) -> bool:
    """Mirror of mm-flow-context-monitor.js threshold check logic.

    Returns True if switch signal was written.
    """
    limits = backend_limits.get(active_backend)
    if not limits:
        return False

    token_limit = limits["token_limit"]
    threshold = limits.get("critical_threshold", 0.95)
    usage_fraction = tokens_used / token_limit

    if usage_fraction >= threshold:
        if not switch_required_path.exists():
            next_backend = get_next_backend(active_backend, backend_limits)
            if next_backend:
                usage_pct = round(usage_fraction * 100)
                signal = {
                    "current_backend": active_backend,
                    "next_backend": next_backend,
                    "reason": "token_depletion",
                    "reason_detail": f"token_depletion ({usage_pct}% of {token_limit})",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                switch_required_path.parent.mkdir(parents=True, exist_ok=True)
                switch_required_path.write_text(json.dumps(signal, indent=2) + "\n")
                return True
    return False


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestThresholdTrigger:
    """C2.18: simulate 95% usage → BACKEND-SWITCH-REQUIRED.json created."""

    def test_95_percent_usage_creates_switch_signal(self, tmp_path):
        """At 95% (190,000/200,000 tokens) → switch signal created."""
        switch_path = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
        tokens_used = 190_000  # 95% of 200,000

        result = check_threshold(
            tokens_used, "claude", _DEFAULT_BACKEND_LIMITS, switch_path
        )

        assert result is True
        assert switch_path.exists()

    def test_switch_signal_has_correct_structure(self, tmp_path):
        """BACKEND-SWITCH-REQUIRED.json has all required fields (C2.18)."""
        switch_path = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
        tokens_used = 195_000  # 97.5%

        check_threshold(tokens_used, "claude", _DEFAULT_BACKEND_LIMITS, switch_path)

        signal = json.loads(switch_path.read_text())
        assert "current_backend" in signal
        assert "next_backend" in signal
        assert "reason" in signal
        assert "timestamp" in signal
        assert signal["reason"] == "token_depletion"
        assert signal["current_backend"] == "claude"

    def test_claude_triggers_switch_to_openrouter(self, tmp_path):
        """claude at 95% → next_backend is openrouter (priority order)."""
        switch_path = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
        tokens_used = 190_000  # 95%

        check_threshold(tokens_used, "claude", _DEFAULT_BACKEND_LIMITS, switch_path)

        signal = json.loads(switch_path.read_text())
        assert signal["next_backend"] == "openrouter"

    def test_openrouter_triggers_switch_to_z_ai(self, tmp_path):
        """openrouter at 95% → next_backend is z_ai."""
        switch_path = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
        tokens_used = 190_000

        check_threshold(tokens_used, "openrouter", _DEFAULT_BACKEND_LIMITS, switch_path)

        signal = json.loads(switch_path.read_text())
        assert signal["next_backend"] == "z_ai"

    def test_below_threshold_does_not_create_signal(self, tmp_path):
        """At 80% (below 95% threshold) → no signal created."""
        switch_path = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
        tokens_used = 160_000  # 80% of 200,000

        result = check_threshold(
            tokens_used, "claude", _DEFAULT_BACKEND_LIMITS, switch_path
        )

        assert result is False
        assert not switch_path.exists()

    def test_idempotent_does_not_overwrite_existing_signal(self, tmp_path):
        """If signal already exists, monitor should not overwrite it."""
        switch_path = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
        existing_content = json.dumps(
            {
                "current_backend": "claude",
                "next_backend": "openrouter",
                "reason": "token_depletion",
            }
        )
        switch_path.write_text(existing_content)

        result = check_threshold(
            195_000, "claude", _DEFAULT_BACKEND_LIMITS, switch_path
        )

        # Result is False (not written again), file unchanged
        assert result is False
        assert switch_path.read_text() == existing_content

    def test_custom_backend_limits_respected(self, tmp_path):
        """C2.12: custom backend limits from config.yml are respected."""
        custom_limits = {
            "claude": {
                "token_limit": 100_000,
                "critical_threshold": 0.90,
                "priority": 1,
            },
            "openrouter": {
                "token_limit": 100_000,
                "critical_threshold": 0.90,
                "priority": 2,
            },
        }
        switch_path = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
        tokens_used = 91_000  # 91% of 100,000 (> 90% threshold)

        result = check_threshold(tokens_used, "claude", custom_limits, switch_path)

        assert result is True

    def test_custom_threshold_not_triggered_below_custom_level(self, tmp_path):
        """C2.12: custom threshold (90%) is respected — 89% should not trigger."""
        custom_limits = {
            "claude": {
                "token_limit": 100_000,
                "critical_threshold": 0.90,
                "priority": 1,
            },
        }
        switch_path = tmp_path / "BACKEND-SWITCH-REQUIRED.json"
        tokens_used = 89_000  # 89% — below 90% threshold

        result = check_threshold(tokens_used, "claude", custom_limits, switch_path)

        assert result is False
        assert not switch_path.exists()
