"""Tests for Creators resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from civitai_api import Creator

if TYPE_CHECKING:
    from respx import MockRouter

    from civitai_api import AsyncCivitAI, CivitAI

PAGE_FIXTURE = {
    "items": [{"username": "artmaker", "modelCount": 5}],
    "metadata": {"nextCursor": None},
}


def test_list(client: CivitAI, civitai_mock: MockRouter) -> None:
    """GET /creators returns a page of Creator objects."""
    civitai_mock.get("/creators").mock(
        return_value=httpx.Response(200, json=PAGE_FIXTURE),
    )
    page = client.creators.list()
    assert len(page.items) == 1
    assert isinstance(page.items[0], Creator)
    assert page.items[0].username == "artmaker"


async def test_async_list(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """GET /creators via async client returns a page of Creator objects."""
    civitai_mock.get("/creators").mock(
        return_value=httpx.Response(200, json=PAGE_FIXTURE),
    )
    page = await async_client.creators.list()
    assert len(page.items) == 1
    assert isinstance(page.items[0], Creator)
    assert page.items[0].username == "artmaker"
