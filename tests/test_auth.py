"""Tests for authentication and OAuth2."""

from __future__ import annotations

import base64
import hashlib
import time
from typing import TYPE_CHECKING

import httpx
import pytest

from civitai_api import AuthenticationError, CivitAI
from civitai_api._internal.oauth2 import OAuth2Token, generate_pkce_pair

if TYPE_CHECKING:
    from respx import MockRouter


def test_api_key_header(civitai_mock: MockRouter) -> None:
    """API key is sent as Authorization: Bearer header on every request."""
    civitai_mock.get("/me").mock(
        return_value=httpx.Response(200, json={"id": 1, "username": "u"}),
    )
    with CivitAI(api_key="sk-test") as c:
        c.users.me()
    req = civitai_mock.calls[-1].request
    assert req.headers["authorization"] == "Bearer sk-test"


def test_no_auth_header_when_no_key(civitai_mock: MockRouter) -> None:
    """No Authorization header is sent when no API key or token is configured."""
    civitai_mock.get("/models").mock(
        return_value=httpx.Response(200, json={"items": [], "metadata": {}}),
    )
    with CivitAI(api_key=None) as c:
        c.models.list()
    req = civitai_mock.calls[-1].request
    assert "authorization" not in req.headers


def test_oauth2_token_used_in_header(civitai_mock: MockRouter) -> None:
    """OAuth2 access token is sent as Authorization: Bearer header."""
    token = OAuth2Token(
        access_token="civitai_abc123",
        token_type="Bearer",
        expires_in=3600,
        issued_at=time.time(),
    )
    civitai_mock.get("/me").mock(
        return_value=httpx.Response(200, json={"id": 1, "username": "u"}),
    )
    with CivitAI(oauth2_token=token) as c:
        c.users.me()
    req = civitai_mock.calls[-1].request
    assert req.headers["authorization"] == "Bearer civitai_abc123"


def test_pkce_challenge_is_correct_sha256() -> None:
    """PKCE challenge is the base64url-encoded SHA-256 digest of the verifier."""
    verifier, challenge = generate_pkce_pair()
    digest = hashlib.sha256(verifier.encode()).digest()
    expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    assert challenge == expected


def test_pkce_verifier_length() -> None:
    """PKCE verifier is exactly 128 characters long."""
    verifier_length_expected = 128
    verifier, _ = generate_pkce_pair()
    assert len(verifier) == verifier_length_expected


def test_oauth2_token_expiry() -> None:
    """OAuth2Token.is_expired() returns True when issued_at + expires_in is past."""
    token = OAuth2Token(
        access_token="t",
        token_type="Bearer",
        expires_in=60,
        issued_at=time.time() - 3600,
    )
    assert token.is_expired()


def test_oauth2_token_not_expired() -> None:
    """OAuth2Token.is_expired() returns False for a freshly issued token."""
    token = OAuth2Token(
        access_token="t",
        token_type="Bearer",
        expires_in=3600,
        issued_at=time.time(),
    )
    assert not token.is_expired()


def test_401_raises_authentication_error(
    client: CivitAI,
    civitai_mock: MockRouter,
) -> None:
    """A 401 response raises AuthenticationError."""
    civitai_mock.get("/me").mock(
        return_value=httpx.Response(401, json={"error": "Unauthorized"}),
    )
    with pytest.raises(AuthenticationError):
        client.users.me()
