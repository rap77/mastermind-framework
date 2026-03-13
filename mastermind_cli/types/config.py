"""
YAML configuration models with discriminated unions.
"""

from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field


class VectorSearchBrain(BaseModel):
    """Vector search brain configuration."""
    type: Literal['vector-search']
    top_k: int = Field(..., description="Number of results to return", ge=1, le=100)
    embedding_model: str = Field(default="text-embedding-ada-002", description="Embedding model name")


class GenerativeBrain(BaseModel):
    """Generative brain configuration."""
    type: Literal['generative']
    temperature: float = Field(..., description="Sampling temperature", ge=0.0, le=2.0)
    max_tokens: int = Field(..., description="Maximum tokens to generate", gt=0)


# Discriminated union - Pydantic uses 'type' field to select model
BrainConfig = Annotated[
    Union[VectorSearchBrain, GenerativeBrain],
    Field(discriminator='type')
]


class ConfigFile(BaseModel):
    """YAML configuration file model."""
    brains: list[BrainConfig] = Field(default_factory=list, description="List of brain configurations")
    default_flow: str = Field(default="discovery", description="Default flow type")
