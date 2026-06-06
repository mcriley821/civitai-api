"""User response types."""

from __future__ import annotations

from ._base import _CivitAIModel


class User(_CivitAIModel):
    """A user returned by ``GET /users/{username}``."""

    id: int | None = None
    username: str
    email: str | None = None
    image: str | None = None
    stats: dict[str, int] | None = None


class Me(User):
    """Current authenticated user (GET /me)."""

    email: str | None = None
    blur_nsfw: bool | None = None
    nsfw: bool | None = None
