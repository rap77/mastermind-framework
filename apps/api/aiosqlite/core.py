# mypy: ignore-errors

"""Lightweight asyncio bridge for sqlite3 used by this repository."""

from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import Generator, Iterable
from pathlib import Path
from typing import Any, Callable, Literal, Optional, Union

from .context import contextmanager
from .cursor import Cursor

__all__ = ["connect", "Connection", "Cursor"]

IsolationLevel = Optional[Literal["DEFERRED", "IMMEDIATE", "EXCLUSIVE"]]


class Connection:
    def __init__(
        self,
        connector: Callable[[], sqlite3.Connection],
        iter_chunk_size: int,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._connection: Optional[sqlite3.Connection] = None
        self._connector = connector
        self._iter_chunk_size = iter_chunk_size
        self._lock = asyncio.Lock()
        if loop is not None:
            del loop

    @property
    def _conn(self) -> sqlite3.Connection:
        if self._connection is None:
            raise ValueError("no active connection")
        return self._connection

    async def _run(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        async with self._lock:
            return fn(*args, **kwargs)

    async def _execute(self, fn, *args, **kwargs):
        return await self._run(fn, *args, **kwargs)

    async def _connect(self) -> "Connection":
        if self._connection is None:
            self._connection = self._connector()
        return self

    def __await__(self) -> Generator[Any, None, "Connection"]:
        return self._connect().__await__()

    async def __aenter__(self) -> "Connection":
        return await self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @contextmanager
    async def cursor(self) -> Cursor:
        return Cursor(self, await self._execute(self._conn.cursor))

    async def commit(self) -> None:
        await self._execute(self._conn.commit)

    async def rollback(self) -> None:
        await self._execute(self._conn.rollback)

    async def close(self) -> None:
        if self._connection is None:
            return
        try:
            await self._execute(self._conn.close)
        finally:
            self._connection = None

    @contextmanager
    async def execute(
        self, sql: str, parameters: Optional[Iterable[Any]] = None
    ) -> Cursor:
        if parameters is None:
            parameters = []
        cursor = await self._execute(self._conn.execute, sql, parameters)
        return Cursor(self, cursor)

    @contextmanager
    async def execute_insert(
        self, sql: str, parameters: Optional[Iterable[Any]] = None
    ) -> Optional[sqlite3.Row]:
        if parameters is None:
            parameters = []

        def _execute_insert() -> Optional[sqlite3.Row]:
            cursor = self._conn.execute(sql, parameters)
            cursor.execute("SELECT last_insert_rowid()")
            return cursor.fetchone()

        return await self._execute(_execute_insert)

    @contextmanager
    async def execute_fetchall(
        self, sql: str, parameters: Optional[Iterable[Any]] = None
    ) -> Iterable[sqlite3.Row]:
        if parameters is None:
            parameters = []

        def _execute_fetchall() -> Iterable[sqlite3.Row]:
            cursor = self._conn.execute(sql, parameters)
            return cursor.fetchall()

        return await self._execute(_execute_fetchall)

    @contextmanager
    async def executemany(
        self, sql: str, parameters: Iterable[Iterable[Any]]
    ) -> Cursor:
        cursor = await self._execute(self._conn.executemany, sql, parameters)
        return Cursor(self, cursor)

    @contextmanager
    async def executescript(self, sql_script: str) -> Cursor:
        cursor = await self._execute(self._conn.executescript, sql_script)
        return Cursor(self, cursor)

    async def interrupt(self) -> None:
        await self._execute(self._conn.interrupt)

    async def create_function(
        self, name: str, num_params: int, func: Callable, deterministic: bool = False
    ) -> None:
        await self._execute(
            self._conn.create_function,
            name,
            num_params,
            func,
            deterministic=deterministic,
        )

    @property
    def in_transaction(self) -> bool:
        return self._conn.in_transaction

    @property
    def isolation_level(self) -> Optional[str]:
        return self._conn.isolation_level

    @isolation_level.setter
    def isolation_level(self, value: IsolationLevel) -> None:
        self._conn.isolation_level = value

    @property
    def row_factory(self) -> Optional[type]:
        return self._conn.row_factory

    @row_factory.setter
    def row_factory(self, factory: Optional[type]) -> None:
        self._conn.row_factory = factory

    @property
    def text_factory(self) -> Callable[[bytes], Any]:
        return self._conn.text_factory

    @text_factory.setter
    def text_factory(self, factory: Callable[[bytes], Any]) -> None:
        self._conn.text_factory = factory

    @property
    def total_changes(self) -> int:
        return self._conn.total_changes

    async def enable_load_extension(self, value: bool) -> None:
        await self._execute(self._conn.enable_load_extension, value)

    async def load_extension(self, path: str):
        await self._execute(self._conn.load_extension, path)


def connect(
    database: Union[str, Path],
    *,
    iter_chunk_size: int = 64,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    **kwargs: Any,
) -> Connection:
    """Create and return a connection proxy to the sqlite database."""

    def connector() -> sqlite3.Connection:
        if isinstance(database, str):
            loc = database
        elif isinstance(database, bytes):
            loc = database.decode("utf-8")
        else:
            loc = str(database)
        kwargs.setdefault("check_same_thread", False)
        return sqlite3.connect(loc, **kwargs)

    return Connection(connector, iter_chunk_size, loop=loop)
