"""
MCP Integration - Real MCP calls from Python when running in Claude Code.

This module provides the ability to make actual NotebookLM MCP calls
when the CLI is executed from within Claude Code.
"""

import os
import json
import subprocess
from typing import Dict, Optional, List


class MCPIntegration:
    """Handles MCP integration for NotebookLM calls."""

    # Notebook IDs for all brains
    NOTEBOOK_IDS = {
        1: "f276ccb3-0bce-4069-8b55-eae8693dbe75",  # Product Strategy
        2: "ea006ece-00a9-4d5c-91f5-012b8b712936",  # UX Research
        3: "8d544475-6860-4cd7-9037-8549325493dd",  # UI Design
        4: "85e47142-0a65-41d9-9848-49b8b5d2db33",  # Frontend
        5: "c6befbbc-b7dd-4ad0-a677-314750684208",  # Backend
        6: "74cd3a81-1350-4927-af14-c0c4fca41a8e",  # QA/DevOps
        7: "d8de74d6-7028-44ed-b4d5-784d6a9256e6",  # Growth/Data
    }

    def __init__(self, use_mcp: bool = False):
        """Initialize MCP integration.

        Args:
            use_mcp: Whether to attempt MCP calls (default: False)
        """
        self.use_mcp = use_mcp
        self._claude_code_available = self._check_claude_code()

    def _check_claude_code(self) -> bool:
        """Check if running in Claude Code environment."""
        # Check if Claude Code environment variables are present
        return os.getenv('CLAUDE_CODE_SESSION') is not None

    def is_available(self) -> bool:
        """Check if MCP integration is available."""
        return self.use_mcp and self._claude_code_available

    def query_notebook(
        self,
        brain_id: int,
        query: str,
        source_ids: Optional[List[str]] = None,
        timeout: int = 120
    ) -> Dict:
        """Query a brain's notebook via MCP.

        Args:
            brain_id: ID of brain (1-7)
            query: Query string
            source_ids: Optional list of source IDs
            timeout: Query timeout in seconds

        Returns:
            Response dictionary with status and content
        """
        notebook_id = self.NOTEBOOK_IDS.get(brain_id)

        if not notebook_id:
            return {
                'status': 'error',
                'error': f'Brain #{brain_id} does not have a notebook ID'
            }

        if not self.is_available():
            return {
                'status': 'unavailable',
                'error': 'MCP not available in this environment',
                'note': 'Use --use-mcp flag when running from Claude Code'
            }

        # Build MCP query spec
        query_spec = {
            'notebook_id': notebook_id,
            'query': query,
            'source_ids': source_ids
        }

        # Execute via subprocess using nlm (NotebookLM CLI)
        try:
            result = self._execute_nl_mcp('notebook_query', query_spec, timeout)
            return {
                'status': 'success',
                'content': result,
                'raw': result
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'query_spec': query_spec
            }

    def _execute_nl_mcp(self, action: str, params: Dict, timeout: int) -> str:
        """Execute NotebookLM MCP command via nlm CLI.

        This uses the nlm command-line tool which wraps MCP calls.

        Args:
            action: MCP action (e.g., 'notebook_query')
            params: Parameters for the action
            timeout: Timeout in seconds

        Returns:
            Response string from NotebookLM
        """
        # Build nlm command
        cmd = ['nlm', 'query']

        # Add notebook ID
        notebook_id = params.get('notebook_id')
        cmd.extend(['--notebook', notebook_id])

        # Add query
        query = params.get('query', '')
        cmd.extend(['--query', query])

        # Execute
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"nlm command failed: {result.stderr}")

        return result.stdout

    def create_brain_1_query(self, brief: str) -> str:
        """Create a formatted query for Brain #1 (Product Strategy)."""
        return f"""Based on the following product brief, provide a comprehensive product strategy analysis:

Brief: {brief}

Please provide:
1. Target Persona (specific, with demographics and pain points)
2. Value Proposition (unique differentiation)
3. Key Features (MVP scope, prioritized)
4. Monetization Strategy (how it makes money)
5. Success Metrics (key indicators to track)
6. Risks (value, usability, feasibility, viability)
7. What we don't know (assumptions and uncertainties)
8. Pre-mortem (what could cause this to fail?)

Format as YAML with the following structure:
```yaml
persona:
  name: "Persona Name"
  description: "Detailed description"
  demographics: {{age_range, role, industry, etc}}
  pain_points: [list of specific problems]
  jtbd: "Job to be done"

value_proposition: "Clear statement of unique value vs alternatives"

key_features:
  - feature: "Feature 1"
    priority: "must-have"
    rationale: "Why this feature matters"

monetization:
  model: "freemium | subscription | transactional"
  pricing_strategy: "How pricing works"
  unit_economics: "LTV/CAC analysis"

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
```

Ensure your response follows the exact YAML structure above.
"""

    def create_brain_7_query(self, output: Dict, brain_id: int = 1) -> str:
        """Create a formatted query for Brain #7 (Evaluator)."""
        matrix_id = "MATRIX-product-brief"  # Default for Brain #1 outputs

        return f"""Using the evaluation matrix '{matrix_id}', evaluate the following product strategy output from Brain #{brain_id}:

OUTPUT TO EVALUATE:
{json.dumps(output, indent=2)}

EVALUATION INSTRUCTIONS:
1. Load the evaluation matrix '{matrix_id}'
2. Evaluate the output against each check (C1-C5, Q1-Q5, H1-H5, V1-V5)
3. For each check, determine PASS or FAIL based on evidence in the output
4. Calculate the score: (sum of passed check weights) / (total possible: 156)
5. Determine veredict:
   - Score >= 80% → APPROVE
   - Score 60-79% → CONDITIONAL
   - Score < 60% → REJECT
6. Detect cognitive biases using the bias catalog
7. Provide specific fix instructions for each failed check

Format your response as:
```yaml
veredict: "APPROVE | CONDITIONAL | REJECT"
score:
  points: <number>
  total: 156
  percentage: <number>

summary: "2-3 sentence summary"

passed_checks:
  - check_id: "C1"
    check: "Check description"
    justification: "Evidence from output"

failed_checks:
  - check_id: "Q2"
    check: "Check description"
    reason: "Why it failed"
    fix_instruction: "Specific instruction to fix"

biases_detected:
  - bias_id: "BIAS-01"
    name: "Confirmation Bias"
    signal: "Text that triggered this"
    question: "What evidence contradicts this?"

redirect_instructions:
  to_brain: "01"
  action: "REDO | ITERATE"
  specific_fixes: ["fix 1", "fix 2"]
  max_iterations: 3
```
"""

    @staticmethod
    def parse_yaml_response(response: str) -> Dict:
        """Parse YAML from a NotebookLM response.

        Args:
            response: Raw response string

        Returns:
            Parsed dictionary
        """
        import yaml
        import re

        # Try to extract YAML from markdown code block
        yaml_patterns = [
            r'```yaml\s*\n(.*?)\n```',  # With yaml tag
            r'```\s*\n(.*?)\n```',       # Without tag
        ]

        for pattern in yaml_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                yaml_content = match.group(1)
                try:
                    parsed = yaml.safe_load(yaml_content)
                    return {
                        'status': 'success',
                        'parsed': True,
                        'content': parsed,
                        'raw': response
                    }
                except yaml.YAMLError as e:
                    return {
                        'status': 'parse_error',
                        'error': str(e),
                        'yaml_content': yaml_content,
                        'raw': response
                    }

        # No YAML found, return as-is
        return {
            'status': 'success',
            'parsed': False,
            'content': response,
            'raw': response
        }

    def get_brain_status(self) -> Dict:
        """Get status of all brain notebooks."""
        return {
            brain_id: {
                'notebook_id': notebook_id,
                'status': 'active'
            }
            for brain_id, notebook_id in self.NOTEBOOK_IDS.items()
        }
