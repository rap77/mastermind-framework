"""
State management for parallel execution.

This module provides database persistence for task state tracking
during parallel brain execution.
"""

from .database import DatabaseConnection, get_db

__all__ = ["database", "DatabaseConnection", "get_db"]
