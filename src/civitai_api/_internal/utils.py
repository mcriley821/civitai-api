"""Internal utilities."""

from __future__ import annotations

from typing import Any

from .types import _Null


def strip_none(d: dict[str, Any]) -> dict[str, Any]:
    """Remove None-valued keys; replace _Null sentinel with None for JSON serialization."""
    result: dict[str, Any] = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, _Null):
            result[k] = None
        else:
            result[k] = v
    return result
