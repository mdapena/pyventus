from dataclasses import dataclass
from typing import Any

from ..processing_service import ProcessingServiceCallbackType


@dataclass(slots=True, frozen=True)
class CeleryPayload:
    """A data class representing the payload of the `CeleryProcessingService`."""

    callback: ProcessingServiceCallbackType
    """The callback to be executed."""

    args: tuple[Any, ...]
    """Positional arguments to be passed to the callback."""

    kwargs: dict[str, Any]
    """Keyword arguments to be passed to the callback."""
