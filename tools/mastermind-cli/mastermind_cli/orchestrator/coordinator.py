"""
Coordinator - Main orchestration coordinator with iteration loop.
"""

import os
from typing import Dict, Optional

from .flow_detector import FlowDetector
from .plan_generator import PlanGenerator
from .brain_executor import BrainExecutor
from .output_formatter import OutputFormatter


class Coordinator:
    """Main orchestration coordinator with iteration support."""

    MAX_ITERATIONS = 3

    def __init__(
        self, formatter: Optional[OutputFormatter] = None, use_mcp: bool = False
    ):
        """Initialize coordinator.

        Args:
            formatter: Output formatter
            use_mcp: Whether to use MCP for real NotebookLM calls
        """
        from .mcp_integration import MCPIntegration

        self.flow_detector = FlowDetector()
        self.plan_generator = PlanGenerator(self.flow_detector)
        self.mcp_integration = MCPIntegration(use_mcp=use_mcp)
        self.brain_executor = BrainExecutor(mcp_client=self.mcp_integration)
        self.formatter = formatter or OutputFormatter()

        # Execution state
        self.current_plan = None
        self.execution_results = {}
        self.iteration_count = 0
        self.rejection_count = 0
        self.use_mcp = use_mcp

    def orchestrate(
        self,
        brief: str,
        flow: Optional[str] = None,
        dry_run: bool = False,
        output_file: Optional[str] = None,
        max_iterations: int = MAX_ITERATIONS,
        use_mcp: bool = False,
    ) -> Dict:
        """
        Main orchestration entry point with iteration support.

        Args:
            brief: User's brief text
            flow: Force specific flow (optional)
            dry_run: Generate plan without executing
            output_file: Save output to file
            max_iterations: Maximum iteration attempts (default: 3)
            use_mcp: Use MCP for real NotebookLM calls (default: False)

        Returns:
            Execution report
        """
        self.iteration_count = 0
        self.rejection_count = 0
        self.use_mcp = use_mcp

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
                "status": "dry_run_complete",
                "plan": self.current_plan,
                "output": plan_output,
            }

        # Step 4: Execute with iteration loop
        execution_report = self._execute_with_iterations(max_iterations)

        # Step 5: Format and deliver final result
        final_output = self.formatter.format_final_deliverable(execution_report)

        if output_file:
            self._save_output(final_output, output_file)

        return execution_report

    def _execute_with_iterations(self, max_iterations: int) -> Dict:
        """Execute the current plan with iteration support."""
        tasks = self.current_plan["tasks"]

        # For validation_only flow: Brain #1 → Brain #7 (with possible iteration)
        # For other flows: Execute all tasks with Brain #7 at the end

        # Check if this is a validation flow (just #1 → #7)
        is_validation_flow = (
            len(tasks) == 2 and tasks[0]["brain_id"] == 1 and tasks[1]["brain_id"] == 7
        )

        if is_validation_flow:
            # Use iteration loop for validation
            return self._execute_validation_flow(tasks, max_iterations)
        else:
            # Standard flow execution
            return self._execute_standard_flow(tasks)

    def _execute_validation_flow(self, tasks: list, max_iterations: int) -> Dict:
        """Execute validation flow (Brain #1 → Brain #7) with iteration."""
        plan_id = self.current_plan["plan_id"]

        outputs = {}
        evaluations = {}

        for iteration in range(1, max_iterations + 1):
            self.iteration_count = iteration

            if iteration > 1:
                print(self.formatter.format_iteration_start(iteration, max_iterations))

            # --- Task 1: Brain #1 (Product Strategy) ---
            task_1 = tasks[0]
            print(self.formatter.format_task_start(task_1))

            # Add context from previous iterations if any
            if iteration > 1 and evaluations:
                last_eval = list(evaluations.values())[-1]
                redirect = last_eval.get("redirect_instructions")
                if redirect:
                    task_1["inputs"]["feedback"] = redirect.get("specific_fixes", [])
                    task_1["inputs"]["iteration"] = iteration

            result_1 = self.brain_executor.execute(1, task_1, use_mcp=self.use_mcp)
            print(self.formatter.format_brain_output(result_1, task_1))

            outputs["TASK-001"] = result_1.get("output", {})

            # --- Task 2: Brain #7 (Evaluator) ---
            task_7 = tasks[1]
            task_7["output_to_evaluate"] = result_1.get("output", {})
            task_7["previous_brain_id"] = 1

            print(self.formatter.format_task_start(task_7))
            result_7 = self.brain_executor.execute(
                7, task_7, use_mcp=False
            )  # Evaluator uses local logic

            # Format evaluation result
            print(self.formatter.format_evaluation_result(result_7))

            evaluations["TASK-002"] = result_7
            outputs["TASK-002"] = result_7

            # Check veredict
            veredict = result_7.get("veredict", "UNKNOWN")

            if veredict == "APPROVE":
                # Success! Exit iteration loop
                self.rejection_count = 0
                return {
                    "plan_id": plan_id,
                    "status": "completed",
                    "tasks_completed": 2,
                    "tasks_total": 2,
                    "iterations": iteration,
                    "outputs": outputs,
                    "evaluations": evaluations,
                    "final_deliverable": self._generate_deliverable(
                        outputs, evaluations
                    ),
                    "veredict": "APPROVE",
                }

            elif veredict == "CONDITIONAL":
                # Try one more iteration with fixes
                if iteration < max_iterations:
                    print(
                        self.formatter.format_info(
                            f"Conditional approval. Applying fixes and retrying... ({iteration}/{max_iterations})"
                        )
                    )
                    continue
                else:
                    print(
                        self.formatter.format_warning(
                            f"Reached max iterations ({max_iterations}) with conditional approval."
                        )
                    )
                    return {
                        "plan_id": plan_id,
                        "status": "completed",
                        "tasks_completed": 2,
                        "tasks_total": 2,
                        "iterations": iteration,
                        "outputs": outputs,
                        "evaluations": evaluations,
                        "final_deliverable": self._generate_deliverable(
                            outputs, evaluations
                        ),
                        "veredict": "CONDITIONAL",
                    }

            elif veredict == "REJECT":
                self.rejection_count += 1

                # Check for escalation
                if self.rejection_count >= 3:
                    print(
                        self.formatter.format_escalation_notice(
                            "3rd consecutive rejection. This brief requires human review."
                        )
                    )
                    return {
                        "plan_id": plan_id,
                        "status": "escalated",
                        "tasks_completed": 2,
                        "tasks_total": 2,
                        "iterations": iteration,
                        "outputs": outputs,
                        "evaluations": evaluations,
                        "final_deliverable": self._generate_deliverable(
                            outputs, evaluations
                        ),
                        "veredict": "ESCALATE",
                        "escalation_reason": "3rd consecutive rejection",
                    }

                # Try again if we have iterations left
                if iteration < max_iterations:
                    print(
                        self.formatter.format_info(
                            f"Rejected. Re-submitting with feedback... ({iteration}/{max_iterations})"
                        )
                    )
                    continue
                else:
                    # Max iterations reached, still rejected
                    print(
                        self.formatter.format_warning(
                            f"Reached max iterations ({max_iterations}) with rejection."
                        )
                    )
                    return {
                        "plan_id": plan_id,
                        "status": "completed",
                        "tasks_completed": 2,
                        "tasks_total": 2,
                        "iterations": iteration,
                        "outputs": outputs,
                        "evaluations": evaluations,
                        "final_deliverable": self._generate_deliverable(
                            outputs, evaluations
                        ),
                        "veredict": "REJECT",
                    }

            elif veredict == "ESCALATE":
                # Immediate escalation
                print(
                    self.formatter.format_escalation_notice(
                        result_7.get("evaluation", {}).get(
                            "summary", "Evaluator requested escalation."
                        )
                    )
                )
                return {
                    "plan_id": plan_id,
                    "status": "escalated",
                    "tasks_completed": 2,
                    "tasks_total": 2,
                    "iterations": iteration,
                    "outputs": outputs,
                    "evaluations": evaluations,
                    "final_deliverable": self._generate_deliverable(
                        outputs, evaluations
                    ),
                    "veredict": "ESCALATE",
                    "escalation_reason": "Evaluator requested escalation",
                }

        # Should not reach here, but fallback
        return {
            "plan_id": plan_id,
            "status": "error",
            "error": "Unexpected end of iteration loop",
            "outputs": outputs,
            "evaluations": evaluations,
        }

    def _execute_standard_flow(self, tasks: list) -> Dict:
        """Execute standard flow (all tasks in sequence)."""
        plan_id = self.current_plan["plan_id"]

        completed_tasks = 0
        outputs = {}
        evaluations = {}

        for task in tasks:
            task_id = task["task_id"]
            brain_id = task["brain_id"]

            # Check if brain is available
            if not self.brain_executor.is_brain_available(brain_id):
                print(
                    self.formatter.format_warning(
                        f"Brain #{brain_id} is not implemented. Skipping."
                    )
                )
                if brain_id not in [1, 7]:
                    outputs[task_id] = f"Skipped: Brain #{brain_id} not implemented"
                    completed_tasks += 1
                    continue
                else:
                    return self._error_report(
                        f"Brain #{brain_id} is required but not implemented."
                    )

            # Print task start
            print(self.formatter.format_task_start(task))

            # Execute brain (use MCP only for non-evaluator brains)
            use_mcp_for_brain = self.use_mcp if brain_id != 7 else False
            result = self.brain_executor.execute(
                brain_id, task, use_mcp=use_mcp_for_brain
            )

            # Format and print brain output
            print(self.formatter.format_brain_output(result, task))

            # Store output
            outputs[task_id] = result.get("output", {})

            # If this is Brain #7 (evaluator), format evaluation
            if brain_id == 7:
                print(self.formatter.format_evaluation_result(result))
                evaluations[task_id] = result

                # Check veredict - may want to stop early
                veredict = result.get("veredict", "PLACEHOLDER")
                if veredict == "ESCALATE":
                    print(
                        self.formatter.format_escalation_notice(
                            "Evaluator requested escalation."
                        )
                    )
                    break

            completed_tasks += 1

        return {
            "plan_id": plan_id,
            "status": "completed",
            "tasks_completed": completed_tasks,
            "tasks_total": len(tasks),
            "outputs": outputs,
            "evaluations": evaluations,
            "final_deliverable": self._generate_deliverable(outputs, evaluations),
        }

    def _generate_deliverable(self, outputs: Dict, evaluations: Dict) -> str:
        """Generate final deliverable from outputs."""
        if not outputs:
            return "No outputs generated."

        # Find the main strategy output (from Brain #1)
        strategy_output = outputs.get("TASK-001", {})

        if not strategy_output:
            return "Orchestration complete. See outputs above."

        lines = []
        lines.append("# Product Strategy Summary")
        lines.append("")

        if isinstance(strategy_output, dict):
            # Persona
            if strategy_output.get("persona"):
                persona = strategy_output["persona"]
                if isinstance(persona, dict):
                    lines.append(f"**Target Persona:** {persona.get('name', 'N/A')}")
                    if persona.get("description"):
                        lines.append(f"{persona['description']}")
                    lines.append("")

            # Value Proposition
            if strategy_output.get("value_proposition"):
                lines.append(
                    f"**Value Proposition:** {strategy_output['value_proposition']}"
                )
                lines.append("")

            # Key Features
            if strategy_output.get("key_features"):
                features = strategy_output["key_features"]
                lines.append("**Key Features:**")
                if isinstance(features, list):
                    for feature in features[:5]:  # Limit to top 5
                        if isinstance(feature, dict):
                            name = feature.get(
                                "feature", feature.get("name", "Unknown")
                            )
                            priority = feature.get("priority", "")
                            lines.append(
                                f"- {name} ({priority})" if priority else f"- {name}"
                            )
                        else:
                            lines.append(f"- {feature}")
                lines.append("")

            # Success Metrics
            if strategy_output.get("success_metrics"):
                metrics = strategy_output["success_metrics"]
                lines.append("**Success Metrics:**")
                if isinstance(metrics, list):
                    for metric in metrics[:5]:
                        if isinstance(metric, dict):
                            name = metric.get("metric", "Unknown")
                            target = metric.get("target", "")
                            confidence = metric.get("confidence", "")
                            lines.append(
                                f"- {name}: {target} (confidence: {confidence})"
                            )
                lines.append("")

            # Risks
            if strategy_output.get("risks"):
                risks = strategy_output["risks"]
                lines.append("**Key Risks:**")
                if isinstance(risks, dict):
                    for risk_type, description in risks.items():
                        lines.append(f"- **{risk_type}:** {description}")
                lines.append("")

        return "\n".join(lines)

    def _error_report(self, error: str) -> Dict:
        """Generate error report."""
        return {"status": "error", "error": error, "plan": self.current_plan}

    def _save_output(self, output: str, filepath: str):
        """Save output to file."""
        os.makedirs(
            os.path.dirname(filepath) if os.path.dirname(filepath) else ".",
            exist_ok=True,
        )
        with open(filepath, "w") as f:
            f.write(output)

    def continue_plan(self, plan_id: str, plan_file: str) -> Dict:
        """Continue execution from a saved plan."""
        # Load plan
        try:
            self.current_plan = self.plan_generator.load_plan(plan_file)
        except FileNotFoundError:
            return self._error_report(f"Plan file not found: {plan_file}")

        # Execute remaining tasks
        return self._execute_standard_flow(self.current_plan["tasks"])
