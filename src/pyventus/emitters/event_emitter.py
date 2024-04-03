from abc import ABC, abstractmethod
from asyncio import gather
from datetime import datetime
from sys import gettrace
from typing import List, Type, TypeAlias, Any, Tuple, Dict, final
from uuid import uuid4

from ..core.constants import StdOutColors
from ..core.exceptions import PyventusException
from ..core.loggers import Logger, StdOutLogger
from ..handlers import EventHandler
from ..linkers import EventLinker

EmittableEventType: TypeAlias = str | Exception | object
"""A type alias representing the supported types of events that can be emitted."""


class EventEmitter(ABC):
    """
    An abstract base class for event emitters.

    **Notes:**

    -   This class defines a common interface for emitting events. It serves as a foundation for
        implementing custom event emitters with specific dispatch strategies. It is designed to
        handle `string-named` events with positional and keyword arguments, as well as instances
        of `dataclass` objects and `Exceptions` objects.

    -   The main goal of this class is to decouple the event emission process from the underlying
        implementation. This loose coupling promotes flexibility, adaptability, and adheres to the
        Open-Closed principle, allowing custom event emitters to be implemented without affecting
        existing consumers.

    ---
    Read more in the
    [Pyventus docs for Event Emitter](https://mdapena.github.io/pyventus/tutorials/emitters/).
    """

    @final
    class EventEmission:
        """
        Represents an event emission that has been triggered but whose propagation is not
        yet complete. It provides a self-contained context for executing the event emission,
        encapsulating both the event data and the associated event handlers.

        This class acts as an isolated unit of work to asynchronously propagate the emission
        of an event. When an event occurs, the `EventEmitter` class creates an `EventEmission`
        instance, which is then processed by the `_process()` method to handle the event
        propagation.
        """

        # Event emission attributes
        __slots__ = ("_id", "_timestamp", "_debug", "_event", "_event_handlers", "_event_args", "_event_kwargs")

        @property
        def id(self) -> str:
            """
            Gets the unique identifier of the event emission.
            :return: The unique identifier of the event emission.
            """
            return self._id

        @property
        def timestamp(self) -> datetime:
            """
            Gets the timestamp when the event emission was created.
            :return: The timestamp when the event emission was created.
            """
            return self._timestamp

        @property
        def event(self) -> str:
            """
            Gets the name of the event being emitted.
            :return: The name of the event.
            """
            return self._event

        def __init__(
            self,
            event: str,
            event_handlers: List[EventHandler],
            event_args: Tuple[Any, ...],
            event_kwargs: Dict[str, Any],
            debug: bool,
        ) -> None:
            """
            Initialize an instance of `EventEmission`.
            :param event: The name of the event being emitted.
            :param event_handlers: List of event handlers associated with the event.
            :param event_args: Positional arguments to be passed to the event handlers.
            :param event_kwargs: Keyword arguments to be passed to the event handlers.
            :param debug: Indicates if debug mode is enabled.
            :raises PyventusException: If `event_handlers` or `event` is empty.
            """
            if not event_handlers:  # pragma: no cover
                raise PyventusException("The 'event_handlers' argument cannot be empty.")

            if not event:  # pragma: no cover
                raise PyventusException("The 'event' argument cannot be empty.")

            # Set the event emission metadata
            self._id: str = str(uuid4())
            self._timestamp: datetime = datetime.now()
            self._debug: bool = debug

            # Set the event emission properties
            self._event: str = event
            self._event_handlers: Tuple[EventHandler, ...] = tuple(event_handlers)
            self._event_args: Tuple[Any, ...] = event_args
            self._event_kwargs: Dict[str, Any] = event_kwargs

        async def __call__(self) -> None:
            """
            Execute the event handlers concurrently.
            :return: None
            """
            # Log the event execution if debug is enabled
            if self._debug:  # pragma: no cover
                StdOutLogger.debug(name=self.__class__.__name__, action="Running:", msg=str(self))

            # Execute the event handlers concurrently
            await gather(
                *[event_handler(*self._event_args, **self._event_kwargs) for event_handler in self._event_handlers],
                return_exceptions=True,
            )

        def __str__(self) -> str:
            """
            Returns a formatted string representation of the event emission.
            :return: The formatted string representation of the event emission.
            """
            return (
                f"ID: {self.id} | Timestamp: {self.timestamp.strftime('%Y-%m-%d %I:%M:%S %p')} | "
                f"Event: {self.event} | Handlers: {len(self._event_handlers)}"
            )

    def __init__(self, event_linker: Type[EventLinker] = EventLinker, debug: bool | None = None) -> None:
        """
        Initialize an instance of `EventEmitter`.
        :param event_linker: Specifies the type of event linker used to manage and access
            events along with their corresponding event handlers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the subclass logger. If `None`,
            it is determined based on the execution environment.
        :raises PyventusException: If the `event_linker` argument is None.
        """
        # Validate the event linker argument
        if event_linker is None:
            raise PyventusException("The 'event_linker' argument cannot be None.")

        # Set the event_linker value
        self._event_linker: Type[EventLinker] = event_linker
        """
        Specifies the type of event linker to use for associating events with their 
        respective event handlers.
        """

        self._logger: Logger = Logger(
            name=self.__class__.__name__,
            debug=debug if debug is not None else bool(gettrace() is not None),
        )
        """
        An instance of the logger used for logging events and debugging information.
        """

    def emit(self, /, event: EmittableEventType, *args: Any, **kwargs: Any) -> None:
        """
        Emits an event and triggers its associated event handlers.

        **Notes:**

        -   When emitting `dataclass` objects or `Exception` objects, they are automatically passed
            to the event handler as the first positional argument, even if you pass additional `*args`
            or `**kwargs`.
        -   If there are event handlers subscribed to the global event `...`, also known as `Ellipsis`,
            they will also be triggered each time an event or exception is emitted.

        :param event: The event to be emitted. It can be `str`, a `dataclass`
            object, or an `Exception` object.
        :param args: Positional arguments to be passed to the event handlers.
        :param kwargs: Keyword arguments to be passed to the event handlers.
        :return: None
        """
        # Raise an exception if the event is None
        if event is None:
            raise PyventusException("The 'event' argument cannot be None.")

        # Raise an exception if the event is a type
        if isinstance(event, type):  # type: ignore[comparison-overlap]
            raise PyventusException("The 'event' argument cannot be a type.")

        # Determine the event name
        event_name: str = self._event_linker.get_event_name(event=event if isinstance(event, str) else type(event))

        # Retrieve the event handlers associated with the event
        event_handlers: List[EventHandler] = self._event_linker.get_event_handlers_by_events(event_name, Ellipsis)

        # Sort the event handlers by timestamp
        event_handlers.sort(key=lambda handler: handler.timestamp)

        # Initialize the list of event handlers to be executed
        pending_event_handlers: List[EventHandler] = []

        # Iterate through each event handler
        for event_handler in event_handlers:
            # Check if the event handler is a one-time subscription
            if event_handler.once:
                # If the event handler is a one-time subscription, we attempt to remove it.
                if self._event_linker.remove_event_handler(event_handler=event_handler):  # pragma: no cover (Race-Cond)
                    # If the removal is successful, it indicates that the handler has not
                    # been processed before, so we add it to the pending list.
                    pending_event_handlers.append(event_handler)
            else:
                pending_event_handlers.append(event_handler)

        # Check if the pending list of event handlers is not empty
        if len(pending_event_handlers) > 0:
            # Create a new EventEmission instance
            event_emission: EventEmitter.EventEmission = EventEmitter.EventEmission(
                event=event_name,
                event_handlers=pending_event_handlers,
                event_args=args if isinstance(event, str) else (event, *args),
                event_kwargs=kwargs,
                debug=self._logger.debug_enabled,
            )

            # Log the event emission when debug is enabled
            if self._logger.debug_enabled:  # pragma: no cover
                self._logger.debug(
                    action="Emitting Event:",
                    msg=f"{event_emission.event}{StdOutColors.PURPLE} ID:{StdOutColors.DEFAULT} {event_emission.id}",
                )

            # Delegate the event emission processing to subclasses
            self._process(event_emission)

        # Log a debug message if there are no event handlers subscribed to the event
        elif self._logger.debug_enabled:  # pragma: no cover
            self._logger.debug(
                action="Emitting Event:",
                msg=f"{event_name}{StdOutColors.PURPLE} Message:{StdOutColors.DEFAULT} No event handlers subscribed",
            )

    @abstractmethod
    def _process(self, event_emission: EventEmission) -> None:
        """
        Process the event emission execution. Subclasses must implement
        this method to define the specific processing logic.

        :param event_emission: The event emission to be processed.
        :return: None
        """
        pass
