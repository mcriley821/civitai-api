"""Sync and async HTTP client base classes."""

from __future__ import annotations

import time
from asyncio import sleep
from typing import TYPE_CHECKING, Any, Self, TypeVar

import httpx
from pydantic import TypeAdapter

from civitai_api import __version__

from .exceptions import APIConnectionError, APITimeoutError, _make_status_error
from .oauth2 import (
    OAuth2Config,
    OAuth2Token,
    async_refresh_access_token,
    refresh_access_token,
)
from .pagination import AsyncPage, PageMetadata, SyncPage
from .utils import strip_none

if TYPE_CHECKING:
    from .config import _Config
    from .types import JsonValue

T = TypeVar("T")

_RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
_RETRY_BASE_DELAY = 0.5


class SyncAPIClient:
    """Synchronous HTTP request engine with retry, auth, and pagination support.

    :param config: Resolved client configuration
    :type config: _Config
    :param http_client: Optional custom httpx.Client; one is created if omitted, defaults to None
    :type http_client: httpx.Client, optional
    :param oauth2_config: OAuth2 application registration details, defaults to None
    :type oauth2_config: OAuth2Config, optional
    :param oauth2_token: Pre-obtained OAuth2 token, defaults to None
    :type oauth2_token: OAuth2Token, optional
    """

    _config: _Config
    _http: httpx.Client
    _oauth2_config: OAuth2Config | None
    _oauth2_token: OAuth2Token | None

    def __init__(
        self,
        config: _Config,
        http_client: httpx.Client | None = None,
        oauth2_config: OAuth2Config | None = None,
        oauth2_token: OAuth2Token | None = None,
    ) -> None:
        self._config = config
        self._oauth2_config = oauth2_config
        self._oauth2_token = oauth2_token
        self._http = http_client or httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=self._build_headers(),
        )

    def _build_headers(self) -> dict[str, str]:
        """Build the default headers sent with every request.

        :return: Headers dict including Accept, User-Agent, and Authorization if an API key is set
        :rtype: dict[str, str]
        """
        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": f"civitai_api/python/{__version__}",
        }
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"
        headers.update(self._config.default_headers)
        return headers

    def _auth_header(self) -> dict[str, str]:
        """Return the Authorization header for the current request, refreshing the OAuth2 token if expired.

        :return: Dict with an ``Authorization`` key, or empty dict if no credentials are configured
        :rtype: dict[str, str]
        """
        if self._oauth2_token is not None:
            if self._oauth2_token.is_expired() and self._oauth2_config is not None:
                self._oauth2_token = refresh_access_token(self._oauth2_config, self._oauth2_token)
            return {"Authorization": f"Bearer {self._oauth2_token.access_token}"}
        if self._config.api_key:
            return {"Authorization": f"Bearer {self._config.api_key}"}
        return {}

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: JsonValue | None = None,
        cast_to: type[T],
    ) -> T:
        """Execute an HTTP request with automatic retry on 429/5xx responses.

        :param method: HTTP method (``"GET"``, ``"POST"``, etc.)
        :type method: str
        :param path: API path relative to the base URL
        :type path: str
        :param params: Query parameters; ``None`` values are stripped, defaults to None
        :type params: dict[str, Any], optional
        :param json_body: Request body serialised as JSON, defaults to None
        :type json_body: Any, optional
        :param cast_to: Type to deserialise the response body into
        :type cast_to: type[T]
        :return: Deserialised response
        :rtype: T
        :raises APITimeoutError: On request timeout after all retries exhausted
        :raises APIConnectionError: On connection failure after all retries exhausted
        :raises APIError: On a non-2xx response that is not retried
        """
        cleaned_params = strip_none(params) if params else None
        headers = self._auth_header()
        last_exc: Exception | None = None

        for attempt in range(self._config.max_retries + 1):
            if attempt > 0:
                time.sleep(_RETRY_BASE_DELAY * (2 ** (attempt - 1)))
            try:
                response = self._http.request(
                    method,
                    path,
                    params=cleaned_params,
                    json=json_body,
                    headers=headers,
                )
            except httpx.TimeoutException as e:
                last_exc = APITimeoutError(str(e), request=e.request)
                continue
            except httpx.RequestError as e:
                last_exc = APIConnectionError(str(e), request=e.request)
                continue

            if response.status_code in _RETRY_STATUS_CODES and attempt < self._config.max_retries:
                last_exc = None
                continue

            if not response.is_success:
                body: Any = None
                try:
                    body = response.json()
                except ValueError:
                    body = response.text
                raise _make_status_error(response, body)

            data = response.json()
            return TypeAdapter(cast_to).validate_python(data)

        if last_exc is not None:
            raise last_exc

        msg = "unreachable"
        raise RuntimeError(msg)

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        cast_to: type[T],
    ) -> T:
        """Send a GET request and return the deserialised response.

        :param path: API path relative to the base URL
        :type path: str
        :param params: Query parameters, defaults to None
        :type params: dict[str, Any], optional
        :param cast_to: Type to deserialise the response body into
        :type cast_to: type[T]
        :return: Deserialised response
        :rtype: T
        """
        return self._request("GET", path, params=params, cast_to=cast_to)

    def post(
        self,
        path: str,
        *,
        json_body: JsonValue | None = None,
        cast_to: type[T],
    ) -> T:
        """Send a POST request with an optional JSON body and return the deserialised response.

        :param path: API path relative to the base URL
        :type path: str
        :param json_body: Request body to serialise as JSON, defaults to None
        :type json_body: Any, optional
        :param cast_to: Type to deserialise the response body into
        :type cast_to: type[T]
        :return: Deserialised response
        :rtype: T
        """
        return self._request("POST", path, json_body=json_body, cast_to=cast_to)

    def get_page(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        item_type: type[T],
    ) -> SyncPage[T]:
        """Fetch a paginated list endpoint and return a :class:`SyncPage`.

        :param path: API path relative to the base URL
        :type path: str
        :param params: Query parameters; ``None`` values are stripped, defaults to None
        :type params: dict[str, Any], optional
        :param item_type: Type to deserialise each item into
        :type item_type: type[T]
        :return: First page of results
        :rtype: SyncPage[T]
        """
        cleaned_params = strip_none(params) if params else {}
        headers = self._auth_header()
        response = self._http.request(
            "GET",
            path,
            params=cleaned_params,
            headers=headers,
        )
        if not response.is_success:
            body: Any = None
            try:
                body = response.json()
            except ValueError:
                body = response.text
            raise _make_status_error(response, body)
        data = response.json()
        raw_items = data.get("items", [])
        raw_meta = data.get("metadata", {})
        items = [TypeAdapter(item_type).validate_python(item) for item in raw_items]
        metadata = PageMetadata.model_validate(raw_meta)
        return SyncPage(
            items=items,
            metadata=metadata,
            client=self,
            path=path,
            params=cleaned_params,
            item_type=item_type,
        )

    def __enter__(self) -> Self:
        """Enter the context manager, returning self.

        :return: This client instance
        :rtype: SyncAPIClient
        """
        return self

    def __exit__(self, *_: object) -> None:
        """Exit the context manager and close the underlying HTTP client."""
        self._http.close()

    def close(self) -> None:
        """Close the underlying httpx client and release its connections."""
        self._http.close()


class AsyncAPIClient:
    """Asynchronous HTTP request engine with retry, auth, and pagination support.

    :param config: Resolved client configuration
    :type config: _Config
    :param http_client: Optional custom httpx.AsyncClient; one is created if omitted, defaults to None
    :type http_client: httpx.AsyncClient, optional
    :param oauth2_config: OAuth2 application registration details, defaults to None
    :type oauth2_config: OAuth2Config, optional
    :param oauth2_token: Pre-obtained OAuth2 token, defaults to None
    :type oauth2_token: OAuth2Token, optional
    """

    _config: _Config
    _http: httpx.AsyncClient
    _oauth2_config: OAuth2Config | None
    _oauth2_token: OAuth2Token | None

    def __init__(
        self,
        config: _Config,
        http_client: httpx.AsyncClient | None = None,
        oauth2_config: OAuth2Config | None = None,
        oauth2_token: OAuth2Token | None = None,
    ) -> None:
        self._config = config
        self._oauth2_config = oauth2_config
        self._oauth2_token = oauth2_token
        self._http = http_client or httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=self._build_headers(),
        )

    def _build_headers(self) -> dict[str, str]:
        """Build the default headers sent with every request.

        :return: Headers dict including Accept, User-Agent, and Authorization if an API key is set
        :rtype: dict[str, str]
        """
        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": f"civitai_api/python/{__version__}",
        }
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"
        headers.update(self._config.default_headers)
        return headers

    async def _auth_header(self) -> dict[str, str]:
        """Return the Authorization header, refreshing the OAuth2 token if expired.

        :return: Dict with an ``Authorization`` key, or empty dict if no credentials are configured
        :rtype: dict[str, str]
        """
        if self._oauth2_token is not None:
            if self._oauth2_token.is_expired() and self._oauth2_config is not None:
                self._oauth2_token = await async_refresh_access_token(self._oauth2_config, self._oauth2_token)
            return {"Authorization": f"Bearer {self._oauth2_token.access_token}"}
        if self._config.api_key:
            return {"Authorization": f"Bearer {self._config.api_key}"}
        return {}

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: JsonValue | None = None,
        cast_to: type[T],
    ) -> T:
        """Execute an async HTTP request with automatic retry on 429/5xx responses.

        :param method: HTTP method (``"GET"``, ``"POST"``, etc.)
        :type method: str
        :param path: API path relative to the base URL
        :type path: str
        :param params: Query parameters; ``None`` values are stripped, defaults to None
        :type params: dict[str, Any], optional
        :param json_body: Request body serialised as JSON, defaults to None
        :type json_body: Any, optional
        :param cast_to: Type to deserialise the response body into
        :type cast_to: type[T]
        :return: Deserialised response
        :rtype: T
        :raises APITimeoutError: On request timeout after all retries exhausted
        :raises APIConnectionError: On connection failure after all retries exhausted
        :raises APIError: On a non-2xx response that is not retried
        """
        cleaned_params = strip_none(params) if params else None
        headers = await self._auth_header()
        last_exc: Exception | None = None

        for attempt in range(self._config.max_retries + 1):
            if attempt > 0:
                await sleep(_RETRY_BASE_DELAY * (2 ** (attempt - 1)))
            try:
                response = await self._http.request(
                    method,
                    path,
                    params=cleaned_params,
                    json=json_body,
                    headers=headers,
                )
            except httpx.TimeoutException as e:
                last_exc = APITimeoutError(str(e), request=e.request)
                continue
            except httpx.RequestError as e:
                last_exc = APIConnectionError(str(e), request=e.request)
                continue

            if response.status_code in _RETRY_STATUS_CODES and attempt < self._config.max_retries:
                last_exc = None
                continue

            if not response.is_success:
                body: Any = None
                try:
                    body = response.json()
                except ValueError:
                    body = response.text
                raise _make_status_error(response, body)

            data = response.json()
            return TypeAdapter(cast_to).validate_python(data)

        if last_exc is not None:
            raise last_exc

        msg = "unreachable"
        raise RuntimeError(msg)

    async def get(self, path: str, *, params: dict[str, Any] | None = None, cast_to: type[T]) -> T:
        """Send a GET request and return the deserialised response.

        :param path: API path relative to the base URL
        :type path: str
        :param params: Query parameters, defaults to None
        :type params: dict[str, Any], optional
        :param cast_to: Type to deserialise the response body into
        :type cast_to: type[T]
        :return: Deserialised response
        :rtype: T
        """
        return await self._request("GET", path, params=params, cast_to=cast_to)

    async def post(self, path: str, *, json_body: JsonValue | None = None, cast_to: type[T]) -> T:
        """Send a POST request with an optional JSON body and return the deserialised response.

        :param path: API path relative to the base URL
        :type path: str
        :param json_body: Request body to serialise as JSON, defaults to None
        :type json_body: Any, optional
        :param cast_to: Type to deserialise the response body into
        :type cast_to: type[T]
        :return: Deserialised response
        :rtype: T
        """
        return await self._request("POST", path, json_body=json_body, cast_to=cast_to)

    async def get_page(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        item_type: type[T],
    ) -> AsyncPage[T]:
        """Fetch a paginated list endpoint and return an :class:`AsyncPage`.

        :param path: API path relative to the base URL
        :type path: str
        :param params: Query parameters; ``None`` values are stripped, defaults to None
        :type params: dict[str, Any], optional
        :param item_type: Type to deserialise each item into
        :type item_type: type[T]
        :return: First page of results
        :rtype: AsyncPage[T]
        """
        cleaned_params = strip_none(params) if params else {}
        headers = await self._auth_header()
        response = await self._http.request("GET", path, params=cleaned_params, headers=headers)
        if not response.is_success:
            body: Any = None
            try:
                body = response.json()
            except ValueError:
                body = response.text
            raise _make_status_error(response, body)
        data = response.json()
        raw_items = data.get("items", [])
        raw_meta = data.get("metadata", {})
        items = [TypeAdapter(item_type).validate_python(item) for item in raw_items]
        metadata = PageMetadata.model_validate(raw_meta)
        return AsyncPage(
            items=items,
            metadata=metadata,
            client=self,
            path=path,
            params=cleaned_params,
            item_type=item_type,
        )

    async def __aenter__(self) -> Self:
        """Enter the async context manager, returning self.

        :return: This client instance
        :rtype: AsyncAPIClient
        """
        return self

    async def __aexit__(self, *_: object) -> None:
        """Exit the async context manager and close the underlying HTTP client."""
        await self._http.aclose()

    async def aclose(self) -> None:
        """Close the underlying httpx async client and release its connections."""
        await self._http.aclose()
