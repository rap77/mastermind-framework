"""Validation functions for source files."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class ValidationError:
    """A validation error for a source file."""

    field: str
    message: str
    severity: str = "error"  # error, warning


@dataclass
class ValidationResult:
    """Result of validating a source file."""

    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)

    def add_error(self, field: str, message: str) -> None:
        """Add an error to the result."""
        self.errors.append(ValidationError(field, message, "error"))
        self.is_valid = False

    def add_warning(self, field: str, message: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(ValidationError(field, message, "warning"))


# Required YAML fields for source files
REQUIRED_YAML_FIELDS = {
    "source_id",
    "brain",
    "niche",
    "title",
    "author",
    "expert_id",
    "type",
    "language",
    "year",
}

# Required content sections
REQUIRED_CONTENT_SECTIONS = {
    "1. Principios Fundamentales",
    "2. Frameworks y Metodologías",
    "3. Modelos Mentales",
    "4. Criterios de Decisión",
    "5. Anti-patrones",
}


def validate_source_file(filepath: str) -> ValidationResult:
    """
    Validate a source file against MasterMind standards.

    Args:
        filepath: Path to the source file

    Returns:
        ValidationResult with errors and warnings
    """
    result = ValidationResult(is_valid=True)

    try:
        from .yaml import read_yaml_frontmatter

        metadata, content = read_yaml_frontmatter(filepath)

        # Validate YAML front matter exists
        if metadata is None:
            result.add_error(
                "yaml_front_matter",
                "No YAML front matter found (requires --- delimiters)",
            )
            return result

        # Validate required YAML fields
        for field in REQUIRED_YAML_FIELDS:
            if field not in metadata:
                result.add_error(f"yaml.{field}", f"Required field '{field}' is missing")

        # Validate source_id format
        source_id = metadata.get("source_id", "")
        if source_id and not source_id.startswith("FUENTE-"):
            result.add_error(
                "yaml.source_id",
                "source_id must start with 'FUENTE-' (e.g., FUENTE-001)",
            )

        # Validate principles count (min 3)
        if content:
            principle_count = content.count("> **P")
            if principle_count < 3:
                result.add_warning(
                    "content.principles",
                    f"Only {principle_count} principles found (minimum 3 recommended)",
                )

        # Validate required content sections
        for section in REQUIRED_CONTENT_SECTIONS:
            if section not in content:
                result.add_error(
                    f"content.{section}",
                    f"Required section '{section}' is missing",
                )

        # Validate type is one of allowed values
        allowed_types = {"book", "video", "article", "course", "documentation"}
        source_type = metadata.get("type", "")
        if source_type and source_type not in allowed_types:
            result.add_error(
                "yaml.type",
                f"Type must be one of: {', '.join(allowed_types)}",
            )

    except Exception as e:
        result.add_error("file", f"Error reading file: {e}")

    return result


def validate_brain_sources(brain_path: str) -> Dict[str, ValidationResult]:
    """
    Validate all sources in a brain directory.

    Args:
        brain_path: Path to brain directory (e.g., docs/software-development/01-product-strategy-brain)

    Returns:
        Dictionary mapping filename to ValidationResult
    """
    results = {}
    sources_dir = Path(brain_path) / "sources"

    if not sources_dir.exists():
        return results

    for source_file in sources_dir.glob("FUENTE-*.md"):
        result = validate_source_file(str(source_file))
        results[source_file.name] = result

    return results


def find_sources_by_id(source_id: str, search_paths: List[str]) -> List[str]:
    """
    Find source files by ID across multiple directories.

    Args:
        source_id: Source ID to search for (e.g., FUENTE-001)
        search_paths: List of directories to search

    Returns:
        List of matching file paths
    """
    matches = []

    for search_path in search_paths:
        path = Path(search_path)
        if not path.exists():
            continue

        # Search in sources subdirectories
        for sources_dir in path.rglob("sources"):
            for source_file in sources_dir.glob(f"{source_id}.md"):
                matches.append(str(source_file))

    return matches
