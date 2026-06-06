"""Shared client configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import httpx

DEFAULT_BASE_URL = "https://civitai.com/api/v1"
DEFAULT_TIMEOUT = httpx.Timeout(60.0, connect=5.0)
DEFAULT_MAX_RETRIES = 2


@dataclass
class _Config:
    """Resolved configuration passed to the HTTP client base class."""

    api_key: str | None
    base_url: str
    timeout: httpx.Timeout
    max_retries: int
    default_headers: dict[str, str] = field(default_factory=dict)

    @classmethod
    def build(
        cls,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: httpx.Timeout | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: dict[str, str] | None = None,
    ) -> _Config:
        """Build a ``_Config`` from caller-supplied values, applying defaults.

        :param api_key: Explicit API key; falls back to ``CIVITAI_API_KEY`` env var, defaults to None
        :type api_key: str, optional
        :param base_url: Override base URL; falls back to ``DEFAULT_BASE_URL``, defaults to None
        :type base_url: str, optional
        :param timeout: Request timeout; falls back to ``DEFAULT_TIMEOUT``, defaults to None
        :type timeout: httpx.Timeout, optional
        :param max_retries: Retry limit for 429/5xx responses, defaults to 2
        :type max_retries: int, optional
        :param default_headers: Extra headers merged into every request, defaults to None
        :type default_headers: dict[str, str], optional
        :return: Fully resolved configuration instance
        :rtype: _Config
        """
        return cls(
            api_key=api_key or os.environ.get("CIVITAI_API_KEY"),
            base_url=base_url or os.environ.get("CIVITAI_BASE_URL") or DEFAULT_BASE_URL,
            timeout=timeout or DEFAULT_TIMEOUT,
            max_retries=max_retries,
            default_headers=default_headers or {},
        )
