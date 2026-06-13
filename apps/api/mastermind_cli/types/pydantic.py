"""Shared Pydantic base models for consistent schema behavior."""

from pydantic import BaseModel, ConfigDict


class StrictRequestModel(BaseModel):
    """Base model for public request payloads.

    Rejects unexpected fields instead of silently ignoring them.
    """

    model_config = ConfigDict(extra="forbid")
