"""Brain Registry - Public Framework Configuration.

These are public NotebookLM notebook identifiers used by the MasterMind
Framework to access knowledge bases. They are NOT API keys, tokens, or
passwords. Access requires separate Google OAuth authentication via the
NotebookLM MCP server. These IDs alone cannot authenticate to anything.

This module is public configuration that belongs in version control.
Source of truth: https://github.com/rap77/mastermind-framework
"""

# Public notebook identifiers for the 7 MasterMind knowledge brains.
# Safe to version control - these are configuration, not credentials.
BRAIN_REGISTRY: dict = {
    "#1": {
        "name": "Product Strategy",
        "notebook_id": "f276ccb3-0bce-4069-8b55-eae8693dbe75",
        "expertise": "What & Why - Product definition, strategy, discovery",
    },
    "#2": {
        "name": "UX Research",
        "notebook_id": "ea006ece-00a9-4d5c-91f5-012b8b712936",
        "expertise": "User Experience - Research methods, user insights",
    },
    "#3": {
        "name": "UI Design",
        "notebook_id": "8d544475-6860-4cd7-9037-8549325493dd",
        "expertise": "Visual Design - Design systems, components, patterns",
    },
    "#4": {
        "name": "Frontend",
        "notebook_id": "85e47142-0a65-41d9-9848-49b8b5d2db33",
        "expertise": "Frontend Architecture - React, Next.js, state management",
    },
    "#5": {
        "name": "Backend",
        "notebook_id": "c6befbbc-b7dd-4ad0-a677-314750684208",
        "expertise": "Backend Architecture - APIs, databases, services",
    },
    "#6": {
        "name": "QA/DevOps",
        "notebook_id": "74cd3a81-1350-4927-af14-c0c4fca41a8e",
        "expertise": "Quality & Operations - Testing, CI/CD, reliability",
    },
    "#7": {
        "name": "Growth/Data",
        "notebook_id": "d8de74d6-7028-44ed-b4d4-784d6a9256e6",
        "expertise": "Growth & Evaluation - Metrics, experimentation, optimization",
    },
}
