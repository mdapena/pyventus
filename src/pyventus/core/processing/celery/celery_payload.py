from dataclasses import asdict, dataclass
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

    def to_json(self) -> dict[str, Any]:
        """
        Convert the payload to a JSON-compatible dictionary.

        :return: A JSON-compatible dictionary representing the payload.
        """
        return asdict(self)
