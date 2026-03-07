"""
Brain Executor - Executes brain tasks via NotebookLM MCP.
"""

import os
import sys
from typing import Dict

# Add project root to path for imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ..brain_registry import load_brain_configs  # noqa: E402
from .notebooklm_client import NotebookLMClient  # noqa: E402
from .evaluator import Evaluator  # noqa: E402


class BrainExecutor:
    """Executes brain tasks via NotebookLM MCP."""

    def __init__(self, mcp_client=None, skills_dir: str = None):
        """Initialize brain executor.

        Args:
            mcp_client: MCPIntegration instance for making NotebookLM calls
            skills_dir: Path to skills directory for evaluator
        """
        self.notebooklm_client = NotebookLMClient()
        self.evaluator = Evaluator(skills_dir=skills_dir)
        self.mcp_client = mcp_client

        # Load brains from YAML (supports N brains, not just 7)
        self.BRAIN_CONFIGS = load_brain_configs()

    def execute(self, brain_id: int, task: Dict, use_mcp: bool = True) -> Dict:
        """
        Execute a brain task.

        Args:
            brain_id: ID of brain to execute (1-8+)
            task: Task definition with inputs
            use_mcp: Whether to use MCP for NotebookLM calls

        Returns:
            Output from brain execution
        """
        brain_config = self.BRAIN_CONFIGS.get(brain_id)

        if not brain_config:
            return self._unimplemented_brain(brain_id, task)

        # Handle pending brains (like #8 before PRP-012)
        if brain_config.get("status") == "pending":
            return self._pending_brain(brain_id, task)

        if brain_config.get("status") != "active":
            return self._unimplemented_brain(brain_id, task)

        # Route to appropriate executor
        if brain_id == 1:
            return self._execute_brain_1(task, use_mcp=use_mcp)
        elif brain_id == 7:
            return self._execute_brain_7(task, use_mcp=use_mcp)
        elif brain_id == 8:
            return self._execute_brain_8(task, use_mcp=use_mcp)
        else:
            return self._execute_generic_brain(brain_id, task, use_mcp=use_mcp)

    def _execute_brain_1(self, task: Dict, use_mcp: bool = True) -> Dict:
        """Execute Product Strategy brain via NotebookLM."""
        brief = task["inputs"].get("brief", "")

        # Construct query for Brain #1
        query = f"""Based on the following product brief, provide a comprehensive product strategy analysis:

Brief: {brief}

Please provide:
1. Target Persona (specific, with demographics and pain points)
2. Value Proposition (unique differentiation)
3. Key Features (MVP scope, prioritized)
4. Monetization Strategy (how it makes money)
5. Success Metrics (key indicators to track)
6. Risks (value, usability, feasibility, viability)
7. What we don't know (assumptions and uncertainties)

Format as YAML with the following structure:
```yaml
persona:
  name: "Persona Name"
  description: "Detailed description"
  demographics: {{age_range, role, industry, etc}}
  pain_points: [list of specific problems]

value_proposition: "Clear statement of unique value"

key_features:
  - feature: "Feature 1"
    priority: "must-have | should-have | nice-to-have"
    rationale: "Why this feature matters"

monetization:
  model: "freemium | subscription | transactional | etc"
  pricing: "Pricing strategy"
  unit_economics: "LTV/CAC analysis if available"

success_metrics:
  - metric: "D7 retention"
    target: ">35%"
    confidence: "medium"
  - metric: "activation_rate"
    target: ">50%"
    confidence: "high"

risks:
  value_risk: "Analysis of whether anyone cares"
  usability_risk: "Analysis of whether users can use it"
  feasibility_risk: "Analysis of whether we can build it"
  viability_risk: "Analysis of whether it can be a business"

assumptions:
  - "Key assumption 1 (not yet validated)"
  - "Key assumption 2 (not yet validated)"

pre_mortem: "What could cause this to fail in 1 year?"

evidence:
  interviews: "Number and summary of user interviews"
  data: "Any supporting data"
  research: "Any external research cited"
```
"""

        if use_mcp and self.mcp_client and self.mcp_client.is_available():
            # Use MCP to query NotebookLM
            try:
                response = self.mcp_client.query_notebook(brain_id=1, query=query)
                if response.get("status") == "success":
                    return self._format_brain_response(
                        1, response.get("content", ""), brief
                    )
                else:
                    # MCP error, fallback to mock
                    return self._mock_brain_1_response(
                        brief, query, error=response.get("error")
                    )
            except Exception as e:
                # Fallback to mock response if MCP fails
                return self._mock_brain_1_response(brief, query, error=str(e))
        else:
            # Mock response for testing without MCP
            return self._mock_brain_1_response(brief, query)

    def _execute_brain_7(self, task: Dict, use_mcp: bool = True) -> Dict:
        """Execute Growth & Data (Evaluator) brain."""
        # Get the output to evaluate
        output_to_evaluate = task.get("output_to_evaluate", {})
        previous_brain_id = task.get("previous_brain_id", 1)

        # Determine which matrix to use
        matrix_map = {
            1: "MATRIX-product-brief",
            2: "MATRIX-ux-research",
            3: "MATRIX-ui-design",
            4: "MATRIX-frontend",
            5: "MATRIX-backend",
            6: "MATRIX-qa-devops",
        }
        matrix_id = matrix_map.get(previous_brain_id, "MATRIX-product-brief")

        # Use the Evaluator class
        evaluation = self.evaluator.evaluate(
            output=output_to_evaluate, matrix_id=matrix_id, brain_id=previous_brain_id
        )

        return {
            "brain_id": 7,
            "brain_name": "Growth & Data (Evaluator)",
            "status": "completed",
            "veredict": evaluation["veredict"],
            "score": evaluation["score"],
            "evaluation": evaluation,
            "message": f"Brain #7 evaluation complete: {evaluation['veredict']} ({evaluation['score']['percentage']}%)",
        }

    def _execute_brain_8(self, task: Dict, use_mcp: bool = True) -> Dict:
        """Execute Master Interviewer brain."""
        context = task.get("context", {})
        brief = task.get("inputs", {}).get("brief", "")

        query = f"""As a Master Interviewer and Discovery expert, analyze the following:

Context: {brief}

Task: {context.get("instruction", "Design an interview strategy")}

Provide your analysis in the following JSON format:
{{
  "interview_strategy": {{
    "categories": [
      {{"id": "users", "name": "Users & Personas", "target_brain": 2}},
      {{"id": "platforms", "name": "Platforms", "target_brain": 4}}
    ],
    "initial_questions": [
      {{"category": "users", "question": "What type of users?", "target_brain": 2}}
    ],
    "detected_gaps": []
  }}
}}
"""

        if use_mcp and self.mcp_client and self.mcp_client.is_available():
            try:
                response = self.mcp_client.query_notebook(brain_id=8, query=query)
                if response.get("status") == "success":
                    return self._format_brain_response(
                        8, response.get("content", ""), brief
                    )
            except Exception as e:
                return self._mock_brain_8_response(brief, query, error=str(e))

        return self._mock_brain_8_response(brief, query)

    def _execute_generic_brain(
        self, brain_id: int, task: Dict, use_mcp: bool = True
    ) -> Dict:
        """Execute a generic brain (2-6)."""
        brain_config = self.BRAIN_CONFIGS[brain_id]
        brief = task["inputs"].get("brief", "")
        context = task.get("context", {})

        query = f"""As a {brain_config["name"]} expert, analyze the following:

Brief: {brief}

Context: {context}

Please provide your analysis and recommendations.
"""

        if use_mcp and self.mcp_client and self.mcp_client.is_available():
            try:
                response = self.mcp_client.query_notebook(
                    brain_id=brain_id, query=query
                )
                if response.get("status") == "success":
                    return self._format_brain_response(
                        brain_id, response.get("content", ""), brief
                    )
                else:
                    return self._mock_generic_response(
                        brain_id, brief, error=response.get("error")
                    )
            except Exception as e:
                return self._mock_generic_response(brain_id, brief, error=str(e))
        else:
            return self._mock_generic_response(brain_id, brief)

    def _format_brain_response(self, brain_id: int, response: str, brief: str) -> Dict:
        """Format a brain response into standard output format."""
        brain_config = self.BRAIN_CONFIGS[brain_id]

        # Try to parse YAML from response
        parsed = self.notebooklm_client.parse_yaml_response(response)

        if "error" in parsed:
            # Return raw text response
            return {
                "brain_id": brain_id,
                "brain_name": brain_config["name"],
                "status": "completed",
                "output": {"raw_response": response, "brief": brief},
                "message": f"Brain #{brain_id} execution complete (text format)",
            }

        return {
            "brain_id": brain_id,
            "brain_name": brain_config["name"],
            "status": "completed",
            "output": parsed,
            "brief": brief,
            "message": f"Brain #{brain_id} execution complete (parsed)",
        }

    def _mock_brain_1_response(self, brief: str, query: str, error: str = None) -> Dict:
        """Generate a mock response for Brain #1 (for testing without MCP)."""
        return {
            "brain_id": 1,
            "brain_name": "Product Strategy",
            "status": "mock",
            "output": {
                "note": "This is a mock response. MCP integration will query NotebookLM for real responses.",
                "query_preview": query[:200] + "...",
                "brief": brief,
                "mcp_error": error,
            },
            "message": "Brain #1 mock response (MCP not available in this environment)",
        }

    def _mock_brain_8_response(self, brief: str, query: str, error: str = None) -> Dict:
        """Mock response for Brain #8 (for testing without MCP)."""
        return {
            "brain_id": 8,
            "brain_name": "Master Interviewer",
            "status": "mock",
            "output": {
                "note": "This is a mock response. Brain #8 will be implemented with NotebookLM integration in PRP-012.",
                "query_preview": query[:200] + "...",
                "brief": brief,
                "mcp_error": error,
            },
            "message": "Brain #8 mock response (MCP not available or brain not yet configured)",
        }

    def _mock_generic_response(
        self, brain_id: int, brief: str, error: str = None
    ) -> Dict:
        """Generate a mock response for brains 2-6."""
        brain_config = self.BRAIN_CONFIGS[brain_id]
        return {
            "brain_id": brain_id,
            "brain_name": brain_config["name"],
            "status": "mock",
            "output": {
                "note": f"This is a mock response. Brain #{brain_id} will be implemented with NotebookLM integration.",
                "brief": brief,
                "mcp_error": error,
            },
            "message": f"Brain #{brain_id} mock response (MCP not available)",
        }

    def _pending_brain(self, brain_id: int, task: Dict) -> Dict:
        """Return response for pending brain."""
        brain_name = self.BRAIN_CONFIGS.get(brain_id, {}).get(
            "name", f"Brain {brain_id}"
        )

        return {
            "brain_id": brain_id,
            "brain_name": brain_name,
            "status": "pending",
            "error": f"Brain #{brain_id} ({brain_name}) is registered but not yet active. Check the corresponding PRP for implementation status.",
            "message": f"Brain #{brain_id} is coming soon! Track progress in GitHub issues.",
        }

    def _unimplemented_brain(self, brain_id: int, task: Dict) -> Dict:
        """Return response for unimplemented brain."""
        brain_names = {
            2: "UX Research",
            3: "UI Design",
            4: "Frontend Development",
            5: "Backend Development",
            6: "QA & DevOps",
            8: "Master Interviewer",
        }

        name = brain_names.get(brain_id, f"Brain {brain_id}")

        return {
            "brain_id": brain_id,
            "brain_name": name,
            "status": "unimplemented",
            "error": f"Brain #{brain_id} ({name}) is not yet fully implemented.",
            "message": f"To use this flow, implement Brain #{brain_id} first or use validation_only flow.",
        }

    def is_brain_available(self, brain_id: int) -> bool:
        """Check if a brain is available for execution."""
        config = self.BRAIN_CONFIGS.get(brain_id)
        return config and config.get("status") == "active"

    def get_available_brains(self) -> list:
        """Get list of available brain IDs."""
        return [
            brain_id
            for brain_id, config in self.BRAIN_CONFIGS.items()
            if config.get("status") == "active"
        ]
