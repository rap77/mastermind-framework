"""
Brain output models and normalizer.
"""

from pydantic import BaseModel, Field
from typing import Optional
import yaml


class StandardSchema(BaseModel):
    """Standard brain output schema with graceful fallback."""
    brain_id: str = Field(..., description="Brain identifier")
    content: str = Field(..., description="Brain output content")
    version: str = Field(default="v1.0.0", description="Schema version")
    raw_fallback: Optional[str] = Field(None, description="Fallback for unparseable output")


def normalize_brain_output(raw_yaml: str) -> StandardSchema:
    """Normalize legacy brain output to standard schema.

    Implements Normalizer Pattern from CONTEXT.md:
    - Try YAML parse → validate fields
    - Parse error → fallback to raw_fallback
    - Missing fields → fill defaults
    """
    try:
        data = yaml.safe_load(raw_yaml)
        return StandardSchema(
            brain_id=data.get("brain_id", "unknown"),
            content=data.get("content", raw_yaml),
            version=data.get("version", "v1.0.0")
        )
    except yaml.YAMLError:
        return StandardSchema(
            brain_id="parse_error",
            content="",
            raw_fallback=raw_yaml
        )
