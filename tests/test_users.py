"""Tests for Users resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from civitai_api import Me, User

if TYPE_CHECKING:
    from respx import MockRouter

    from civitai_api import AsyncCivitAI, CivitAI

USER_FIXTURE = {"id": 1, "username": "johndoe", "image": None}
ME_FIXTURE = {"id": 2, "username": "me", "email": "me@example.com"}


def test_retrieve(client: CivitAI, civitai_mock: MockRouter) -> None:
    """GET /users/{username} returns a User object."""
    civitai_mock.get("/users/johndoe").mock(
        return_value=httpx.Response(200, json=USER_FIXTURE),
    )
    user = client.users.retrieve("johndoe")
    assert isinstance(user, User)
    assert user.username == "johndoe"


def test_me(client: CivitAI, civitai_mock: MockRouter) -> None:
    """GET /me returns the authenticated user as a Me object."""
    civitai_mock.get("/me").mock(return_value=httpx.Response(200, json=ME_FIXTURE))
    me = client.users.me()
    assert isinstance(me, Me)
    assert me.username == "me"


async def test_async_retrieve(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """GET /users/{username} via async client returns a User object."""
    civitai_mock.get("/users/johndoe").mock(
        return_value=httpx.Response(200, json=USER_FIXTURE),
    )
    user = await async_client.users.retrieve("johndoe")
    assert user.username == "johndoe"


async def test_async_me(
    async_client: AsyncCivitAI,
    civitai_mock: MockRouter,
) -> None:
    """GET /me via async client returns the authenticated user as a Me object."""
    civitai_mock.get("/me").mock(return_value=httpx.Response(200, json=ME_FIXTURE))
    me = await async_client.users.me()
    assert isinstance(me, Me)
    assert me.username == "me"
