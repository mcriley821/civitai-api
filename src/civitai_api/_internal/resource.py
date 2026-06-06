"""Base classes for API resource namespaces."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_client import AsyncAPIClient, SyncAPIClient


class SyncAPIResource:
    """Base class for synchronous resource namespaces.

    :param client: The sync client that owns this resource
    :type client: SyncAPIClient
    """

    _client: SyncAPIClient

    def __init__(self, client: SyncAPIClient) -> None:
        self._client = client


class AsyncAPIResource:
    """Base class for asynchronous resource namespaces.

    :param client: The async client that owns this resource
    :type client: AsyncAPIClient
    """

    _client: AsyncAPIClient

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client
