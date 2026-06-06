"""GET /tags."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from civitai_api._internal.resource import AsyncAPIResource, SyncAPIResource
from civitai_api.types.tag import Tag

if TYPE_CHECKING:
    from civitai_api._internal.pagination import AsyncPage, SyncPage


class Tags(SyncAPIResource):
    """Sync resource for /tags endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
        query: str | None = None,
        cursor: str | None = None,
    ) -> SyncPage[Tag]:
        """Return a paginated list of tags.

        :param limit: Maximum number of results per page, defaults to None
        :type limit: int, optional
        :param page: Page number to fetch, defaults to None
        :type page: int, optional
        :param query: Search query string, defaults to None
        :type query: str, optional
        :param cursor: Pagination cursor from a previous response, defaults to None
        :type cursor: str, optional
        :return: First page of matching tags
        :rtype: SyncPage[Tag]
        """
        params: dict[str, Any] = {
            "limit": limit,
            "page": page,
            "query": query,
            "cursor": cursor,
        }
        return self._client.get_page("/tags", params=params, item_type=Tag)


class AsyncTags(AsyncAPIResource):
    """Async resource for /tags endpoints."""

    async def list(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
        query: str | None = None,
        cursor: str | None = None,
    ) -> AsyncPage[Tag]:
        """Return a paginated list of tags.

        :param limit: Maximum number of results per page, defaults to None
        :type limit: int, optional
        :param page: Page number to fetch, defaults to None
        :type page: int, optional
        :param query: Search query string, defaults to None
        :type query: str, optional
        :param cursor: Pagination cursor from a previous response, defaults to None
        :type cursor: str, optional
        :return: First page of matching tags
        :rtype: AsyncPage[Tag]
        """
        params: dict[str, Any] = {
            "limit": limit,
            "page": page,
            "query": query,
            "cursor": cursor,
        }
        return await self._client.get_page("/tags", params=params, item_type=Tag)
