"""
Evaluator Module - Brain #7 Evaluation Logic.

Implements the evaluation protocol from skills/evaluator/SKILL.md
"""

import yaml
from typing import Dict, List, Optional
from pathlib import Path


class Evaluator:
    """Brain #7 - Growth & Data (Evaluator)."""

    def __init__(self, skills_dir: str = None):
        """Initialize evaluator.

        Args:
            skills_dir: Path to skills directory (default: skills/evaluator/)
        """
        if skills_dir is None:
            # Assume we're running from project root
            project_root = Path(__file__).parent.parent.parent.parent.parent
            skills_dir = project_root / "skills" / "evaluator"

        self.skills_dir = Path(skills_dir)
        self.matrices_dir = self.skills_dir / "evaluation-matrices"
        self.templates_dir = self.skills_dir / "templates"

        # Load bias catalog and benchmarks
        self.bias_catalog = self._load_yaml("bias-catalog.yaml")
        self.benchmarks = self._load_yaml("benchmarks.yaml")

    def _load_yaml(self, filename: str) -> Dict:
        """Load a YAML file from skills directory."""
        filepath = self.skills_dir / filename
        try:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}

    def load_matrix(self, matrix_id: str) -> Dict:
        """Load an evaluation matrix by ID.

        Args:
            matrix_id: Matrix ID (e.g., 'MATRIX-product-brief')

        Returns:
            Matrix dictionary or error dict
        """
        matrix_file = self.matrices_dir / f"{matrix_id.replace('MATRIX-', '')}.yaml"

        if not matrix_file.exists():
            return {
                'error': f'Matrix not found: {matrix_id}',
                'available_matrices': self._list_matrices()
            }

        try:
            with open(matrix_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            return {
                'error': f'Failed to load matrix: {str(e)}',
                'matrix_id': matrix_id
            }

    def _list_matrices(self) -> List[str]:
        """List available evaluation matrices."""
        if not self.matrices_dir.exists():
            return []

        return [
            f"MATRIX-{f.stem}"
            for f in self.matrices_dir.glob("*.yaml")
        ]

    def evaluate(
        self,
        output: Dict,
        matrix_id: str = "MATRIX-product-brief",
        brain_id: int = 1
    ) -> Dict:
        """
        Evaluate an output using an evaluation matrix.

        Args:
            output: Output dictionary from a brain to evaluate
            matrix_id: ID of evaluation matrix to use
            brain_id: ID of the brain that produced the output

        Returns:
            Evaluation report with:
                - veredict: 'APPROVE' | 'CONDITIONAL' | 'REJECT' | 'ESCALATE'
                - score: Numeric score and percentage
                - summary: 2-3 sentence summary
                - passed_checks: List of passed checks with justification
                - failed_checks: List of failed checks with specific instructions
                - biases: List of biases detected
                - redirect_instructions: What to do next (if not APPROVE)
        """
        # Load the evaluation matrix
        matrix = self.load_matrix(matrix_id)

        if 'error' in matrix:
            return {
                'veredict': 'ESCALATE',
                'score': 0,
                'summary': f"Cannot evaluate: {matrix['error']}",
                'error': matrix['error'],
                'available_matrices': matrix.get('available_matrices', [])
            }

        # Get checks from matrix
        checks = matrix.get('checks', {})

        # Evaluate each category
        all_results = {}
        total_score = 0
        total_possible = matrix.get('scoring', {}).get('total_possible', 100)

        for category, category_checks in checks.items():
            category_results = []
            for check in category_checks:
                result = self._evaluate_check(check, output)
                category_results.append(result)

                # Add to total score if passed
                if result['status'] == 'PASS':
                    total_score += check.get('weight', 0)

            all_results[category] = category_results

        # Calculate percentage
        score_percentage = (total_score / total_possible) * 100

        # Determine veredict
        thresholds = matrix.get('scoring', {}).get('thresholds', {})
        approve_threshold = thresholds.get('approve', 80)
        conditional_threshold = thresholds.get('conditional', 60)

        if score_percentage >= approve_threshold:
            veredict = 'APPROVE'
        elif score_percentage >= conditional_threshold:
            veredict = 'CONDITIONAL'
        else:
            veredict = 'REJECT'

        # Compile results
        passed = []
        failed = []

        for category_results in all_results.values():
            for result in category_results:
                if result['status'] == 'PASS':
                    passed.append({
                        'check_id': result['check_id'],
                        'check': result['check'],
                        'justification': result['justification']
                    })
                else:
                    failed.append({
                        'check_id': result['check_id'],
                        'check': result['check'],
                        'reason': result['reason'],
                        'fix_instruction': result['fix_instruction']
                    })

        # Detect biases
        biases = self._detect_biases(output, failed)

        return {
            'veredict': veredict,
            'score': {
                'points': total_score,
                'total': total_possible,
                'percentage': round(score_percentage, 1)
            },
            'summary': self._generate_summary(veredict, score_percentage, passed, failed),
            'passed_checks': passed,
            'failed_checks': failed,
            'biases_detected': biases,
            'redirect_instructions': self._generate_redirect(veredict, failed, brain_id)
        }

    def _evaluate_check(self, check: Dict, output: Dict) -> Dict:
        """Evaluate a single check against the output.

        Args:
            check: Check definition from matrix
            output: Output to evaluate

        Returns:
            Result dict with status, justification/reason, etc.
        """
        check_id = check['id']
        check_description = check['check']
        pass_criteria = check.get('pass_criteria', '')
        fail_message = check.get('fail_message', '')
        fix_instruction = check.get('fix_instruction', '')

        # For MVP: Simple heuristic evaluation
        # In production, this would use LLM to assess evidence

        # Convert output to text for searching
        output_text = self._output_to_text(output)

        # Look for evidence based on check type
        evidence_found = self._look_for_evidence(check_id, check_description, output_text)

        if evidence_found:
            return {
                'check_id': check_id,
                'check': check_description,
                'status': 'PASS',
                'justification': evidence_found
            }
        else:
            return {
                'check_id': check_id,
                'check': check_description,
                'status': 'FAIL',
                'reason': fail_message,
                'fix_instruction': fix_instruction
            }

    def _output_to_text(self, output: Dict) -> str:
        """Convert output dictionary to searchable text."""
        if isinstance(output, str):
            return output

        # Extract relevant fields
        text_parts = []

        # Common fields in product briefs
        for field in ['problem', 'persona', 'value_proposition', 'key_features',
                      'monetization', 'success_metrics', 'assumptions',
                      'risks', 'evidence', 'analysis']:
            if field in output:
                value = output[field]
                if isinstance(value, list):
                    # Handle list items (could be strings or dicts)
                    for item in value:
                        if isinstance(item, dict):
                            # Extract string values from dict
                            text_parts.extend(str(v) for v in item.values() if v)
                        else:
                            text_parts.append(str(item))
                elif isinstance(value, dict):
                    # Extract string values from dict
                    text_parts.extend(str(v) for v in value.values() if v)
                else:
                    text_parts.append(str(value))

        return ' '.join(text_parts).lower()

    def _look_for_evidence(self, check_id: str, check_desc: str, output_text: str) -> Optional[str]:
        """Look for evidence of a check in the output text.

        Args:
            check_id: Check ID (e.g., 'C1', 'Q2')
            check_desc: Check description
            output_text: Output text to search

        Returns:
            Justification string if evidence found, None otherwise
        """
        # Simple keyword-based heuristics for MVP
        # In production, this would use an LLM to assess evidence quality

        heuristics = {
            # Completeness checks
            'C1': ['problem', 'issue', 'challenge', 'pain point'],
            'C2': ['persona', 'target', 'audience', 'user', 'customer'],
            'C3': ['metric', 'okr', 'kpi', 'retention', 'activation'],
            'C4': ['risk', 'value risk', 'usability', 'feasibility', 'viability'],
            'C5': ['alternative', 'competitor', 'existing solution', 'status quo'],

            # Quality checks
            'Q1': ['interview', 'data', 'evidence', 'research', 'survey'],
            'Q2': ['retention', 'activation', 'engagement', 'nps'],
            'Q3': ['different', 'unique', 'better than', 'vs', 'versus'],
            'Q4': ['framework', 'jobs to be done', 'jtbd', 'model'],
            'Q5': ['tam', 'sam', 'som', 'market size', 'billion'],

            # Intellectual honesty checks
            'H1': ['dont know', 'unknown', 'uncertain', 'assumption', 'todo'],
            'H2': ['hypothesis', 'assume', 'believe', 'estimate'],
            'H3': ['pre-mortem', 'fail', 'failure risk', 'why might'],
            'H4': ['confidence', 'range', 'uncertainty'],
            'H5': ['counter', 'opposite', 'contrary', 'however', 'but'],

            # Commercial viability checks
            'V1': ['pay', 'willingness', 'pre-order', 'commit', 'waitlist'],
            'V2': ['ltv', 'cac', 'unit economics', 'arpu'],
            'V3': ['growth', 'sticky', 'viral', 'paid'],
            'V4': ['benchmark', 'industry standard', 'typical'],
            'V5': ['revenue', 'pricing', 'monetization', 'freemium', 'subscription']
        }

        keywords = heuristics.get(check_id, [])

        # Check if any keyword is present
        found_keywords = [kw for kw in keywords if kw.lower() in output_text]

        if found_keywords:
            return f"Evidence found: mentions {', '.join(found_keywords[:3])}"

        return None

    def _detect_biases(self, output: Dict, failed_checks: List[Dict]) -> List[Dict]:
        """Detect cognitive biases in the output.

        Args:
            output: Output to analyze
            failed_checks: Checks that failed (may indicate bias)

        Returns:
            List of detected biases with details
        """
        biases = []
        output_text = self._output_to_text(output)

        # Simple bias detection heuristics
        bias_signals = {
            'BIAS-01': {  # Confirmation Bias
                'signals': ['only', 'just', 'proves', 'confirms', 'all agree'],
                'name': 'Confirmation Bias',
                'question': 'What evidence contradicts this?'
            },
            'BIAS-07': {  # WYSIATI
                'signals': ['clearly', 'obviously', 'definitely', 'certainly'],
                'name': 'WYSIATI (What You See Is All There Is)',
                'question': 'What information are you missing?'
            },
            'BIAS-08': {  # Planning Fallacy
                'signals': ['easily', 'quickly', 'simple', 'just add'],
                'name': 'Planning Fallacy',
                'question': 'What historical data supports this timeline?'
            }
        }

        for bias_id, info in bias_signals.items():
            for signal in info['signals']:
                if signal.lower() in output_text:
                    biases.append({
                        'bias_id': bias_id,
                        'name': info['name'],
                        'signal': signal,
                        'question': info['question']
                    })
                    break  # Only report each bias once

        return biases

    def _generate_summary(
        self,
        veredict: str,
        score_percentage: float,
        passed: List[Dict],
        failed: List[Dict]
    ) -> str:
        """Generate evaluation summary."""
        passed_count = len(passed)
        failed_count = len(failed)
        total = passed_count + failed_count

        if veredict == 'APPROVE':
            return f"""Output approved with score of {score_percentage:.0f}%.
{passed_count} of {total} checks passed. The output meets quality standards."""
        elif veredict == 'CONDITIONAL':
            return f"""Output requires improvements (score: {score_percentage:.0f}%).
{passed_count} of {total} checks passed. {failed_count} specific issues need addressing."""
        else:
            return f"""Output rejected (score: {score_percentage:.0f}%).
{failed_count} critical issues found. The output needs fundamental rework."""

    def _generate_redirect(self, veredict: str, failed: List[Dict], brain_id: int) -> Optional[Dict]:
        """Generate redirect instructions for non-APPROVE verdicts."""
        if veredict == 'APPROVE':
            return None

        # Collect fix instructions from failed checks
        fixes = [check['fix_instruction'] for check in failed if check.get('fix_instruction')]

        return {
            'to_brain': f'0{brain_id}',
            'action': 'REDO' if veredict == 'REJECT' else 'ITERATE',
            'specific_fixes': fixes[:5],  # Limit to top 5
            'max_iterations': 3
        }
