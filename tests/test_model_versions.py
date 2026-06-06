"""Tests for ModelVersions resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from civitai_api import ModelVersion

if TYPE_CHECKING:
    from respx import MockRouter

    from civitai_api import AsyncCivitAI, CivitAI

VERSION_ID = 100
SECOND_VERSION_ID = 101
VERSION_FIXTURE = {
    "id": VERSION_ID,
    "name": "v1.0",
    "trainedWords": ["realistic"],
    "files": [],
    "images": [],
}


def test_retrieve(client: CivitAI, civitai_mock: MockRouter) -> None:
    """GET /model-versions/{id} returns a ModelVersion object."""
    civitai_mock.get("/model-versions/100").mock(
        return_value=httpx.Response(200, json=VERSION_FIXTURE),
    )
    v = client.model_versions.retrieve(100)
    assert isinstance(v, ModelVersion)
    assert v.id == VERSION_ID


def test_by_hash(client: CivitAI, civitai_mock: MockRouter) -> None:
    """GET /model-versions/by-hash/{hash} returns the matching ModelVersion."""
    civitai_mock.get("/model-versions/by-hash/abc123").mock(
        return_value=httpx.Response(200, json=VERSION_FIXTURE),
    )
    v = client.model_versions.by_hash("abc123")
    assert v.id == VERSION_ID


async def test_async_retrieve(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """GET /model-versions/{id} via async client returns a ModelVersion object."""
    civitai_mock.get("/model-versions/100").mock(
        return_value=httpx.Response(200, json=VERSION_FIXTURE),
    )
    v = await async_client.model_versions.retrieve(100)
    assert v.id == VERSION_ID


async def test_async_by_hash(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """GET /model-versions/by-hash/{hash} via async client returns the matching ModelVersion."""
    civitai_mock.get("/model-versions/by-hash/abc123").mock(
        return_value=httpx.Response(200, json=VERSION_FIXTURE),
    )
    v = await async_client.model_versions.by_hash("abc123")
    assert v.id == VERSION_ID


def test_by_hash_batch(client: CivitAI, civitai_mock: MockRouter) -> None:
    """POST /model-versions/by-hash with a list of hashes returns a list of ModelVersions."""
    batch_fixture = [VERSION_FIXTURE, {**VERSION_FIXTURE, "id": SECOND_VERSION_ID}]
    civitai_mock.post("/model-versions/by-hash").mock(
        return_value=httpx.Response(200, json=batch_fixture),
    )
    results = client.model_versions.by_hash_batch(["hash1", "hash2"])
    expected_count = 2
    assert len(results) == expected_count
    assert isinstance(results[0], ModelVersion)
    assert results[0].id == VERSION_ID
    assert results[1].id == SECOND_VERSION_ID


async def test_async_by_hash_batch(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """POST /model-versions/by-hash via async client returns a list of ModelVersions."""
    batch_fixture = [VERSION_FIXTURE, {**VERSION_FIXTURE, "id": SECOND_VERSION_ID}]
    civitai_mock.post("/model-versions/by-hash").mock(
        return_value=httpx.Response(200, json=batch_fixture),
    )
    results = await async_client.model_versions.by_hash_batch(["hash1", "hash2"])
    expected_count = 2
    assert len(results) == expected_count
    assert results[1].id == SECOND_VERSION_ID
