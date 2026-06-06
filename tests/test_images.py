"""Tests for Images resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from civitai_api import Image

if TYPE_CHECKING:
    from respx import MockRouter

    from civitai_api import AsyncCivitAI, CivitAI

IMAGE_ID = 42
IMAGE_FIXTURE = {"id": IMAGE_ID, "url": "https://example.com/img.jpg"}
PAGE_FIXTURE = {
    "items": [IMAGE_FIXTURE],
    "metadata": {"nextCursor": None, "totalItems": 1},
}


def test_list(client: CivitAI, civitai_mock: MockRouter) -> None:
    """GET /images returns a page of Image objects."""
    civitai_mock.get("/images").mock(
        return_value=httpx.Response(200, json=PAGE_FIXTURE),
    )
    page = client.images.list()
    assert len(page.items) == 1
    assert isinstance(page.items[0], Image)
    assert page.items[0].id == IMAGE_ID


async def test_async_list(async_client: AsyncCivitAI, civitai_mock: MockRouter) -> None:
    """GET /images via async client returns a page of Image objects."""
    civitai_mock.get("/images").mock(
        return_value=httpx.Response(200, json=PAGE_FIXTURE),
    )
    page = await async_client.images.list()
    assert page.items[0].id == IMAGE_ID
