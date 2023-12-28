from dataclasses import dataclass, field
from datetime import datetime


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

    For more information and code examples, please refer to the `Event` tutorials at:
    [https://mdapena.github.io/pyventus/tutorials/event/](https://mdapena.github.io/pyventus/tutorials/event/).
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
        return f"{self.name} | {self.timestamp.strftime('%Y-%m-%d %I:%M:%S %p')} | Payload: {super().__str__()}"
