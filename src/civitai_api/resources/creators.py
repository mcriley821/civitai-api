"""GET /creators."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from civitai_api._internal.resource import AsyncAPIResource, SyncAPIResource
from civitai_api.types.creator import Creator

if TYPE_CHECKING:
    from civitai_api._internal.pagination import AsyncPage, SyncPage


class Creators(SyncAPIResource):
    """Sync resource for /creators endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
        query: str | None = None,
        cursor: str | None = None,
    ) -> SyncPage[Creator]:
        """Return a paginated list of creators.

        :param limit: Maximum number of results per page, defaults to None
        :type limit: int, optional
        :param page: Page number to fetch, defaults to None
        :type page: int, optional
        :param query: Search query string, defaults to None
        :type query: str, optional
        :param cursor: Pagination cursor from a previous response, defaults to None
        :type cursor: str, optional
        :return: First page of matching creators
        :rtype: SyncPage[Creator]
        """
        params: dict[str, Any] = {
            "limit": limit,
            "page": page,
            "query": query,
            "cursor": cursor,
        }
        return self._client.get_page("/creators", params=params, item_type=Creator)


class AsyncCreators(AsyncAPIResource):
    """Async resource for /creators endpoints."""

    async def list(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
        query: str | None = None,
        cursor: str | None = None,
    ) -> AsyncPage[Creator]:
        """Return a paginated list of creators.

        :param limit: Maximum number of results per page, defaults to None
        :type limit: int, optional
        :param page: Page number to fetch, defaults to None
        :type page: int, optional
        :param query: Search query string, defaults to None
        :type query: str, optional
        :param cursor: Pagination cursor from a previous response, defaults to None
        :type cursor: str, optional
        :return: First page of matching creators
        :rtype: AsyncPage[Creator]
        """
        params: dict[str, Any] = {
            "limit": limit,
            "page": page,
            "query": query,
            "cursor": cursor,
        }
        return await self._client.get_page("/creators", params=params, item_type=Creator)
