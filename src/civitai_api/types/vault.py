"""Vault response types."""

from __future__ import annotations

from ._base import _CivitAIModel


class VaultItem(_CivitAIModel):
    """A single item in the authenticated user's vault."""

    vault_item_id: int | None = None
    model_version_id: int
    model_id: int | None = None
    model_name: str | None = None
    version_name: str | None = None
    created_at: str | None = None
    files_downloaded_at: str | None = None
    files_size_kb: float | None = None


class VaultStatus(_CivitAIModel):
    """Storage quota and usage for the authenticated user's vault."""

    storage_used: int | None = None
    storage_limit: int | None = None
    used_storage_kb: float | None = None
    created_at: str | None = None
