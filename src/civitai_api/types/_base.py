"""Base model config for all CivitAI response types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

if TYPE_CHECKING:
    from collections.abc import Callable


class _CivitAIModel(BaseModel):
    """Base Pydantic model for all CivitAI response types.

    Configures camelCase alias generation, snake_case field access, and
    ``extra="allow"`` so undocumented API fields are tolerated without error.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )


def _none_to_default(
    factory: Callable[[], Any],
) -> Callable[[Any], Any]:
    """Build a ``mode="before"`` validator mapping an explicit ``null`` to a default.

    The API sometimes sends ``null`` for collection fields; a plain
    ``default_factory`` only covers omitted keys.
    """

    def _validate(value: Any) -> Any:  # noqa: ANN401
        return factory() if value is None else value

    return _validate
