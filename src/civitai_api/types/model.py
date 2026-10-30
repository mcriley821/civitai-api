"""Model and ModelVersion response types."""

from typing import Any

from pydantic import Field, field_validator

from ._base import _CivitAIModel, _none_to_default
from .enums import BaseModel, CommercialUse, ModelType


class ModelStats(_CivitAIModel):
    """Aggregate statistics for a model."""

    download_count: int | None = None
    favorite_count: int | None = None
    thumbs_up_count: int | None = None
    thumbs_down_count: int | None = None
    comment_count: int | None = None
    rating_count: int | None = None
    rating: float | None = None
    tipped_amount_count: int | None = None


class ModelVersionStats(_CivitAIModel):
    """Aggregate statistics for a model version."""

    download_count: int | None = None
    rating_count: int | None = None
    rating: float | None = None
    thumbs_up_count: int | None = None
    thumbs_down_count: int | None = None


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

    _hashes_null = field_validator("hashes", mode="before")(_none_to_default(dict))


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

    _lists_null = field_validator("trained_words", "files", "images", mode="before")(
        _none_to_default(list),
    )


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
    poi: bool | None = False
    nsfw: bool | None = False
    allow_no_credit: bool | None = True
    allow_commercial_use: CommercialUse | str | list[CommercialUse | str] | None = None
    allow_derivatives: bool | None = True
    allow_different_license: bool | None = True
    stats: ModelStats | None = None
    creator: Creator | None = None
    tags: list[str] = Field(default_factory=list)
    model_versions: list[ModelVersion] = Field(default_factory=list)

    _lists_null = field_validator("tags", "model_versions", mode="before")(
        _none_to_default(list),
    )
