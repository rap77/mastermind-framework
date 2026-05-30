"""SQLAlchemy session management for window scheduler."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from mastermind_cli.window_scheduler.database.base import Base

_ENGINES: dict[str, Engine] = {}
_SESSION_FACTORIES: dict[str, sessionmaker[Session]] = {}


def get_engine(database_url: str) -> Engine:
    """Return a cached SQLAlchemy engine for the given URL."""
    engine = _ENGINES.get(database_url)
    if engine is None:
        engine_kwargs: dict[str, object] = {"future": True}
        if database_url.startswith("sqlite"):
            engine_kwargs["connect_args"] = {"check_same_thread": False}
            if database_url.endswith(":memory:"):
                engine_kwargs["poolclass"] = StaticPool
        engine = create_engine(database_url, **engine_kwargs)
        _ENGINES[database_url] = engine
    return engine


def get_session_factory(database_url: str) -> sessionmaker[Session]:
    """Return a cached session factory for the given URL."""
    factory = _SESSION_FACTORIES.get(database_url)
    if factory is None:
        factory = sessionmaker(bind=get_engine(database_url), expire_on_commit=False)
        _SESSION_FACTORIES[database_url] = factory
    return factory


def get_session(database_url: str) -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for the given URL."""
    factory = get_session_factory(database_url)
    session = factory()
    try:
        yield session
    finally:
        session.close()


def initialize_database(database_url: str) -> None:
    """Create all window scheduler tables for the given database URL."""
    # Import models to register them with Base.metadata
    from mastermind_cli.window_scheduler.models import (  # noqa: F401
        AvailabilityState,
        BackendSession,
        RunPolicy,
        SchedulerCheckpoint,
        SchedulerEvent,
    )

    engine = get_engine(database_url)
    # For in-memory SQLite with StaticPool, connection must be established first
    # to allow table creation to be visible to subsequent connections
    if database_url.endswith(":memory:"):
        # Establish connection without storing (context manager handles cleanup)
        _ = engine.connect().__enter__()
    Base.metadata.create_all(bind=engine)


def dispose_engines() -> None:
    """Dispose all cached SQLAlchemy engines."""
    for engine in _ENGINES.values():
        engine.dispose()
    _ENGINES.clear()
    _SESSION_FACTORIES.clear()
