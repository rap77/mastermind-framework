"""
Brain Executor - Executes brain tasks via NotebookLM MCP.
"""

import yaml
from typing import Dict, Optional


class BrainExecutor:
    """Executes brain tasks via NotebookLM MCP."""

    # Brain configurations
    BRAIN_CONFIGS = {
        1: {
            'id': 'product-strategy',
            'name': 'Product Strategy',
            'system_prompt': 'agents/brains/product-strategy.md',
            'notebook_id': 'f276ccb3-0bce-4069-8b55-eae8693dbe75',
            'status': 'active'
        },
        7: {
            'id': 'growth-data',
            'name': 'Growth & Data (Evaluator)',
            'system_prompt': 'agents/brains/growth-data.md',
            'evaluator_skill': 'skills/evaluator/SKILL.md',
            'status': 'active'
        }
    }

    def __init__(self, mcp_notebooklm=None):
        """Initialize brain executor.

        Args:
            mcp_notebooklm: NotebookLM MCP client (optional)
        """
        self.mcp_notebooklm = mcp_notebooklm

    def execute(self, brain_id: int, task: Dict) -> Dict:
        """
        Execute a brain task.

        Args:
            brain_id: ID of brain to execute (1-7)
            task: Task definition with inputs

        Returns:
            Output from brain execution
        """
        brain_config = self.BRAIN_CONFIGS.get(brain_id)

        if not brain_config:
            return self._unimplemented_brain(brain_id, task)

        if brain_config['status'] != 'active':
            return self._unimplemented_brain(brain_id, task)

        if brain_id == 1:
            return self._execute_brain_1(task)
        elif brain_id == 7:
            return self._execute_brain_7(task)

        return self._unimplemented_brain(brain_id, task)

    def _execute_brain_1(self, task: Dict) -> Dict:
        """Execute Product Strategy brain via NotebookLM."""
        # Load system prompt
        try:
            with open('agents/brains/product-strategy.md', 'r') as f:
                system_prompt = f.read()
        except FileNotFoundError:
            system_prompt = "You are a Product Strategy expert."

        # Construct query
        brief = task['inputs'].get('brief', '')
        query = f"""
Based on the following product brief, provide a comprehensive product strategy analysis:

Brief: {brief}

Please provide:
1. Target Persona (specific, with demographics and pain points)
2. Value Proposition (unique differentiation)
3. Key Features (MVP scope, prioritized)
4. Monetization Strategy (how it makes money)
5. Success Metrics (key indicators to track)

Format as YAML with the following structure:
```yaml
persona:
  name: "Persona Name"
  description: "Detailed description"
  demographics: {...}
  pain_points: [...]

value_proposition: "..."
key_features: [...]
monetization: {...}
success_metrics: [...]
assumptions: [...]
```
"""

        # For MVP: Return placeholder (actual MCP call would go here)
        return {
            'brain_id': 1,
            'brain_name': 'Product Strategy',
            'status': 'placeholder',  # Would be 'completed' with real MCP
            'output': {
                'note': 'This is a placeholder output. In full implementation, this would query NotebookLM.',
                'query': query.strip(),
                'notebook_id': 'f276ccb3-0bce-4069-8b55-eae8693dbe75'
            },
            'message': 'Brain #1 execution: NotebookLM integration pending (placeholder output)'
        }

    def _execute_brain_7(self, task: Dict) -> Dict:
        """Execute Growth & Data (Evaluator) brain."""
        # Load evaluator skill
        try:
            with open('skills/evaluator/SKILL.md', 'r') as f:
                evaluator_prompt = f.read()
        except FileNotFoundError:
            evaluator_prompt = "You are a Critical Evaluator."

        # Get output to evaluate
        output_to_evaluate = task.get('output_to_evaluate', {})

        # For MVP: Return placeholder evaluation
        return {
            'brain_id': 7,
            'brain_name': 'Growth & Data (Evaluator)',
            'status': 'placeholder',
            'veredict': 'PLACEHOLDER',
            'score': 0,
            'evaluation': {
                'note': 'This is a placeholder evaluation. In full implementation, this would apply the evaluation matrix.',
                'evaluator_skill': 'skills/evaluator/SKILL.md',
                'output_to_evaluate': output_to_evaluate
            },
            'message': 'Brain #7 evaluation: Placeholder (full evaluation pending MCP integration)'
        }

    def _unimplemented_brain(self, brain_id: int, task: Dict) -> Dict:
        """Return response for unimplemented brain."""
        brain_names = {
            2: 'UX Research',
            3: 'UI Design',
            4: 'Frontend Development',
            5: 'Backend Development',
            6: 'QA & DevOps'
        }

        return {
            'brain_id': brain_id,
            'brain_name': brain_names.get(brain_id, f'Brain {brain_id}'),
            'status': 'unimplemented',
            'error': f'Brain #{brain_id} ({brain_names.get(brain_id)}) is not yet implemented.',
            'message': f'To use this flow, implement Brain #{brain_id} first or use validation_only flow.'
        }

    def is_brain_available(self, brain_id: int) -> bool:
        """Check if a brain is available for execution."""
        config = self.BRAIN_CONFIGS.get(brain_id)
        return config and config.get('status') == 'active'

    def get_available_brains(self) -> list:
        """Get list of available brain IDs."""
        return [
            brain_id for brain_id, config in self.BRAIN_CONFIGS.items()
            if config.get('status') == 'active'
        ]
