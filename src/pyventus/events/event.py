from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Event:
    """
    A base class that serves as a blueprint for creating event objects.

    **Notes:**

    -   The `Event` class is marked with `frozen=True` to ensure that its attributes
        cannot be modified once the event object is created. This is crucial because
        Pyventus supports both asynchronous and synchronous event handling concurrently.
        When payloads are accessible from multiple threads, having mutable payloads
        could lead to data inconsistencies. By freezing event objects, their
        integrity is preserved as they propagate through the system.

    ---
    Read more in the
    [Pyventus docs for Event](https://mdapena.github.io/pyventus/tutorials/event/).
    """

    timestamp: datetime = field(init=False, default_factory=datetime.now)
    """The timestamp when the event was created."""

    @property
    def name(self) -> str:
        """
        Gets the name of the event.
        :return: The name of the event as a string.
        """
        return self.__class__.__name__

    def __str__(self) -> str:
        """
        Returns a formatted string representation of the event.
        :return: The formatted string representation of the event.
        """
        return f"{self.name} | {self.timestamp.strftime('%Y-%m-%d %I:%M:%S %p')} | Payload: {super().__str__()}"
