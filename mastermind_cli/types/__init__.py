"""
Type definitions for MasterMind Framework v2.0.

Provides Pydantic v2 models for all orchestration data structures:
- Coordinator: Request/response models
- MCP: NotebookLM integration models
- Brains: Brain output schemas
- Config: YAML configuration models
- Common: Shared literals and enums
- Interfaces: Pure function brain input/output models (v2.0)
"""

# Import and re-export all types from submodules
from .coordinator import *
from .mcp import *
from .brains import *
from .config import *
from .common import *
from .interfaces import *
