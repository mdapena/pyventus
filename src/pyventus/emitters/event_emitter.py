from abc import ABC, abstractmethod
from sys import gettrace
from typing import List, Type, TypeAlias, Any, Tuple

from ..core.constants import StdOutColors
from ..core.exceptions import PyventusException
from ..core.loggers import Logger
from ..events import Event
from ..handlers import EventHandler
from ..linkers import EventLinker

EmittableEventType: TypeAlias = Event | Exception | str
""" A type alias representing the supported types of events that can be emitted. """


class EventEmitter(ABC):
    """
    An abstract base class for event emitters.

    This abstract base class defines a common interface for emitting events. It serves as
    a foundation for  implementing custom event emitters with specific dispatch strategies.
    It is designed to handle `string-named` events with variable-length argument list and
    arbitrary keyword arguments, as well as instances of `Event` objects and `Exceptions`.

    The main goal of this class is to decouple the dispatching of event handler callbacks
    from the underlying implementation. This loose coupling promotes flexibility and
    adaptability through separation of concerns, allowing custom event emitters to
    be implemented without affecting existing consumers.

    **Example**: Here is an example of how to subclass `EventEmitter` and customize
    event handling:

    ```Python
    class CustomEventEmitter(EventEmitter):

        def _execute(self, event_handlers: List[EventHandler], *args: Any, **kwargs: Any) -> None:
            # Underlying implementation...
            pass
    ```
    """

    def __init__(self, event_linker: Type[EventLinker] = EventLinker, debug_mode: bool | None = None):
        """
        Initializes an instance of the `EventEmitter`.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event handlers. Defaults to `EventLinker`.
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
        use for associating events with their respective event handlers.
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

    def emit(self, /, event: EmittableEventType, *args: Any, **kwargs: Any) -> None:
        """
        Emits an event and triggers any associated event handlers. When emitting `Event` or
        `Exception` objects, they are automatically passed to the event handler as the
        first positional argument, even if you pass `*args` or `**kwargs`.

        **Note:** If there are event handlers subscribed to the emission of any `Event` or
        `Exception`, they will also be executed.

        :param event: The event to emit. It can be an instance of `Event`, `Exception`,
            or a simple `str`.
        :param args: Additional positional arguments to pass to the event handlers.
        :param kwargs: Additional keyword arguments to pass to the event handlers.
        :return: None
        """
        # Raises an exception if the event is None
        if event is None:
            raise PyventusException("The 'event' argument cannot be None.")

        # Raises an exception if the event is a type object
        if event.__class__ is type:  # type: ignore
            raise PyventusException("The 'event' argument cannot be a type object.")

        # Determines if the event is a string instance
        is_string: bool = isinstance(event, str)

        # Raises an exception if the event is a string and it is empty
        if is_string and len(event) == 0:  # type: ignore
            raise PyventusException("The 'event' argument cannot be an empty string.")

        # Constructs the arguments tuple based on whether the event is a string or an object
        event_args: Tuple[Any, ...] = args if is_string else (event, *args)

        # Retrieves the event handlers associated with the event sorted by their timestamp
        event_handlers: List[EventHandler] = sorted(
            self._event_linker.get_handlers_by_events(
                event if is_string else event.__class__,  # type: ignore
                Event if not issubclass(event.__class__, Exception) else Exception,
            ),
            key=lambda handler: handler.timestamp,
        )

        # Initializes the list of event handlers to be executed
        pending_event_handlers: List[EventHandler] = []

        # Iterates through each event handler and triggers the associated callbacks
        for event_handler in event_handlers:
            # Checks if the event handler is a one-time handler before executing the event handler
            if event_handler.once:
                # If the event handler is a one-time handler, we try to remove it. If it is successfully
                # removed, it means it hasn't been executed before, so we execute the callback
                if self._event_linker.remove_event_handler(event_handler=event_handler):
                    # Adds the current event handler to the execution list
                    pending_event_handlers.append(event_handler)
            else:
                # Adds the current event handler to the execution list
                pending_event_handlers.append(event_handler)

        # Log the event emission if debug mode is enabled
        if self._logger.debug_enabled:
            self._logger.debug(
                action="Emitting:",
                msg=(
                    f"{event if is_string else event.__class__.__name__} "
                    f"{StdOutColors.PURPLE}\tHandlers:{StdOutColors.DEFAULT} {len(pending_event_handlers)}"
                ),
            )

        # Checks if the pending_event_handlers is not empty
        if len(pending_event_handlers) > 0:
            # Executes the pending event handlers along with their arguments and keyword arguments
            self._execute(pending_event_handlers, *event_args, **kwargs)

    @abstractmethod
    def _execute(self, event_handlers: List[EventHandler], /, *args: Any, **kwargs: Any) -> None:
        """
        Executes the callbacks associated with the specified event handlers.

        This method is responsible for executing the callbacks associated with each event
        handler provided in the `event_handlers` parameter. The callbacks will be executed
        with the positional arguments provided in `*args` and the keyword arguments provided
        in `**kwargs`.

        **Note:** Subclasses must implement this method to define how the event handler
        callbacks should be executed based on their specific context and requirements.

        :param event_handlers: List of event handlers to be executed.
        :param args: Positional arguments to pass to the callbacks.
        :param kwargs: Keyword arguments to pass to the callbacks.
        :return: None
        """
        pass
