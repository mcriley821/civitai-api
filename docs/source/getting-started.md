# Getting Started

## Installation

```bash
pip install py-civitai-api
```

To use the CLI as well:

```bash
pip install "py-civitai-api[cli]"
```

## Quick Start

### Synchronous

```python
from civitai_api import CivitAI

with CivitAI() as client:
    page = client.models.list(query="anime", limit=5)
    for model in page:
        print(model.name)
```

### Asynchronous

```python
import asyncio
from civitai_api import AsyncCivitAI

async def main():
    async with AsyncCivitAI() as client:
        page = await client.models.list(query="anime", limit=5)
        async for item in page.auto_paging_iter():
            print(item.name)

asyncio.run(main())
```

### API Key

Most endpoints work without authentication, but some (vault, `/me`) require it.
Set `CIVITAI_API_KEY` in your environment or pass it explicitly:

```python
client = CivitAI(api_key="your_key_here")
```

See {doc}`authentication` for OAuth2 options.
