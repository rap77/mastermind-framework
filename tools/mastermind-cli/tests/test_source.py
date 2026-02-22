"""Tests for source commands."""

import os
import tempfile
from pathlib import Path

import pytest


def test_yaml_parsing():
    """Test YAML front matter parsing."""
    from mastermind_cli.utils.yaml import read_yaml_frontmatter, write_yaml_frontmatter

    # Create test file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write("---\nsource_id: FUENTE-001\nbrain: test-brain\n---\n\n# Content\n")
        temp_path = f.name

    try:
        metadata, content = read_yaml_frontmatter(temp_path)

        assert metadata is not None
        assert metadata["source_id"] == "FUENTE-001"
        assert metadata["brain"] == "test-brain"
        assert "# Content" in content
    finally:
        os.unlink(temp_path)


def test_yaml_writing():
    """Test YAML front matter writing."""
    from mastermind_cli.utils.yaml import write_yaml_frontmatter, read_yaml_frontmatter

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        temp_path = f.name

    try:
        metadata = {
            "source_id": "FUENTE-002",
            "brain": "test-brain",
            "title": "Test Title",
        }
        content = "# Test Content"

        write_yaml_frontmatter(temp_path, metadata, content)

        # Read back
        read_metadata, read_content = read_yaml_frontmatter(temp_path)

        assert read_metadata["source_id"] == "FUENTE-002"
        assert read_metadata["brain"] == "test-brain"
        # Note: write_yaml_frontmatter adds \n\n between YAML and content
        assert read_content.strip() == content.strip()
    finally:
        os.unlink(temp_path)


def test_validation():
    """Test source file validation."""
    from mastermind_cli.utils.validation import validate_source_file

    # Create valid test file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write("""---
source_id: "FUENTE-001"
brain: "test-brain"
niche: "software-development"
title: "Test"
author: "Test Author"
expert_id: "EXP-001"
type: "book"
language: "en"
year: 2020
---

# Content

## 1. Principios Fundamentales

> **P1: Test principle**
> Test description

## 2. Frameworks y Metodologías

Test section.

## 3. Modelos Mentales

Test section.

## 4. Criterios de Decisión

Test section.

## 5. Anti-patrones

Test section.
""")
        temp_path = f.name

    try:
        result = validate_source_file(temp_path)
        assert result.is_valid
        assert len(result.errors) == 0
    finally:
        os.unlink(temp_path)


def test_validation_missing_fields():
    """Test validation with missing required fields."""
    from mastermind_cli.utils.validation import validate_source_file

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write("---\nsource_id: FUENTE-001\n---\n\n# Content\n")
        temp_path = f.name

    try:
        result = validate_source_file(temp_path)
        assert not result.is_valid
        assert len(result.errors) > 0
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
