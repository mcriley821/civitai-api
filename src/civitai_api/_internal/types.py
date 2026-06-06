"""Type aliases and sentinels used throughout the library."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

__all__ = ["NULL", "JsonValue"]


class _Null:
    """Sentinel that serialises to JSON ``null`` when passed as a request parameter.

    Use the module-level :data:`NULL` constant rather than instantiating directly.
    """

    _instance: _Null | None = None

    def __new__(cls) -> _Null:  # noqa: PYI034
        """Return the singleton instance, creating it on first call.

        :return: The sole ``_Null`` instance
        :rtype: _Null
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        """Return the string representation of the sentinel.

        :return: ``"NULL"``
        :rtype: str
        """
        return "NULL"


NULL = _Null()

type JsonValue = str | int | float | bool | None | Sequence[JsonValue] | dict[str, JsonValue]

Headers = dict[str, str]
Query = dict[str, Any]
Body = dict[str, Any]
