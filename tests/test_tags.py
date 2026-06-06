"""Tests for Tags resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from civitai_api import Tag

if TYPE_CHECKING:
    from respx import MockRouter

    from civitai_api import AsyncCivitAI, CivitAI

PAGE_FIXTURE = {
    "items": [{"name": "realistic", "modelCount": 100}],
    "metadata": {"nextCursor": None},
}


def test_list(client: CivitAI, civitai_mock: MockRouter) -> None:
    """GET /tags returns a page of Tag objects."""
    civitai_mock.get("/tags").mock(return_value=httpx.Response(200, json=PAGE_FIXTURE))
    page = client.tags.list()
    assert len(page.items) == 1
    assert isinstance(page.items[0], Tag)
    assert page.items[0].name == "realistic"


async def test_async_list(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """GET /tags via async client returns a page of Tag objects."""
    civitai_mock.get("/tags").mock(return_value=httpx.Response(200, json=PAGE_FIXTURE))
    page = await async_client.tags.list()
    assert len(page.items) == 1
    assert isinstance(page.items[0], Tag)
    assert page.items[0].name == "realistic"
