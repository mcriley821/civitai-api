"""Public client entry points: CivitAI (sync) and AsyncCivitAI (async)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from civitai_api.resources.creators import AsyncCreators, Creators
from civitai_api.resources.enums import AsyncEnums, Enums
from civitai_api.resources.images import AsyncImages, Images
from civitai_api.resources.model_versions import AsyncModelVersions, ModelVersions
from civitai_api.resources.models import AsyncModels, Models
from civitai_api.resources.tags import AsyncTags, Tags
from civitai_api.resources.users import AsyncUsers, Users
from civitai_api.resources.vault import AsyncVault, Vault

from .base_client import AsyncAPIClient, SyncAPIClient
from .config import DEFAULT_MAX_RETRIES, _Config

if TYPE_CHECKING:
    from collections.abc import Mapping

    import httpx

    from .oauth2 import OAuth2Config, OAuth2Token


class CivitAI(SyncAPIClient):
    """Synchronous CivitAI API client.

    Authentication (pick one):

    - ``api_key``: explicit key, or set ``CIVITAI_API_KEY`` env var
    - ``oauth2_token``: pre-obtained OAuth2 token

    :param api_key: API key; falls back to ``CIVITAI_API_KEY`` env var, defaults to None
    :type api_key: str, optional
    :param base_url: Override the default API base URL, defaults to None
    :type base_url: str, optional
    :param timeout: Custom request timeout, defaults to None
    :type timeout: httpx.Timeout, optional
    :param max_retries: Number of automatic retries on 429/5xx responses, defaults to 2
    :type max_retries: int, optional
    :param default_headers: Extra headers merged into every request, defaults to None
    :type default_headers: Mapping[str, str], optional
    :param http_client: Custom httpx.Client; a new one is created if omitted, defaults to None
    :type http_client: httpx.Client, optional
    :param oauth2_config: OAuth2 application registration details, defaults to None
    :type oauth2_config: OAuth2Config, optional
    :param oauth2_token: Pre-obtained OAuth2 access token, defaults to None
    :type oauth2_token: OAuth2Token, optional
    """

    models: Models
    model_versions: ModelVersions
    images: Images
    creators: Creators
    tags: Tags
    users: Users
    vault: Vault
    enums: Enums

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: httpx.Timeout | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        http_client: httpx.Client | None = None,
        oauth2_config: OAuth2Config | None = None,
        oauth2_token: OAuth2Token | None = None,
    ) -> None:
        config = _Config.build(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=dict(default_headers) if default_headers else None,
        )
        super().__init__(
            config,
            http_client,
            oauth2_config=oauth2_config,
            oauth2_token=oauth2_token,
        )
        self.models = Models(self)
        self.model_versions = ModelVersions(self)
        self.images = Images(self)
        self.creators = Creators(self)
        self.tags = Tags(self)
        self.users = Users(self)
        self.vault = Vault(self)
        self.enums = Enums(self)


class AsyncCivitAI(AsyncAPIClient):
    """Asynchronous CivitAI API client.

    Authentication (pick one):

    - ``api_key``: explicit key, or set ``CIVITAI_API_KEY`` env var
    - ``oauth2_token``: pre-obtained OAuth2 token

    :param api_key: API key; falls back to ``CIVITAI_API_KEY`` env var, defaults to None
    :type api_key: str, optional
    :param base_url: Override the default API base URL, defaults to None
    :type base_url: str, optional
    :param timeout: Custom request timeout, defaults to None
    :type timeout: httpx.Timeout, optional
    :param max_retries: Number of automatic retries on 429/5xx responses, defaults to 2
    :type max_retries: int, optional
    :param default_headers: Extra headers merged into every request, defaults to None
    :type default_headers: Mapping[str, str], optional
    :param http_client: Custom httpx.AsyncClient; a new one is created if omitted, defaults to None
    :type http_client: httpx.AsyncClient, optional
    :param oauth2_config: OAuth2 application registration details, defaults to None
    :type oauth2_config: OAuth2Config, optional
    :param oauth2_token: Pre-obtained OAuth2 access token, defaults to None
    :type oauth2_token: OAuth2Token, optional
    """

    models: AsyncModels
    model_versions: AsyncModelVersions
    images: AsyncImages
    creators: AsyncCreators
    tags: AsyncTags
    users: AsyncUsers
    vault: AsyncVault
    enums: AsyncEnums

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: httpx.Timeout | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        http_client: httpx.AsyncClient | None = None,
        oauth2_config: OAuth2Config | None = None,
        oauth2_token: OAuth2Token | None = None,
    ) -> None:
        config = _Config.build(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=dict(default_headers) if default_headers else None,
        )
        super().__init__(
            config,
            http_client,
            oauth2_config=oauth2_config,
            oauth2_token=oauth2_token,
        )
        self.models = AsyncModels(self)
        self.model_versions = AsyncModelVersions(self)
        self.images = AsyncImages(self)
        self.creators = AsyncCreators(self)
        self.tags = AsyncTags(self)
        self.users = AsyncUsers(self)
        self.vault = AsyncVault(self)
        self.enums = AsyncEnums(self)
