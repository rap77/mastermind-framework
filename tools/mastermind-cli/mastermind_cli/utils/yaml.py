"""YAML front matter parser for source files."""

import re
import yaml
from typing import Any, Dict, Tuple, Optional


def read_yaml_frontmatter(filepath: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Parse YAML front matter from markdown file.

    Args:
        filepath: Path to the markdown file

    Returns:
        Tuple of (metadata_dict, markdown_content)
        Returns (None, full_content) if no YAML front matter found
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract YAML between --- markers
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not match:
        return None, content

    yaml_str, markdown = match.groups()
    try:
        metadata = yaml.safe_load(yaml_str)
        return metadata, markdown
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {filepath}: {e}")


def write_yaml_frontmatter(
    filepath: str, metadata: Dict[str, Any], content: str
) -> None:
    """
    Write file with YAML front matter.

    Args:
        filepath: Path to write the file
        metadata: Dictionary of YAML metadata
        content: Markdown content (after YAML front matter)
    """
    yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"---\n{yaml_str}---\n\n{content}")


def update_yaml_metadata(
    filepath: str, updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update specific fields in YAML front matter.

    Args:
        filepath: Path to the file
        updates: Dictionary of fields to update

    Returns:
        Updated metadata dictionary
    """
    metadata, content = read_yaml_frontmatter(filepath)
    if metadata is None:
        raise ValueError(f"No YAML front matter found in {filepath}")

    metadata.update(updates)
    write_yaml_frontmatter(filepath, metadata, content)
    return metadata
