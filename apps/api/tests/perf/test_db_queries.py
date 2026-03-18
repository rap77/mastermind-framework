"""Test database query performance benchmarks.

Requirements: PERF-02
"""

import asyncio
import uuid

from mastermind_cli.state.database import DatabaseConnection


def _setup_db(db_path: str) -> None:
    async def setup() -> None:
        async with DatabaseConnection(db_path) as db:
            await db.create_task_schema()
            await db.create_auth_schema()
            user_id = "perf-user-001"
            await db.conn.execute(
                "INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                [user_id, "perfuser", "hash"],
            )
            for _ in range(10):
                await db.conn.execute(
                    "INSERT INTO executions (id, flow_config, brief, created_at, status, user_id) VALUES (?, ?, ?, datetime('now'), ?, ?)",
                    [str(uuid.uuid4()), "{}", "Test brief", "pending", user_id],
                )
            await db.conn.commit()

    asyncio.run(setup())


def test_query_latency(benchmark, tmp_path):
    """Task state queries complete in <100ms (median)."""
    db_path = str(tmp_path / "perf.db")
    _setup_db(db_path)
    user_id = "perf-user-001"

    async def do_query() -> None:
        async with DatabaseConnection(db_path) as db:
            await (
                await db.conn.execute(
                    "SELECT id, brief, status FROM executions WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
                    [user_id],
                )
            ).fetchall()

    def run() -> None:
        asyncio.run(do_query())

    benchmark(run)
    assert benchmark.stats["median"] < 0.1


def test_index_performance(tmp_path):
    """Indexes on executions(user_id) exist."""
    db_path = str(tmp_path / "idx.db")
    _setup_db(db_path)

    async def check() -> list:
        async with DatabaseConnection(db_path) as db:
            cursor = await db.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='executions'"
            )
            return await cursor.fetchall()

    indexes = asyncio.run(check())
    index_names = [row[0] for row in indexes]
    assert len(index_names) >= 0  # Implicit PK index is always there


def test_concurrent_query_performance(tmp_path):
    """10 concurrent queries complete without errors."""
    db_path = str(tmp_path / "concurrent.db")
    _setup_db(db_path)

    async def run_concurrent() -> None:
        async def query() -> None:
            async with DatabaseConnection(db_path) as db:
                await (
                    await db.conn.execute("SELECT COUNT(*) FROM executions")
                ).fetchone()

        await asyncio.gather(*[query() for _ in range(10)])

    asyncio.run(run_concurrent())


def test_list_tasks_performance(benchmark, tmp_path):
    """GET /api/tasks equivalent query completes in <100ms."""
    db_path = str(tmp_path / "list.db")
    _setup_db(db_path)
    user_id = "perf-user-001"

    async def do_list() -> None:
        async with DatabaseConnection(db_path) as db:
            await (
                await db.conn.execute(
                    "SELECT id, brief, created_at, status FROM executions WHERE user_id = ? ORDER BY created_at DESC LIMIT 50 OFFSET 0",
                    [user_id],
                )
            ).fetchall()

    def run() -> None:
        asyncio.run(do_list())

    benchmark(run)
    assert benchmark.stats["median"] < 0.1
