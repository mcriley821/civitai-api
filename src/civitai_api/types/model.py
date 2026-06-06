"""Model and ModelVersion response types."""

from typing import Any

from pydantic import Field

from ._base import _CivitAIModel
from .enums import BaseModel, CommercialUse, ModelType


class ModelStats(_CivitAIModel):
    """Aggregate statistics for a model."""

    download_count: int = 0
    favorite_count: int = 0
    thumbs_up_count: int = 0
    thumbs_down_count: int = 0
    comment_count: int = 0
    rating_count: int = 0
    rating: float = 0.0
    tipped_amount_count: int = 0


class ModelVersionStats(_CivitAIModel):
    """Aggregate statistics for a model version."""

    download_count: int = 0
    rating_count: int = 0
    rating: float = 0.0
    thumbs_up_count: int = 0
    thumbs_down_count: int = 0


class ModelFile(_CivitAIModel):
    """A downloadable file attached to a model version."""

    id: int
    size_kb: float | None = None
    name: str
    type: str | None = None
    pickle_scan_result: str | None = None
    pickle_scan_message: str | None = None
    virus_scan_result: str | None = None
    scanned_at: str | None = None
    primary: bool | None = None
    download_url: str


class ModelImage(_CivitAIModel):
    """A preview image attached to a model version."""

    id: int | None = None
    url: str
    nsfw: bool | str | None = None
    width: int | None = None
    height: int | None = None
    hash: str | None = None
    meta: dict[str, Any] | None = None


class ModelVersionFile(_CivitAIModel):
    """A downloadable file attached to a model version, with hash map."""

    id: int
    size_kb: float | None = None
    name: str
    type: str | None = None
    primary: bool | None = None
    download_url: str
    hashes: dict[str, str] = Field(default_factory=dict)


class ModelVersion(_CivitAIModel):
    """A specific version of a model."""

    id: int
    model_id: int | None = None
    name: str
    created_at: str | None = None
    updated_at: str | None = None
    trained_words: list[str] = Field(default_factory=list)
    base_model: BaseModel | str | None = None
    early_access_time_frame: int | None = None
    description: str | None = None
    stats: ModelVersionStats | None = None
    files: list[ModelVersionFile] = Field(default_factory=list)
    images: list[ModelImage] = Field(default_factory=list)
    download_url: str | None = None


class Creator(_CivitAIModel):
    """Minimal creator info embedded in a ``Model`` response."""

    username: str
    image: str | None = None


class Model(_CivitAIModel):
    """A model returned by ``GET /models`` or ``GET /models/{id}``."""

    id: int
    name: str
    description: str | None = None
    type: ModelType | str
    poi: bool = False
    nsfw: bool = False
    allow_no_credit: bool = True
    allow_commercial_use: CommercialUse | list[CommercialUse] | str | None = None
    allow_derivatives: bool = True
    allow_different_license: bool = True
    stats: ModelStats | None = None
    creator: Creator | None = None
    tags: list[str] = Field(default_factory=list)
    model_versions: list[ModelVersion] = Field(default_factory=list)
