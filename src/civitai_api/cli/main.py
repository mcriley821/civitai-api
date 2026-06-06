"""civitai CLI — manual interface to the CivitAI API."""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

try:
    import jmespath as _jmespath
    import typer
except ImportError as e:
    msg = "CLI extras not installed. Run: pip install civitai_api[cli]"
    raise ImportError(msg) from e

from civitai_api import __version__
from civitai_api._internal.client import CivitAI
from civitai_api._internal.oauth2 import (
    FileTokenStore,
    OAuth2Config,
    Scope,
    revoke_token,
    run_pkce_flow,
)

# typer resolves annotations at runtime via inspect.signature(eval_str=True), so these
# enums must be importable at runtime even though they only appear in annotations.
from civitai_api.types.enums import (  # noqa: TC001
    ImageSort,
    ModelSort,
    ModelType,
    NsfwLevel,
    Period,
)

if TYPE_CHECKING:
    from civitai_api._internal.pagination import SyncPage

app = typer.Typer(name="civitai", help="CivitAI API CLI", no_args_is_help=True)
models_app = typer.Typer(help="Model operations", no_args_is_help=True)
model_versions_app = typer.Typer(help="Model version operations", no_args_is_help=True)
images_app = typer.Typer(help="Image operations", no_args_is_help=True)
creators_app = typer.Typer(help="Creator operations", no_args_is_help=True)
tags_app = typer.Typer(help="Tag operations", no_args_is_help=True)
users_app = typer.Typer(help="User operations", no_args_is_help=True)
vault_app = typer.Typer(help="Vault operations (requires auth)", no_args_is_help=True)
enums_app = typer.Typer(help="Enum operations", no_args_is_help=True)
auth_app = typer.Typer(help="OAuth2 authentication", no_args_is_help=True)

app.add_typer(models_app, name="models")
app.add_typer(model_versions_app, name="model-versions")
app.add_typer(images_app, name="images")
app.add_typer(creators_app, name="creators")
app.add_typer(tags_app, name="tags")
app.add_typer(users_app, name="users")
app.add_typer(vault_app, name="vault")
app.add_typer(enums_app, name="enums")
app.add_typer(auth_app, name="auth")

_TOKEN_PATH = Path.home() / ".config" / "civitai" / "token.json"
_store = FileTokenStore(_TOKEN_PATH)


def jmespath(value: str) -> _jmespath.parser.ParsedResult:
    """Parse the value as a jmespath.

    :param value: the value of the ``--jmespath`` flag
    :type value: str
    :return: value compiled as a jmespath
    :rtype: jmespath.parser.ParsedResult
    :raises typer.BadParameter: If value fails to compile as jmespath
    """
    try:
        return _jmespath.compile(value)
    except _jmespath.exceptions.ParseError as e:
        raise typer.BadParameter(str(e)) from None


_JMESPathOption = Annotated[
    _jmespath.parser.ParsedResult | None,
    typer.Option("--jmespath", help="JMESPath expression to filter/transform the JSON output", parser=jmespath),
]

_PagerOption = Annotated[
    bool,
    typer.Option("--pager/--no-pager", help="Pipe output through a pager (auto-disabled when stdout is not a tty)"),
]


def _out(data: object, *, jmespath_expr: _jmespath.parser.ParsedResult | None = None, pager: bool = True) -> None:
    if jmespath_expr is not None:
        data = jmespath_expr.search(data)
    output = json.dumps(data, indent=2, default=str)
    if pager and sys.stdout.isatty():
        cmd = os.environ.get("PAGER", "less -FRX")
        try:
            with subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE) as proc:  # noqa: S602
                proc.communicate(output.encode())
        except (OSError, KeyboardInterrupt):
            print(output)  # noqa: T201
            return
    else:
        print(output)  # noqa: T201


def _page_loop[T](
    page: SyncPage[T],
    *,
    jmespath_expr: _jmespath.parser.ParsedResult | None,
    pager: bool,
) -> None:
    while True:
        _out([item.model_dump(by_alias=False) for item in page], jmespath_expr=jmespath_expr, pager=pager)  # type: ignore[attr-defined]
        if not page.has_next_page() or not sys.stdin.isatty():
            break
        if not typer.confirm("Fetch next page?", default=False):
            break
        page = page.next_page()


def _client(api_key: str | None = None) -> CivitAI:
    """Return a :class:`CivitAI` client using a stored OAuth2 token or an API key.

    :param api_key: Explicit API key; falls back to ``CIVITAI_API_KEY`` env var, defaults to None
    :type api_key: str, optional
    :return: Configured sync client
    :rtype: CivitAI
    """
    token = _store.load()
    if token:
        return CivitAI(oauth2_token=token)
    return CivitAI(api_key=api_key or os.environ.get("CIVITAI_API_KEY"))


# --- version ---


@app.command("version")
def version() -> None:
    """Print the civitai_api package version."""
    typer.echo(__version__)


# --- auth ---


@auth_app.command("login")
def auth_login(
    client_id: Annotated[str, typer.Option(envvar="CIVITAI_CLIENT_ID", help="OAuth2 client ID")],
    client_secret: Annotated[str, typer.Option(envvar="CIVITAI_CLIENT_SECRET", help="OAuth2 client secret")],
    redirect_uri: Annotated[
        str,
        typer.Option(help="Local redirect URI for the PKCE callback"),
    ] = "http://localhost:8080/callback",
    scopes: Annotated[
        str,
        typer.Option(help="Permission scope: read_only, creator, ai_services, or full_access"),
    ] = "read_only",
) -> None:
    """Run OAuth2 PKCE login flow and save token."""
    scope_map = {
        "read_only": Scope.READ_ONLY,
        "creator": Scope.CREATOR,
        "ai_services": Scope.AI_SERVICES,
        "full_access": Scope.FULL_ACCESS,
    }
    scope = scope_map.get(scopes, Scope.READ_ONLY)
    config = OAuth2Config(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=scope,
    )
    typer.echo("Opening browser for authentication...")
    token = run_pkce_flow(config, store=_store)
    typer.echo(f"Logged in. Token expires at: {token.expires_at:.0f}")


@auth_app.command("logout")
def auth_logout(
    client_id: Annotated[
        str,
        typer.Option(envvar="CIVITAI_CLIENT_ID", help="OAuth2 client ID for server-side token revocation"),
    ] = "",
    client_secret: Annotated[
        str,
        typer.Option(envvar="CIVITAI_CLIENT_SECRET", help="OAuth2 client secret for server-side token revocation"),
    ] = "",
) -> None:
    """Revoke token and clear local storage."""
    token = _store.load()
    if token is None:
        typer.echo("Not logged in.")
        return
    if client_id and client_secret:
        config = OAuth2Config(client_id=client_id, client_secret=client_secret, redirect_uri="")
        with contextlib.suppress(Exception):
            revoke_token(config, token)
    _store.clear()
    typer.echo("Logged out.")


@auth_app.command("status")
def auth_status() -> None:
    """Show current authentication status."""
    token = _store.load()
    if token is None:
        typer.echo("Not logged in (no stored token).")
        return
    expired = token.is_expired()
    typer.echo(f"Token: {'EXPIRED' if expired else 'valid'}")
    typer.echo(f"Expires at: {token.expires_at:.0f}")


# --- models ---


@models_app.command("list")
def models_list(
    *,
    query: Annotated[str | None, typer.Option(help="Search query string")] = None,
    limit: Annotated[int | None, typer.Option(help="Max results per page (default 3; model JSON is large)")] = 3,
    page: Annotated[int | None, typer.Option(help="Page number to fetch")] = None,
    types: Annotated[
        ModelType | None,
        typer.Option(help="Model type filter (e.g. Checkpoint, LORA, TextualInversion)"),
    ] = None,
    sort: Annotated[
        ModelSort | None,
        typer.Option(help="Sort order (e.g. 'Highest Rated', 'Most Downloaded', 'Newest')"),
    ] = None,
    period: Annotated[Period | None, typer.Option(help="Time period for sort (e.g. AllTime, Month, Week, Day)")] = None,
    nsfw: Annotated[bool | None, typer.Option(help="Include NSFW results")] = True,
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """List models.

    The default limit is set to 3 because model jsons are quite large.
    """
    with _client(api_key) as c:
        first = c.models.list(
            query=query,
            limit=limit,
            page=page,
            types=types,
            sort=sort,
            period=period,
            nsfw=nsfw,
        )
        _page_loop(first, jmespath_expr=jmespath_expr, pager=pager)


@models_app.command("get")
def models_get(
    model_id: Annotated[int, typer.Argument(help="Model ID to retrieve")],
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    *,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """Get a model by ID."""
    with _client(api_key) as c:
        model = c.models.retrieve(model_id)
        _out(model.model_dump(by_alias=False), jmespath_expr=jmespath_expr, pager=pager)


# --- model-versions ---


@model_versions_app.command("get")
def mv_get(
    version_id: Annotated[int, typer.Argument(help="Model version ID to retrieve")],
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    *,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """Get a model version by ID."""
    with _client(api_key) as c:
        v = c.model_versions.retrieve(version_id)
        _out(v.model_dump(by_alias=False), jmespath_expr=jmespath_expr, pager=pager)


@model_versions_app.command("by-hash")
def mv_by_hash(
    hash_value: Annotated[str, typer.Argument(help="File hash of the model version (AutoV1, AutoV2, SHA256, etc.)")],
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    *,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """Get a model version by file hash."""
    with _client(api_key) as c:
        v = c.model_versions.by_hash(hash_value)
        _out(v.model_dump(by_alias=False), jmespath_expr=jmespath_expr, pager=pager)


# --- images ---


@images_app.command("list")
def images_list(
    *,
    limit: Annotated[int | None, typer.Option(help="Max results per page")] = None,
    page: Annotated[int | None, typer.Option(help="Page number to fetch")] = None,
    model_id: Annotated[int | None, typer.Option(help="Filter images by model ID")] = None,
    model_version_id: Annotated[int | None, typer.Option(help="Filter images by model version ID")] = None,
    username: Annotated[str | None, typer.Option(help="Filter images by creator username")] = None,
    nsfw: Annotated[NsfwLevel | None, typer.Option(help="NSFW level filter (None, Soft, Mature, X)")] = None,
    sort: Annotated[
        ImageSort | None,
        typer.Option(help="Sort order (e.g. 'Most Reactions', 'Most Comments', 'Newest')"),
    ] = None,
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """List images."""
    with _client(api_key) as c:
        first = c.images.list(
            limit=limit,
            page=page,
            model_id=model_id,
            model_version_id=model_version_id,
            username=username,
            nsfw=nsfw,
            sort=sort,
        )
        _page_loop(first, jmespath_expr=jmespath_expr, pager=pager)


# --- creators ---


@creators_app.command("list")
def creators_list(
    *,
    query: Annotated[str | None, typer.Option(help="Search query string")] = None,
    limit: Annotated[int | None, typer.Option(help="Max results per page")] = None,
    page: Annotated[int | None, typer.Option(help="Page number to fetch")] = None,
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """List creators."""
    with _client(api_key) as c:
        first = c.creators.list(query=query, limit=limit, page=page)
        _page_loop(first, jmespath_expr=jmespath_expr, pager=pager)


# --- tags ---


@tags_app.command("list")
def tags_list(
    *,
    query: Annotated[str | None, typer.Option(help="Search query string")] = None,
    limit: Annotated[int | None, typer.Option(help="Max results per page")] = None,
    page: Annotated[int | None, typer.Option(help="Page number to fetch")] = None,
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """List tags."""
    with _client(api_key) as c:
        first = c.tags.list(query=query, limit=limit, page=page)
        _page_loop(first, jmespath_expr=jmespath_expr, pager=pager)


# --- users ---


@users_app.command("get")
def users_get(
    username: Annotated[str, typer.Argument(help="Username of the creator to look up")],
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    *,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """Get a user by username."""
    with _client(api_key) as c:
        user = c.users.retrieve(username)
        _out(user.model_dump(by_alias=False), jmespath_expr=jmespath_expr, pager=pager)


@users_app.command("me")
def users_me(
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    *,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """Get the current authenticated user."""
    with _client(api_key) as c:
        me = c.users.me()
        _out(me.model_dump(by_alias=False), jmespath_expr=jmespath_expr, pager=pager)


# --- vault ---


@vault_app.command("status")
def vault_status(
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    *,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """Get vault storage status."""
    with _client(api_key) as c:
        status = c.vault.status()
        _out(status.model_dump(by_alias=False), jmespath_expr=jmespath_expr, pager=pager)


@vault_app.command("list")
def vault_list(
    *,
    limit: Annotated[int | None, typer.Option(help="Max results per page")] = None,
    page: Annotated[int | None, typer.Option(help="Page number to fetch")] = None,
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """List vault items."""
    with _client(api_key) as c:
        first = c.vault.list(limit=limit, page=page)
        _page_loop(first, jmespath_expr=jmespath_expr, pager=pager)


@vault_app.command("toggle-version")
def vault_toggle(
    version_id: Annotated[int, typer.Argument(help="Model version ID to add or remove from vault")],
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    *,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """Toggle a model version in/out of vault."""
    with _client(api_key) as c:
        result = c.vault.toggle_version(version_id)
        _out(result, jmespath_expr=jmespath_expr, pager=pager)


# --- enums ---


@enums_app.command("list")
def enums_list(
    api_key: Annotated[
        str | None,
        typer.Option(envvar="CIVITAI_API_KEY", help="CivitAI API key; falls back to CIVITAI_API_KEY env var"),
    ] = None,
    *,
    jmespath_expr: _JMESPathOption = None,
    pager: _PagerOption = True,
) -> None:
    """List available enum values."""
    with _client(api_key) as c:
        data = c.enums.list()
        _out(data, jmespath_expr=jmespath_expr, pager=pager)


if __name__ == "__main__":
    app()
