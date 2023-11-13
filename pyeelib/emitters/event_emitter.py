from abc import ABC, abstractmethod
from typing import List, Type, TypeAlias, Any, Tuple

from pyeelib.events import Event
from pyeelib.exceptions import PyeelibException
from pyeelib.linkers import EventLinker
from pyeelib.listeners import EventListener

EmittableEventType: TypeAlias = Event | Exception | str
""" A type alias representing the supported types of events that can be emitted. """


class EventEmitter(ABC):
    """
    An abstract base class for event emitters.

    This class provides a common interface for emitting events and can be used as a foundation for creating specific
    event emitter classes. It is designed to handle string events with arguments and keyword arguments, as well as
    instances of the `Event` and `Exception` class.

    The main goal of this class is to separate the invocation of event listener callbacks from the underlying
    implementation. This decoupling allows for greater flexibility and adaptability. By relying on this base
    class as a dependency, you can easily modify the behavior of the event emitter during runtime.
    """

    def __init__(self, event_linker: Type[EventLinker] = EventLinker):
        """
        Initializes an instance of the `EventEmitter`.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event listeners. Defaults to `EventLinker`.
        """
        # Validate the event linker argument
        if event_linker is None:
            raise PyeelibException("The 'event_linker' argument cannot be None.")

        # Set the event_linker value
        self._event_linker: Type[EventLinker] = event_linker
        """
        The `EventLinker` attribute specifies the type of event linker to 
        use for associating events with their respective event listeners.
        """

    def emit(self, event: EmittableEventType, *args: Any, **kwargs: Any) -> None:
        """
        Emits an event and triggers the associated event listeners. When emitting `Event` or `Exception` objects,
        there is no need to add them as an argument or keyword argument; they are automatically passed to the
        `EventListener` as the first positional argument.

        **Notes**: If there are event listeners subscribed to the emission of any event (`Event`),
        they will also be executed. The specific behavior and handling of events may vary
        depending on the implementation of the event system.

        :param event: The event to emit. It can be an instance of `Event`, `Exception`, or a `str`.
        :param args: Additional positional arguments to pass to the event listeners.
        :param kwargs: Additional keyword arguments to pass to the event listeners.
        :return: None
        """
        # Raises an exception if the event is None
        if event is None:
            raise PyeelibException("The 'event' argument cannot be None.")

        # Raises an exception if the event is a type object
        if event.__class__ is Type:
            raise PyeelibException("The 'event' argument cannot be a type object.")

        # Determines if the event is a string instance
        is_string: bool = isinstance(event, str)

        # Constructs the arguments tuple based on whether the event is a string or an object
        event_args: Tuple[Any, ...] = args if is_string else (event, *args)

        # Retrieves the event listeners associated with the event
        event_listeners: List[EventListener] = self._event_linker.get_listeners_by_events(
            event if is_string else event.__class__, Event
        )

        # Iterates through each event listener and triggers the associated callback function
        for event_listener in event_listeners:

            # Checks if the event listener is a one-time listener before executing the event listener
            if event_listener.once:

                # If the event listener is a one-time listener, we try to remove it. If it is
                # successfully removed, it means it hasn't been executed before, so we execute the callback
                if self._event_linker.remove_event_listener(event_listener=event_listener):
                    # Executes the event listener callback function with the arguments and keyword arguments
                    self._execute(*event_args, event_listener=event_listener, **kwargs)
            else:
                # Executes the event listener callback function with the arguments and keyword arguments
                self._execute(*event_args, event_listener=event_listener, **kwargs)

    def _emit_exception(self, exception: Exception):
        """
        Emits an exception and triggers the associated exception event listeners.

        **Notes**: If there are event listeners subscribed to the emission
        of any exception (`Exception`), they will also be executed.

        :param exception: The exception to emit.
        :return: None
        """
        # Retrieves the exception event listeners associated with the exception class
        event_listeners: List[EventListener] = self._event_linker.get_listeners_by_events(
            exception.__class__, Exception
        )

        # Iterates through each exception event listener and triggers the associated callback function
        for event_listener in event_listeners:

            # Checks if the exception event listener is a one-time listener before executing the event listener
            if event_listener.once:

                # If the exception event listener is a one-time listener, we try to remove it. If it is
                # successfully removed, it means it hasn't been executed before, so we execute the callback
                if self._event_linker.remove_event_listener(event_listener=event_listener):
                    # Executes the event listener callback function with the exception as the first positional argument
                    self._execute(exception, event_listener=event_listener)
            else:
                # Executes the event listener callback function with the exception as the first positional argument
                self._execute(exception, event_listener=event_listener)

    @abstractmethod
    def _execute(self, *args: Any, event_listener: EventListener, **kwargs: Any) -> None:
        """
        Executes the callback function associated with an event listener.

        This method is responsible for executing the callback function associated with the given event listener.
        The callback function should be executed with the positional arguments provided as `*args`, along with any
        keyword arguments provided as `**kwargs`.

        Subclasses should provide their own implementation of this method to handle the execution of event listener
        callbacks based on their specific requirements and context.

        :param args: The positional arguments to pass to the callback function.
        :param event_listener: The event listener whose callback function should be executed.
        :param kwargs: The keyword arguments to pass to the callback function.
        :return: None
        """
        pass
