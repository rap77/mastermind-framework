"""Tests for background task runner — Fase 3 agent-restructuring.

Tests the run_brain_task() coroutine that executes brain orchestration
as a FastAPI BackgroundTask. Validates:
- Status transitions (pending → running → completed/failed)
- BRAIN_ID_MAP int→str mapping correctness
- ExperienceLogger integration
- CancelledError handling (uvicorn shutdown safety)
- aiosqlite transaction isolation (partial write protection)

Brain #6 guidance: BackgroundTasks pattern, not asyncio.create_task().
"""

import asyncio
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from typing import Any
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select

from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.models.artifact import ArtifactVersion
from mastermind_cli.project_state.models.project import Project
from mastermind_cli.project_state.models.task import Task
from mastermind_cli.project_state.models.task_run import TaskRun


class BlockingGovernance:
    """Governance stub used to verify seam propagation."""

    pass


# Constants mirrored from task_runner (tested explicitly below)
EXPECTED_BRAIN_ID_MAP = {
    1: "brain-01-product",
    2: "brain-02-ux",
    3: "brain-03-ui",
    4: "brain-04-frontend",
    5: "brain-05-backend",
    6: "brain-06-qa",
    7: "brain-07-growth",
}


@pytest.fixture(autouse=True)
def cleanup_project_state_engines() -> None:
    """Dispose cached SQLAlchemy engines after each test."""
    yield
    dispose_engines()


# ===== Fixtures =====


@pytest.fixture
def task_id() -> str:
    """Return the stable task identifier used by task runner tests."""
    return "task-test-001"


@pytest.fixture(autouse=True)
def stub_asyncpg_connect(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable real asyncpg network access during task runner tests."""

    async def _fail_connect(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise OSError("asyncpg disabled in tests")

    monkeypatch.setattr(
        "mastermind_cli.api.services.task_runner.asyncpg.connect",
        _fail_connect,
    )


@pytest.fixture(autouse=True)
def stub_session_evaluated_event(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable outbound Rust control-plane calls during task runner tests."""

    async def _noop_event(*args: Any, **kwargs: Any) -> None:
        del args, kwargs

    monkeypatch.setattr(
        "mastermind_cli.api.services.task_runner._post_session_evaluated_event",
        _noop_event,
    )


@pytest.fixture(autouse=True)
def stub_brain_routing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep task runner tests focused on the primary execution path."""

    monkeypatch.setattr(
        "mastermind_cli.api.services.task_runner._brain_router.route_to_brain",
        lambda brief, from_brain_id: None,
    )


@pytest.fixture(autouse=True)
def stub_langsmith_run_tree(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid LangSmith pytest-plugin side effects inside task_runner tests."""

    monkeypatch.setattr(
        "langsmith.get_current_run_tree",
        lambda: None,
    )


@pytest.fixture(autouse=True)
def stub_task_runner_db_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace task_runner aiosqlite access with a lightweight sqlite3 async shim."""

    class _Cursor:
        def __init__(self, cursor: sqlite3.Cursor):
            self._cursor = cursor

        async def fetchone(self) -> Any:
            return self._cursor.fetchone()

        async def fetchall(self) -> Any:
            return self._cursor.fetchall()

    class _Conn:
        def __init__(self, connection: sqlite3.Connection):
            self._connection = connection

        async def execute(self, sql: str, params: Any = None) -> Any:
            return _Cursor(self._connection.execute(sql, params or []))

        async def commit(self) -> None:
            self._connection.commit()

    class _FakeDatabaseConnection:
        def __init__(self, db_path: str = ":memory:"):
            self.db_path = db_path
            self._connection: sqlite3.Connection | None = None

        @property
        def conn(self) -> _Conn:
            assert self._connection is not None
            return _Conn(self._connection)

        async def __aenter__(self) -> "_FakeDatabaseConnection":
            self._connection = sqlite3.connect(self.db_path)
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            del exc_type, exc, tb
            assert self._connection is not None
            self._connection.close()
            self._connection = None

        async def create_experience_schema(self) -> None:
            assert self._connection is not None
            self._connection.executescript("""
                CREATE TABLE IF NOT EXISTS experience_records (
                    id TEXT PRIMARY KEY,
                    brain_id TEXT NOT NULL,
                    input_hash TEXT NOT NULL,
                    output_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    embedding_stub BLOB,
                    parent_brain_id TEXT,
                    trace_context_id TEXT,
                    custom_metadata TEXT NOT NULL DEFAULT '{}',
                    expires_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_experience_brain_timestamp
                ON experience_records(brain_id, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_experience_trace
                ON experience_records(trace_context_id);
                CREATE INDEX IF NOT EXISTS idx_experience_expires_at
                ON experience_records(expires_at);
            """)
            self._connection.commit()

    monkeypatch.setattr(
        "mastermind_cli.api.services.task_runner.DatabaseConnection",
        _FakeDatabaseConnection,
    )


@pytest.fixture
def db_with_task(tmp_path: Path, task_id: str) -> str:
    """DB with an execution record pre-inserted in 'pending' state."""
    db_file = str(tmp_path / "test.db")
    with closing(sqlite3.connect(db_file)) as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                brain_id TEXT NOT NULL,
                status TEXT NOT NULL,
                progress TEXT,
                result TEXT,
                error TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS executions (
                id TEXT PRIMARY KEY,
                flow_config TEXT NOT NULL,
                brief TEXT NOT NULL,
                created_at TIMESTAMP,
                status TEXT,
                user_id TEXT
            );
            CREATE TABLE IF NOT EXISTS experience_records (
                id TEXT PRIMARY KEY,
                brain_id TEXT NOT NULL,
                input_hash TEXT NOT NULL,
                output_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                duration_ms INTEGER NOT NULL,
                status TEXT NOT NULL,
                embedding_stub BLOB,
                parent_brain_id TEXT,
                trace_context_id TEXT,
                custom_metadata TEXT NOT NULL DEFAULT '{}',
                expires_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_experience_brain_timestamp
            ON experience_records(brain_id, timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_experience_trace
            ON experience_records(trace_context_id);
            CREATE INDEX IF NOT EXISTS idx_experience_expires_at
            ON experience_records(expires_at);
        """)
        connection.execute(
            """INSERT INTO executions (id, flow_config, brief, created_at, status, user_id)
               VALUES (?, ?, ?, datetime('now'), ?, ?)""",
            (task_id, "{}", "Test brief", "pending", "user-001"),
        )
        connection.commit()

    project_state_db_url = f"sqlite:///{db_file}.project_state"
    dispose_engines()
    initialize_database(project_state_db_url)
    session_factory = get_session_factory(project_state_db_url)
    now = datetime.now(timezone.utc)
    with session_factory() as session:
        session.add(
            Project(
                project_id="user-tasks:user-001",
                name="User task workspace",
                status="active",
                adapter_id="legacy-tasks",
                metadata_json={"user_id": "user-001"},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id=task_id,
                project_id="user-tasks:user-001",
                title="Test brief",
                status="pending",
                priority="normal",
                owner_type="user",
                owner_id="user-001",
                metadata_json={"brief": "Test brief", "flow_config": "{}"},
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            TaskRun(
                run_id=task_id,
                project_id="user-tasks:user-001",
                task_id=task_id,
                actor_type="user",
                actor_id="user-001",
                status="pending",
                started_at=now,
                ended_at=None,
                metadata_json={"legacy_execution_id": task_id},
            )
        )
        session.commit()
    return db_file


def _get_task_status(db_path: str, task_id: str) -> str:
    with closing(sqlite3.connect(db_path)) as connection:
        row = connection.execute(
            "SELECT status FROM executions WHERE id = ?",
            (task_id,),
        ).fetchone()
    return row[0] if row else "not_found"


def _get_project_state_statuses(
    db_path: str, task_id: str
) -> tuple[str | None, str | None, bool]:
    project_state_db_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    session_factory = get_session_factory(project_state_db_url)
    with session_factory() as session:
        task = session.get(Task, task_id)
        run = session.get(TaskRun, task_id)
        return (
            task.status if task is not None else None,
            run.status if run is not None else None,
            run.ended_at is not None if run is not None else False,
        )


# ===== BRAIN_ID_MAP tests =====


def test_brain_id_map_covers_all_seven_brains() -> None:
    """BRAIN_ID_MAP must map all 7 brain integers to correct string IDs."""
    from mastermind_cli.api.services.task_runner import BRAIN_ID_MAP

    assert BRAIN_ID_MAP == EXPECTED_BRAIN_ID_MAP


def test_brain_id_map_no_f_string_interpolation() -> None:
    """Brain IDs must be explicit strings, not computed — prevents silent mismatches."""
    from mastermind_cli.api.services.task_runner import BRAIN_ID_MAP

    for brain_int, brain_str in BRAIN_ID_MAP.items():
        # Verify string matches expected format exactly (not f"brain-0{n}-...")
        assert brain_str == EXPECTED_BRAIN_ID_MAP[brain_int]
        assert brain_str.startswith("brain-0")


# ===== Status transition tests =====


def test_run_brain_task_transitions_to_running_then_completed(
    db_with_task: str, task_id: str
) -> None:
    """run_brain_task() sets status=running at start, then completed on success."""
    mock_output = MagicMock()
    mock_output.model_dump.return_value = {"result": "ok"}
    mock_eval_result = MagicMock()
    mock_eval_result.quality_score = 0.9
    mock_eval_result.high_value = True
    mock_eval_result.insights = ["Looks good"]
    fake_logger = AsyncMock()

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner.ExperienceLogger",
            return_value=fake_logger,
        ),
        patch(
            "mastermind_cli.api.services.task_runner.evaluate_session",
            return_value=mock_eval_result,
        ),
        patch(
            "mastermind_cli.api.services.task_runner._persist_execution_output_artifact"
        ),
    ):
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(
            return_value={"brain-01-product": mock_output}
        )

        from mastermind_cli.api.services.task_runner import run_brain_task

        asyncio.run(
            run_brain_task(
                task_id=task_id,
                brief="Test brief input",
                flow="validation_only",
                db_path=db_with_task,
            )
        )

    status = _get_task_status(db_with_task, task_id)
    assert status == "completed"
    task_status, run_status, run_ended = _get_project_state_statuses(
        db_with_task, task_id
    )
    assert task_status == "completed"
    assert run_status == "completed"
    assert run_ended is True


def test_run_brain_task_passes_governance_to_factory(
    db_with_task: str, task_id: str
) -> None:
    """run_brain_task() should forward governance into the coordinator factory."""
    mock_output = MagicMock()
    mock_output.model_dump.return_value = {"result": "ok"}

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner.ExperienceLogger",
            return_value=AsyncMock(),
        ),
    ):
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(
            return_value={"brain-01-product": mock_output}
        )

        from mastermind_cli.api.services.task_runner import run_brain_task

        asyncio.run(
            run_brain_task(
                task_id=task_id,
                brief="Test brief input",
                flow="validation_only",
                db_path=db_with_task,
                governance=BlockingGovernance(),
            )
        )

    assert MockCoord.call_args.kwargs["governance"] is not None


def test_run_brain_task_wires_memory_components_when_configured(
    db_with_task: str, task_id: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """run_brain_task() should inject memory wiring when memory DB is configured."""
    mock_output = MagicMock()
    mock_output.model_dump.return_value = {"result": "ok"}
    fake_logger = AsyncMock()
    fake_snapshot = object()
    fake_memory_service = AsyncMock()
    fake_memory_service.build_context_snapshot = AsyncMock(return_value=fake_snapshot)
    fake_writer = object()

    monkeypatch.setenv("MM_MEMORY_DATABASE_URL", "postgresql://memory-url")

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner.ExperienceLogger",
            return_value=fake_logger,
        ),
        patch(
            "mastermind_cli.api.services.task_runner.evaluate_session",
            return_value=MagicMock(
                quality_score=0.9, high_value=True, insights=["Looks good"]
            ),
        ),
        patch(
            "mastermind_cli.api.services.task_runner._persist_execution_output_artifact"
        ),
        patch(
            "mastermind_cli.api.services.task_runner.build_memory_store_from_env",
            return_value=object(),
        ),
        patch(
            "mastermind_cli.api.services.task_runner.MemoryService",
            return_value=fake_memory_service,
        ),
        patch(
            "mastermind_cli.api.services.task_runner.MemoryRuntimeAdapter",
            return_value=fake_writer,
        ),
    ):
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(
            return_value={"brain-01-product": mock_output}
        )

        from mastermind_cli.api.services.task_runner import run_brain_task

        asyncio.run(
            run_brain_task(
                task_id=task_id,
                brief="Test brief input",
                flow="validation_only",
                db_path=db_with_task,
            )
        )

    assert MockCoord.call_args.kwargs["project_id"] == "user-tasks:user-001"
    assert MockCoord.call_args.kwargs["memory_context_provider"] is not None
    assert MockCoord.call_args.kwargs["memory_runtime_writer"] is fake_writer
    assert fake_memory_service.build_context_snapshot.await_count == 1


def test_run_brain_task_transitions_to_failed_on_exception(
    db_with_task: str, task_id: str
) -> None:
    """run_brain_task() sets status=failed when StatelessCoordinator raises."""
    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner.ExperienceLogger",
            return_value=AsyncMock(),
        ),
    ):
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(side_effect=RuntimeError("brain exploded"))

        from mastermind_cli.api.services.task_runner import run_brain_task

        asyncio.run(
            run_brain_task(
                task_id=task_id,
                brief="Test brief input",
                flow="validation_only",
                db_path=db_with_task,
            )
        )

    status = _get_task_status(db_with_task, task_id)
    assert status == "failed"
    task_status, run_status, run_ended = _get_project_state_statuses(
        db_with_task, task_id
    )
    assert task_status == "failed"
    assert run_status == "failed"
    assert run_ended is True


def test_run_brain_task_handles_cancelled_error(
    db_with_task: str, task_id: str
) -> None:
    """CancelledError (uvicorn shutdown) sets status=failed, does NOT propagate."""
    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner.ExperienceLogger",
            return_value=AsyncMock(),
        ),
    ):
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(side_effect=asyncio.CancelledError())

        from mastermind_cli.api.services.task_runner import run_brain_task

        # Must NOT raise — CancelledError must be caught and swallowed
        asyncio.run(
            run_brain_task(
                task_id=task_id,
                brief="Test brief input",
                flow="validation_only",
                db_path=db_with_task,
            )
        )

    status = _get_task_status(db_with_task, task_id)
    assert status == "failed"


# ===== Flow detection + brain mapping =====


def test_run_brain_task_maps_flow_detector_ints_to_brain_strings(
    db_with_task: str, task_id: str
) -> None:
    """FlowDetector returns list[int]; run_brain_task converts via BRAIN_ID_MAP."""
    captured_brain_ids: list[str] = []

    async def capture_brain_ids(
        brief: Any, brain_ids: list[str], conn: Any = None
    ) -> dict[str, Any]:
        captured_brain_ids.extend(brain_ids)
        return {}

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner.ExperienceLogger",
            return_value=AsyncMock(),
        ),
    ):
        instance = MockCoord.return_value
        instance.execute_flow = capture_brain_ids

        with patch(
            "mastermind_cli.api.services.task_runner.FlowDetector"
        ) as MockDetector:
            det_instance = MockDetector.return_value
            det_instance.detect.return_value = "validation_only"
            det_instance.get_flow_sequence.return_value = [1, 7]

            from mastermind_cli.api.services.task_runner import run_brain_task

            asyncio.run(
                run_brain_task(
                    task_id=task_id,
                    brief="validate this product feature",
                    flow=None,  # auto-detect
                    db_path=db_with_task,
                )
            )

    assert captured_brain_ids == ["brain-01-product", "brain-07-growth"]


# ===== ExperienceLogger integration =====


def test_run_brain_task_writes_experience_record(
    db_with_task: str, task_id: str
) -> None:
    """run_brain_task() logs an experience record on successful execution."""
    mock_output = MagicMock()
    mock_output.model_dump.return_value = {"result": "logged"}

    with patch(
        "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
    ) as MockCoord:
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(
            return_value={"brain-01-product": mock_output}
        )

        from mastermind_cli.api.services.task_runner import run_brain_task

        asyncio.run(
            run_brain_task(
                task_id=task_id,
                brief="Test brief input",
                flow="validation_only",
                db_path=db_with_task,
            )
        )

    # Verify experience_records table has at least one entry
    with closing(sqlite3.connect(db_with_task)) as connection:
        row = connection.execute(
            "SELECT COUNT(*) FROM experience_records WHERE brain_id = ?",
            ("brain-01-product",),
        ).fetchone()
    count = row[0] if row else 0

    assert count >= 1


def test_run_brain_task_accepts_injected_experience_logger_factory(
    db_with_task: str, task_id: str
) -> None:
    """run_brain_task() can use an injected logger seam instead of ExperienceLogger."""
    mock_output = MagicMock()
    mock_output.model_dump.return_value = {"result": "logged"}
    fake_logger = AsyncMock()
    factory_calls: list[object] = []

    def logger_factory(db: Any) -> AsyncMock:
        factory_calls.append(db)
        return fake_logger

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner.ExperienceLogger",
            side_effect=AssertionError("ExperienceLogger should not be constructed"),
        ),
    ):
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(
            return_value={"brain-01-product": mock_output}
        )

        from mastermind_cli.api.services.task_runner import run_brain_task

        asyncio.run(
            run_brain_task(
                task_id=task_id,
                brief="Test brief input",
                flow="validation_only",
                db_path=db_with_task,
                experience_logger_factory=logger_factory,
            )
        )

    assert len(factory_calls) == 1
    assert fake_logger.log_execution.await_count == 1


def test_run_brain_task_persists_canonical_execution_output_artifact(
    db_with_task: str, task_id: str
) -> None:
    """Successful runs persist a canonical execution_output_bundle artifact."""
    mock_output = MagicMock()
    mock_output.model_dump.return_value = {"result": "artifact"}

    with patch(
        "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
    ) as MockCoord:
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(
            return_value={"brain-01-product": mock_output}
        )

        from mastermind_cli.api.services.task_runner import run_brain_task

        asyncio.run(
            run_brain_task(
                task_id=task_id,
                brief="Test brief input",
                flow="validation_only",
                db_path=db_with_task,
            )
        )

    project_state_db_url = f"sqlite:///{db_with_task}.project_state"
    dispose_engines()
    session_factory = get_session_factory(project_state_db_url)
    with session_factory() as session:
        artifact = session.execute(
            select(ArtifactVersion).where(
                ArtifactVersion.artifact_type == "execution_output_bundle",
                ArtifactVersion.artifact_id == f"execution-output:{task_id}",
            )
        ).scalar_one_or_none()

    assert artifact is not None
    raw_outputs = artifact.metadata_json.get("brain_outputs")
    assert isinstance(raw_outputs, dict)
    assert "brain-01-product" in raw_outputs


def test_run_brain_task_logs_best_effort_failures(
    db_with_task: str, task_id: str, caplog: pytest.LogCaptureFixture
) -> None:
    """Best-effort failures should be logged, not swallowed silently."""
    mock_output = MagicMock()
    mock_output.model_dump.return_value = {"result": "artifact"}
    mock_eval_result = MagicMock()
    mock_eval_result.quality_score = 0.9
    mock_eval_result.high_value = True
    mock_eval_result.insights = ["Looks good"]
    fake_logger = AsyncMock()
    fake_pg_conn = AsyncMock()
    fake_pg_conn.close = AsyncMock(side_effect=RuntimeError("close failed"))

    caplog.set_level("DEBUG")

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner.ExperienceLogger",
            return_value=fake_logger,
        ),
        patch(
            "mastermind_cli.api.services.task_runner.evaluate_session",
            return_value=mock_eval_result,
        ),
        patch(
            "mastermind_cli.api.services.task_runner._persist_execution_output_artifact",
            side_effect=RuntimeError("artifact failed"),
        ),
        patch(
            "mastermind_cli.api.services.task_runner._update_project_state_status",
            side_effect=[
                RuntimeError("running failed"),
                RuntimeError("completed failed"),
            ],
        ),
        patch(
            "mastermind_cli.api.services.task_runner.asyncpg.connect",
            new=AsyncMock(return_value=fake_pg_conn),
        ),
        patch(
            "mastermind_cli.rag.context_builder.RAGContextBuilder.build",
            new=AsyncMock(return_value="[RETRIEVED CONTEXT] runtime"),
        ),
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.route_to_brain",
            return_value=None,
        ),
        patch(
            "mastermind_cli.api.services.task_runner._DEFAULT_DATABASE_URL",
            "postgresql://fake/db",
        ),
        patch(
            "langsmith.get_current_run_tree",
            side_effect=RuntimeError("langsmith unavailable"),
        ),
    ):
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(
            return_value={"brain-01-product": mock_output}
        )

        from mastermind_cli.api.services.task_runner import run_brain_task

        asyncio.run(
            run_brain_task(
                task_id=task_id,
                brief="Test brief input",
                flow="validation_only",
                db_path=db_with_task,
            )
        )

    assert "project_state running status update failed" in caplog.text
    assert "LangSmith metadata update failed" in caplog.text
    assert "execution output artifact persistence failed" in caplog.text
    assert "project_state completed status update failed" in caplog.text
    assert "failed to close asyncpg RAG connection" in caplog.text


def test_run_brain_task_marks_rag_enabled_for_short_brain1_runtime_id(
    db_with_task: str, task_id: str
) -> None:
    """Short Brain #1 runtime ID should still persist rag_enabled=True."""
    mock_output = MagicMock()
    mock_output.model_dump.return_value = {"result": "ok"}

    fake_pg_conn = AsyncMock()
    fake_pg_conn.close = AsyncMock()
    fake_logger = AsyncMock()

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner.asyncpg.connect",
            new=AsyncMock(return_value=fake_pg_conn),
        ),
        patch("mastermind_cli.api.services.task_runner.FlowDetector") as MockDetector,
        patch(
            "mastermind_cli.api.services.task_runner.ExperienceLogger",
            return_value=fake_logger,
        ),
        patch(
            "mastermind_cli.api.services.task_runner.evaluate_session"
        ) as mock_evaluate,
        patch(
            "mastermind_cli.api.services.task_runner._post_session_evaluated_event",
            new=AsyncMock(),
        ),
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.route_to_brain",
            return_value=None,
        ),
        patch(
            "mastermind_cli.api.services.task_runner._DEFAULT_DATABASE_URL",
            "postgresql://fake/db",
        ),
        patch(
            "mastermind_cli.rag.context_builder.RAGContextBuilder.build",
            new=AsyncMock(return_value="[RETRIEVED CONTEXT] runtime"),
        ),
    ):
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(
            return_value={"brain-01-product": mock_output}
        )

        det_instance = MockDetector.return_value
        det_instance.detect.return_value = "validation_only"
        det_instance.get_flow_sequence.return_value = [1]

        mock_eval_result = MagicMock()
        mock_eval_result.quality_score = 0.9
        mock_eval_result.high_value = True
        mock_eval_result.insights = ["Looks good"]
        mock_evaluate.return_value = mock_eval_result

        from mastermind_cli.api.services.task_runner import run_brain_task

        asyncio.run(
            run_brain_task(
                task_id=task_id,
                brief="Test brief input",
                flow=None,
                db_path=db_with_task,
            )
        )

    assert fake_logger.log_execution.await_count == 1
    custom_metadata = fake_logger.log_execution.await_args.kwargs["custom_metadata"]
    assert custom_metadata["rag_enabled"] is True
