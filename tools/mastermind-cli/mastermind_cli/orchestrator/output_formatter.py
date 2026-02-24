"""
Output Formatter - Formats orchestrator outputs for human consumption.
"""

from typing import Dict


class OutputFormatter:
    """Formats orchestrator outputs for human consumption."""

    def format_execution_plan(self, plan: Dict) -> str:
        """Format execution plan for display."""
        lines = []
        lines.append("=" * 60)
        lines.append(f"EXECUTION PLAN: {plan['plan_id']}")
        lines.append("=" * 60)
        lines.append("")

        # Brief
        lines.append("📋 Brief:")
        lines.append(f"   {plan['brief']['original'][:100]}")
        lines.append("")

        # Flow info
        lines.append(f"🔄 Flow Type: {plan['flow_type']}")
        lines.append("")

        # Tasks
        lines.append(f"📝 Tasks ({plan['summary']['total_tasks']} total):")
        lines.append("")

        for task in plan['tasks']:
            deps = f" (after: {', '.join(task['dependencies'])})" if task['dependencies'] else ""
            lines.append(f"   {task['task_id']}: {task['brain_name']}")
            lines.append(f"      └─ {task['title']}{deps}")
            lines.append(f"      └─ Effort: {task['estimated_effort']}")
            lines.append("")

        # Summary
        lines.append("📊 Summary:")
        lines.append(f"   Total Tasks: {plan['summary']['total_tasks']}")
        lines.append(f"   Estimated Duration: {plan['summary']['estimated_duration']}")
        lines.append(f"   Brains Involved: {', '.join(map(str, plan['summary']['brains_involved']))}")
        lines.append("")

        return "\n".join(lines)

    def format_task_start(self, task: Dict) -> str:
        """Format task start notification."""
        return f"\n▶️  Executing {task['task_id']}: {task['brain_name']} — {task['title']}"

    def format_brain_output(self, result: Dict, task: Dict) -> str:
        """Format brain output for display."""
        lines = []
        lines.append("")
        lines.append(f"✅ {task['task_id']} Complete")
        lines.append(f"   Brain: {result['brain_name']}")

        if result.get('status') == 'unimplemented':
            lines.append(f"   ⚠️  Status: {result['error']}")
        elif result.get('status') == 'placeholder':
            lines.append(f"   📝 Status: {result['message']}")
        elif result.get('status') == 'completed':
            lines.append(f"   Output: {result.get('output', 'No output')}")

        lines.append("")
        return "\n".join(lines)

    def format_evaluation_result(self, result: Dict) -> str:
        """Format evaluation result for display."""
        lines = []
        lines.append("")
        lines.append("🔍 EVALUATION RESULT")
        lines.append("-" * 40)

        veredict = result.get('veredict', 'UNKNOWN')
        score = result.get('score', 0)

        # Color code veredict
        veredict_symbols = {
            'APPROVE': '✅',
            'CONDITIONAL': '⚠️ ',
            'REJECT': '❌',
            'ESCALATE': '🚨',
            'PLACEHOLDER': '📝'
        }

        symbol = veredict_symbols.get(veredict, '❓')
        lines.append(f"{symbol} Veredict: {veredict} (Score: {score}/100)")

        if result.get('evaluation'):
            evaluation = result['evaluation']

            if evaluation.get('completeness'):
                lines.append(f"   Completeness: {evaluation['completeness']['score']}/100")
            if evaluation.get('quality'):
                lines.append(f"   Quality: {evaluation['quality']['score']}/100")
            if evaluation.get('honesty'):
                lines.append(f"   Honesty: {evaluation['honesty']['score']}/100")
            if evaluation.get('viability'):
                lines.append(f"   Viability: {evaluation['viability']['score']}/100")

        if result.get('feedback'):
            feedback = result['feedback']
            if feedback.get('major_issues'):
                lines.append("")
                lines.append("   Major Issues:")
                for issue in feedback['major_issues']:
                    lines.append(f"      • {issue}")
            if feedback.get('minor_issues'):
                lines.append("")
                lines.append("   Minor Issues:")
                for issue in feedback['minor_issues']:
                    lines.append(f"      • {issue}")

        if result.get('message'):
            lines.append("")
            lines.append(f"   {result['message']}")

        lines.append("")
        return "\n".join(lines)

    def format_final_deliverable(self, report: Dict) -> str:
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
        lines.append(f"Tasks Completed: {report.get('tasks_completed', 0)}/{report.get('tasks_total', 0)}")
        lines.append("")

        # Outputs
        if report.get('outputs'):
            lines.append("📦 Outputs:")
            for task_id, output in report['outputs'].items():
                lines.append(f"   {task_id}: {output}")
            lines.append("")

        # Evaluations summary
        if report.get('evaluations'):
            lines.append("📊 Evaluations Summary:")
            approved = sum(1 for e in report['evaluations'].values() if e.get('veredict') == 'APPROVE')
            conditional = sum(1 for e in report['evaluations'].values() if e.get('veredict') == 'CONDITIONAL')
            rejected = sum(1 for e in report['evaluations'].values() if e.get('veredict') == 'REJECT')

            lines.append(f"   ✅ Approved: {approved}")
            lines.append(f"   ⚠️  Conditional: {conditional}")
            lines.append(f"   ❌ Rejected: {rejected}")
            lines.append("")

        # Final deliverable
        if report.get('final_deliverable'):
            lines.append("📄 FINAL DELIVERABLE:")
            lines.append("-" * 40)
            lines.append(report['final_deliverable'])
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
