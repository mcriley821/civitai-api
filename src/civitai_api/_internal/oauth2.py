"""OAuth2 helpers for CivitAI's Authorization Code + PKCE flow."""

from __future__ import annotations

import base64
import hashlib
import http.server
import json
import os
import secrets
import threading
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass, field
from enum import IntFlag
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import urlencode
from warnings import warn

import httpx

DEFAULT_OAUTH2_BASE_URL = "https://civitai.com/api/auth/oauth"
DEFAULT_AUTHORIZE_ENDPOINT = "/authorize"
DEFAULT_TOKEN_ENDPOINT = "/token"  # noqa: S105 - is a path
DEFAULT_REVOKE_ENDPOINT = "/revoke"
DEFAULT_USERINFO_ENDPOINT = "/userinfo"


class Scope(IntFlag):
    """CivitAI OAuth2 permission scopes (bitwise flags).

    Values are derived from https://developer.civitai.com/site/oauth/.
    UserRead is always included by CivitAI regardless of requested scopes.
    """

    UserRead = 1
    UserWrite = 2
    ModelsRead = 4
    ModelsWrite = 8
    ImagesRead = 16
    ImagesWrite = 32
    CreatorsRead = 64
    VaultRead = 128
    VaultWrite = 256
    AIServicesRead = 512
    AIServicesWrite = 1024
    BountiesRead = 2048
    BountiesWrite = 4096

    # Convenience presets
    READ_ONLY = UserRead | ModelsRead | ImagesRead | CreatorsRead | VaultRead
    CREATOR = READ_ONLY | ModelsWrite | ImagesWrite | VaultWrite
    AI_SERVICES = READ_ONLY | AIServicesRead | AIServicesWrite
    FULL_ACCESS = (
        UserRead
        | UserWrite
        | ModelsRead
        | ModelsWrite
        | ImagesRead
        | ImagesWrite
        | CreatorsRead
        | VaultRead
        | VaultWrite
        | AIServicesRead
        | AIServicesWrite
        | BountiesRead
        | BountiesWrite
    )


@dataclass
class OAuth2Config:
    """OAuth2 application registration details."""

    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: Scope = Scope.READ_ONLY
    oauth2_base_url: str = field(
        default_factory=lambda: os.environ.get("CIVITAI_OAUTH2_BASE_URL") or DEFAULT_OAUTH2_BASE_URL,
    )
    authorize_endpoint: str = DEFAULT_AUTHORIZE_ENDPOINT
    token_endpoint: str = DEFAULT_TOKEN_ENDPOINT
    revoke_endpoint: str = DEFAULT_REVOKE_ENDPOINT
    userinfo_endpoint: str = DEFAULT_USERINFO_ENDPOINT

    @property
    def authorize_url(self) -> str:
        """Full authorization endpoint URL."""
        return f"{self.oauth2_base_url}{self.authorize_endpoint}"

    @property
    def token_url(self) -> str:
        """Full token endpoint URL."""
        return f"{self.oauth2_base_url}{self.token_endpoint}"

    @property
    def revoke_url(self) -> str:
        """Full token revocation endpoint URL."""
        return f"{self.oauth2_base_url}{self.revoke_endpoint}"

    @property
    def userinfo_url(self) -> str:
        """Full userinfo endpoint URL."""
        return f"{self.oauth2_base_url}{self.userinfo_endpoint}"


@dataclass
class OAuth2Token:
    """A CivitAI OAuth2 token pair."""

    access_token: str
    token_type: str
    expires_in: int
    issued_at: float = field(default_factory=time.time)
    refresh_token: str | None = None

    @property
    def expires_at(self) -> float:
        """Unix timestamp at which the access token expires.

        :return: ``issued_at + expires_in``
        :rtype: float
        """
        return self.issued_at + self.expires_in

    def is_expired(self, buffer_seconds: int = 30) -> bool:
        """Return ``True`` if the access token has expired or is about to expire.

        :param buffer_seconds: Seconds before actual expiry to consider the token expired, defaults to 30
        :type buffer_seconds: int, optional
        :return: Whether the token should be refreshed
        :rtype: bool
        """
        return time.time() >= self.expires_at - buffer_seconds

    def to_dict(self) -> dict[str, Any]:
        """Serialise the token to a plain dictionary for persistence.

        :return: Token fields as a JSON-serialisable dict
        :rtype: dict[str, Any]
        """
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "issued_at": self.issued_at,
            "refresh_token": self.refresh_token,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OAuth2Token:
        """Deserialise a token from a dictionary (e.g. loaded from a file).

        :param data: Dictionary previously produced by :meth:`to_dict`
        :type data: dict[str, Any]
        :return: Reconstructed token
        :rtype: OAuth2Token
        """
        return cls(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_in=data["expires_in"],
            issued_at=data.get("issued_at", time.time()),
            refresh_token=data.get("refresh_token"),
        )

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> OAuth2Token:
        """Construct a token from a raw token endpoint response.

        :param data: Parsed JSON body from the token endpoint
        :type data: dict[str, Any]
        :return: Token populated from the response
        :rtype: OAuth2Token
        """
        return cls(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_in=data["expires_in"],
            refresh_token=data.get("refresh_token"),
        )


class TokenStore(Protocol):
    """Protocol for persisting OAuth2 tokens."""

    def load(self) -> OAuth2Token | None:
        """Load a previously saved token, or return ``None`` if none exists.

        :return: Stored token, or ``None``
        :rtype: OAuth2Token or None
        """
        ...

    def save(self, token: OAuth2Token) -> None:
        """Persist a token.

        :param token: Token to store
        :type token: OAuth2Token
        """
        ...

    def clear(self) -> None:
        """Delete any stored token."""
        ...


class MemoryTokenStore:
    """In-process token storage (default).

    Stores the token in a plain instance attribute; not persisted across processes.
    """

    def __init__(self) -> None:
        self._token: OAuth2Token | None = None

    def load(self) -> OAuth2Token | None:
        """Return the in-memory token, or ``None`` if none has been saved.

        :return: Stored token, or ``None``
        :rtype: OAuth2Token or None
        """
        return self._token

    def save(self, token: OAuth2Token) -> None:
        """Store a token in memory.

        :param token: Token to store
        :type token: OAuth2Token
        """
        self._token = token

    def clear(self) -> None:
        """Clear the in-memory token."""
        self._token = None


class FileTokenStore:
    """JSON file token storage, suitable for CLI use.

    :param path: Path to the JSON file used for persistence
    :type path: str or Path
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

        if self._path.exists() and self._path.lstat().st_mode ^ 0o600 != 0:
            msg = f"token should have stricter permissions: {self._path}"
            warn(msg, None, stacklevel=-1)

    def load(self) -> OAuth2Token | None:
        """Load a token from the JSON file.

        :return: Stored token, or ``None`` if the file does not exist or is invalid
        :rtype: OAuth2Token or None
        """
        if not self._path.exists():
            return None
        try:
            return OAuth2Token.from_dict(json.loads(self._path.read_text()))
        except (json.JSONDecodeError, KeyError):
            return None

    def save(self, token: OAuth2Token) -> None:
        """Write a token to the JSON file, creating parent directories as needed.

        :param token: Token to persist
        :type token: OAuth2Token
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(token.to_dict(), indent=2))

    def clear(self) -> None:
        """Delete the token file if it exists."""
        if self._path.exists():
            self._path.unlink()


def generate_pkce_pair() -> tuple[str, str]:
    """Return ``(code_verifier, code_challenge)`` for PKCE S256.

    :return: Tuple of (verifier, SHA-256 base64url challenge)
    :rtype: tuple[str, str]
    """
    verifier = secrets.token_urlsafe(96)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def build_authorization_url(
    config: OAuth2Config,
    state: str,
    code_challenge: str,
) -> str:
    """Build the authorization URL for the PKCE flow.

    :param config: OAuth2 application registration details
    :type config: OAuth2Config
    :param state: Random state value for CSRF protection
    :type state: str
    :param code_challenge: PKCE S256 challenge derived from the verifier
    :type code_challenge: str
    :return: Full authorization URL to redirect the user to
    :rtype: str
    """
    params = {
        "client_id": config.client_id,
        "redirect_uri": config.redirect_uri,
        "scope": int(config.scopes),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
        "response_type": "code",
    }
    return f"{config.authorize_url}?{urlencode(params)}"


def _exchange_code(
    config: OAuth2Config,
    code: str,
    code_verifier: str,
) -> OAuth2Token:
    """Exchange an authorization code for tokens (sync).

    :param config: OAuth2 application registration details
    :type config: OAuth2Config
    :param code: Authorization code received from the callback
    :type code: str
    :param code_verifier: PKCE code verifier matching the original challenge
    :type code_verifier: str
    :return: Token issued by the token endpoint
    :rtype: OAuth2Token
    """
    with httpx.Client() as client:
        response = client.post(
            config.token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "code": code,
                "code_verifier": code_verifier,
                "redirect_uri": config.redirect_uri,
            },
        )
        response.raise_for_status()
        return OAuth2Token.from_response(response.json())


async def _async_exchange_code(
    config: OAuth2Config,
    code: str,
    code_verifier: str,
) -> OAuth2Token:
    """Exchange an authorization code for tokens (async).

    :param config: OAuth2 application registration details
    :type config: OAuth2Config
    :param code: Authorization code received from the callback
    :type code: str
    :param code_verifier: PKCE code verifier matching the original challenge
    :type code_verifier: str
    :return: Token issued by the token endpoint
    :rtype: OAuth2Token
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            config.token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "code": code,
                "code_verifier": code_verifier,
                "redirect_uri": config.redirect_uri,
            },
        )
        response.raise_for_status()
        return OAuth2Token.from_response(response.json())


def refresh_access_token(config: OAuth2Config, token: OAuth2Token) -> OAuth2Token:
    """Exchange a refresh token for a new access token (sync).

    :param config: OAuth2 application registration details
    :type config: OAuth2Config
    :param token: Existing token whose ``refresh_token`` will be used
    :type token: OAuth2Token
    :return: New token issued by the token endpoint
    :rtype: OAuth2Token
    :raises ValueError: If ``token.refresh_token`` is ``None``
    """
    if token.refresh_token is None:
        msg = "token has no refresh token"
        raise ValueError(msg)
    with httpx.Client() as client:
        response = client.post(
            config.token_url,
            data={
                "grant_type": "refresh_token",
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "refresh_token": token.refresh_token,
            },
        )
        response.raise_for_status()
        return OAuth2Token.from_response(response.json())


async def async_refresh_access_token(config: OAuth2Config, token: OAuth2Token) -> OAuth2Token:
    """Exchange a refresh token for a new access token (async).

    :param config: OAuth2 application registration details
    :type config: OAuth2Config
    :param token: Existing token whose ``refresh_token`` will be used
    :type token: OAuth2Token
    :return: New token issued by the token endpoint
    :rtype: OAuth2Token
    :raises ValueError: If ``token.refresh_token`` is ``None``
    """
    if token.refresh_token is None:
        msg = "token has no refresh token"
        raise ValueError(msg)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            config.token_url,
            data={
                "grant_type": "refresh_token",
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "refresh_token": token.refresh_token,
            },
        )
        response.raise_for_status()
        return OAuth2Token.from_response(response.json())


def revoke_token(config: OAuth2Config, token: OAuth2Token) -> None:
    """Revoke an access token at the revocation endpoint.

    :param config: OAuth2 application registration details
    :type config: OAuth2Config
    :param token: Token to revoke
    :type token: OAuth2Token
    """
    with httpx.Client() as client:
        client.post(
            config.revoke_url,
            data={
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "token": token.access_token,
            },
        )


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    """Minimal HTTP handler that captures the OAuth2 callback."""

    code: str | None = None
    state: str | None = None
    error: str | None = None

    def do_GET(self) -> None:
        """Handle the GET callback from the authorization server.

        Parses ``code``, ``state``, and ``error`` from the query string and
        stores them as class attributes, then responds with a success page.
        """
        parsed = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        _CallbackHandler.code = params.get("code")
        _CallbackHandler.state = params.get("state")
        _CallbackHandler.error = params.get("error")

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        body = b"<html><body><p>Authentication successful. You may close this window.</p></body></html>"
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:
        """Suppress the default server request log output."""


def run_pkce_flow(
    config: OAuth2Config,
    *,
    port: int = 8080,
    store: TokenStore | None = None,
) -> OAuth2Token:
    """Run Authorization Code + PKCE flow interactively (opens browser).

    Starts a temporary local HTTP server to receive the callback, then
    exchanges the authorization code for tokens.

    :param config: OAuth2 application registration details
    :type config: OAuth2Config
    :param port: Local port for the temporary callback server, defaults to 8080
    :type port: int, optional
    :param store: Optional token store; if provided the new token is saved, defaults to None
    :type store: TokenStore, optional
    :return: Freshly issued OAuth2 token
    :rtype: OAuth2Token
    :raises RuntimeError: If the authorization server returns an error, the callback
        receives no code, or the state parameter does not match (CSRF check)
    """
    verifier, challenge = generate_pkce_pair()
    state = secrets.token_urlsafe(16)
    url = build_authorization_url(config, state, challenge)

    _CallbackHandler.code = None
    _CallbackHandler.state = None
    _CallbackHandler.error = None

    server = http.server.HTTPServer(("localhost", port), _CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()

    webbrowser.open(url)
    thread.join(timeout=120)
    server.server_close()

    if _CallbackHandler.error:
        msg = f"OAuth2 error: {_CallbackHandler.error}"
        raise RuntimeError(msg)
    if not _CallbackHandler.code:
        msg = "No authorization code received from callback"
        raise RuntimeError(msg)
    if _CallbackHandler.state != state:
        msg = "OAuth2 state mismatch — possible CSRF attack"
        raise RuntimeError(msg)

    token = _exchange_code(config, _CallbackHandler.code, verifier)
    if store is not None:
        store.save(token)
    return token
