"""
Coordinator - Main orchestration coordinator with iteration loop.
"""

import os
from typing import Any

from .flow_detector import FlowDetector
from .plan_generator import PlanGenerator
from .brain_executor import BrainExecutor
from .output_formatter import OutputFormatter
from ..memory import EvaluationLogger


class Coordinator:
    """Main orchestration coordinator with iteration support."""

    FLOW_DISCOVERY = "discovery"
    MAX_ITERATIONS = 3

    def __init__(
        self,
        formatter: OutputFormatter | None = None,
        use_mcp: bool = False,
        enable_logging: bool = True
    ) -> None:
        """Initialize coordinator.

        Args:
            formatter: Output formatter
            use_mcp: Whether to use MCP for real NotebookLM calls
            enable_logging: Whether to enable evaluation logging
        """
        from .mcp_integration import MCPIntegration

        self.flow_detector = FlowDetector()
        self.plan_generator = PlanGenerator(self.flow_detector)  # type: ignore[no-untyped-call]
        self.mcp_integration = MCPIntegration(use_mcp=use_mcp)
        self.brain_executor = BrainExecutor(mcp_client=self.mcp_integration)
        self.formatter = formatter or OutputFormatter()
        self.eval_logger = EvaluationLogger(enabled=enable_logging) if enable_logging else None

        # Execution state
        self.current_plan: dict[str, Any] | None = None
        self.execution_results: dict[str, Any] = {}
        self.iteration_count = 0
        self.rejection_count = 0
        self.use_mcp = use_mcp

    def orchestrate(
        self,
        brief: str,
        flow: str | None = None,
        dry_run: bool = False,
        output_file: str | None = None,
        max_iterations: int = MAX_ITERATIONS,
        use_mcp: bool = False
    ) -> dict[str, Any]:
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
            flow = self._detect_flow(brief)
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

        # Step 4: Execute with iteration loop
        execution_report = self._execute_with_iterations(max_iterations)

        # Step 5: Format and deliver final result
        final_output = self.formatter.format_final_deliverable(execution_report)

        if output_file:
            self._save_output(final_output, output_file)

        return execution_report

    def _execute_with_iterations(self, max_iterations: int) -> dict[str, Any]:
        """Execute the current plan with iteration support."""
        if self.current_plan is None:
            return self._error_report("No plan generated")
        tasks = self.current_plan['tasks']

        # For validation_only flow: Brain #1 → Brain #7 (with possible iteration)
        # For other flows: Execute all tasks with Brain #7 at the end

        # Check if this is a validation flow (just #1 → #7)
        is_validation_flow = (
            len(tasks) == 2 and
            tasks[0]['brain_id'] == 1 and
            tasks[1]['brain_id'] == 7
        )

        # Check if this is a discovery flow
        is_discovery_flow = self.current_plan.get('flow_type') == self.FLOW_DISCOVERY

        if is_discovery_flow:
            # Use discovery flow with Brain #8
            brief = self.current_plan['brief']['original']
            return self._execute_discovery_flow(brief)
        elif is_validation_flow:
            # Use iteration loop for validation
            return self._execute_validation_flow(tasks, max_iterations)
        else:
            # Standard flow execution
            return self._execute_standard_flow(tasks)

    def _execute_discovery_flow(self, brief: str) -> dict[str, Any]:
        """
        Execute discovery interview with Brain #8.

        This is the main entry point for the discovery flow.

        Args:
            brief: User's brief text

        Returns:
            Execution report with Q&A document and recommendations
        """
        plan_id = self._generate_session_id()

        print(self.formatter.format_info("🎤 Starting Discovery Interview with Brain #8"))
        print(self.formatter.format_separator())

        try:
            # Step 1: Generate interview plan via Brain #8
            print(self.formatter.format_info("Step 1: Generating interview strategy..."))
            interview_plan = self._generate_interview_plan(brief)

            if not interview_plan or interview_plan.get('status') == 'error':
                return self._error_report("Failed to generate interview plan")

            print(self.formatter.format_interview_plan(interview_plan))

            # Step 2: Execute iterative interview
            print(self.formatter.format_info("Step 2: Conducting interview..."))
            print(self.formatter.format_info("(Type your answers. Press Ctrl+C to end interview early)"))
            print(self.formatter.format_separator())

            interview_doc = self._conduct_interview(interview_plan, brief)

            # Step 3: Generate final deliverable
            print(self.formatter.format_separator())
            print(self.formatter.format_info("Step 3: Generating final recommendations..."))

            # Format the interview document as deliverable
            deliverable = self._format_interview_deliverable(interview_doc)

            print(self.formatter.format_interview_complete(interview_doc))
            print(deliverable)

            # Step 4: Log interview (if enabled)
            if self.eval_logger:
                try:
                    # Try to use interview logger if available
                    # Fallback: log as evaluation
                    self._log_interview_as_evaluation(interview_doc, brief)
                except Exception as e:
                    print(f"Warning: Could not log interview: {e}")

            return {
                'plan_id': plan_id,
                'status': 'completed',
                'flow_type': 'discovery',
                'interview_document': interview_doc,
                'final_deliverable': deliverable,
                'message': 'Discovery interview completed successfully'
            }

        except KeyboardInterrupt:
            print(self.formatter.format_warning("\nInterview interrupted by user."))
            return {
                'plan_id': plan_id,
                'status': 'interrupted',
                'flow_type': 'discovery',
                'message': 'Discovery interview interrupted by user'
            }
        except Exception as e:
            return self._error_report(f"Discovery flow error: {str(e)}")

    def _format_interview_deliverable(self, interview_doc: dict[str, Any]) -> str:
        """Format interview document as final deliverable."""
        lines = []
        lines.append("# Discovery Interview Results")
        lines.append("")

        # Metadata
        metadata = interview_doc.get('metadata', {})
        lines.append("## Interview Metadata")
        lines.append(f"- **Session ID:** {metadata.get('session_id', 'unknown')}")
        lines.append(f"- **Date:** {metadata.get('timestamp', 'unknown')}")
        lines.append(f"- **Original Brief:** {metadata.get('brief', 'N/A')}")
        lines.append("")

        # Summary
        outcome = interview_doc.get('outcome', {})
        lines.append("## Summary")
        lines.append(f"- **Questions Asked:** {outcome.get('total_questions_asked', 0)}")
        lines.append(f"- **Categories Explored:** {outcome.get('categories_completed', 0)}")
        lines.append("")

        # Q&A by Category
        lines.append("## Questions & Answers")
        lines.append("")

        qa_pairs = interview_doc.get('qa_pairs', [])
        if qa_pairs:
            # Group by category
            by_category: dict[str, list[dict[str, Any]]] = {}
            for qa in qa_pairs:
                cat = qa.get('category', 'General')
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(qa)

            for cat, items in by_category.items():
                lines.append(f"### {cat}")
                lines.append("")

                for i, qa in enumerate(items, 1):
                    lines.append(f"**Q{i}:** {qa.get('question', '')}")
                    lines.append("")
                    lines.append(f"**A{i}:** {qa.get('user_answer', '')}")
                    lines.append("")

                    # Add follow-up insights if available
                    follow_up = qa.get('follow_up', {})
                    insights = follow_up.get('insights', [])
                    if insights:
                        lines.append(f"*Insights:* {', '.join(insights[:3])}")
                        lines.append("")
                    lines.append("")

        return "\n".join(lines)

    def _log_interview_as_evaluation(self, interview_doc: dict[str, Any], brief: str) -> None:
        """Log interview as evaluation for tracking."""
        if not self.eval_logger:
            return

        outcome = interview_doc.get('outcome', {})
        metadata = interview_doc.get('metadata', {})

        # Convert interview to evaluation format
        self.eval_logger.log_evaluation(
            project=metadata.get('session_id', 'discovery'),
            brief=brief,
            flow_type='discovery',
            score_total=outcome.get('total_questions_asked', 0),
            score_max=50,  # Arbitrary scale
            verdict='APPROVE',
            issues=[],  # No issues in discovery
            strengths=[
                f"Explored {outcome.get('categories_completed', 0)} categories",
                f"Asked {outcome.get('total_questions_asked', 0)} questions"
            ],
            full_output=self._format_interview_deliverable(interview_doc),
            tags=['discovery', 'brain_8'],
            brains_involved=[8] + [
                qa.get('brain', 0) for qa in interview_doc.get('qa_pairs', [])
            ]
        )

    def _execute_validation_flow(self, tasks: list[dict[str, Any]], max_iterations: int) -> dict[str, Any]:
        """Execute validation flow (Brain #1 → Brain #7) with iteration."""
        if self.current_plan is None:
            return self._error_report("No plan available")
        plan_id = self.current_plan['plan_id']
        brief = self.current_plan['brief']['original']

        outputs: dict[str, Any] = {}
        evaluations: dict[str, Any] = {}

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
                redirect = last_eval.get('redirect_instructions')
                if redirect:
                    task_1['inputs']['feedback'] = redirect.get('specific_fixes', [])
                    task_1['inputs']['iteration'] = iteration

            result_1 = self.brain_executor.execute(1, task_1, use_mcp=self.use_mcp)
            print(self.formatter.format_brain_output(result_1, task_1))

            outputs['TASK-001'] = result_1.get('output', {})

            # --- Task 2: Brain #7 (Evaluator) ---
            task_7 = tasks[1]
            task_7['output_to_evaluate'] = result_1.get('output', {})
            task_7['previous_brain_id'] = 1

            print(self.formatter.format_task_start(task_7))
            result_7 = self.brain_executor.execute(7, task_7, use_mcp=False)  # Evaluator uses local logic

            # Format evaluation result
            print(self.formatter.format_evaluation_result(result_7))

            # Log evaluation if enabled
            if self.eval_logger:
                self._log_evaluation(result_7, brief, self.current_plan.get('flow_type', 'validation_only'))

            evaluations['TASK-002'] = result_7
            outputs['TASK-002'] = result_7

            # Check veredict
            veredict = result_7.get('veredict', 'UNKNOWN')

            if veredict == 'APPROVE':
                # Success! Exit iteration loop
                self.rejection_count = 0
                return {
                    'plan_id': plan_id,
                    'status': 'completed',
                    'tasks_completed': 2,
                    'tasks_total': 2,
                    'iterations': iteration,
                    'outputs': outputs,
                    'evaluations': evaluations,
                    'final_deliverable': self._generate_deliverable(outputs, evaluations),
                    'veredict': 'APPROVE'
                }

            elif veredict == 'CONDITIONAL':
                # Try one more iteration with fixes
                if iteration < max_iterations:
                    print(self.formatter.format_info(
                        f"Conditional approval. Applying fixes and retrying... ({iteration}/{max_iterations})"
                    ))
                    continue
                else:
                    print(self.formatter.format_warning(
                        f"Reached max iterations ({max_iterations}) with conditional approval."
                    ))
                    return {
                        'plan_id': plan_id,
                        'status': 'completed',
                        'tasks_completed': 2,
                        'tasks_total': 2,
                        'iterations': iteration,
                        'outputs': outputs,
                        'evaluations': evaluations,
                        'final_deliverable': self._generate_deliverable(outputs, evaluations),
                        'veredict': 'CONDITIONAL'
                    }

            elif veredict == 'REJECT':
                self.rejection_count += 1

                # Check for escalation
                if self.rejection_count >= 3:
                    print(self.formatter.format_escalation_notice(
                        "3rd consecutive rejection. This brief requires human review."
                    ))
                    return {
                        'plan_id': plan_id,
                        'status': 'escalated',
                        'tasks_completed': 2,
                        'tasks_total': 2,
                        'iterations': iteration,
                        'outputs': outputs,
                        'evaluations': evaluations,
                        'final_deliverable': self._generate_deliverable(outputs, evaluations),
                        'veredict': 'ESCALATE',
                        'escalation_reason': '3rd consecutive rejection'
                    }

                # Try again if we have iterations left
                if iteration < max_iterations:
                    print(self.formatter.format_info(
                        f"Rejected. Re-submitting with feedback... ({iteration}/{max_iterations})"
                    ))
                    continue
                else:
                    # Max iterations reached, still rejected
                    print(self.formatter.format_warning(
                        f"Reached max iterations ({max_iterations}) with rejection."
                    ))
                    return {
                        'plan_id': plan_id,
                        'status': 'completed',
                        'tasks_completed': 2,
                        'tasks_total': 2,
                        'iterations': iteration,
                        'outputs': outputs,
                        'evaluations': evaluations,
                        'final_deliverable': self._generate_deliverable(outputs, evaluations),
                        'veredict': 'REJECT'
                    }

            elif veredict == 'ESCALATE':
                # Immediate escalation
                print(self.formatter.format_escalation_notice(
                    result_7.get('evaluation', {}).get('summary', 'Evaluator requested escalation.')
                ))
                return {
                    'plan_id': plan_id,
                    'status': 'escalated',
                    'tasks_completed': 2,
                    'tasks_total': 2,
                    'iterations': iteration,
                    'outputs': outputs,
                    'evaluations': evaluations,
                    'final_deliverable': self._generate_deliverable(outputs, evaluations),
                    'veredict': 'ESCALATE',
                    'escalation_reason': 'Evaluator requested escalation'
                }

        # Should not reach here, but fallback
        return {
            'plan_id': plan_id,
            'status': 'error',
            'error': 'Unexpected end of iteration loop',
            'outputs': outputs,
            'evaluations': evaluations
        }

    def _execute_standard_flow(self, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        """Execute standard flow (all tasks in sequence)."""
        if self.current_plan is None:
            return self._error_report("No plan available")
        plan_id = self.current_plan['plan_id']

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
            result = self.brain_executor.execute(brain_id, task, use_mcp=use_mcp_for_brain)

            # Format and print brain output
            print(self.formatter.format_brain_output(result, task))

            # Store output
            outputs[task_id] = result.get('output', {})

            # If this is Brain #7 (evaluator), format evaluation
            if brain_id == 7:
                print(self.formatter.format_evaluation_result(result))
                evaluations[task_id] = result

                # Check veredict - may want to stop early
                veredict = result.get('veredict', 'PLACEHOLDER')
                if veredict == 'ESCALATE':
                    print(self.formatter.format_escalation_notice("Evaluator requested escalation."))
                    break

            completed_tasks += 1

        return {
            'plan_id': plan_id,
            'status': 'completed',
            'tasks_completed': completed_tasks,
            'tasks_total': len(tasks),
            'outputs': outputs,
            'evaluations': evaluations,
            'final_deliverable': self._generate_deliverable(outputs, evaluations)
        }

    def _generate_deliverable(self, outputs: dict[str, Any], evaluations: dict[str, Any]) -> str:
        """Generate final deliverable from outputs."""
        if not outputs:
            return "No outputs generated."

        # Find the main strategy output (from Brain #1)
        strategy_output = outputs.get('TASK-001', {})

        if not strategy_output:
            return "Orchestration complete. See outputs above."

        lines = []
        lines.append("# Product Strategy Summary")
        lines.append("")

        if isinstance(strategy_output, dict):
            # Persona
            if strategy_output.get('persona'):
                persona = strategy_output['persona']
                if isinstance(persona, dict):
                    lines.append(f"**Target Persona:** {persona.get('name', 'N/A')}")
                    if persona.get('description'):
                        lines.append(f"{persona['description']}")
                    lines.append("")

            # Value Proposition
            if strategy_output.get('value_proposition'):
                lines.append(f"**Value Proposition:** {strategy_output['value_proposition']}")
                lines.append("")

            # Key Features
            if strategy_output.get('key_features'):
                features = strategy_output['key_features']
                lines.append("**Key Features:**")
                if isinstance(features, list):
                    for feature in features[:5]:  # Limit to top 5
                        if isinstance(feature, dict):
                            name = feature.get('feature', feature.get('name', 'Unknown'))
                            priority = feature.get('priority', '')
                            lines.append(f"- {name} ({priority})" if priority else f"- {name}")
                        else:
                            lines.append(f"- {feature}")
                lines.append("")

            # Success Metrics
            if strategy_output.get('success_metrics'):
                metrics = strategy_output['success_metrics']
                lines.append("**Success Metrics:**")
                if isinstance(metrics, list):
                    for metric in metrics[:5]:
                        if isinstance(metric, dict):
                            name = metric.get('metric', 'Unknown')
                            target = metric.get('target', '')
                            confidence = metric.get('confidence', '')
                            lines.append(f"- {name}: {target} (confidence: {confidence})")
                lines.append("")

            # Risks
            if strategy_output.get('risks'):
                risks = strategy_output['risks']
                lines.append("**Key Risks:**")
                if isinstance(risks, dict):
                    for risk_type, description in risks.items():
                        lines.append(f"- **{risk_type}:** {description}")
                lines.append("")

        return "\n".join(lines)

    def _error_report(self, error: str) -> dict[str, Any]:
        """Generate error report."""
        return {
            'status': 'error',
            'error': error,
            'plan': self.current_plan
        }

    def _save_output(self, output: str, filepath: str) -> None:
        """Save output to file."""
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(output)

    def _log_evaluation(self, result_7: dict[str, Any], brief: str, flow_type: str) -> None:
        """Log evaluation to memory system.

        Args:
            result_7: Evaluation result from brain #7
            brief: Original user brief
            flow_type: Flow type used
        """
        if not self.eval_logger or self.current_plan is None:
            return
        try:
            # Extract evaluation data
            score_data = result_7.get('score', {})
            veredict = result_7.get('veredict', 'UNKNOWN')

            # Convert failed_checks to issues format
            issues = []
            for failed in result_7.get('failed_checks', []):
                issues.append({
                    'type': failed.get('check_id', 'unknown'),
                    'severity': 'high',
                    'description': failed.get('reason', ''),
                    'recommendation': failed.get('fix_instruction', '')
                })

            # Convert passed_checks to strengths
            strengths = [
                passed.get('justification', passed.get('check', ''))
                for passed in result_7.get('passed_checks', [])
            ]

            # Build full output text
            full_output = result_7.get('summary', '')
            if result_7.get('failed_checks'):
                full_output += "\n\n**Issues Found:**\n"
                for failed in result_7.get('failed_checks', []):
                    full_output += f"- {failed.get('check', '')}: {failed.get('reason', '')}\n"

            # Generate tags from flow and brief
            tags = [flow_type]
            brief_lower = brief.lower()
            if 'b2b' in brief_lower or 'saas' in brief_lower:
                tags.append('b2b')
            elif 'b2c' in brief_lower or 'app' in brief_lower:
                tags.append('b2c')

            # Log the evaluation
            self.eval_logger.log_evaluation(
                project=self.current_plan.get('project_name', 'unknown'),
                brief=brief,
                flow_type=flow_type,
                score_total=score_data.get('points', 0),
                score_max=score_data.get('total', 100),
                verdict=veredict,
                issues=issues,
                strengths=strengths,
                full_output=full_output,
                tags=tags,
                brains_involved=[1, 7]
            )
        except Exception as e:
            # Don't fail orchestration if logging fails
            print(f"Warning: Failed to log evaluation: {e}")

    def _detect_flow(self, brief: str) -> str:
        """
        Detect if brief needs discovery interview.

        A brief needs discovery if:
        - Too short (less than 15 words)
        - Contains ambiguity markers (modern, nuevo, bueno, mejor)
        - No clear problem statement

        Args:
            brief: User's brief text

        Returns:
            Flow type (FLOW_DISCOVERY or result from flow_detector)
        """
        # Check 1: Word count
        word_count = len(brief.split())
        if word_count < 15:
            print(self.formatter.format_info(
                f"Brief is too short ({word_count} words). Starting discovery interview."
            ))
            return self.FLOW_DISCOVERY

        # Check 2: Ambiguity markers
        ambiguity_markers = [
            "moderno", "nuevo", "buena", "mejor", "app",
            "sistema", "plataforma", "feature", "algo"
        ]

        brief_lower = brief.lower()
        marker_count = sum(1 for marker in ambiguity_markers if marker in brief_lower)

        # If 2+ ambiguity markers, needs discovery
        if marker_count >= 2:
            print(self.formatter.format_info(
                f"Brief contains {marker_count} ambiguity markers. Starting discovery interview."
            ))
            return self.FLOW_DISCOVERY

        # Check 3: Missing problem statement keywords
        problem_keywords = ["problema", "necesito", "requiero", "quiero", "goal", "objetivo", "issue", "error"]
        has_problem = any(kw in brief_lower for kw in problem_keywords)

        if not has_problem and word_count < 30:
            print(self.formatter.format_info(
                "Brief lacks clear problem statement. Starting discovery interview."
            ))
            return self.FLOW_DISCOVERY

        # Default: use existing flow detector
        return self.flow_detector.detect(brief)

    def generate_discovery_plan(self, brief: str, use_mcp: bool = False) -> dict[str, Any]:
        """
        Generate discovery interview plan (public API for skills/CLI).

        This method only generates the plan without conducting the interview.
        Useful for external tools that want to handle the interview flow themselves.

        Args:
            brief: User's brief text
            use_mcp: Whether to use MCP for Brain #8 query

        Returns:
            Interview plan dict with:
            - status: 'success' or 'fallback'
            - plan: dict with categories, questions, gaps
            - raw_response: raw Brain #8 response
            - method: 'mcp' or 'local'
        """
        # Temporarily override use_mcp for this call
        original_use_mcp = self.use_mcp
        self.use_mcp = use_mcp

        try:
            result = self._generate_interview_plan(brief)
            return result
        finally:
            # Restore original setting
            self.use_mcp = original_use_mcp

    def _generate_interview_plan(self, brief: str) -> dict[str, Any]:
        """
        Generate interview plan by querying Brain #8.

        Args:
            brief: User's brief text

        Returns:
            Interview plan with categories, questions, and target brains
        """
        # Construct query for Brain #8
        query = f"""As a Master Interviewer and Discovery expert, analyze the following brief and design an interview strategy:

Brief: "{brief}"

Your task is to create a structured interview plan to discover what the user really needs. Provide your response in this exact JSON format:

{{
  "interview_strategy": {{
    "assessment": "Brief assessment - what's vague, what's missing",
    "categories": [
      {{"id": "users", "name": "Users & Personas", "target_brain": 2, "priority": "high"}},
      {{"id": "platforms", "name": "Platforms & Tech", "target_brain": 4, "priority": "medium"}}
    ],
    "initial_questions": [
      {{
        "category": "users",
        "question": "What type of users will use this?",
        "target_brain": 2,
        "context": "Need to understand target audience"
      }}
    ],
    "detected_gaps": [
      "Missing user persona definition",
      "No clear platform specified"
    ],
    "estimated_questions": 6
  }}
}}

Focus on:
1. Identifying what information is MISSING (gaps)
2. Creating specific questions to extract that info
3. Mapping each question to the relevant domain brain (#1-7)
4. Prioritizing high-value categories

Keep the JSON format clean and parseable.
"""

        try:
            # Try MCP first
            if self.use_mcp and self.mcp_integration and self.mcp_integration.is_available():
                response = self.mcp_integration.query_notebook(brain_id=8, query=query)

                if response.get("status") == "success":
                    content = response.get("content", "")
                    # Try to parse JSON from the response
                    parsed_plan = self._parse_interview_plan(content)

                    if parsed_plan:
                        return {
                            'status': 'success',
                            'plan': parsed_plan,
                            'raw_response': content,
                            'method': 'mcp'
                        }

            # Fallback: Generate basic plan locally
            return self._generate_basic_interview_plan(brief)

        except Exception as e:
            print(self.formatter.format_warning(f"Brain #8 query failed: {e}. Using basic plan."))
            return self._generate_basic_interview_plan(brief)

    def _parse_interview_plan(self, content: str) -> dict[str, Any] | None:
        """Parse interview plan from Brain #8 response."""
        import json
        import re

        # Try to extract JSON from the response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)

        if json_match:
            try:
                plan_data = json.loads(json_match.group())
                return plan_data if isinstance(plan_data, dict) else None
            except json.JSONDecodeError:
                pass

        # If parsing failed, try to extract structure manually
        return None

    def _generate_basic_interview_plan(self, brief: str) -> dict[str, Any]:
        """Generate a basic interview plan when Brain #8 is unavailable."""
        # Simple heuristic-based plan generation
        word_count = len(brief.split())
        brief_lower = brief.lower()

        # Default categories based on brief content
        categories = []

        # Always include users/personas
        categories.append({
            "id": "users",
            "name": "Users & Personas",
            "target_brain": 2,
            "priority": "high"
        })

        # Add platform if tech keywords present
        tech_keywords = ["web", "app", "móvil", "api", "frontend", "backend"]
        if any(kw in brief_lower for kw in tech_keywords):
            categories.append({
                "id": "platforms",
                "name": "Platforms & Tech Stack",
                "target_brain": 4,
                "priority": "medium"
            })

        # Add monetization if business keywords
        business_keywords = ["venta", "pago", "suscripción", "negocio", "ingresos"]
        if any(kw in brief_lower for kw in business_keywords):
            categories.append({
                "id": "monetization",
                "name": "Monetization & Business Model",
                "target_brain": 1,
                "priority": "high"
            })

        # Add problem domain if vague
        if word_count < 20:
            categories.append({
                "id": "problem",
                "name": "Problem Domain",
                "target_brain": 1,
                "priority": "high"
            })

        # Generate initial questions
        initial_questions = []
        for category in categories:
            question_templates = {
                "users": "What type of users will use this?",
                "platforms": "What platforms should we target?",
                "monetization": "How will this make money?",
                "problem": "What problem are you trying to solve?"
            }
            initial_questions.append({
                "category": category["id"],
                "question": question_templates.get(str(category["id"]), "Tell me more about this"),
                "target_brain": category["target_brain"],
                "context": f"Understanding {category['name']}"
            })

        return {
            'status': 'success',
            'plan': {
                "interview_strategy": {
                    "assessment": f"Basic plan generated (word count: {word_count})",
                    "categories": categories,
                    "initial_questions": initial_questions,
                    "detected_gaps": ["Brief needs clarification"],
                    "estimated_questions": len(initial_questions) * 2
                }
            },
            'method': 'fallback'
        }

    def _conduct_interview(self, interview_plan: dict[str, Any], brief: str) -> dict[str, Any]:
        """
        Conduct iterative interview with user.

        For each category, ask questions, route to domain brains, and collect responses.

        ENHANCED: Uses historical interviews to improve questions.

        Args:
            interview_plan: Plan from Brain #8 with categories and questions
            brief: Original user brief

        Returns:
            Interview document with all Q&A
        """
        # NEW: Find similar interviews for learning
        useful_questions_from_history = set()
        similar_interviews_count = 0

        try:
            from mastermind_cli.memory.interview_logger import InterviewLogger

            interview_logger = InterviewLogger(enabled=True)

            similar = interview_logger.find_similar_interviews(brief, limit=3)

            if similar:
                similar_interviews_count = len(similar)
                print(self.formatter.format_separator())
                print(self.formatter.format_info(
                    f"📚 Found {similar_interviews_count} similar interview(s) for context"
                ))

                # Extract useful questions from similar interviews
                for sim in similar:
                    useful_questions_from_history.update(sim.get("useful_questions", []))

                if useful_questions_from_history:
                    print(self.formatter.format_info(
                        f"💡 Learned from past: {len(useful_questions_from_history)} useful questions"
                    ))
                print(self.formatter.format_separator())
        except Exception:
            # Non-blocking: if learning fails, continue without it
            pass

        strategy = interview_plan.get('plan', {}).get('interview_strategy', {})
        categories = strategy.get('categories', [])
        initial_questions = strategy.get('initial_questions', [])

        if not categories:
            return {
                'status': 'error',
                'error': 'No categories in interview plan'
            }

        # Initialize interview document
        interview_doc: dict[str, Any] = {
            'metadata': {
                'session_id': self._generate_session_id(),
                'brief': brief,
                'timestamp': self._get_timestamp(),
                'categories_count': len(categories)
            },
            'categories': {},
            'qa_pairs': [],
            'outcome': {}
        }

        print(self.formatter.format_separator())
        print(self.formatter.format_info(f"Interview Plan: {len(categories)} categories to explore"))
        print(self.formatter.format_separator())

        # Process each category
        for category in categories:
            category_id = category.get('id')
            category_name = category.get('name')
            target_brain = category.get('target_brain')

            print(f"\n📂 Category: {category_name}")
            print(f"   Target Brain: #{target_brain}")

            # Get initial question for this category
            category_questions = [
                q for q in initial_questions
                if q.get('category') == category_id
            ]

            if not category_questions:
                # Skip if no questions for this category
                continue

            # Conduct Q&A for this category
            category_qa = []

            for question_item in category_questions:
                question = question_item.get('question')

                # Ask question to user
                print(self.formatter.format_question_to_user(question))

                # Get user response
                try:
                    user_response = input("Your answer: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print(self.formatter.format_warning("\nInterview interrupted by user."))
                    break

                if not user_response:
                    print("Empty response, skipping...")
                    continue

                # Route to domain brain for follow-up
                follow_up = self._route_to_domain_brain(
                    question, user_response, target_brain, brief
                )

                # Store Q&A
                qa_pair = {
                    'category': category_name,
                    'category_id': category_id,
                    'brain': target_brain,
                    'question': question,
                    'user_answer': user_response,
                    'follow_up': follow_up,
                    'timestamp': self._get_timestamp()
                }

                category_qa.append(qa_pair)
                interview_doc['qa_pairs'].append(qa_pair)

                # Display follow-up
                if follow_up.get('has_follow_up'):
                    print(self.formatter.format_followup_response(follow_up.get('follow_up_question', 'Thinking...')))

                    # Check if we should continue or move on
                    if follow_up.get('should_continue'):
                        # Could ask another question here
                        pass
                    else:
                        # This category is complete
                        break

            interview_doc['categories'][category_id] = {
                'name': category_name,
                'qa_count': len(category_qa),
                'status': 'complete'
            }

        # Generate outcome summary
        interview_doc['outcome'] = self._generate_interview_outcome(
            interview_doc,
            useful_questions_from_history=useful_questions_from_history
        )

        return interview_doc

    def _route_to_domain_brain(self, question: str, answer: str, brain_id: int, brief: str) -> dict[str, Any]:
        """
        Route user's answer to domain brain and get follow-up.

        Args:
            question: Question asked to user
            answer: User's response
            brain_id: Target brain ID
            brief: Original brief context

        Returns:
            Follow-up information with next question or completion signal
        """
        # Construct query for domain brain
        query = f"""Based on this interview exchange:

Question: "{question}"
User's Answer: "{answer}"
Context: {brief}

Analyze the answer and provide:
1. A relevant follow-up question to dig deeper OR "complete" if this category is well understood
2. Key insights extracted from the answer
3. Any gaps or assumptions detected

Format as JSON:
{{
  "has_follow_up": true/false,
  "follow_up_question": "Next question" OR null,
  "insights": ["insight1", "insight2"],
  "gaps": ["gap1"],
  "should_continue": true/false
}}
"""

        try:
            if self.use_mcp and self.mcp_integration and self.mcp_integration.is_available():
                response = self.mcp_integration.query_notebook(brain_id=brain_id, query=query)

                if response.get("status") == "success":
                    content = response.get("content", "")
                    # Try to parse follow-up
                    return self._parse_follow_up(content)

            # Fallback: basic follow-up
            return self._generate_basic_follow_up(question, answer)

        except Exception as e:
            print(self.formatter.format_warning(f"Domain brain query failed: {e}"))
            return {
                'has_follow_up': False,
                'insights': [answer[:100]],  # Partial insight
                'gaps': [],
                'should_continue': False
            }

    def _parse_follow_up(self, content: str) -> dict[str, Any]:
        """Parse follow-up from brain response."""
        import json
        import re

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)

        if json_match:
            try:
                parsed = json.loads(json_match.group())
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                pass

        # Fallback
        return {
            'has_follow_up': True,
            'follow_up_question': "Tell me more about that.",
            'insights': [content[:200]],
            'gaps': [],
            'should_continue': True
        }

    def _generate_basic_follow_up(self, _question: str, answer: str) -> dict[str, Any]:
        """Generate basic follow-up when brain is unavailable."""
        # Simple heuristic: if answer is short, ask for more
        if len(answer.split()) < 10:
            return {
                'has_follow_up': True,
                'follow_up_question': "Could you elaborate on that?",
                'insights': [answer],
                'gaps': ['More detail needed'],
                'should_continue': True
            }
        else:
            return {
                'has_follow_up': False,
                'follow_up_question': None,
                'insights': [answer],
                'gaps': [],
                'should_continue': False
            }

    def _generate_interview_outcome(
        self,
        interview_doc: dict[str, Any],
        useful_questions_from_history: set[str] | None = None
    ) -> dict[str, Any]:
        """Generate outcome summary from interview."""
        total_qa = len(interview_doc.get('qa_pairs', []))
        categories_complete = len(interview_doc.get('categories', {}))

        outcome: dict[str, Any] = {
            'total_questions_asked': total_qa,
            'categories_completed': categories_complete,
            'status': 'complete' if total_qa > 0 else 'incomplete'
        }

        # Add useful questions from learning if available
        if useful_questions_from_history:
            outcome['useful_questions_from_history'] = list(useful_questions_from_history)

        return outcome

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid
        return f"session-{uuid.uuid4().hex[:8]}"

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def continue_plan(self, _plan_id: str, plan_file: str) -> dict[str, Any]:
        """Continue execution from a saved plan."""
        # Load plan
        try:
            self.current_plan = self.plan_generator.load_plan(plan_file)
        except FileNotFoundError:
            return self._error_report(f"Plan file not found: {plan_file}")

        # Execute remaining tasks
        return self._execute_standard_flow(self.current_plan['tasks'])
