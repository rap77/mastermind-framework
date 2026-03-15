"""
NotebookLM MCP Client - Wrapper for NotebookLM MCP operations.

This module provides a Python interface to NotebookLM MCP tools.
"""

from typing import Dict, Optional, List


class NotebookLMClient:
    """Client for NotebookLM MCP operations."""

    # Brain notebook IDs (from Framework Status 2026-02-28)
    BRAIN_NOTEBOOKS = {
        1: "f276ccb3-0bce-4069-8b55-eae8693dbe75",  # Product Strategy
        2: "ea006ece-00a9-4d5c-91f5-012b8b712936",  # UX Research
        3: "8d544475-6860-4cd7-9037-8549325493dd",  # UI Design
        4: "85e47142-0a65-41d9-9848-49b8b5d2db33",  # Frontend
        5: "c6befbbc-b7dd-4ad0-a677-314750684208",  # Backend
        6: "74cd3a81-1350-4927-af14-c0c4fca41a8e",  # QA/DevOps
        7: "d8de74d6-7028-44ed-b4d5-784d6a9256e6",  # Growth/Data (Evaluator)
    }

    # Brain names
    BRAIN_NAMES = {
        1: "Product Strategy",
        2: "UX Research",
        3: "UI Design",
        4: "Frontend Development",
        5: "Backend Development",
        6: "QA & DevOps",
        7: "Growth & Data (Evaluator)",
    }

    def __init__(self):
        """Initialize NotebookLM client."""
        # Check if we're running in Claude Code with MCP available
        self.mcp_available = self._check_mcp_available()

    def _check_mcp_available(self) -> bool:
        """Check if NotebookLM MCP is available."""
        # In Claude Code, MCP tools are available directly
        # We'll detect this when we try to use them
        return True

    def get_notebook_id(self, brain_id: int) -> Optional[str]:
        """Get notebook ID for a brain."""
        return self.BRAIN_NOTEBOOKS.get(brain_id)

    def is_brain_available(self, brain_id: int) -> bool:
        """Check if a brain has an active notebook."""
        return brain_id in self.BRAIN_NOTEBOOKS

    def query_brain(
        self,
        brain_id: int,
        query: str,
        source_ids: Optional[List[str]] = None,
        timeout: float = 180.0,
    ) -> Dict:
        """
        Query a brain's notebook.

        Args:
            brain_id: ID of brain to query (1-7)
            query: Question to ask the brain
            source_ids: Optional list of source IDs to query
            timeout: Query timeout in seconds

        Returns:
            Response dictionary with:
                - status: 'success' | 'error'
                - answer: Brain's response text
                - notebook_id: ID of the queried notebook
                - brain_name: Name of the brain
                - error: Error message if status='error'
        """
        notebook_id = self.get_notebook_id(brain_id)

        if not notebook_id:
            return {
                "status": "error",
                "error": f"Brain #{brain_id} does not have an active notebook",
                "brain_id": brain_id,
                "brain_name": self.BRAIN_NAMES.get(brain_id, f"Brain {brain_id}"),
            }

        # Try to use MCP tool (will be available in Claude Code)
        try:
            # This will be called via the MCP tool in the actual execution
            # For now, return a structure that indicates what we need
            return {
                "status": "mcp_required",
                "notebook_id": notebook_id,
                "brain_id": brain_id,
                "brain_name": self.BRAIN_NAMES[brain_id],
                "query": query,
                "source_ids": source_ids,
                "message": "MCP tool call required - use notebook_query tool",
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "brain_id": brain_id,
                "brain_name": self.BRAIN_NAMES.get(brain_id),
            }

    def parse_yaml_response(self, response_text: str) -> Dict:
        """
        Parse YAML from a NotebookLM response.

        Args:
            response_text: Raw text response from NotebookLM

        Returns:
            Parsed YAML as dictionary, or error dict if parsing fails
        """
        import yaml
        import re

        # Try to extract YAML block from markdown response
        yaml_pattern = r"```yaml\s*\n(.*?)\n```"
        match = re.search(yaml_pattern, response_text, re.DOTALL)

        if match:
            yaml_content = match.group(1)
        else:
            # Try without language specifier
            yaml_pattern = r"```\s*\n(.*?)\n```"
            match = re.search(yaml_pattern, response_text, re.DOTALL)
            if match:
                yaml_content = match.group(1)
            else:
                # Assume entire response is YAML
                yaml_content = response_text

        try:
            return yaml.safe_load(yaml_content)
        except Exception as e:
            return {
                "error": f"Failed to parse YAML: {str(e)}",
                "raw_response": response_text,
            }

    def get_available_brains(self) -> List[Dict]:
        """Get list of available brains with their notebook IDs."""
        return [
            {
                "brain_id": brain_id,
                "brain_name": self.BRAIN_NAMES[brain_id],
                "notebook_id": notebook_id,
                "status": "active",
            }
            for brain_id, notebook_id in self.BRAIN_NOTEBOOKS.items()
        ]
