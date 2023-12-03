from abc import ABC, abstractmethod
from sys import gettrace
from typing import List, Type, TypeAlias, Any, Tuple

from src.pyventus.core.constants import StdOutColors
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

    This abstract base class defines a common interface for emitting events. It serves as
    a foundation for  implementing custom event emitters with specific dispatch strategies.
    It is designed to handle `string-named` events with variable-length argument list and
    arbitrary keyword arguments, as well as instances of `Event` objects and `Exceptions`.

    The main goal of this class is to decouple the dispatching of event listener callbacks
    from the underlying implementation. This loose coupling promotes flexibility and
    adaptability through separation of concerns, allowing custom event emitters to
    be implemented without affecting existing consumers.

    **Important:** Concrete subclasses should address these core aspects to integrate
    smoothly:

    - **Sync/Async Support:** Subclasses must dispatch events appropriately across
      async/sync scopes in order to align with Pyventus' unified async/sync design.

    - **Error Handling:** Errors during emission should be captured and handled to
      ensure reliability.

    **Example**: Here is an example of how to subclass `EventEmitter` and customize
    event handling:

    ```Python
    class CustomEventEmitter(EventEmitter):

        def _execute(self, event_listeners: List[EventListener], *args: Any, **kwargs: Any) -> None:
            # Underlying implementation...
            pass
    ```
    """

    def __init__(self, event_linker: Type[EventLinker] = EventLinker, debug_mode: bool | None = None):
        """
        Initializes an instance of the `EventEmitter`.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event listeners. Defaults to `EventLinker`.
        :param debug_mode: Specifies the debug mode for the subclass logger. If `None`,
            it is determined based on the execution environment.
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
        An instance of the logger used for logging events and debugging information. The 
        debug mode of the logger can be explicitly set by providing a boolean value for the 
        `debug_mode` argument in the constructor. If `debug_mode` is set to `None`, the debug
        mode will be automatically determined based on the execution environment and the
        value returned by the `gettrace()` function.
        """

    def emit(self, event: EmittableEventType, *args: Any, **kwargs: Any) -> None:
        """
        Emits an event and triggers any associated event listeners. When emitting `Event` or
        `Exception` objects, they are automatically passed to the `Event Listener` as the
        first positional argument, even if you pass `*args` or `**kwargs`.

        **Note:** If there are event listeners subscribed to the emission of any event
        (`Event`), they will also be executed. The specific behavior and handling of events
        may vary depending on the implementation of the event system.

        :param event: The event to emit. It can be an instance of `Event`, `Exception`,
            or a `str`.
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

        # Initializes the list of event listeners to be executed
        pending_event_listeners: List[EventListener] = []

        # Iterates through each event listener and triggers the associated callback function
        for event_listener in event_listeners:

            # Checks if the event listener is a one-time listener before executing the event listener
            if event_listener.once:

                # If the event listener is a one-time listener, we try to remove it. If it is
                # successfully removed, it means it hasn't been executed before, so we execute the callback
                if self._event_linker.remove_event_listener(event_listener=event_listener):
                    # Adds the current event listener to the execution list
                    pending_event_listeners.append(event_listener)
            else:
                # Adds the current event listener to the execution list
                pending_event_listeners.append(event_listener)

        # Log the event emission if debug mode is enabled
        if self._logger.debug_enabled:
            self._logger.debug(
                action="Emitting:",
                msg=(
                    f"{event if is_string else event.__class__.__name__} "
                    f"{StdOutColors.PURPLE}\tListeners:{StdOutColors.DEFAULT} {len(pending_event_listeners)}"
                )
            )

        # Checks if the pending_event_listeners is not empty
        if len(pending_event_listeners) > 0:
            # Executes the pending event listeners along with their arguments and keyword arguments
            self._execute(pending_event_listeners, *event_args, **kwargs)

    @abstractmethod
    def _execute(self, event_listeners: List[EventListener], *args: Any, **kwargs: Any) -> None:
        """
        Executes the callback functions associated with the specified event listeners.

        This method is responsible for executing the callback function associated with
        each event listener provided in the `event_listeners` parameter. The callback
        function will be executed with the positional arguments provided in `*args`
        and the keyword arguments provided in `**kwargs`.

        **Note:** Subclasses must implement this method to define how the event
        listener callbacks should be executed based on their specific context
        and requirements.

        :param event_listeners: List of event listeners to be executed.
        :param args: Positional arguments to pass to the callback functions.
        :param kwargs: Keyword arguments to pass to the callback functions.
        :return: None
        """
        pass
