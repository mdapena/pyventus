from abc import ABC, abstractmethod
from sys import gettrace
from typing import List, Type, TypeAlias, Any, Tuple

from src.pyventus.core.exceptions import PyventusException
from src.pyventus.core.loggers import Logger
from src.pyventus.events import Event
from src.pyventus.linkers import EventLinker
from src.pyventus.listeners import EventListener

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

    def __init__(self, event_linker: Type[EventLinker] = EventLinker, debug_mode: bool | None = None):
        """
        Initializes an instance of the `EventEmitter`.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event listeners. Defaults to `EventLinker`.
        :param debug_mode: Specifies the debug mode for the subclass logger.
            If `None`, it is determined based on the execution environment.
        :raises PyventusException: If the `event_linker` argument is None.
        """
        # Validate the event linker argument
        if event_linker is None:
            raise PyventusException("The 'event_linker' argument cannot be None.")

        # Set the event_linker value
        self._event_linker: Type[EventLinker] = event_linker
        """
        The `EventLinker` attribute specifies the type of event linker to 
        use for associating events with their respective event listeners.
        """

        self._logger: Logger = Logger(
            name=self.__class__.__name__,
            debug=debug_mode if debug_mode is not None else bool(gettrace() is not None),
        )
        """
        An instance of the logger used for logging events and debugging information. The debug mode
        of the logger can be explicitly set by providing a boolean value for the `debug_mode` argument in 
        the constructor. If `debug_mode` is set to `None`, the debug mode will be automatically determined
        based on the execution environment and the value returned by the `gettrace()` function.
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
            raise PyventusException("The 'event' argument cannot be None.")

        # Raises an exception if the event is a type object
        if event.__class__ is type:
            raise PyventusException("The 'event' argument cannot be a type object.")

        # Determines if the event is a string instance
        is_string: bool = isinstance(event, str)

        # Raises an exception if the event is a string and it is empty
        if is_string and len(event) == 0:
            raise PyventusException("The 'event' argument cannot be an empty string.")

        # Constructs the arguments tuple based on whether the event is a string or an object
        event_args: Tuple[Any, ...] = args if is_string else (event, *args)

        # Retrieves the event listeners associated with the event
        event_listeners: List[EventListener] = self._event_linker.get_listeners_by_events(
            Event if not issubclass(event.__class__, Exception) else Exception,
            event if is_string else event.__class__,
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
