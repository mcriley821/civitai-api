"""Image response types."""

from typing import Any

from ._base import _CivitAIModel
from .enums import NsfwLevel


class ImageMeta(_CivitAIModel):
    """Generation metadata embedded in an image response."""

    prompt: str | None = None
    negative_prompt: str | None = None
    cfg_scale: float | None = None
    steps: int | None = None
    sampler: str | None = None
    seed: int | None = None
    size: str | None = None
    model: str | None = None
    clip_skip: int | None = None


class ImageTag(_CivitAIModel):
    """A tag associated with an image."""

    name: str


class Image(_CivitAIModel):
    """An image returned by ``GET /images``."""

    id: int
    url: str
    hash: str | None = None
    width: int | None = None
    height: int | None = None
    nsfw: bool | str | None = None
    nsfw_level: NsfwLevel | str | None = None
    created_at: str | None = None
    post_id: int | None = None
    stats: dict[str, Any] | None = None
    meta: ImageMeta | dict[str, Any] | None = None
    username: str | None = None
