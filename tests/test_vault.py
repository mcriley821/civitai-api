"""Tests for Vault resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from civitai_api import VaultItem, VaultStatus

if TYPE_CHECKING:
    from respx import MockRouter

    from civitai_api import AsyncCivitAI, CivitAI

STATUS_FIXTURE = {"storageUsed": 1024, "storageLimit": 10240}

MODEL_VERSION_ID = 50
LIST_FIXTURE = {
    "items": [{"modelVersionId": MODEL_VERSION_ID, "vaultItemId": 1}],
    "metadata": {"nextCursor": None},
}


def test_status(client: CivitAI, civitai_mock: MockRouter) -> None:
    """GET /vault/get returns a VaultStatus object."""
    civitai_mock.get("/vault/get").mock(
        return_value=httpx.Response(200, json=STATUS_FIXTURE),
    )
    status = client.vault.status()
    assert isinstance(status, VaultStatus)


def test_list(client: CivitAI, civitai_mock: MockRouter) -> None:
    """GET /vault/all returns a page of VaultItem objects."""
    civitai_mock.get("/vault/all").mock(
        return_value=httpx.Response(200, json=LIST_FIXTURE),
    )
    page = client.vault.list()
    assert len(page.items) == 1
    assert isinstance(page.items[0], VaultItem)
    assert page.items[0].model_version_id == MODEL_VERSION_ID


def test_toggle_version(client: CivitAI, civitai_mock: MockRouter) -> None:
    """POST /vault/toggle-version/{id} returns the toggle result."""
    civitai_mock.post(f"/vault/toggle-version/{MODEL_VERSION_ID}").mock(
        return_value=httpx.Response(200, json={"added": True}),
    )
    result = client.vault.toggle_version(MODEL_VERSION_ID)
    assert result == {"added": True}


async def test_async_status(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """GET /vault/get via async client returns a VaultStatus object."""
    civitai_mock.get("/vault/get").mock(
        return_value=httpx.Response(200, json=STATUS_FIXTURE),
    )
    status = await async_client.vault.status()
    assert isinstance(status, VaultStatus)


async def test_async_list(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """GET /vault/all via async client returns a page of VaultItem objects."""
    civitai_mock.get("/vault/all").mock(
        return_value=httpx.Response(200, json=LIST_FIXTURE),
    )
    page = await async_client.vault.list()
    assert len(page.items) == 1
    assert isinstance(page.items[0], VaultItem)
    assert page.items[0].model_version_id == MODEL_VERSION_ID


async def test_async_toggle_version(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """POST /vault/toggle-version/{id} via async client returns the toggle result."""
    civitai_mock.post(f"/vault/toggle-version/{MODEL_VERSION_ID}").mock(
        return_value=httpx.Response(200, json={"added": True}),
    )
    result = await async_client.vault.toggle_version(MODEL_VERSION_ID)
    assert result == {"added": True}
