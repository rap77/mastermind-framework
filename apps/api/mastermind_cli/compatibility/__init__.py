"""
MasterMind Framework - Compatibility Layer.

This module provides backward compatibility with v1.x brains.
"""

from .legacy_wrapper import LegacyBrainAdapter

__all__ = ["LegacyBrainAdapter"]
