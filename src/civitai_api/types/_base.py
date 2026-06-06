"""Base model config for all CivitAI response types."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _CivitAIModel(BaseModel):
    """Base Pydantic model for all CivitAI response types.

    Configures camelCase alias generation, snake_case field access, and
    ``extra="allow"`` so undocumented API fields are tolerated without error.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )
