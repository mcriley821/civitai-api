"""Tests for the CLI."""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

import httpx
import pytest
from typer.testing import CliRunner

from civitai_api import __version__
from civitai_api._internal.oauth2 import MemoryTokenStore, OAuth2Token
from civitai_api.cli.main import app

if TYPE_CHECKING:
    from respx import MockRouter

# --- fixtures ---

MODEL_FIXTURE = {
    "id": 1,
    "name": "Test Model",
    "type": "Checkpoint",
    "poi": False,
    "nsfw": False,
    "allowNoCredit": True,
    "allowDerivatives": True,
    "allowDifferentLicense": True,
    "tags": ["realistic"],
    "modelVersions": [],
}
MODEL_PAGE_FIXTURE: dict = {
    "items": [MODEL_FIXTURE],
    "metadata": {"nextCursor": None},
}

VERSION_ID = 100
VERSION_FIXTURE = {
    "id": VERSION_ID,
    "name": "v1.0",
    "trainedWords": [],
    "files": [],
    "images": [],
}

IMAGE_ID = 42
IMAGE_PAGE_FIXTURE: dict = {
    "items": [{"id": IMAGE_ID, "url": "https://example.com/img.jpg"}],
    "metadata": {"nextCursor": None},
}

CREATOR_PAGE_FIXTURE: dict = {
    "items": [{"username": "artmaker", "modelCount": 5}],
    "metadata": {"nextCursor": None},
}

TAG_PAGE_FIXTURE: dict = {
    "items": [{"name": "realistic", "modelCount": 100}],
    "metadata": {"nextCursor": None},
}

USER_FIXTURE = {"id": 1, "username": "johndoe", "image": None}
ME_FIXTURE = {"id": 2, "username": "me", "email": "me@example.com"}

VAULT_STATUS_FIXTURE = {"storageUsed": 1024, "storageLimit": 10240}
VAULT_PAGE_FIXTURE: dict = {
    "items": [{"modelVersionId": 50, "vaultItemId": 1}],
    "metadata": {"nextCursor": None},
}
VAULT_TOGGLE_VERSION_ID = 50


@pytest.fixture
def runner() -> CliRunner:
    """Return a typer CliRunner for invoking CLI commands in tests."""
    return CliRunner()


@pytest.fixture(autouse=True)
def no_token_store(monkeypatch: pytest.MonkeyPatch) -> MemoryTokenStore:
    """Patch the module-level token store with a fresh MemoryTokenStore."""
    store = MemoryTokenStore()
    monkeypatch.setattr("civitai_api.cli.main._store", store)
    return store


# --- shared flag tests ---


def test_jmespath_filter(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """--jmespath filters JSON output to the matching expression result."""
    civitai_mock.get("/models/1").mock(return_value=httpx.Response(200, json=MODEL_FIXTURE))
    result = runner.invoke(app, ["models", "get", "1", "--jmespath", "id"])
    assert result.exit_code == 0
    assert result.output.strip() == "1"


def test_jmespath_invalid(runner: CliRunner) -> None:
    """An invalid JMESPath expression causes a non-zero exit code."""
    result = runner.invoke(app, ["models", "list", "--jmespath", "]["])
    assert result.exit_code != 0


def test_api_key_forwarded(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """--api-key is sent as the Authorization: Bearer header on requests."""
    civitai_mock.get("/models/1").mock(return_value=httpx.Response(200, json=MODEL_FIXTURE))
    result = runner.invoke(app, ["models", "get", "1", "--api-key", "sk-test"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.headers["authorization"] == "Bearer sk-test"


def test_no_pager_flag(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """--no-pager causes output to be printed directly without invoking a pager."""
    civitai_mock.get("/models/1").mock(return_value=httpx.Response(200, json=MODEL_FIXTURE))
    result = runner.invoke(app, ["models", "get", "1", "--no-pager"])
    assert result.exit_code == 0
    assert '"id"' in result.output


# --- auth tests ---


def test_auth_status_no_token(runner: CliRunner) -> None:
    """Auth status with no stored token outputs 'Not logged in'."""
    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 0
    assert "Not logged in" in result.output


def test_auth_status_valid_token(
    runner: CliRunner,
    no_token_store: MemoryTokenStore,
) -> None:
    """Auth status with a fresh token reports 'valid'."""
    no_token_store.save(OAuth2Token(access_token="t", token_type="Bearer", expires_in=3600))
    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 0
    assert "valid" in result.output


def test_auth_status_expired_token(
    runner: CliRunner,
    no_token_store: MemoryTokenStore,
) -> None:
    """Auth status with an expired token reports 'EXPIRED'."""
    no_token_store.save(
        OAuth2Token(
            access_token="t",
            token_type="Bearer",
            expires_in=60,
            issued_at=time.time() - 3600,
        ),
    )
    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 0
    assert "EXPIRED" in result.output


def test_auth_logout_no_token(runner: CliRunner) -> None:
    """Auth logout with no stored token outputs 'Not logged in'."""
    result = runner.invoke(app, ["auth", "logout"])
    assert result.exit_code == 0
    assert "Not logged in" in result.output


def test_auth_logout_clears_store(
    runner: CliRunner,
    no_token_store: MemoryTokenStore,
) -> None:
    """Auth logout removes the stored token from the store."""
    no_token_store.save(OAuth2Token(access_token="t", token_type="Bearer", expires_in=3600))
    result = runner.invoke(app, ["auth", "logout"])
    assert result.exit_code == 0
    assert no_token_store.load() is None


# --- models tests ---


def test_models_list(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Models list outputs a JSON array of models."""
    civitai_mock.get("/models").mock(return_value=httpx.Response(200, json=MODEL_PAGE_FIXTURE))
    result = runner.invoke(app, ["models", "list"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["id"] == 1


def test_models_list_query(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Models list --query forwards the query param to the request."""
    civitai_mock.get("/models").mock(return_value=httpx.Response(200, json=MODEL_PAGE_FIXTURE))
    result = runner.invoke(app, ["models", "list", "--query", "realism"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["query"] == "realism"


def test_models_list_limit(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Models list --limit forwards the limit param to the request."""
    civitai_mock.get("/models").mock(return_value=httpx.Response(200, json=MODEL_PAGE_FIXTURE))
    result = runner.invoke(app, ["models", "list", "--limit", "5"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["limit"] == "5"


def test_models_list_page(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Models list --page forwards the page param to the request."""
    civitai_mock.get("/models").mock(return_value=httpx.Response(200, json=MODEL_PAGE_FIXTURE))
    result = runner.invoke(app, ["models", "list", "--page", "2"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["page"] == "2"


def test_models_list_types(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Models list --types forwards the types param to the request."""
    civitai_mock.get("/models").mock(return_value=httpx.Response(200, json=MODEL_PAGE_FIXTURE))
    result = runner.invoke(app, ["models", "list", "--types", "Checkpoint"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["types"] == "Checkpoint"


def test_models_list_sort(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Models list --sort forwards the sort param to the request."""
    civitai_mock.get("/models").mock(return_value=httpx.Response(200, json=MODEL_PAGE_FIXTURE))
    result = runner.invoke(app, ["models", "list", "--sort", "Highest Rated"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["sort"] == "Highest Rated"


def test_models_list_period(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Models list --period forwards the period param to the request."""
    civitai_mock.get("/models").mock(return_value=httpx.Response(200, json=MODEL_PAGE_FIXTURE))
    result = runner.invoke(app, ["models", "list", "--period", "Month"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["period"] == "Month"


def test_models_list_nsfw_false(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Models list --no-nsfw forwards nsfw=False to the request."""
    civitai_mock.get("/models").mock(return_value=httpx.Response(200, json=MODEL_PAGE_FIXTURE))
    result = runner.invoke(app, ["models", "list", "--no-nsfw"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["nsfw"] == "false"


def test_models_get(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Models get outputs a JSON object for the requested model ID."""
    civitai_mock.get("/models/1").mock(return_value=httpx.Response(200, json=MODEL_FIXTURE))
    result = runner.invoke(app, ["models", "get", "1"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["id"] == 1


# --- model-versions tests ---


def test_mv_get(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """model-versions get outputs a JSON object for the requested version ID."""
    civitai_mock.get(f"/model-versions/{VERSION_ID}").mock(
        return_value=httpx.Response(200, json=VERSION_FIXTURE),
    )
    result = runner.invoke(app, ["model-versions", "get", str(VERSION_ID)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["id"] == VERSION_ID


def test_mv_by_hash(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """model-versions by-hash outputs a JSON object for the requested hash."""
    civitai_mock.get("/model-versions/by-hash/abc123").mock(
        return_value=httpx.Response(200, json=VERSION_FIXTURE),
    )
    result = runner.invoke(app, ["model-versions", "by-hash", "abc123"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["id"] == VERSION_ID


# --- images tests ---


def test_images_list(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Images list outputs a JSON array of images."""
    civitai_mock.get("/images").mock(return_value=httpx.Response(200, json=IMAGE_PAGE_FIXTURE))
    result = runner.invoke(app, ["images", "list"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["id"] == IMAGE_ID


def test_images_list_limit(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Images list --limit forwards the limit param to the request."""
    civitai_mock.get("/images").mock(return_value=httpx.Response(200, json=IMAGE_PAGE_FIXTURE))
    result = runner.invoke(app, ["images", "list", "--limit", "10"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["limit"] == "10"


def test_images_list_page(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Images list --page forwards the page param to the request."""
    civitai_mock.get("/images").mock(return_value=httpx.Response(200, json=IMAGE_PAGE_FIXTURE))
    result = runner.invoke(app, ["images", "list", "--page", "2"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["page"] == "2"


def test_images_list_model_id(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Images list --model-id forwards modelId to the request."""
    civitai_mock.get("/images").mock(return_value=httpx.Response(200, json=IMAGE_PAGE_FIXTURE))
    result = runner.invoke(app, ["images", "list", "--model-id", "5"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["modelId"] == "5"


def test_images_list_model_version_id(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Images list --model-version-id forwards modelVersionId to the request."""
    civitai_mock.get("/images").mock(return_value=httpx.Response(200, json=IMAGE_PAGE_FIXTURE))
    result = runner.invoke(app, ["images", "list", "--model-version-id", "100"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["modelVersionId"] == "100"


def test_images_list_username(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Images list --username forwards the username param to the request."""
    civitai_mock.get("/images").mock(return_value=httpx.Response(200, json=IMAGE_PAGE_FIXTURE))
    result = runner.invoke(app, ["images", "list", "--username", "johndoe"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["username"] == "johndoe"


def test_images_list_nsfw(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Images list --nsfw forwards the nsfw level param to the request."""
    civitai_mock.get("/images").mock(return_value=httpx.Response(200, json=IMAGE_PAGE_FIXTURE))
    result = runner.invoke(app, ["images", "list", "--nsfw", "Soft"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["nsfw"] == "Soft"


def test_images_list_sort(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Images list --sort forwards the sort param to the request."""
    civitai_mock.get("/images").mock(return_value=httpx.Response(200, json=IMAGE_PAGE_FIXTURE))
    result = runner.invoke(app, ["images", "list", "--sort", "Newest"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["sort"] == "Newest"


# --- creators tests ---


def test_creators_list(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Creators list outputs a JSON array of creators."""
    civitai_mock.get("/creators").mock(return_value=httpx.Response(200, json=CREATOR_PAGE_FIXTURE))
    result = runner.invoke(app, ["creators", "list"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["username"] == "artmaker"


def test_creators_list_query(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Creators list --query forwards the query param to the request."""
    civitai_mock.get("/creators").mock(return_value=httpx.Response(200, json=CREATOR_PAGE_FIXTURE))
    result = runner.invoke(app, ["creators", "list", "--query", "artmaker"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["query"] == "artmaker"


def test_creators_list_limit(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Creators list --limit forwards the limit param to the request."""
    civitai_mock.get("/creators").mock(return_value=httpx.Response(200, json=CREATOR_PAGE_FIXTURE))
    result = runner.invoke(app, ["creators", "list", "--limit", "5"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["limit"] == "5"


def test_creators_list_page(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Creators list --page forwards the page param to the request."""
    civitai_mock.get("/creators").mock(return_value=httpx.Response(200, json=CREATOR_PAGE_FIXTURE))
    result = runner.invoke(app, ["creators", "list", "--page", "1"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["page"] == "1"


# --- tags tests ---


def test_tags_list(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Tags list outputs a JSON array of tags."""
    civitai_mock.get("/tags").mock(return_value=httpx.Response(200, json=TAG_PAGE_FIXTURE))
    result = runner.invoke(app, ["tags", "list"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["name"] == "realistic"


def test_tags_list_query(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Tags list --query forwards the query param to the request."""
    civitai_mock.get("/tags").mock(return_value=httpx.Response(200, json=TAG_PAGE_FIXTURE))
    result = runner.invoke(app, ["tags", "list", "--query", "realistic"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["query"] == "realistic"


def test_tags_list_limit(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Tags list --limit forwards the limit param to the request."""
    civitai_mock.get("/tags").mock(return_value=httpx.Response(200, json=TAG_PAGE_FIXTURE))
    result = runner.invoke(app, ["tags", "list", "--limit", "5"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["limit"] == "5"


def test_tags_list_page(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Tags list --page forwards the page param to the request."""
    civitai_mock.get("/tags").mock(return_value=httpx.Response(200, json=TAG_PAGE_FIXTURE))
    result = runner.invoke(app, ["tags", "list", "--page", "1"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["page"] == "1"


# --- users tests ---


def test_users_get(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Users get outputs a JSON object for the requested username."""
    civitai_mock.get("/users/johndoe").mock(return_value=httpx.Response(200, json=USER_FIXTURE))
    result = runner.invoke(app, ["users", "get", "johndoe"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["username"] == "johndoe"


def test_users_me(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Users me outputs a JSON object for the authenticated user."""
    civitai_mock.get("/me").mock(return_value=httpx.Response(200, json=ME_FIXTURE))
    result = runner.invoke(app, ["users", "me"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["username"] == "me"


# --- vault tests ---


def test_vault_status(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Vault status outputs a JSON object with vault storage information."""
    civitai_mock.get("/vault/get").mock(return_value=httpx.Response(200, json=VAULT_STATUS_FIXTURE))
    result = runner.invoke(app, ["vault", "status"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "storage_used" in data


def test_vault_list(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Vault list outputs a JSON array of vault items."""
    civitai_mock.get("/vault/all").mock(return_value=httpx.Response(200, json=VAULT_PAGE_FIXTURE))
    result = runner.invoke(app, ["vault", "list"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["model_version_id"] == VAULT_TOGGLE_VERSION_ID


def test_vault_list_limit(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Vault list --limit forwards the limit param to the request."""
    civitai_mock.get("/vault/all").mock(return_value=httpx.Response(200, json=VAULT_PAGE_FIXTURE))
    result = runner.invoke(app, ["vault", "list", "--limit", "5"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["limit"] == "5"


def test_vault_list_page(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Vault list --page forwards the page param to the request."""
    civitai_mock.get("/vault/all").mock(return_value=httpx.Response(200, json=VAULT_PAGE_FIXTURE))
    result = runner.invoke(app, ["vault", "list", "--page", "2"])
    assert result.exit_code == 0
    assert civitai_mock.calls[-1].request.url.params["page"] == "2"


def test_vault_toggle(runner: CliRunner, civitai_mock: MockRouter) -> None:
    """Vault toggle-version outputs the toggle result as JSON."""
    civitai_mock.post(f"/vault/toggle-version/{VAULT_TOGGLE_VERSION_ID}").mock(
        return_value=httpx.Response(200, json={"added": True}),
    )
    result = runner.invoke(app, ["vault", "toggle-version", str(VAULT_TOGGLE_VERSION_ID)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["added"] is True


# --- version tests ---


def test_version_exits_zero(runner: CliRunner) -> None:
    """Version command exits with code 0."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0


def test_version_output(runner: CliRunner) -> None:
    """Version command prints the installed package version."""
    result = runner.invoke(app, ["version"])
    assert result.output.strip() == __version__
