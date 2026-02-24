"""
Plan Generator - Generates execution plans from briefs.
"""

import uuid
from datetime import datetime
from typing import Dict, List


class PlanGenerator:
    """Generates execution plans from briefs."""

    def __init__(self, flow_detector=None):
        """Initialize plan generator."""
        from .flow_detector import FlowDetector
        self.flow_detector = flow_detector or FlowDetector()

    def generate(self, brief: str, flow_type: str) -> Dict:
        """
        Generate execution plan.

        Args:
            brief: User's brief text
            flow_type: Type of flow to use

        Returns:
            Execution plan dictionary
        """
        sequence = self.flow_detector.get_flow_sequence(flow_type)
        tasks = self._generate_tasks(sequence, brief, flow_type)

        return {
            'plan_id': self._generate_id(),
            'date': datetime.now().isoformat(),
            'flow_type': flow_type,
            'brief': {
                'original': brief,
                'clarified': self._clarify(brief)
            },
            'tasks': tasks,
            'summary': self._generate_summary(tasks)
        }

    def _generate_id(self) -> str:
        """Generate unique plan ID."""
        return f"PLAN-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"

    def _clarify(self, brief: str) -> str:
        """Clarify brief if needed."""
        # For MVP, return as-is
        # Future: ask clarifying questions if brief is vague
        return brief

    def _generate_tasks(self, sequence: List[int], brief: str, flow_type: str) -> List[Dict]:
        """Generate task list from brain sequence."""
        tasks = []
        dependencies = []

        for i, brain_id in enumerate(sequence):
            task = self._task_for_brain(brain_id, brief, flow_type, i)
            task['dependencies'] = dependencies.copy() if dependencies else []
            task['task_id'] = f"TASK-{i+1:03d}"
            task['priority'] = 10 - i  # Earlier tasks have higher priority

            tasks.append(task)
            dependencies.append(task['task_id'])

        return tasks

    def _task_for_brain(self, brain_id: int, brief: str, flow_type: str, index: int) -> Dict:
        """Generate task definition for a brain."""
        brain_configs = {
            1: {
                'brain_id': 1,
                'brain_name': 'Product Strategy',
                'title': 'Definir estrategia de producto',
                'description': f'Analizar oportunidad y definir estrategia para: {brief[:100]}...',
                'expected_output': 'product-brief',
                'estimated_effort': '30 min'
            },
            2: {
                'brain_id': 2,
                'brain_name': 'UX Research',
                'title': 'Investigación UX',
                'description': 'Entender necesidades del usuario y contexto de uso',
                'expected_output': 'ux-research-report',
                'estimated_effort': '45 min'
            },
            3: {
                'brain_id': 3,
                'brain_name': 'UI Design',
                'title': 'Diseño de interfaz',
                'description': 'Diseñar sistema visual y componentes',
                'expected_output': 'ui-design-system',
                'estimated_effort': '60 min'
            },
            4: {
                'brain_id': 4,
                'brain_name': 'Frontend Development',
                'title': 'Implementación Frontend',
                'description': 'Construir interfaz de usuario',
                'expected_output': 'frontend-implementation',
                'estimated_effort': '2-3 hours'
            },
            5: {
                'brain_id': 5,
                'brain_name': 'Backend Development',
                'title': 'Implementación Backend',
                'description': 'Construir API y lógica de servidor',
                'expected_output': 'backend-implementation',
                'estimated_effort': '2-3 hours'
            },
            6: {
                'brain_id': 6,
                'brain_name': 'QA & DevOps',
                'title': 'Testing y Deploy',
                'description': 'Asegurar calidad y desplegar a producción',
                'expected_output': 'qa-deployment-report',
                'estimated_effort': '1-2 hours'
            },
            7: {
                'brain_id': 7,
                'brain_name': 'Growth & Data (Evaluator)',
                'title': 'Evaluación de calidad',
                'description': 'Evaluar outputs y proporcionar feedback',
                'expected_output': 'evaluation-report',
                'estimated_effort': '5-10 min'
            }
        }

        config = brain_configs.get(brain_id, brain_configs[1])

        return {
            'brain_id': config['brain_id'],
            'brain_name': config['brain_name'],
            'title': config['title'],
            'description': config['description'],
            'inputs': {
                'brief': brief if index == 0 else '[Output from previous task]',
                'flow_type': flow_type
            },
            'expected_output': {
                'schema': config['expected_output'],
                'format': 'yaml'
            },
            'estimated_effort': config['estimated_effort'],
            'status': 'pending'
        }

    def _generate_summary(self, tasks: List[Dict]) -> Dict:
        """Generate plan summary."""
        import re
        total_effort_mins = 0
        for task in tasks:
            effort = task.get('estimated_effort', '0 min')
            # Parse effort (rough estimation)
            # Extract first number from effort string
            match = re.search(r'(\d+)', effort.split()[0] if effort.split() else '0')
            if match:
                value = int(match.group(1))
                if 'hour' in effort.lower():
                    total_effort_mins += value * 60
                elif 'min' in effort.lower():
                    total_effort_mins += value
                else:
                    # Default to minutes if no unit specified
                    total_effort_mins += value

        hours = total_effort_mins // 60
        mins = total_effort_mins % 60

        return {
            'total_tasks': len(tasks),
            'estimated_duration': f"{hours}h {mins}m" if hours > 0 else f"{mins}m",
            'critical_path': [t['task_id'] for t in tasks],
            'brains_involved': list(set([t['brain_id'] for t in tasks]))
        }

    def save_plan(self, plan: Dict, filepath: str):
        """Save plan to YAML file."""
        import yaml
        with open(filepath, 'w') as f:
            yaml.dump(plan, f, default_flow_style=False, sort_keys=False)

    def load_plan(self, filepath: str) -> Dict:
        """Load plan from YAML file."""
        import yaml
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
