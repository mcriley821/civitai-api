"""Tests for Models resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest

from civitai_api import AuthenticationError, Model, NotFoundError

if TYPE_CHECKING:
    from respx import MockRouter

    from civitai_api import AsyncCivitAI, CivitAI

MODEL_FIXTURE = {
    "id": 1,
    "name": "Test Model",
    "type": "Checkpoint",
    "poi": False,
    "nsfw": False,
    "allowNoCredit": True,
    "allowDerivatives": True,
    "allowDifferentLicense": True,
    "tags": ["realistic"],
    "modelVersions": [],
}

PAGE_FIXTURE = {
    "items": [MODEL_FIXTURE],
    "metadata": {
        "totalItems": 1,
        "currentPage": 1,
        "pageSize": 20,
        "totalPages": 1,
        "nextCursor": None,
    },
}


def test_models_retrieve(client: CivitAI, civitai_mock: MockRouter) -> None:
    """GET /models/{id} returns a Model object with correct fields."""
    civitai_mock.get("/models/1").mock(
        return_value=httpx.Response(200, json=MODEL_FIXTURE),
    )
    model = client.models.retrieve(1)
    assert isinstance(model, Model)
    assert model.id == 1
    assert model.name == "Test Model"


def test_models_list(client: CivitAI, civitai_mock: MockRouter) -> None:
    """GET /models returns a page of Model objects."""
    civitai_mock.get("/models").mock(
        return_value=httpx.Response(200, json=PAGE_FIXTURE),
    )
    page = client.models.list()
    assert len(page.items) == 1
    assert page.items[0].id == 1


def test_models_list_pagination(client: CivitAI, civitai_mock: MockRouter) -> None:
    """auto_paging_iter() fetches subsequent pages via nextCursor until exhausted."""
    page1_item_id = 1
    page1 = {
        "items": [MODEL_FIXTURE],
        "metadata": {"nextCursor": "cursor1", "totalItems": 2},
    }

    page2_item_id = 2
    page2 = {
        "items": [{**MODEL_FIXTURE, "id": page2_item_id, "name": "Model 2"}],
        "metadata": {"nextCursor": None, "totalItems": 2},
    }
    civitai_mock.get("/models").mock(
        side_effect=[
            httpx.Response(200, json=page1),
            httpx.Response(200, json=page2),
        ],
    )
    page = client.models.list()
    all_models = list(page.auto_paging_iter())

    expected_len = 2

    assert len(all_models) == expected_len
    assert all_models[0].id == page1_item_id
    assert all_models[1].id == page2_item_id


def test_models_retrieve_not_found(client: CivitAI, civitai_mock: MockRouter) -> None:
    """A 404 response from GET /models/{id} raises NotFoundError."""
    civitai_mock.get("/models/999").mock(
        return_value=httpx.Response(404, json={"error": "Not Found"}),
    )
    with pytest.raises(NotFoundError):
        client.models.retrieve(999)


def test_models_retrieve_auth_error(client: CivitAI, civitai_mock: MockRouter) -> None:
    """A 401 response from GET /models/{id} raises AuthenticationError."""
    civitai_mock.get("/models/1").mock(
        return_value=httpx.Response(401, json={"error": "Unauthorized"}),
    )
    with pytest.raises(AuthenticationError):
        client.models.retrieve(1)


async def test_async_models_retrieve(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """GET /models/{id} via async client returns a Model object."""
    civitai_mock.get("/models/1").mock(
        return_value=httpx.Response(200, json=MODEL_FIXTURE),
    )
    model = await async_client.models.retrieve(1)
    assert model.id == 1


async def test_async_models_list(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """GET /models via async client returns a page of Model objects."""
    civitai_mock.get("/models").mock(
        return_value=httpx.Response(200, json=PAGE_FIXTURE),
    )
    page = await async_client.models.list()
    assert len(page.items) == 1
