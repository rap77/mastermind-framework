"""
Flow Detector - Detects which flow to use based on brief content.
"""

from typing import Optional


class FlowDetector:
    """Detects which flow to use based on brief content."""

    # Flow triggers from agents/orchestrator/config/flows.yaml
    FLOW_TRIGGERS = {
        'full_product': [
            'nuevo proyecto', 'app completa', 'producto desde cero',
            'startup', 'crear una app', 'nuevo producto', 'nueva app',
            'desarrollar una app', 'construir una app'
        ],
        'validation_only': [
            'validar idea', 'es buena idea', 'viabilidad',
            'feedback concepto', 'market fit', 'opinión sobre',
            'crees que', 'funcionaría', 'vale la pena'
        ],
        'design_sprint': [
            'diseñar', 'prototipar', 'wireframe', 'mockup',
            'design sprint', 'diseño de interfaz', 'diseñar ux',
            'diseñar ui', 'prototipo'
        ],
        'build_feature': [
            'implementar', 'construir', 'codificar', 'feature',
            'desarrollar', 'programar', 'crear feature'
        ],
        'optimization': [
            'optimizar', 'mejorar', 'crecimiento', 'métricas',
            'performance', 'retención', 'aumentar', 'reducir'
        ],
        'technical_review': [
            'auditoría técnica', 'revisión de código', 'qa',
            'seguridad', 'refactor', 'revisar código'
        ]
    }

    def __init__(self):
        """Initialize flow detector."""
        self.flow_config = None
        self._load_flows()

    def _load_flows(self):
        """Load flow configuration from YAML."""
        import yaml
        try:
            with open('agents/orchestrator/config/flows.yaml', 'r') as f:
                self.flow_config = yaml.safe_load(f)
        except FileNotFoundError:
            # Use hardcoded triggers if config not found
            pass

    def detect(self, brief: str) -> str:
        """
        Detect flow from brief text.

        Args:
            brief: User's brief text

        Returns:
            Flow type (e.g., 'full_product', 'validation_only')
        """
        brief_lower = brief.lower()

        # Count matches for each flow
        flow_scores = {}
        for flow, triggers in self.FLOW_TRIGGERS.items():
            score = sum(1 for trigger in triggers if trigger in brief_lower)
            if score > 0:
                flow_scores[flow] = score

        # Return flow with highest score
        if flow_scores:
            return max(flow_scores, key=flow_scores.get)

        # Default to validation_only if no matches
        return 'validation_only'

    def get_flow_sequence(self, flow_type: str) -> list:
        """
        Get brain sequence for a flow.

        Args:
            flow_type: Flow type name

        Returns:
            List of brain IDs in sequence
        """
        if self.flow_config and 'flows' in self.flow_config:
            flow = self.flow_config['flows'].get(flow_type)
            if flow:
                return flow.get('sequence', [])

        # Fallback sequences
        sequences = {
            'full_product': [1, 2, 3, 4, 5, 6, 7],
            'validation_only': [1, 7],
            'design_sprint': [1, 2, 3, 7],
            'build_feature': [4, 5, 6, 7],
            'optimization': [7, 1],
            'technical_review': [5, 6, 7],
        }
        return sequences.get(flow_type, [1, 7])

    def get_available_flows(self) -> list:
        """Get list of available flow types."""
        if self.flow_config and 'flows' in self.flow_config:
            return list(self.flow_config['flows'].keys())
        return list(self.FLOW_TRIGGERS.keys())

    def validate_flow(self, flow_type: str) -> bool:
        """Check if a flow type is valid."""
        return flow_type in self.get_available_flows()
