"""Creator response type."""

from __future__ import annotations

from ._base import _CivitAIModel


class Creator(_CivitAIModel):
    """A creator returned by ``GET /creators``."""

    username: str
    model_count: int | None = None
    link: str | None = None
    image: str | None = None
