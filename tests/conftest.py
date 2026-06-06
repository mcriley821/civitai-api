"""Shared test fixtures."""

from __future__ import annotations

import pytest
import respx

from civitai_api import AsyncCivitAI, CivitAI

BASE = "https://civitai.com/api/v1"
OAUTH_BASE = "https://civitai.com/api/auth/oauth"


@pytest.fixture
def civitai_mock() -> respx.MockRouter:
    """Mock router for the CivitAI v1 API base URL."""
    with respx.mock(base_url=BASE, assert_all_called=False) as router:
        yield router


@pytest.fixture
def oauth2_mock() -> respx.MockRouter:
    """Mock router for the CivitAI OAuth2 endpoint base URL."""
    with respx.mock(base_url=OAUTH_BASE, assert_all_called=False) as router:
        yield router


@pytest.fixture
def client(civitai_mock: respx.MockRouter) -> CivitAI:  # noqa: ARG001
    """Sync CivitAI client wired to the mock router."""
    with CivitAI(api_key="test-key") as c:
        yield c


@pytest.fixture
async def async_client(civitai_mock: respx.MockRouter) -> AsyncCivitAI:  # noqa: ARG001
    """Async CivitAI client wired to the mock router."""
    async with AsyncCivitAI(api_key="test-key") as c:
        yield c
