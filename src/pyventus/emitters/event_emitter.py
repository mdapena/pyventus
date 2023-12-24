from abc import ABC, abstractmethod
from asyncio import gather
from datetime import datetime
from sys import gettrace
from typing import List, Type, TypeAlias, Any, Tuple, Dict
from uuid import uuid4

from ..core.constants import StdOutColors
from ..core.exceptions import PyventusException
from ..core.loggers import Logger, StdOutLogger
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

    For more information and code examples, please refer to the `EventEmitter` tutorials
    at: [https://mdapena.github.io/pyventus/tutorials/emitters/](https://mdapena.github.io/pyventus/tutorials/emitters/).
    """

    class EventDelegate:
        """
        A class that acts as a delegate for event execution. It encapsulates related
        event handler callbacks, shared execution context, and arguments for loose
        coupling and concurrent execution.

        By bundling the handlers and data, it allows event emitters to delegate
        downstream processing of the event handler callbacks in a decoupled manner.
        The event handlers are executed concurrently for optimized performance.
        """

        # Event delegate attributes
        __slots__ = ("_id", "_timestamp", "_debug", "_event_handlers", "_args", "_kwargs")

        @property
        def id(self) -> str:
            """
            Get the unique identifier for the event delegate.
            :return: The unique identifier.
            """
            return self._id

        @property
        def timestamp(self) -> datetime:
            """
            Get the timestamp representing the creation time of the event delegate.
            :return: The timestamp.
            """
            return self._timestamp

        def __init__(self, debug: bool, event_handlers: List[EventHandler], /, *args: Any, **kwargs: Any):
            """
            Initialize a new `EventDelegate` instance.
            :param debug: Specifies the debug flag for the event delegate.
            :param event_handlers: List of event handlers to execute.
            :param args: Positional arguments to pass to the event handlers.
            :param kwargs: Keyword arguments to pass to the event handlers.
            """
            if not event_handlers:
                raise PyventusException("The 'event_handlers' argument cannot be empty.")

            self._id: str = str(uuid4())
            """The unique identifier for the event delegate."""

            self._timestamp: datetime = datetime.now()
            """The timestamp representing the creation time of the event delegate."""

            self._debug: bool = debug
            """A flag indicating whether or not debug mode is enabled."""

            self._event_handlers: Tuple[EventHandler] = tuple(event_handlers)
            """A tuple of event handlers to be executed."""

            self._args: Tuple[Any, ...] = args
            """Positional arguments to be passed to the event handlers."""

            self._kwargs: Dict[str, Any] = kwargs
            """Keyword arguments to be passed to the event handlers."""

        async def __call__(self) -> None:
            """
            Execute the event handlers concurrently.
            :return: None
            """
            # Log the event execution if debug mode is enabled
            if self._debug:
                StdOutLogger.debug(name=self.__class__.__name__, action="Executing:", msg=str(self))

            # Execute the event handlers concurrently
            await gather(
                *[event_handler(*self._args, **self._kwargs) for event_handler in self._event_handlers],
                return_exceptions=True,
            )

        def __str__(self) -> str:
            """
            Return a string representation of the event delegate.
            :return: The string representation.
            """
            return f"Id: {self.id} | Timestamp: {self.timestamp} | Event Handlers: {len(self._event_handlers)}"

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
                if self._event_linker.remove_event_handler(event_handler=event_handler):  # pragma: no cover (Race-Cond)
                    # Adds the current event handler to the execution list
                    pending_event_handlers.append(event_handler)
            else:
                # Adds the current event handler to the execution list
                pending_event_handlers.append(event_handler)

        # Log the event emission if debug mode is enabled
        if self._logger.debug_enabled:  # pragma: no cover
            self._logger.debug(
                action="Emitting:",
                msg=(
                    f"{event if is_string else event.__class__.__name__} "
                    f"{StdOutColors.PURPLE} Handlers:{StdOutColors.DEFAULT} {len(pending_event_handlers)}"
                ),
            )

        # Checks if the pending_event_handlers is not empty
        if len(pending_event_handlers) > 0:
            # Delegates the event execution to the event
            # delegate and submits it for processing.
            self._process(
                delegate=EventEmitter.EventDelegate(
                    self._logger.debug_enabled,
                    pending_event_handlers,
                    *event_args,
                    **kwargs,
                )
            )

    @abstractmethod
    def _process(self, delegate: EventDelegate) -> None:
        """
        Processes the execution of the event delegate.

        **Note:** Subclasses must implement this method to define the specific
        processing logic for the event delegate.

        :param delegate: The event delegate to be processed.
        :return: None
        """
        pass
