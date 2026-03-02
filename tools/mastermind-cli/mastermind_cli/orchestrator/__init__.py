"""
Orchestrator package for mastermind-cli.

Implements the central coordination logic for the MasterMind Framework,
including flow detection, task generation, and brain execution.
"""

from .flow_detector import FlowDetector
from .plan_generator import PlanGenerator
from .brain_executor import BrainExecutor
from .notebooklm_client import NotebookLMClient
from .evaluator import Evaluator
from .mcp_wrapper import MCPWrapper, DirectMCPInvoker, get_brain_notebook_id, list_active_brains
from .output_formatter import OutputFormatter
from .coordinator import Coordinator

__all__ = [
    'FlowDetector',
    'PlanGenerator',
    'BrainExecutor',
    'NotebookLMClient',
    'Evaluator',
    'MCPWrapper',
    'DirectMCPInvoker',
    'get_brain_notebook_id',
    'list_active_brains',
    'OutputFormatter',
    'Coordinator',
]
