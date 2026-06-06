# Authentication

Most CivitAI endpoints are public, but the vault and `/me` endpoints require authentication.

## API Key

The simplest approach is an API key. Set the environment variable:

```bash
export CIVITAI_API_KEY=your_key_here
```

Or pass it explicitly:

```python
from civitai_api import CivitAI

client = CivitAI(api_key="your_key_here")
```

## OAuth2 (PKCE)

For user-delegated access, use the OAuth2 PKCE flow. You need a registered CivitAI OAuth2 application.

### Scopes

`Scope` is an `IntFlag` — combine flags or use the convenience presets:

| Preset | Included Scopes |
|--------|----------------|
| `READ_ONLY` | UserRead, ModelsRead, ImagesRead, CreatorsRead, VaultRead |
| `CREATOR` | READ_ONLY + ModelsWrite, ImagesWrite, VaultWrite |
| `AI_SERVICES` | READ_ONLY + AIServicesRead, AIServicesWrite |
| `FULL_ACCESS` | All scopes |

### Running the PKCE flow

```python
from civitai_api import CivitAI, OAuth2Config, Scope, run_pkce_flow, FileTokenStore
from pathlib import Path

config = OAuth2Config(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:8080/callback",
    scopes=Scope.READ_ONLY,
)

store = FileTokenStore(Path.home() / ".config" / "civitai" / "token.json")
token = run_pkce_flow(config, store=store)

with CivitAI(oauth2_token=token) as client:
    me = client.users.me()
    print(me.username)
```

The token is stored by `FileTokenStore` and auto-refreshed on subsequent requests.

### Pre-obtained token

If you already have a token (e.g. from a web flow):

```python
from civitai_api import CivitAI, OAuth2Token

token = OAuth2Token(
    access_token="...",
    expires_in=3600,
)
client = CivitAI(oauth2_token=token)
```

## Error Handling

```python
from civitai_api import CivitAI, AuthenticationError, RateLimitError

with CivitAI() as client:
    try:
        me = client.users.me()
    except AuthenticationError:
        print("Invalid or missing credentials.")
    except RateLimitError:
        print("Too many requests.")
```

See {doc}`api/exceptions` for the full exception hierarchy.
