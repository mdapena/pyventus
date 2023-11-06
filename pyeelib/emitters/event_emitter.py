from abc import ABC, abstractmethod

from pyeelib.events import Event


class EventEmitter(ABC):
    """
    An abstract base class for event emitters.

    This class serves as an event emitter that can handle string events with arguments and keyword arguments or
    an instance of Event. It provides a common interface for emitting events and can be used as a base class for
    implementing specific event emitter classes.

    The purpose of this class is to decouple the event listener's callback invocations from the real implementation,
    allowing for more flexibility and versatility. By using this base class as a dependency, you can easily change the
    behavior of the event emitter at runtime.
    """

    @abstractmethod
    def emit(self, event: str | Event, *args, **kwargs) -> None:
        """
        Invokes all registered callback functions for a given event.
        :param event: The event to emit. It can be a string or an instance of Event.
        :param args: Additional positional arguments to pass to the event listeners.
        :param kwargs: Additional keyword arguments to pass to the event listeners.
        :return: None
        """
        pass
