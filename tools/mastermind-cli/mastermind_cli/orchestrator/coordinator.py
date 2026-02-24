"""
Coordinator - Main orchestration coordinator.
"""

import os
import yaml
from typing import Dict, Optional

from .flow_detector import FlowDetector
from .plan_generator import PlanGenerator
from .brain_executor import BrainExecutor
from .output_formatter import OutputFormatter


class Coordinator:
    """Main orchestration coordinator."""

    def __init__(self, formatter: Optional[OutputFormatter] = None):
        """Initialize coordinator."""
        self.flow_detector = FlowDetector()
        self.plan_generator = PlanGenerator(self.flow_detector)
        self.brain_executor = BrainExecutor()
        self.formatter = formatter or OutputFormatter()

        # Execution state
        self.current_plan = None
        self.execution_results = {}
        self.rejection_counters = {}

    def orchestrate(
        self,
        brief: str,
        flow: Optional[str] = None,
        dry_run: bool = False,
        output_file: Optional[str] = None
    ) -> Dict:
        """
        Main orchestration entry point.

        Args:
            brief: User's brief text
            flow: Force specific flow (optional)
            dry_run: Generate plan without executing
            output_file: Save output to file

        Returns:
            Execution report
        """
        # Step 1: Detect or validate flow
        if not flow:
            flow = self.flow_detector.detect(brief)
        elif not self.flow_detector.validate_flow(flow):
            return self._error_report(f"Invalid flow type: {flow}")

        # Step 2: Generate execution plan
        self.current_plan = self.plan_generator.generate(brief, flow)

        # Step 3: If dry_run, print plan and exit
        if dry_run:
            plan_output = self.formatter.format_execution_plan(self.current_plan)
            if output_file:
                self._save_output(plan_output, output_file)
            return {
                'status': 'dry_run_complete',
                'plan': self.current_plan,
                'output': plan_output
            }

        # Step 4: Execute tasks
        execution_report = self._execute_plan()

        # Step 5: Format and deliver final result
        final_output = self.formatter.format_final_deliverable(execution_report)

        if output_file:
            self._save_output(final_output, output_file)

        return execution_report

    def _execute_plan(self) -> Dict:
        """Execute the current plan."""
        plan_id = self.current_plan['plan_id']
        tasks = self.current_plan['tasks']

        completed_tasks = 0
        outputs = {}
        evaluations = {}

        for task in tasks:
            task_id = task['task_id']
            brain_id = task['brain_id']

            # Check if brain is available
            if not self.brain_executor.is_brain_available(brain_id):
                print(self.formatter.format_warning(
                    f"Brain #{brain_id} is not implemented. Skipping."
                ))
                # For MVP, we'll mark as skipped and continue if it's not brain 1 or 7
                if brain_id not in [1, 7]:
                    outputs[task_id] = f"Skipped: Brain #{brain_id} not implemented"
                    completed_tasks += 1
                    continue
                else:
                    # Brain 1 or 7 must be available
                    return self._error_report(
                        f"Brain #{brain_id} is required but not implemented."
                    )

            # Print task start
            print(self.formatter.format_task_start(task))

            # Execute brain
            result = self.brain_executor.execute(brain_id, task)

            # Format and print brain output
            print(self.formatter.format_brain_output(result, task))

            # Store output
            outputs[task_id] = result.get('output', {})

            # If this is Brain #7 (evaluator), format evaluation
            if brain_id == 7:
                print(self.formatter.format_evaluation_result(result))
                evaluations[task_id] = result

                # Check veredict
                veredict = result.get('veredict', 'PLACEHOLDER')

                if veredict == 'REJECT':
                    # In full implementation, would re-assign to previous brain
                    print(self.formatter.format_warning(
                        "Output rejected. In full implementation, would re-assign to brain."
                    ))
                elif veredict == 'ESCALATE':
                    print(self.formatter.format_warning(
                        "Escalation required. Stopping execution."
                    ))
                    break

            completed_tasks += 1

        return {
            'plan_id': plan_id,
            'status': 'completed',
            'tasks_completed': completed_tasks,
            'tasks_total': len(tasks),
            'outputs': outputs,
            'evaluations': evaluations,
            'final_deliverable': self._generate_deliverable(outputs)
        }

    def _generate_deliverable(self, outputs: Dict) -> str:
        """Generate final deliverable from outputs."""
        if not outputs:
            return "No outputs generated."

        # Find the main strategy output (from Brain #1)
        strategy_output = outputs.get('TASK-001', {})

        if isinstance(strategy_output, dict):
            if strategy_output.get('persona'):
                return f"""
# Product Strategy Summary

**Persona:** {strategy_output.get('persona', {}).get('name', 'N/A')}
**Value Proposition:** {strategy_output.get('value_proposition', 'N/A')}

**Key Features:**
{chr(10).join(f"- {f}" for f in strategy_output.get('key_features', []))}

**Monetization:** {strategy_output.get('monetization', 'N/A')}
"""
            elif strategy_output.get('note'):
                return f"""
# Product Strategy

{strategy_output.get('note')}

*This is placeholder output. Full implementation would query NotebookLM.*
"""

        return "Orchestration complete. See outputs above."

    def _error_report(self, error: str) -> Dict:
        """Generate error report."""
        return {
            'status': 'error',
            'error': error,
            'plan': self.current_plan
        }

    def _save_output(self, output: str, filepath: str):
        """Save output to file."""
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(output)

    def continue_plan(self, plan_id: str, plan_file: str) -> Dict:
        """Continue execution from a saved plan."""
        # Load plan
        try:
            self.current_plan = self.plan_generator.load_plan(plan_file)
        except FileNotFoundError:
            return self._error_report(f"Plan file not found: {plan_file}")

        # Execute remaining tasks
        return self._execute_plan()
