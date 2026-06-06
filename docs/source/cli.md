# CLI

The `civitai` CLI provides a manual interface to the CivitAI API.

## Installation

```bash
pip install "py-civitai-api[cli]"
```

## Usage

```{tip}
Run `civitai --help` or `civitai <command> --help` for up-to-date flags.
Typer generates help text directly from the source, so it always reflects the current options.
```

## Authentication

Log in with OAuth2 PKCE (token stored at `~/.config/civitai/token.json`):

```bash
civitai auth login --client-id $CIVITAI_CLIENT_ID --client-secret $CIVITAI_CLIENT_SECRET
civitai auth status
civitai auth logout
```

Or use an API key:

```bash
export CIVITAI_API_KEY=your_key_here
```

## Commands

### Models

```bash
# List models (default limit: 3 — model JSON is large)
civitai models list

# Search with filters
civitai models list --query "anime" --types LORA --limit 5

# Get a specific model
civitai models get 12345
```

### Model Versions

```bash
# Get a version by ID
civitai model-versions get 67890

# Look up by file hash
civitai model-versions by-hash <SHA256>
```

### Images

```bash
# List recent images
civitai images list --limit 20

# Filter by model
civitai images list --model-id 12345 --nsfw None
```

### Creators, Tags, Users

```bash
civitai creators list --query "anime"
civitai tags list --query "style"
civitai users get some_username
civitai users me
```

### Vault (requires auth)

```bash
civitai vault status
civitai vault list
civitai vault toggle-version 67890
```

### Enums

```bash
civitai enums list
```

## JMESPath Filtering

All commands accept `--jmespath` to filter or transform JSON output using
[JMESPath](https://jmespath.org/) expressions.

```bash
# Extract only model names from a list result
civitai models list --query "anime" --jmespath "[].name"

# Get the download URL of the first file of a specific version
civitai model-versions get 67890 --jmespath "files[0].downloadUrl"

# Count images returned
civitai images list --limit 100 --jmespath "length(@)"
```

## Pager

Output is sent through `$PAGER` (defaults to `less -FRX`) when stdout is a TTY.
Disable with `--no-pager`:

```bash
civitai models list --no-pager | head -n 20
```
