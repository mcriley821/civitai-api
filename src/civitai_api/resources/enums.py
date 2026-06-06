"""GET /enums — available enumeration values."""

from __future__ import annotations

from typing import Any

from civitai_api._internal.resource import AsyncAPIResource, SyncAPIResource


class Enums(SyncAPIResource):
    """Sync resource for /enums endpoint."""

    def list(self) -> dict[str, Any]:
        """Return all available enumeration values from the API.

        :return: Mapping of enum name to its allowed values
        :rtype: dict[str, Any]
        """
        return self._client.get("/enums", cast_to=dict)


class AsyncEnums(AsyncAPIResource):
    """Async resource for /enums endpoint."""

    async def list(self) -> dict[str, Any]:
        """Return all available enumeration values from the API.

        :return: Mapping of enum name to its allowed values
        :rtype: dict[str, Any]
        """
        return await self._client.get("/enums", cast_to=dict)
