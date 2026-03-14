"""
Legacy Brain Wrapper - Backward compatibility layer for v1.x brains.

This module allows v1.x brains (which use orchestrator.state) to work with
v2.0 pure function architecture by wrapping them in isolated state contexts.

The key insight: v1.x brains access self.state (global), so we create a LOCAL
orchestrator instance for each call, preventing cross-talk between concurrent users.
"""

from __future__ import annotations

from typing import TypeVar, Generic, Any, Callable
from dataclasses import dataclass

from pydantic import BaseModel

# Type variables for generic wrapper
T = TypeVar("T", bound=BaseModel)


@dataclass
class LegacyExecutionContext:
    """
    Execution context for legacy brain calls.

    Attributes:
        brief: The user's brief/problem statement
        orchestrator: Local orchestrator instance (isolated per call)
        mcp_client: MCP client for NotebookLM queries
    """

    brief: str
    orchestrator: Any  # Legacy Coordinator class
    mcp_client: Any  # MCPIntegration or None


class LegacyBrainAdapter(Generic[T]):
    """
    Wraps legacy brains (with state) to pure function interface.

    Allows v1.x brains to work in v2.0 without modification by creating
    an isolated orchestrator context for each execution.

    Example:
        # Legacy brain uses orchestrator.state
        class OldProductStrategyBrain:
            def execute(self, brief: str, orchestrator: Coordinator):
                orchestrator.state["brief"] = brief  # Uses global state!
                # ... process ...
                return {"positioning": "...", ...}

        # Wrap it for v2.0 pure function architecture
        adapter = LegacyBrainAdapter(
            brain_executor=OldProductStrategyBrain().execute,
            output_model=ProductStrategy
        )

        # Now callable as pure function (input → output, no side effects)
        result = adapter(
            input=BrainInput(brief=Brief(problem_statement="...")),
            mcp_client=mcp_client
        )
        # result is ProductStrategy instance

    Type Args:
        T: Output Pydantic model type (e.g., ProductStrategy, UXResearch)
    """

    def __init__(
        self,
        brain_executor: Callable[[str, Any], dict],
        output_model: type[T],
        brain_id: int = 1,
    ):
        """
        Initialize legacy brain adapter.

        Args:
            brain_executor: Function that executes the brain
                          Signature: (brief: str, orchestrator: Coordinator) -> dict
            output_model: Pydantic model class for the output
            brain_id: Numeric brain ID (1-8) for config lookup
        """
        self.brain_executor = brain_executor
        self.output_model = output_model
        self.brain_id = brain_id

    def __call__(
        self,
        input: BaseModel,
        mcp_client: Any = None,
    ) -> T:
        """
        Call legacy brain with isolated context.

        This method creates a LOCAL orchestrator for each call, ensuring
        that legacy brains which use global state don't pollute shared state.

        Args:
            input: BrainInput with brief problem statement
            mcp_client: MCP client for NotebookLM (optional)

        Returns:
            Output model instance (e.g., ProductStrategy)

        Raises:
            ValidationError: If legacy brain output doesn't match output_model
            RuntimeError: If orchestrator creation fails
        """
        from mastermind_cli.orchestrator.coordinator import Coordinator
        from mastermind_cli.orchestrator.output_formatter import OutputFormatter

        # Extract brief from input
        brief_text = self._extract_brief(input)

        # Create LOCAL orchestrator (not shared!)
        # This is the KEY to isolation - each call gets its own orchestrator
        local_orchestrator = Coordinator(
            formatter=OutputFormatter(),
            use_mcp=False,  # Don't use MCP in legacy wrapper (use pure functions instead)
            enable_logging=False,  # Disable logging to avoid side effects
        )

        # Call legacy brain with LOCAL orchestrator
        try:
            result_dict = self.brain_executor(
                brief=brief_text,
                orchestrator=local_orchestrator,
            )
        except Exception as e:
            raise RuntimeError(
                f"Legacy brain #{self.brain_id} execution failed: {e}"
            ) from e

        # Normalize output dict
        normalized_dict = self._normalize_output(result_dict)

        # Convert dict to Pydantic model
        try:
            return self.output_model(**normalized_dict)
        except Exception as e:
            # Provide helpful error message
            raise ValueError(
                f"Legacy brain #{self.brain_id} output doesn't match "
                f"{self.output_model.__name__} schema: {e}\n"
                f"Got: {normalized_dict}"
            ) from e

    def _extract_brief(self, input: BaseModel) -> str:
        """
        Extract brief text from input model.

        Handles both BrainInput and raw Brief models.

        Args:
            input: Input model

        Returns:
            Brief text string
        """
        # Check if input has brief attribute
        if hasattr(input, "brief"):
            brief_obj = input.brief
            if hasattr(brief_obj, "problem_statement"):
                return brief_obj.problem_statement
            return str(brief_obj)

        # Check if input has problem_statement directly
        if hasattr(input, "problem_statement"):
            return input.problem_statement

        # Fallback: convert to string
        return str(input)

    def _normalize_output(self, result_dict: dict) -> dict:
        """
        Normalize legacy brain output to match output_model schema.

        Handles common mismatches between legacy and v2.0 schemas:
        - "persona" → "target_audience"
        - "name" → "positioning"
        - Nested dicts flattened

        Args:
            result_dict: Raw output from legacy brain

        Returns:
            Normalized dict matching output_model schema
        """
        # Brain #1 normalization
        if self.brain_id == 1:
            return self._normalize_brain_1_output(result_dict)

        # Brain #7 normalization
        if self.brain_id == 7:
            return self._normalize_brain_7_output(result_dict)

        # Default: return as-is
        return result_dict

    def _normalize_brain_1_output(self, result_dict: dict) -> dict:
        """
        Normalize Brain #1 (Product Strategy) output.

        Legacy format → v2.0 format:
        - persona.name → target_audience
        - value_proposition → positioning
        - key_features → key_features (already matches)
        - monetization → monetization_strategy
        """
        normalized = {}

        # positioning (from value_proposition or fallback)
        if "value_proposition" in result_dict:
            normalized["positioning"] = result_dict["value_proposition"]
        elif "positioning" in result_dict:
            normalized["positioning"] = result_dict["positioning"]

        # target_audience (from persona or fallback)
        if "persona" in result_dict:
            persona = result_dict["persona"]
            if isinstance(persona, dict):
                normalized["target_audience"] = persona.get("name", "Unknown Persona")
            else:
                normalized["target_audience"] = str(persona)
        elif "target_audience" in result_dict:
            normalized["target_audience"] = result_dict["target_audience"]

        # key_features (extract feature names)
        if "key_features" in result_dict:
            features = result_dict["key_features"]
            if isinstance(features, list):
                if features:  # Non-empty list
                    normalized["key_features"] = [
                        f["feature"] if isinstance(f, dict) else str(f)
                        for f in features
                    ]
                # else: empty list - let default fill it later
            # else: not a list - let default fill it later

        # success_metrics (extract metric names)
        if "success_metrics" in result_dict:
            metrics = result_dict["success_metrics"]
            if isinstance(metrics, list):
                if metrics:  # Non-empty list
                    normalized["success_metrics"] = [
                        m["metric"] if isinstance(m, dict) else str(m)
                        for m in metrics
                    ]
                # else: empty list - let default fill it later
            # else: not a list - let default fill it later

        # Fill required fields with defaults if missing or empty
        defaults = {
            "positioning": "Not specified",
            "target_audience": "Not specified",
            "key_features": ["Feature 1 (default)"],
            "success_metrics": ["Metric 1 (default)"],
        }

        for key, default_value in defaults.items():
            if key not in normalized or not normalized[key]:  # Missing or empty
                normalized[key] = default_value

        return normalized

    def _normalize_brain_7_output(self, result_dict: dict) -> dict:
        """
        Normalize Brain #7 (Growth/Data Evaluator) output.

        Legacy format → v2.0 format:
        - veredict → verdict (uppercase)
        - score (percentage → 0-10 float)
        - evaluation → feedback
        """
        normalized = {}

        # verdict (fix typo: veredict → verdict, convert to uppercase)
        if "veredict" in result_dict:
            verdict_val = str(result_dict["veredict"]).upper()
            # Map common verdicts to valid literals
            verdict_map = {
                "APPROVED": "APPROVE",
                "APPROVE": "APPROVE",
                "REJECTED": "REJECT",
                "REJECT": "REJECT",
                "CONDITIONAL": "CONDITIONAL",
                "ESCALATE": "ESCALATE",
                "PENDING": "CONDITIONAL",
                "NEEDS_WORK": "CONDITIONAL",
            }
            normalized["verdict"] = verdict_map.get(verdict_val, "CONDITIONAL")
        elif "verdict" in result_dict:
            verdict_val = str(result_dict["verdict"]).upper()
            verdict_map = {
                "APPROVED": "APPROVE",
                "APPROVE": "APPROVE",
                "REJECTED": "REJECT",
                "REJECT": "REJECT",
                "CONDITIONAL": "CONDITIONAL",
                "ESCALATE": "ESCALATE",
            }
            normalized["verdict"] = verdict_map.get(verdict_val, "CONDITIONAL")
        else:
            normalized["verdict"] = "CONDITIONAL"

        # score (convert percentage to 0-10 float)
        if "score" in result_dict:
            score = result_dict["score"]
            if isinstance(score, dict):
                percentage = score.get("percentage", 50)
                normalized["score"] = float(percentage) / 10.0  # Convert to 0-10
            elif isinstance(score, (int, float)):
                if score > 10:  # Assume percentage
                    normalized["score"] = float(score) / 10.0
                else:
                    normalized["score"] = float(score)
            else:
                normalized["score"] = 5.0
        else:
            normalized["score"] = 5.0

        # feedback (from evaluation or reasoning)
        if "evaluation" in result_dict:
            normalized["feedback"] = str(result_dict["evaluation"])
        elif "reasoning" in result_dict:
            normalized["feedback"] = result_dict["reasoning"]
        elif "message" in result_dict:
            normalized["feedback"] = result_dict["message"]
        else:
            normalized["feedback"] = "No feedback provided"

        # approval_conditions (optional, from evaluation if available)
        if "approval_conditions" in result_dict:
            normalized["approval_conditions"] = result_dict["approval_conditions"]
        else:
            normalized["approval_conditions"] = []

        return normalized


# ===== CONVENIENCE FUNCTIONS =====

def wrap_legacy_brain_1():
    """
    Wrap legacy Brain #1 (Product Strategy) for v2.0.

    Returns:
        LegacyBrainAdapter that outputs ProductStrategy
    """
    from mastermind_cli.types.interfaces import ProductStrategy
    from mastermind_cli.orchestrator.brain_executor import BrainExecutor

    # Create legacy executor
    executor = BrainExecutor(mcp_client=None)

    # Create adapter
    return LegacyBrainAdapter(
        brain_executor=lambda brief, orchestrator: executor._execute_brain_1(
            task={"inputs": {"brief": brief}}, use_mcp=False
        ),
        output_model=ProductStrategy,
        brain_id=1,
    )


def wrap_legacy_brain_7():
    """
    Wrap legacy Brain #7 (Growth/Data Evaluator) for v2.0.

    Returns:
        LegacyBrainAdapter that outputs GrowthDataEvaluation
    """
    from mastermind_cli.types.interfaces import GrowthDataEvaluation
    from mastermind_cli.orchestrator.brain_executor import BrainExecutor

    # Create legacy executor
    executor = BrainExecutor(mcp_client=None)

    # Create adapter
    return LegacyBrainAdapter(
        brain_executor=lambda brief, orchestrator: executor._execute_brain_7(
            task={"output_to_evaluate": {"brief": brief}, "previous_brain_id": 1},
            use_mcp=False
        ),
        output_model=GrowthDataEvaluation,
        brain_id=7,
    )


# ===== EXPORTS =====

__all__ = [
    "LegacyBrainAdapter",
    "LegacyExecutionContext",
    "wrap_legacy_brain_1",
    "wrap_legacy_brain_7",
]
