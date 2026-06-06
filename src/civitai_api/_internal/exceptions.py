"""Exception hierarchy for civitai_api."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    import httpx

    from .types import JsonValue


class _ErrorKwargs(TypedDict):
    status_code: int
    request: httpx.Request
    response: httpx.Response
    body: JsonValue | None


class CivitAIError(Exception):
    """Base exception for all civitai_api errors."""


class APIConnectionError(CivitAIError):
    """Failed to connect to the CivitAI API.

    :param message: Human-readable error description
    :type message: str
    :param request: The httpx request that failed
    :type request: httpx.Request
    """

    def __init__(self, message: str, *, request: httpx.Request) -> None:
        super().__init__(message)
        self.request = request


class APITimeoutError(APIConnectionError):
    """Request timed out."""


class APIError(CivitAIError):
    """Non-2xx response from the CivitAI API.

    :param message: Human-readable error description
    :type message: str
    :param status_code: HTTP status code of the response
    :type status_code: int
    :param request: The httpx request that triggered the error
    :type request: httpx.Request
    :param response: The httpx response containing the error
    :type response: httpx.Response
    :param body: Parsed response body, if available, defaults to None
    :type body: Any, optional
    """

    status_code: int
    request: httpx.Request
    response: httpx.Response
    body: JsonValue | None

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        request: httpx.Request,
        response: httpx.Response,
        body: JsonValue | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.request = request
        self.response = response
        self.body = body


class AuthenticationError(APIError):
    """401 Unauthorized."""


class PermissionDeniedError(APIError):
    """403 Forbidden."""


class NotFoundError(APIError):
    """404 Not Found."""


class RateLimitError(APIError):
    """429 Too Many Requests."""


class InternalServerError(APIError):
    """5xx server-side error."""


def _make_status_error(
    response: httpx.Response,
    body: JsonValue | None = None,
) -> APIError:
    """Map an HTTP response to the appropriate :class:`APIError` subclass.

    :param response: The non-2xx httpx response
    :type response: httpx.Response
    :param body: Parsed response body, if available, defaults to None
    :type body: Any, optional
    :return: The most specific APIError subclass for the status code
    :rtype: APIError
    """
    message = f"HTTP {response.status_code}"
    if isinstance(body, dict) and "message" in body:
        message = str(body["message"])
    elif isinstance(body, dict) and "error" in body:
        message = str(body["error"])

    kwargs: _ErrorKwargs = {
        "status_code": response.status_code,
        "request": response.request,
        "response": response,
        "body": body,
    }

    server_error_code_family = 500

    match response.status_code:
        case 401:
            return AuthenticationError(message, **kwargs)
        case 403:
            return PermissionDeniedError(message, **kwargs)
        case 404:
            return NotFoundError(message, **kwargs)
        case 429:
            return RateLimitError(message, **kwargs)
        case _ if response.status_code >= server_error_code_family:
            return InternalServerError(message, **kwargs)
        case _:
            return APIError(message, **kwargs)
