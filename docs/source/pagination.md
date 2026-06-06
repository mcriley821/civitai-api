# Pagination

List endpoints return a `SyncPage[T]` or `AsyncPage[T]` object wrapping the current page of results and cursor metadata.

## Iterating the current page

```python
from civitai_api import CivitAI

with CivitAI() as client:
    page = client.models.list(limit=10)
    for model in page:          # iterates only the current page
        print(model.name)
```

## Auto-paging through all results

`auto_paging_iter()` follows cursors automatically and yields every item:

```python
with CivitAI() as client:
    for model in client.models.list().auto_paging_iter():
        print(model.name)
```

Async variant:

```python
async with AsyncCivitAI() as client:
    page = await client.models.list()
    async for model in page.auto_paging_iter():
        print(model.name)
```

## Manual pagination

```python
with CivitAI() as client:
    page = client.models.list(limit=5)
    while True:
        for model in page:
            print(model.name)
        if not page.has_next_page():
            break
        page = page.next_page()
```

## Page metadata

```python
print(page.metadata.total_items)
print(page.metadata.next_cursor)
```

See {doc}`api/pagination` for the full `SyncPage` / `AsyncPage` reference.
