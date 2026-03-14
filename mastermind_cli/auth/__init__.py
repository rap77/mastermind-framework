"""
MasterMind Framework - Authentication Module.

This module provides API key authentication for both CLI and Web UI.
"""

from .api_keys import APIKey, validate_api_key

__all__ = ["APIKey", "validate_api_key"]
