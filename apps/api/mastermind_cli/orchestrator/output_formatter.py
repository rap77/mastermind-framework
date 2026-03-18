"""
Output Formatter - Formats orchestrator outputs for human consumption.
"""

from typing import Any


class OutputFormatter:
    """Formats orchestrator outputs for human consumption."""

    # Colors for terminal output
    COLORS = {
        "APPROVE": "\033[92m",  # Green
        "CONDITIONAL": "\033[93m",  # Yellow
        "REJECT": "\033[91m",  # Red
        "ESCALATE": "\033[95m",  # Magenta
        "RESET": "\033[0m",
    }

    def format_execution_plan(self, plan: dict[str, Any]) -> str:
        """Format execution plan for display."""
        lines = []
        lines.append("=" * 60)
        lines.append(f"EXECUTION PLAN: {plan['plan_id']}")
        lines.append("=" * 60)
        lines.append("")

        # Brief
        lines.append("📋 Brief:")
        lines.append(f"   {plan['brief']['original'][:100]}...")
        lines.append("")

        # Flow info
        lines.append(f"🔄 Flow Type: {plan['flow_type']}")
        lines.append("")

        # Tasks
        lines.append(f"📝 Tasks ({plan['summary']['total_tasks']} total):")
        lines.append("")

        for task in plan["tasks"]:
            deps = (
                f" (after: {', '.join(task['dependencies'])})"
                if task.get("dependencies")
                else ""
            )
            lines.append(f"   {task['task_id']}: {task['brain_name']}")
            lines.append(f"      └─ {task['title']}{deps}")
            lines.append(f"      └─ Effort: {task.get('estimated_effort', 'Unknown')}")
            lines.append("")

        # Summary
        lines.append("📊 Summary:")
        lines.append(f"   Total Tasks: {plan['summary']['total_tasks']}")
        lines.append(
            f"   Estimated Duration: {plan['summary'].get('estimated_duration', 'Unknown')}"
        )
        brains_involved = plan["summary"].get("brains_involved", [])
        lines.append(f"   Brains Involved: {', '.join(map(str, brains_involved))}")
        lines.append("")

        return "\n".join(lines)

    def format_task_start(self, task: dict[str, Any]) -> str:
        """Format task start notification."""
        return (
            f"\n▶️  Executing {task['task_id']}: {task['brain_name']} — {task['title']}"
        )

    def format_brain_output(self, result: dict[str, Any], task: dict[str, Any]) -> str:
        """Format brain output for display."""
        lines = []
        lines.append("")
        lines.append(f"✅ {task['task_id']} Complete")
        lines.append(f"   Brain: {result['brain_name']}")

        status = result.get("status", "unknown")

        if status == "unimplemented":
            lines.append(f"   ⚠️  Status: {result.get('error', 'Not implemented')}")
        elif status == "placeholder" or status == "mock":
            lines.append(f"   📝 Status: {result.get('message', 'Placeholder output')}")
        elif status == "completed":
            output = result.get("output", {})

            # Show a summary of the output
            if isinstance(output, dict):
                if output.get("persona"):
                    persona = output["persona"]
                    lines.append(f"   👤 Persona: {persona.get('name', 'N/A')}")
                if output.get("value_proposition"):
                    lines.append(f"   💡 Value: {output['value_proposition'][:60]}...")
                if output.get("key_features"):
                    features = output["key_features"]
                    count = len(features) if isinstance(features, list) else 1
                    lines.append(f"   ⚙️  Features: {count} defined")
                if output.get("success_metrics"):
                    metrics = output["success_metrics"]
                    count = len(metrics) if isinstance(metrics, list) else 1
                    lines.append(f"   📈 Metrics: {count} defined")
            else:
                lines.append(f"   Output: {str(output)[:100]}...")

        lines.append("")
        return "\n".join(lines)

    def format_evaluation_result(self, result: dict[str, Any]) -> str:
        """Format evaluation result for display."""
        lines = []
        lines.append("")
        lines.append("🔍 EVALUATION RESULT")
        lines.append("-" * 50)

        veredict = result.get("veredict", "UNKNOWN")
        score_data = result.get("score", {})

        # Format score
        points = score_data.get("points", 0)
        total = score_data.get("total", 100)
        percentage = score_data.get("percentage", 0)

        # Color code veredict
        veredict_colors = {
            "APPROVE": "✅",
            "CONDITIONAL": "⚠️ ",
            "REJECT": "❌",
            "ESCALATE": "🚨",
            "PLACEHOLDER": "📝",
            "UNKNOWN": "❓",
        }

        symbol = veredict_colors.get(veredict, "❓")
        lines.append(f"{symbol} Veredict: {veredict}")
        lines.append(f"   Score: {points}/{total} ({percentage}%)")
        lines.append("")

        # Summary
        if result.get("summary"):
            lines.append("📝 Summary:")
            lines.append(f"   {result['summary']}")
            lines.append("")

        # Passed/Failed checks
        passed = result.get("passed_checks", [])
        failed = result.get("failed_checks", [])

        if passed:
            lines.append(f"✅ Checks Passed: {len(passed)}")
            # Show first 3 passed checks
            for check in passed[:3]:
                lines.append(f"   ✓ {check['check_id']}: {check.get('check', 'N/A')}")
            if len(passed) > 3:
                lines.append(f"   ... and {len(passed) - 3} more")
            lines.append("")

        if failed:
            lines.append(f"❌ Checks Failed: {len(failed)}")
            # Show first 3 failed checks with fixes
            for check in failed[:3]:
                lines.append(f"   ✗ {check['check_id']}: {check.get('check', 'N/A')}")
                fix = check.get("fix_instruction", "")
                if fix:
                    lines.append(f"      → {fix[:80]}...")
            if len(failed) > 3:
                lines.append(f"   ... and {len(failed) - 3} more")
            lines.append("")

        # Biases detected
        biases = result.get("biases_detected", [])
        if biases:
            lines.append(f"🧠 Biases Detected: {len(biases)}")
            for bias in biases:
                lines.append(
                    f"   • {bias.get('bias_id', 'UNKNOWN')}: {bias.get('name', 'Unknown bias')}"
                )
                if bias.get("question"):
                    lines.append(f"      Question: {bias['question']}")
            lines.append("")

        # Redirect instructions
        redirect = result.get("redirect_instructions")
        if redirect and veredict in ["CONDITIONAL", "REJECT"]:
            lines.append("🔄 Next Steps:")
            lines.append(f"   To Brain: #{redirect.get('to_brain', '1')}")
            lines.append(f"   Action: {redirect.get('action', 'ITERATE')}")
            fixes = redirect.get("specific_fixes", [])
            if fixes:
                lines.append("   Fixes to apply:")
                for i, fix in enumerate(fixes[:3], 1):
                    lines.append(f"      {i}. {fix[:70]}...")
            lines.append("")

        lines.append("-" * 50)
        lines.append("")

        return "\n".join(lines)

    def format_final_deliverable(self, report: dict[str, Any]) -> str:
        """Format final deliverable for display."""
        lines = []
        lines.append("")
        lines.append("=" * 60)
        lines.append("🎉 ORCHESTRATION COMPLETE")
        lines.append("=" * 60)
        lines.append("")

        # Summary
        lines.append(f"Plan ID: {report.get('plan_id', 'N/A')}")
        lines.append(f"Status: {report.get('status', 'N/A')}")
        completed = report.get("tasks_completed", 0)
        total = report.get("tasks_total", 0)
        lines.append(f"Tasks Completed: {completed}/{total}")
        lines.append("")

        # Final evaluation
        evaluations = report.get("evaluations", {})
        if evaluations:
            lines.append("📊 Final Evaluation:")
            for task_id, eval_result in evaluations.items():
                veredict = eval_result.get("veredict", "UNKNOWN")
                score_data = eval_result.get("score", {})
                percentage = score_data.get("percentage", 0)
                lines.append(f"   {task_id}: {veredict} ({percentage}%)")
            lines.append("")

        # Final deliverable content
        if report.get("final_deliverable"):
            lines.append("📄 FINAL DELIVERABLE:")
            lines.append("-" * 40)
            lines.append(report["final_deliverable"])
            lines.append("")

        # Recommendations based on veredict
        if evaluations:
            last_eval = list(evaluations.values())[-1]
            veredict = last_eval.get("veredict")

            if veredict == "APPROVE":
                lines.append("🚀 Ready to proceed!")
                lines.append("   The brief has been validated. You can move forward")
                lines.append("   with implementation or further development.")
            elif veredict == "CONDITIONAL":
                lines.append("⚠️  Improvements needed")
                lines.append("   Address the failed checks above before proceeding.")
                lines.append("   Re-run orchestrate after making changes.")
            elif veredict == "REJECT":
                lines.append("❌ Fundamental issues")
                lines.append("   The brief needs significant rework.")
                lines.append("   Please review and revise before re-submitting.")
            elif veredict == "ESCALATE":
                lines.append("🚨 Escalation required")
                lines.append("   This requires human review.")
                lines.append("   Please consult with a product strategist.")

            lines.append("")

        return "\n".join(lines)

    def format_error(self, error: str) -> str:
        """Format error message."""
        return f"\n❌ Error: {error}\n"

    def format_info(self, message: str) -> str:
        """Format info message."""
        return f"ℹ️  {message}"

    def format_warning(self, message: str) -> str:
        """Format warning message."""
        return f"⚠️  {message}"

    def format_iteration_start(self, iteration: int, max_iterations: int) -> str:
        """Format iteration start notification."""
        lines = []
        lines.append("")
        lines.append("🔄" * 20)
        lines.append(f"ITERATION {iteration}/{max_iterations}")
        lines.append("🔄" * 20)
        lines.append("")
        return "\n".join(lines)

    def format_escalation_notice(self, reason: str) -> str:
        """Format escalation notice."""
        lines = []
        lines.append("")
        lines.append("🚨" * 20)
        lines.append("ESCALATION TRIGGERED")
        lines.append("🚨" * 20)
        lines.append("")
        lines.append(f"Reason: {reason}")
        lines.append("")
        lines.append("This brief requires human review.")
        lines.append("Please consult with a product strategist.")
        lines.append("")
        return "\n".join(lines)

    def format_verbose(self, message: str) -> str:
        """Format verbose/debug message."""
        return f"🔧 {message}"

    # Discovery Flow Methods

    def format_separator(self, char: str = "=", length: int = 60) -> str:
        """Format separator line."""
        return char * length

    def format_interview_plan(self, interview_plan: dict[str, Any]) -> str:
        """Format interview plan for display."""
        lines = []
        lines.append("")
        lines.append("📋 Interview Strategy Generated")
        lines.append("-" * 40)

        plan = interview_plan.get("plan", {})
        strategy = plan.get("interview_strategy", {})

        # Assessment
        assessment = strategy.get("assessment", "No assessment")
        lines.append(f"Assessment: {assessment}")
        lines.append("")

        # Categories
        categories = strategy.get("categories", [])
        if categories:
            lines.append(f"Categories to Explore ({len(categories)}):")
            for cat in categories:
                priority = cat.get("priority", "medium")
                brain = cat.get("target_brain", "N/A")
                lines.append(
                    f"  • {cat.get('name')} (Brain #{brain}, {priority} priority)"
                )
            lines.append("")

        # Initial Questions
        questions = strategy.get("initial_questions", [])
        if questions:
            lines.append(f"Initial Questions ({len(questions)}):")
            for q in questions[:5]:  # Show first 5
                lines.append(f"  • [{q.get('category')}] {q.get('question')}")
            if len(questions) > 5:
                lines.append(f"  ... and {len(questions) - 5} more")
            lines.append("")

        # Detected Gaps
        gaps = strategy.get("detected_gaps", [])
        if gaps:
            lines.append("Detected Gaps:")
            for gap in gaps:
                lines.append(f"  • {gap}")
            lines.append("")

        # Estimated questions
        estimated = strategy.get("estimated_questions", 0)
        if estimated:
            lines.append(f"Estimated Questions: {estimated}")
            lines.append("")

        return "\n".join(lines)

    def format_question_to_user(self, question: str) -> str:
        """Format question to display to user."""
        lines = []
        lines.append("")
        lines.append("❓ Question:")
        lines.append(f"   {question}")
        lines.append("")
        return "\n".join(lines)

    def format_followup_response(self, followup: str) -> str:
        """Format follow-up response from domain brain."""
        lines = []
        lines.append("")
        lines.append("💡 Follow-up Analysis:")
        lines.append(f"   {followup}")
        lines.append("")
        return "\n".join(lines)

    def format_interview_complete(self, interview_doc: dict[str, Any]) -> str:
        """Format interview completion summary."""
        lines = []
        lines.append("")
        lines.append("=" * 60)
        lines.append("✅ INTERVIEW COMPLETE")
        lines.append("=" * 60)
        lines.append("")

        # Metadata
        metadata = interview_doc.get("metadata", {})
        lines.append(f"Session ID: {metadata.get('session_id', 'unknown')}")
        lines.append(f"Timestamp: {metadata.get('timestamp', 'unknown')}")
        lines.append("")

        # Outcome
        outcome = interview_doc.get("outcome", {})
        total_questions = outcome.get("total_questions_asked", 0)
        categories_complete = outcome.get("categories_completed", 0)

        lines.append(f"Questions Asked: {total_questions}")
        lines.append(f"Categories Explored: {categories_complete}")
        lines.append("")

        # Q&A Summary
        qa_pairs = interview_doc.get("qa_pairs", [])
        if qa_pairs:
            lines.append("📝 Q&A Summary:")
            lines.append("")

            # Group by category
            by_category: dict[str, list[Any]] = {}
            for qa in qa_pairs:
                cat = qa.get("category", "General")
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(qa)

            for cat, items in by_category.items():
                lines.append(f"  {cat}:")
                for qa in items:
                    question = qa.get("question", "")[:60]
                    answer = qa.get("user_answer", "")[:60]
                    lines.append(f"    Q: {question}...")
                    lines.append(f"    A: {answer}...")
                lines.append("")

        lines.append("-" * 60)
        lines.append("")

        return "\n".join(lines)
