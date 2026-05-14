"""
Brain Registry Module — PostgreSQL-backed registry for the 7 MasterMind brain agents.

Provides:
- BrainRegistryRepository: async asyncpg-based data access
- Migration runner: applies SQL migrations to PostgreSQL
- Seed script: populates the 7 default brain rows
"""

__all__ = ["BrainRegistryRepository"]


def __getattr__(name: str) -> object:
    if name == "BrainRegistryRepository":
        from .repository import BrainRegistryRepository

        return BrainRegistryRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
