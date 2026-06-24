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
from .mcp_wrapper import (
    MCPWrapper,
    DirectMCPInvoker,
    get_brain_notebook_id,
    list_active_brains,
)
from .mcp_integration import MCPIntegration
from .output_formatter import OutputFormatter
from .coordinator import Coordinator
from .runtime_contracts import (
    CapabilityDefinition,
    CapabilityRegistry,
    CapabilitySet,
    ExecutionEnvelope,
    HarnessDefinition,
    HarnessRegistry,
    LoopPolicy,
    LoopSelector,
    RecoveryPayload,
    TaskProfile,
    VerificationPayload,
    build_execution_envelope,
    validate_execution_envelope,
)

__all__ = [
    "FlowDetector",
    "PlanGenerator",
    "BrainExecutor",
    "NotebookLMClient",
    "Evaluator",
    "MCPWrapper",
    "DirectMCPInvoker",
    "get_brain_notebook_id",
    "list_active_brains",
    "MCPIntegration",
    "OutputFormatter",
    "Coordinator",
    "CapabilityDefinition",
    "CapabilityRegistry",
    "CapabilitySet",
    "ExecutionEnvelope",
    "HarnessDefinition",
    "HarnessRegistry",
    "LoopPolicy",
    "LoopSelector",
    "RecoveryPayload",
    "TaskProfile",
    "VerificationPayload",
    "build_execution_envelope",
    "validate_execution_envelope",
]
