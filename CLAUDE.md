# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync --extra dev          # install all deps
uv run poe test              # run tests
uv run poe lint              # ruff check
uv run poe format            # ruff format
uv run poe typecheck         # mypy strict
uv run poe check             # lint + typecheck + test (all)
uv run pytest tests/test_models.py          # single test file
uv run pytest tests/test_models.py::test_name  # single test
```

## Architecture

### Dual client pattern

`CivitAI(SyncAPIClient)` and `AsyncCivitAI(AsyncAPIClient)` in `_client.py` are the two entry points. Each owns its own `httpx.Client` / `httpx.AsyncClient` and mirrors resource namespaces. No shared base — this is intentional (Anthropic/OpenAI pattern).

### Layer stack

```
_client.py          CivitAI / AsyncCivitAI (resource namespaces, constructor args)
_base_client.py     SyncAPIClient / AsyncAPIClient (request engine, retry, auth)
_resource.py        SyncAPIResource / AsyncAPIResource (base for all resources)
resources/*.py      paired Sync+Async resource classes per endpoint group
types/*.py          Pydantic response models (camelCase → snake_case via alias_generator)
pagination.py       SyncPage[T] / AsyncPage[T] with auto_paging_iter()
```

### Key internals

**`_base_client._request()`** strips `None` params via `_utils.strip_none()`, retries on `{429, 500, 502, 503, 504}` with exponential backoff (`0.5s * 2^attempt`), parses responses with `TypeAdapter(cast_to).validate_python()`, and maps errors via `_exceptions._make_status_error()`.

**`_types.py` sentinel:** `NULL` (singleton) → sends JSON `null`. `None` (default) → param omitted entirely.

**`types/_base.py`:** All response models inherit `_CivitAIModel`, which uses `alias_generator=to_camel` and `extra="allow"` to tolerate undocumented API fields.

**`pagination.py`:** `SyncPage[T]` / `AsyncPage[T]` wrap `{"items": [...], "metadata": {"nextCursor": ...}}`. `auto_paging_iter()` walks pages via cursor; `__iter__` yields only current page items.

**`_oauth2.py`:** PKCE (S256) + Client Credentials. `Scope` is an `IntFlag`. Auto-refresh in `_base_client._auth_header()` — checks `token.is_expired()` before each request when `OAuth2Config` is present.

### Adding a resource

1. Add response types in `types/<name>.py` inheriting `_CivitAIModel`
2. Add param TypedDicts in `types/params/`
3. Create `resources/<name>.py` with paired `Foo(SyncAPIResource)` + `AsyncFoo(AsyncAPIResource)`
4. Wire up both on `CivitAI` and `AsyncCivitAI` in `_client.py`
5. Add tests in `tests/test_<name>.py` using `client` / `async_client` fixtures + `civitai_mock`

### Tests

`conftest.py` provides `civitai_mock` (respx router for `https://civitai.com/api/v1`), `oauth2_mock` (respx router for oauth endpoints), `client` (sync `CivitAI`), and `async_client` (async). `pytest-asyncio` runs in `auto` mode so async tests need no decorator.

## Release process

PRs are opened against `main` and squash-merged to keep history linear. When ready to cut a release, merge the release-please PR — it bumps `project.version` in `pyproject.toml` and creates a `vx.x.x` tag. Pushing that tag triggers `.github/workflows/release.yml`, which builds with `uv build` and publishes to PyPI via OIDC trusted publishing (no API token needed; configure a "pypi" environment in GitHub repo settings).

## Ruff

`select = ["ALL"]` in `pyproject.toml`. Should not be changed.
