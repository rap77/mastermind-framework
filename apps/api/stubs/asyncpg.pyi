"""Type stubs for asyncpg."""

from typing import Any, Protocol, AsyncContextManager

class Record(Protocol):
    """Protocol for asyncpg.Record - dict-like row access."""

    def __getitem__(self, key: str) -> Any: ...
    def get(self, key: str, default: Any = None) -> Any: ...

class Connection:
    """asyncpg connection stub."""

    async def fetch(self, query: str, *args: Any) -> list[Record]: ...
    async def fetchrow(self, query: str, *args: Any) -> Record | None: ...
    async def fetchval(self, query: str, *args: Any) -> Any: ...
    async def execute(self, query: str, *args: Any) -> str: ...
    async def close(self) -> None: ...

class Pool:
    """asyncpg connection pool stub."""

    def acquire(self) -> AsyncContextManager[Connection]: ...
    async def close(self) -> None: ...

async def connect(dsn: str, **kwargs: Any) -> Connection: ...
async def create_pool(
    *,
    host: str = ...,
    port: int = ...,
    user: str = ...,
    password: str = ...,
    database: str = ...,
    min_size: int = ...,
    max_size: int = ...,
    **kwargs: Any,
) -> Pool: ...
