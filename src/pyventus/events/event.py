from dataclasses import dataclass, field
from datetime import datetime

from src.pyventus.core.constants import StdOutColors


@dataclass(frozen=True)
class Event:
    """
    A base class for event objects.

    This class serves as a blueprint for creating event objects. It is
    intended to be subclassed and extended by concrete event classes.

    **Note**: The Event class is marked as `frozen=True`, which makes
    its instances immutable. This ensures that once an event object
    is created, its attributes cannot be modified.

    **Example**: To create a concrete event class, subclass the Event class and
    define the desired attributes using dataclass fields.

    .. code-block:: python

        @dataclass(frozen=True)
        class OrderCreated(Event):
            id: str

        event = OrderCreated(id="65486c788bba30ff7e0152ae")
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
        return (f"{highlight}{self.name}{default}  {self.timestamp.strftime('%Y-%m-%d %H:%M:%S %p')}"
                f"\t{highlight}[Payload]{default} {super().__str__()}")
