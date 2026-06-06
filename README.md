# civitai-api

[![build](https://github.com/mcriley821/civitai-api/actions/workflows/ci.yml/badge.svg)](https://github.com/mcriley821/civitai-api/actions/workflows/ci.yml)

[![codecov](https://codecov.io/gh/mcriley821/civitai-api/graph/badge.svg?token=FKOX46HFKF)](https://codecov.io/gh/mcriley821/civitai-api)

Unofficial Python client for the [CivitAI API](https://developer.civitai.com/site/) — sync and async.

## Install

```bash
pip install py-civitai-api

# with CLI
pip install "py-civitai-api[cli]"
```

## Quick start

```python
from civitai_api import CivitAI

# api key or CIVITAI_API_KEY env var
with CivitAI(api_key="...") as client:
    for model in client.models.list(query="dreamshaper", limit=5).auto_paging_iter():
        print(model.name, model.id)
```

### Async

```python
import asyncio
from civitai_api import AsyncCivitAI

async def main():
    async with AsyncCivitAI() as client:
        version = await client.model_versions.retrieve(12345)
        print(version.name)

asyncio.run(main())
```

### CLI

```bash
civitai auth login
civitai models list --query dreamshaper --limit 5
civitai models get 12345
civitai images list --model-id 12345
```

## Development

```bash
git clone https://github.com/mcriley821/civitai-api
cd civitai-api
uv sync --extra dev
uv run poe install-hooks  # install pre-commit hook (runs lint + typecheck + test)
uv run poe check   # lint + typecheck + test
```

## Note

Built with AI assistance ([Claude](https://claude.ai), Anthropic). All code is reviewed by the author.
Not affiliated with or endorsed by CivitAI.
