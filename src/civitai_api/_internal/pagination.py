"""Pagination helpers for CivitAI list endpoints.

CivitAI response shape:
  {"items": [...], "metadata": {"nextCursor": "...", "totalItems": N, ...}}
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, model_validator

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from .base_client import AsyncAPIClient, SyncAPIClient


class PageMetadata(BaseModel):
    """Pagination metadata returned alongside each page of results."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    total_items: int | None = None
    current_page: int | None = None
    page_size: int | None = None
    total_pages: int | None = None
    next_page: str | None = None
    next_cursor: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _camel_to_snake(cls, data: object) -> object:
        """Remap camelCase metadata keys to snake_case before validation.

        :param data: Raw input data from the API response
        :type data: Any
        :return: Input with camelCase keys replaced by snake_case equivalents
        :rtype: Any
        """
        if not isinstance(data, dict):
            return data
        mapping = {
            "totalItems": "total_items",
            "currentPage": "current_page",
            "pageSize": "page_size",
            "totalPages": "total_pages",
            "nextPage": "next_page",
            "nextCursor": "next_cursor",
        }
        return {mapping.get(k, k): v for k, v in data.items()}


class SyncPage[T]:
    """A single page of results with cursor-based auto-pagination.

    :param items: Deserialised items for this page
    :type items: list[T]
    :param metadata: Pagination metadata from the API response
    :type metadata: PageMetadata
    :param client: The API client used to fetch subsequent pages
    :type client: SyncAPIClient
    :param path: API path that produced this page
    :type path: str
    :param params: Query parameters used for this request
    :type params: dict[str, Any]
    :param item_type: The type to deserialise each item into
    :type item_type: type[T]
    """

    items: list[T]
    metadata: PageMetadata

    def __init__(
        self,
        items: list[T],
        metadata: PageMetadata,
        *,
        client: SyncAPIClient,
        path: str,
        params: dict[str, Any],
        item_type: type[T],
    ) -> None:
        self.items = items
        self.metadata = metadata
        self._client = client
        self._path = path
        self._params = params
        self._item_type = item_type

    def has_next_page(self) -> bool:
        """Return ``True`` if a subsequent page is available.

        :return: Whether ``metadata.next_cursor`` is set
        :rtype: bool
        """
        return self.metadata.next_cursor is not None

    def next_page(self) -> SyncPage[T]:
        """Fetch and return the next page using the current cursor.

        :return: The next page of results
        :rtype: SyncPage[T]
        """
        params = {**self._params, "cursor": self.metadata.next_cursor}
        return self._client.get_page(self._path, params=params, item_type=self._item_type)

    def __iter__(self) -> Iterator[T]:
        """Iterate over items on the current page only.

        :return: Iterator over this page's items
        :rtype: Iterator[T]
        """
        return iter(self.items)

    def auto_paging_iter(self) -> Iterator[T]:
        """Iterate over all items across all pages, fetching subsequent pages automatically.

        :return: Iterator that walks every page via cursor
        :rtype: Iterator[T]
        """
        page: SyncPage[T] = self
        while True:
            yield from page.items
            if not page.has_next_page():
                break
            page = page.next_page()


class AsyncPage[T]:
    """Async version of :class:`SyncPage`.

    :param items: Deserialised items for this page
    :type items: list[T]
    :param metadata: Pagination metadata from the API response
    :type metadata: PageMetadata
    :param client: The async API client used to fetch subsequent pages
    :type client: AsyncAPIClient
    :param path: API path that produced this page
    :type path: str
    :param params: Query parameters used for this request
    :type params: dict[str, Any]
    :param item_type: The type to deserialise each item into
    :type item_type: type[T]
    """

    items: list[T]
    metadata: PageMetadata

    def __init__(
        self,
        items: list[T],
        metadata: PageMetadata,
        *,
        client: AsyncAPIClient,
        path: str,
        params: dict[str, Any],
        item_type: type[T],
    ) -> None:
        self.items = items
        self.metadata = metadata
        self._client = client
        self._path = path
        self._params = params
        self._item_type = item_type

    def has_next_page(self) -> bool:
        """Return ``True`` if a subsequent page is available.

        :return: Whether ``metadata.next_cursor`` is set
        :rtype: bool
        """
        return self.metadata.next_cursor is not None

    async def next_page(self) -> AsyncPage[T]:
        """Fetch and return the next page using the current cursor.

        :return: The next page of results
        :rtype: AsyncPage[T]
        """
        params = {**self._params, "cursor": self.metadata.next_cursor}
        return await self._client.get_page(self._path, params=params, item_type=self._item_type)

    def __aiter__(self) -> AsyncIterator[T]:
        """Return an async iterator that walks all pages via cursor.

        :return: Async iterator over all items across all pages
        :rtype: AsyncIterator[T]
        """
        return self._aiter()

    async def _aiter(self) -> AsyncIterator[T]:
        """Async generator that walks all pages and yields every item.

        :return: Async iterator over all items across all pages
        :rtype: AsyncIterator[T]
        """
        page: AsyncPage[T] = self
        while True:
            for item in page.items:
                yield item
            if not page.has_next_page():
                break
            page = await page.next_page()

    async def auto_paging_iter(self) -> AsyncIterator[T]:
        """Iterate over all items across all pages, fetching subsequent pages automatically.

        :return: Async iterator that walks every page via cursor
        :rtype: AsyncIterator[T]
        """
        async for item in self:
            yield item
