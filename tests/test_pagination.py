"""Tests for pagination behavior."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from respx import MockRouter

    from civitai_api import AsyncCivitAI, CivitAI

MODEL_FIXTURE = {
    "id": 1,
    "name": "M",
    "type": "Checkpoint",
    "poi": False,
    "nsfw": False,
    "allowNoCredit": True,
    "allowDerivatives": True,
    "allowDifferentLicense": True,
    "tags": [],
    "modelVersions": [],
}


def test_has_next_page_true(client: CivitAI, civitai_mock: MockRouter) -> None:
    """has_next_page() returns True when metadata contains a nextCursor."""
    page_data = {
        "items": [MODEL_FIXTURE],
        "metadata": {"nextCursor": "abc"},
    }
    civitai_mock.get("/models").mock(return_value=httpx.Response(200, json=page_data))
    page = client.models.list()
    assert page.has_next_page() is True


def test_has_next_page_false(client: CivitAI, civitai_mock: MockRouter) -> None:
    """has_next_page() returns False when nextCursor is null."""
    page_data = {
        "items": [MODEL_FIXTURE],
        "metadata": {"nextCursor": None},
    }
    civitai_mock.get("/models").mock(return_value=httpx.Response(200, json=page_data))
    page = client.models.list()
    assert page.has_next_page() is False


def test_auto_paging_exhausts_all_pages(
    client: CivitAI,
    civitai_mock: MockRouter,
) -> None:
    """auto_paging_iter() walks all pages until nextCursor is null."""
    pages = [
        {"items": [MODEL_FIXTURE], "metadata": {"nextCursor": "c1"}},
        {"items": [{**MODEL_FIXTURE, "id": 2}], "metadata": {"nextCursor": "c2"}},
        {"items": [{**MODEL_FIXTURE, "id": 3}], "metadata": {"nextCursor": None}},
    ]
    civitai_mock.get("/models").mock(
        side_effect=[httpx.Response(200, json=p) for p in pages],
    )
    all_items = list(client.models.list().auto_paging_iter())
    assert [m.id for m in all_items] == [1, 2, 3]


async def test_async_auto_paging(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """Async __aiter__ yields items from all pages across the cursor chain."""
    pages = [
        {"items": [MODEL_FIXTURE], "metadata": {"nextCursor": "c1"}},
        {"items": [{**MODEL_FIXTURE, "id": 2}], "metadata": {"nextCursor": None}},
    ]
    civitai_mock.get("/models").mock(
        side_effect=[httpx.Response(200, json=p) for p in pages],
    )
    page = await async_client.models.list()
    items = [m async for m in page]
    assert len(items) == len(pages)
