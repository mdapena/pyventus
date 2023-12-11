from dataclasses import dataclass, field
from datetime import datetime

from ..core.constants import StdOutColors


@dataclass(frozen=True)
class Event:
    """
    A base class for event objects.

    This class serves as a blueprint for creating event objects. It
    is intended to be subclassed and extended by concrete event classes.

    **Note:** The `Event` class is marked with `frozen=True`, to ensure that its
    attributes cannot be modified once the event object is created. This is crucial
    because Pyventus supports both asynchronous and synchronous event handling concurrently.
    When payloads are accessible from multiple threads, having mutable payloads could lead
    to data inconsistencies. By freezing event objects, their integrity is preserved as
    they propagate through the system.

    To define a new event type:

    1. Subclass `Event` and add fields for the payload
    2. Decorate the subclass with `@dataclass(frozen=True)`

    **Example:**

    ```Python
    @dataclass(frozen=True)
    class OrderCreated(Event):
        id: str
        total: float

    event = OrderCreated(id="65486c788bba30ff7e0152ae", total=29.99)
    ```
    """

    timestamp: datetime = field(init=False, default_factory=datetime.now)
    """ The date and time when the event occurred. """

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
        default, highlight = StdOutColors.DEFAULT, StdOutColors.GREEN
        return (
            f"{highlight}{self.name}{default} {self.timestamp.strftime('%Y-%m-%d %H:%M:%S %p')}"
            f"\t{highlight}[Payload]{default} {super().__str__()}"
        )
