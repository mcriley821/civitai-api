"""Tag response type."""

from __future__ import annotations

from ._base import _CivitAIModel


class Tag(_CivitAIModel):
    """A tag returned by ``GET /tags``."""

    name: str
    model_count: int | None = None
    link: str | None = None
