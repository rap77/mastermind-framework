"""
MCP Wrapper - Bridge between Python and Claude Code MCP tools.

This module provides a Python interface that can be used from within
Claude Code to invoke MCP tools like NotebookLM.
"""

import json
from typing import Dict, Optional, List


class MCPWrapper:
    """Wrapper for Claude Code MCP tools.

    When running in Claude Code, the actual MCP tools are invoked
    at the tool level. This class provides a Python API that
    expects to receive the results from those tool calls.

    Usage pattern:
    1. Create query specification
    2. Call Claude Code MCP tool externally
    3. Pass results to this wrapper for processing
    """

    @staticmethod
    def create_notebook_query_spec(
        notebook_id: str,
        query: str,
        source_ids: Optional[List[str]] = None
    ) -> Dict:
        """Create a specification for a NotebookLM query.

        This spec can be used to invoke the MCP tool:

        Args:
            notebook_id: ID of the notebook to query
            query: Question to ask
            source_ids: Optional list of source IDs

        Returns:
            Dictionary with query specification
        """
        return {
            'tool': 'mcp__notebooklm-mcp__notebook_query',
            'parameters': {
                'notebook_id': notebook_id,
                'query': query,
                'source_ids': source_ids
            }
        }

    @staticmethod
    def parse_notebook_response(response: str) -> Dict:
        """Parse a NotebookLM query response.

        Args:
            response: Raw response string from NotebookLM

        Returns:
            Parsed response dictionary
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

    @staticmethod
    def format_evaluation_query(
        output: Dict,
        matrix_id: str,
        brain_id: int
    ) -> str:
        """Format a query for Brain #7 (Evaluator).

        Args:
            output: Output to evaluate
            matrix_id: ID of evaluation matrix to use
            brain_id: ID of brain that produced the output

        Returns:
            Query string for NotebookLM
        """
        return f"""Using the evaluation matrix '{matrix_id}', evaluate the following output from Brain #{brain_id}:

OUTPUT TO EVALUATE:
{json.dumps(output, indent=2)}

Please:
1. Load the evaluation matrix '{matrix_id}'
2. Evaluate the output against each check in the matrix
3. Return a veredict (APPROVE/CONDITIONAL/REJECT/ESCALATE)
4. Calculate the score (sum of passed check weights / total possible)
5. List all passed checks with justification
6. List all failed checks with specific fix instructions
7. Detect any cognitive biases from the bias catalog
8. Provide redirect instructions if not APPROVED

Format your response as YAML following the evaluation-report template.
"""


class DirectMCPInvoker:
    """Direct invoker for MCP tools when available.

    This class is meant to be used from within Claude Code where
    MCP tools are directly available as tool calls.
    """

    NOTEBOOK_IDS = {
        1: "f276ccb3-0bce-4069-8b55-eae8693dbe75",  # Product Strategy
        2: "ea006ece-00a9-4d5c-91f5-012b8b712936",  # UX Research
        3: "8d544475-6860-4cd7-9037-8549325493dd",  # UI Design
        4: "85e47142-0a65-41d9-9848-49b8b5d2db33",  # Frontend
        5: "c6befbbc-b7dd-4ad0-a677-314750684208",  # Backend
        6: "74cd3a81-1350-4927-af14-c0c4fca41a8e",  # QA/DevOps
        7: "d8de74d6-7028-44ed-b4d4-784d6a9256e6",  # Growth/Data
    }

    @classmethod
    def query_brain(
        cls,
        brain_id: int,
        query: str,
        source_ids: Optional[List[str]] = None
    ) -> Dict:
        """Query a brain's notebook.

        NOTE: This method returns a specification for the MCP tool call.
        The actual call must be made at the Claude Code tool level.

        Args:
            brain_id: ID of brain (1-7)
            query: Query string
            source_ids: Optional source IDs

        Returns:
            Specification dict for MCP tool invocation
        """
        notebook_id = cls.NOTEBOOK_IDS.get(brain_id)

        if not notebook_id:
            return {
                'status': 'error',
                'error': f'Brain #{brain_id} does not have a notebook ID'
            }

        return {
            'status': 'spec_ready',
            'tool': 'notebook_query',
            'notebook_id': notebook_id,
            'query': query,
            'source_ids': source_ids
        }

    @classmethod
    def create_brain_1_query(cls, brief: str) -> str:
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

    @classmethod
    def create_brain_7_query(cls, output: Dict, brain_id: int = 1) -> str:
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


def get_brain_notebook_id(brain_id: int) -> Optional[str]:
    """Get the NotebookLM notebook ID for a brain."""
    return DirectMCPInvoker.NOTEBOOK_IDS.get(brain_id)


def list_active_brains() -> List[Dict]:
    """List all brains with active notebooks."""
    return [
        {
            'brain_id': bid,
            'notebook_id': nid,
            'status': 'active'
        }
        for bid, nid in DirectMCPInvoker.NOTEBOOK_IDS.items()
    ]
