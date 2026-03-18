"""
Experience logging module for MasterMind Framework.

This module provides full-fidelity execution logging with PII redaction,
JSONB storage, and archive rotation for v3.0 ML readiness.

Key features:
- ExperienceRecord schema for storing brain executions
- PII/Secret redaction utilities
- Async experience logger with SQLite backend
- Archive rotation to compressed JSONL files
"""

from .models import ExperienceRecord
from .redaction import redact_pii, redact_for_storage
from .logger import ExperienceLogger, log_execution

__all__ = [
    "ExperienceRecord",
    "redact_pii",
    "redact_for_storage",
    "ExperienceLogger",
    "log_execution",
]
