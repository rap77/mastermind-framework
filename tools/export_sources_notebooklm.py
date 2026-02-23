#!/usr/bin/env python3
"""
Export sources to NotebookLM format (without YAML front matter).
"""

import re
from pathlib import Path

SOURCES_DIR = Path("docs/software-development/01-product-strategy-brain/sources")
OUTPUT_DIR = Path("dist/notebooklm/01-product-strategy")


def remove_yaml_frontmatter(content: str) -> str:
    """Remove YAML front matter from markdown content."""
    # Match YAML delimiters (---) at the start
    pattern = r'^---\n.*?\n---\n\n?'
    result = re.sub(pattern, '', content, flags=re.DOTALL)
    return result


def export_source(source_path: Path) -> None:
    """Export a single source file without YAML front matter."""
    content = source_path.read_text(encoding='utf-8')
    clean_content = remove_yaml_frontmatter(content)

    output_path = OUTPUT_DIR / source_path.name
    output_path.write_text(clean_content, encoding='utf-8')
    print(f"✓ Exported: {source_path.name}")


def main():
    """Export all sources."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sources = sorted(SOURCES_DIR.glob("FUENTE-*.md"))
    print(f"Found {len(sources)} sources")
    print(f"Output: {OUTPUT_DIR}/")
    print()

    for source in sources:
        export_source(source)

    print()
    print(f"✓ Exported {len(sources)} sources to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
