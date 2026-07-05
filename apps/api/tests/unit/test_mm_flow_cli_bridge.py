"""Tests for MM-Flow CLI integration with the planning bridge adapter."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from mastermind_cli.mm_flow import cli as mm_flow_cli
from mastermind_cli.mm_flow.config_loader import HarnessLibraryConfig, MMFlowConfig
from mastermind_cli.mm_flow.config_loader import BrainRoutingRule, ModelProfile


class _FakeTransaction:
    async def __aenter__(self) -> "_FakeTransaction":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        del exc_type, exc, tb
        return False


class _FakeConnection:
    def __init__(self, update_status: str = "UPDATE 1") -> None:
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.closed = False
        self._update_status = update_status

    def transaction(self) -> _FakeTransaction:
        return _FakeTransaction()

    async def execute(self, sql: str, *args: object) -> str:
        self.executed.append((sql, args))
        if sql.lstrip().upper().startswith("UPDATE"):
            return self._update_status
        return ""

    async def close(self) -> None:
        self.closed = True


def _minimal_config(enabled: bool = False) -> MMFlowConfig:
    """Build a minimal config object for CLI helper tests."""
    return MMFlowConfig(
        model_profiles={
            "quality": ModelProfile(model="anthropic:test", use_when="test"),
            "balanced": ModelProfile(model="anthropic:test", use_when="test"),
            "budget": ModelProfile(model="anthropic:test", use_when="test"),
        },
        brain_routing={
            "EXECUTION_WAVE": BrainRoutingRule(
                brains=[7],
                parallel=False,
            )
        },
        verification_gates={},
        providers={},
        harness_library=HarnessLibraryConfig(
            enabled=enabled,
            path=".mm-flow/harness-library",
            bundle_output_path=".run-bundles",
        ),
    )


def _write_cli_harness_library(root: Path) -> None:
    """Write a small Agent Harness library for CLI helper tests."""
    role = root / "roles" / "implementation-lead"
    role.mkdir(parents=True)
    (role / "HARNESS.md").write_text(
        "---\nname: Implementation Lead\ndescription: Implement safely.\n---\n",
        encoding="utf-8",
    )
    (role / ".leaf-detectors").write_text("skill=SKILL.md\n", encoding="utf-8")
    skill = root / "shared-skills" / "codebase-scan"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: Codebase Scan\ndescription: Scan codebase.\n---\n",
        encoding="utf-8",
    )
    (root / "registry.yaml").write_text(
        "harnesses:\n"
        "  - id: implementation-lead\n"
        "    path: roles/implementation-lead\n"
        "    type: role\n"
        "    domains: [software]\n"
        "    phases: [implementation]\n"
        "    outputs: [artifact]\n"
        "    supported_loops: [goal-loop]\n"
        "    skills: [codebase-scan]\n"
        "skills:\n"
        "  - id: codebase-scan\n"
        "    path: shared-skills/codebase-scan\n"
        "    domains: [software]\n"
        "    phases: [implementation]\n",
        encoding="utf-8",
    )


def _write_cli_routing_cases(path: Path) -> None:
    """Write routing cases that match the CLI harness library."""
    path.write_text(
        "schema_version: '1'\n"
        "routing_cases:\n"
        "  - case_id: implementation-change\n"
        "    prompt: Implement a safe code change\n"
        "    objective_profile:\n"
        "      objective_id: obj-001\n"
        "      domain: software\n"
        "      phase: implementation\n"
        "      output_type: artifact\n"
        "      complexity: medium\n"
        "      risk_level: medium\n"
        "      verifiability: medium\n"
        "      requires_write: true\n"
        "      requires_fresh_context: false\n"
        "      requires_memory: false\n"
        "      requires_mcp: false\n"
        "      requires_review: false\n"
        "      requires_recovery: false\n"
        "    expected_primary_harness: implementation-lead\n"
        "    expected_supporting_harnesses: []\n"
        "    expected_skills: [codebase-scan]\n"
        "    forbidden_skills: []\n"
        "    max_context_budget: 4000\n",
        encoding="utf-8",
    )


def _write_enabled_harness_config(root: Path) -> None:
    """Write MM-Flow config that enables the local harness library."""
    config_dir = root / ".planning" / ".mm-flow"
    config_dir.mkdir(parents=True)
    (config_dir / "config.yml").write_text(
        "harness_library:\n  enabled: true\n",
        encoding="utf-8",
    )


def test_build_multi_harness_pipeline_respects_disabled_config(tmp_path: Path) -> None:
    """Disabled harness library config should keep legacy execution unchanged."""
    assert (
        mm_flow_cli._build_multi_harness_pipeline(tmp_path, _minimal_config()) is None
    )


def test_build_multi_harness_pipeline_from_enabled_config(tmp_path: Path) -> None:
    """Enabled config should build a pipeline from `.mm-flow/harness-library`."""
    _write_cli_harness_library(tmp_path / ".mm-flow" / "harness-library")

    pipeline = mm_flow_cli._build_multi_harness_pipeline(
        tmp_path,
        _minimal_config(enabled=True),
    )

    assert pipeline is not None


def test_evaluate_harness_routing_cases_from_enabled_config(tmp_path: Path) -> None:
    """CLI helper should evaluate routing cases from the configured harness library."""
    library_root = tmp_path / ".mm-flow" / "harness-library"
    _write_cli_harness_library(library_root)
    _write_cli_routing_cases(library_root / "routing-cases.yaml")

    report = mm_flow_cli._evaluate_harness_routing_cases(
        tmp_path,
        _minimal_config(enabled=True),
        cases_path=None,
    )

    assert report.passed is True
    assert report.schema_version == "1"
    assert report.case_results[0].case_id == "implementation-change"


def test_harness_routing_check_command_outputs_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """harness-routing-check should print a JSON report."""
    library_root = tmp_path / ".mm-flow" / "harness-library"
    _write_cli_harness_library(library_root)
    _write_cli_routing_cases(library_root / "routing-cases.yaml")
    _write_enabled_harness_config(tmp_path)
    monkeypatch.chdir(tmp_path)

    mm_flow_cli.harness_routing_check.callback(  # type: ignore[attr-defined]
        config_path=None,
        cases_path=None,
    )

    captured = capsys.readouterr()
    assert '"passed": true' in captured.out
    assert '"case_id": "implementation-change"' in captured.out


def test_run_phase_in_progress_invokes_executor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """run-phase --start should build an executor and call execute_harness_run."""
    from mastermind_cli.mm_flow.integrated_run import (
        IntegratedRun,
        ValidationCheck,
        ValidationReport,
    )
    from mastermind_cli.mm_flow.planning_bridge import HarnessRequest

    fake_conn = _FakeConnection()
    executor_calls: list[dict[str, object]] = []
    runtime_state_calls: list[tuple[object, ...]] = []

    class FakeExecutor:
        def __init__(self, **_: object) -> None:
            pass

        async def execute_harness_run(self, **kwargs: object) -> IntegratedRun:
            executor_calls.append(kwargs)
            return IntegratedRun(
                project_id="proj-001",
                request=HarnessRequest(
                    project_name="Project Alpha",
                    design_objective="alpha-v1",
                    operational_objective="alpha-v1",
                    active_uow="UOW-1",
                    project_root=Path("/tmp/project-alpha"),
                    constraints=(),
                    expected_outputs=(),
                    required_checks=(),
                ),
                memory_snapshot=None,
                runtime_result=None,
                memory_write=None,
                archive_record=None,
                warnings=(),
                validation=ValidationReport(
                    passed=True,
                    checks=(
                        ValidationCheck(
                            check_id="manifest_present",
                            label="Project manifest fields present",
                            passed=True,
                        ),
                    ),
                    warnings=(),
                ),
            )

    def fake_build_memory_store_from_env(
        database_url: str, enable_vector: bool, enable_index: bool
    ) -> SimpleNamespace:
        del database_url, enable_vector, enable_index
        return SimpleNamespace()

    def fake_write_runtime_state(*args: object) -> None:
        runtime_state_calls.append(args)

    async def fake_connect(database_url: str) -> _FakeConnection:
        del database_url
        return fake_conn

    monkeypatch.setenv("DATABASE_URL", "postgresql://example.test/db")
    monkeypatch.setattr(mm_flow_cli.asyncpg, "connect", fake_connect)
    monkeypatch.setattr(
        mm_flow_cli, "build_memory_store_from_env", fake_build_memory_store_from_env
    )
    monkeypatch.setattr(mm_flow_cli, "_write_runtime_state", fake_write_runtime_state)
    monkeypatch.setattr(mm_flow_cli, "HarnessRunExecutor", FakeExecutor)

    mm_flow_cli.run_phase.callback(  # type: ignore[attr-defined]
        phase=21,
        brief="Implement and design a migration plan",
        brain_ids="brain-01-product-strategy,brain-03-ui-design",
        status="in_progress",
        summary="Alpha slice 6 run.",
        tokens=0,
        commit=None,
    )

    assert len(executor_calls) == 1
    call = executor_calls[0]
    assert call["status"] == "in_progress"
    assert call["brain_ids"] == ("brain-01-product-strategy", "brain-03-ui-design")
    assert call["summary"] == "Alpha slice 6 run."
    assert len(runtime_state_calls) == 1
    assert runtime_state_calls[0][2] == "EXECUTION_WAVE"
    assert fake_conn.closed is True


def test_run_phase_completed_archives_bridge_status(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """run-phase --complete should trigger archive path on the bridge and reuse the started execution_id."""

    from mastermind_cli.mm_flow.integrated_run import (
        IntegratedRun,
        ValidationCheck,
        ValidationReport,
    )
    from mastermind_cli.mm_flow.planning_bridge import (
        ArchiveRecord,
        HarnessRequest,
    )

    fake_conn = _FakeConnection()
    fake_conn.executed.append(("__seeded_in_progress__", ("exec-aaaa-1111", 21)))
    executor_calls: list[dict[str, object]] = []
    runtime_state_calls: list[tuple[object, ...]] = []
    started_execution_id = "exec-aaaa-1111"
    runtime_state_dir = tmp_path / ".planning" / ".mm-flow"
    runtime_state_dir.mkdir(parents=True, exist_ok=True)
    (runtime_state_dir / "runtime-state.json").write_text(
        '{"execution_id": "' + started_execution_id + '"}',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    class FakeExecutor:
        def __init__(self, **_: object) -> None:
            pass

        async def execute_harness_run(self, **kwargs: object) -> IntegratedRun:
            executor_calls.append(kwargs)
            return IntegratedRun(
                project_id="proj-001",
                request=HarnessRequest(
                    project_name="Project Alpha",
                    design_objective="alpha-v1",
                    operational_objective="alpha-v1",
                    active_uow="UOW-1",
                    project_root=Path("/tmp/project-alpha"),
                    constraints=(),
                    expected_outputs=(),
                    required_checks=(),
                ),
                memory_snapshot=None,
                runtime_result=None,
                memory_write=None,
                archive_record=ArchiveRecord(
                    objective="alpha-v1",
                    uow="UOW-1",
                    summary="Alpha slice 6 closed.",
                    archived_at=datetime.now(timezone.utc).isoformat(),
                ),
                warnings=(),
                validation=ValidationReport(
                    passed=True,
                    checks=(
                        ValidationCheck(
                            check_id="manifest_present",
                            label="Project manifest fields present",
                            passed=True,
                        ),
                    ),
                    warnings=(),
                ),
            )

    def fake_write_runtime_state(*args: object) -> None:
        runtime_state_calls.append(args)

    def fake_build_memory_store_from_env(
        database_url: str, enable_vector: bool, enable_index: bool
    ) -> SimpleNamespace:
        del database_url, enable_vector, enable_index
        return SimpleNamespace()

    monkeypatch.setenv("DATABASE_URL", "postgresql://example.test/db")
    monkeypatch.setattr(
        mm_flow_cli.asyncpg, "connect", lambda url: _async_return(fake_conn)
    )
    monkeypatch.setattr(
        mm_flow_cli, "build_memory_store_from_env", fake_build_memory_store_from_env
    )
    monkeypatch.setattr(mm_flow_cli, "_write_runtime_state", fake_write_runtime_state)
    monkeypatch.setattr(mm_flow_cli, "HarnessRunExecutor", FakeExecutor)

    mm_flow_cli.run_phase.callback(  # type: ignore[attr-defined]
        phase=21,
        brief="Implement and design a migration plan",
        brain_ids="brain-01-product-strategy",
        status="completed",
        summary="Alpha slice 6 closed.",
        tokens=42,
        commit="abc123",
    )

    assert len(executor_calls) == 1
    assert executor_calls[0]["status"] == "completed"
    assert executor_calls[0]["verification_outcome"] == "passed"
    assert len(runtime_state_calls) == 1
    assert runtime_state_calls[0][0] == started_execution_id
    assert runtime_state_calls[0][2] == "COMPLETED"
    update_sql, update_args = fake_conn.executed[-1]
    assert "UPDATE phase_executions" in update_sql
    assert update_args[0] == started_execution_id
    assert fake_conn.closed is True


async def _async_return(value: object) -> object:
    return value
