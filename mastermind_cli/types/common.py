"""
Common types used across modules.
"""

from enum import Enum


class FlowType(str, Enum):
    """Flow type literals."""
    DISCOVERY = "discovery"
    VALIDATION_ONLY = "validation_only"
    FULL_PRODUCT = "full_product"


class EvaluationVerdict(str, Enum):
    """Evaluation verdict literals."""
    APPROVE = "APPROVE"
    CONDITIONAL = "CONDITIONAL"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"
