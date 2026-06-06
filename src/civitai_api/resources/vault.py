"""Vault endpoints. All require authentication."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from civitai_api._internal.resource import AsyncAPIResource, SyncAPIResource
from civitai_api.types.vault import VaultItem, VaultStatus

if TYPE_CHECKING:
    from civitai_api._internal.pagination import AsyncPage, SyncPage


class Vault(SyncAPIResource):
    """Sync resource for /vault endpoints."""

    def status(self) -> VaultStatus:
        """Return the authenticated user's vault storage status.

        :return: Current vault storage usage and quota
        :rtype: VaultStatus
        :raises AuthenticationError: If no valid credentials are configured
        """
        return self._client.get("/vault/get", cast_to=VaultStatus)

    def list(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
        cursor: str | None = None,
    ) -> SyncPage[VaultItem]:
        """Return a paginated list of the authenticated user's vault items.

        :param limit: Maximum number of results per page, defaults to None
        :type limit: int, optional
        :param page: Page number to fetch, defaults to None
        :type page: int, optional
        :param cursor: Pagination cursor from a previous response, defaults to None
        :type cursor: str, optional
        :return: First page of vault items
        :rtype: SyncPage[VaultItem]
        :raises AuthenticationError: If no valid credentials are configured
        """
        params: dict[str, Any] = {"limit": limit, "page": page, "cursor": cursor}
        return self._client.get_page("/vault/all", params=params, item_type=VaultItem)

    def toggle_version(self, model_version_id: int) -> dict[str, Any]:
        """Add or remove a model version from the authenticated user's vault.

        :param model_version_id: Numeric model version ID to toggle
        :type model_version_id: int
        :return: API response indicating the resulting vault state
        :rtype: dict[str, Any]
        :raises AuthenticationError: If no valid credentials are configured
        """
        return self._client.post(f"/vault/toggle-version/{model_version_id}", cast_to=dict)


class AsyncVault(AsyncAPIResource):
    """Async resource for /vault endpoints."""

    async def status(self) -> VaultStatus:
        """Return the authenticated user's vault storage status.

        :return: Current vault storage usage and quota
        :rtype: VaultStatus
        :raises AuthenticationError: If no valid credentials are configured
        """
        return await self._client.get("/vault/get", cast_to=VaultStatus)

    async def list(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
        cursor: str | None = None,
    ) -> AsyncPage[VaultItem]:
        """Return a paginated list of the authenticated user's vault items.

        :param limit: Maximum number of results per page, defaults to None
        :type limit: int, optional
        :param page: Page number to fetch, defaults to None
        :type page: int, optional
        :param cursor: Pagination cursor from a previous response, defaults to None
        :type cursor: str, optional
        :return: First page of vault items
        :rtype: AsyncPage[VaultItem]
        :raises AuthenticationError: If no valid credentials are configured
        """
        params: dict[str, Any] = {"limit": limit, "page": page, "cursor": cursor}
        return await self._client.get_page("/vault/all", params=params, item_type=VaultItem)

    async def toggle_version(self, model_version_id: int) -> dict[str, Any]:
        """Add or remove a model version from the authenticated user's vault.

        :param model_version_id: Numeric model version ID to toggle
        :type model_version_id: int
        :return: API response indicating the resulting vault state
        :rtype: dict[str, Any]
        :raises AuthenticationError: If no valid credentials are configured
        """
        return await self._client.post(f"/vault/toggle-version/{model_version_id}", cast_to=dict)
