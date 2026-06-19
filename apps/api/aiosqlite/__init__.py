"""asyncio bridge to the standard sqlite3 module."""

from sqlite3 import (
    DatabaseError,
    Error,
    IntegrityError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    Row,
    Warning,
    paramstyle,
    register_adapter,
    register_converter,
    sqlite_version,
    sqlite_version_info,
)

from .__version__ import __version__
from .core import Connection, Cursor, connect

__all__ = [
    "__version__",
    "paramstyle",
    "register_adapter",
    "register_converter",
    "sqlite_version",
    "sqlite_version_info",
    "connect",
    "Connection",
    "Cursor",
    "Row",
    "Warning",
    "Error",
    "DatabaseError",
    "IntegrityError",
    "ProgrammingError",
    "OperationalError",
    "NotSupportedError",
]
