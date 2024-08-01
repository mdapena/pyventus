from abc import ABC, abstractmethod
from asyncio import gather
from datetime import datetime
from sys import gettrace
from typing import List, Type, TypeAlias, Any, Tuple, Dict, final
from uuid import uuid4

from ..linkers import EventLinker
from ..subscribers import EventSubscriber
from ...core.constants import StdOutColors
from ...core.exceptions import PyventusException
from ...core.loggers import Logger, StdOutLogger

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
    [Pyventus docs for Event Emitter](https://mdapena.github.io/pyventus/tutorials/events/emitters/).
    """

    @final
    class EventEmission:
        """
        Represents an event emission that has been triggered but whose propagation is not
        yet complete. It provides a self-contained context for executing the event emission,
        encapsulating both the event data and the associated event subscribers.

        This class acts as an isolated unit of work to asynchronously propagate the emission
        of an event. When an event occurs, the `EventEmitter` class creates an `EventEmission`
        instance, which is then processed by the `_process()` method to handle the event
        propagation.
        """

        # Attributes for the EventEmission
        __slots__ = (
            "__id",
            "__timestamp",
            "__debug",
            "__event",
            "__event_subscribers",
            "__event_args",
            "__event_kwargs",
        )

        @property
        def id(self) -> str:
            """
            Gets the unique identifier of the event emission.
            :return: The unique identifier of the event emission.
            """
            return self.__id

        @property
        def timestamp(self) -> datetime:
            """
            Gets the timestamp when the event emission was created.
            :return: The timestamp when the event emission was created.
            """
            return self.__timestamp

        @property
        def event(self) -> str:
            """
            Gets the name of the event being emitted.
            :return: The name of the event.
            """
            return self.__event

        def __init__(
            self,
            event: str,
            event_subscribers: List[EventSubscriber],
            event_args: Tuple[Any, ...],
            event_kwargs: Dict[str, Any],
            debug: bool,
        ) -> None:
            """
            Initialize an instance of `EventEmission`.
            :param event: The name of the event being emitted.
            :param event_subscribers: List of event subscribers associated with the event.
            :param event_args: Positional arguments containing event-specific data.
            :param event_kwargs: Keyword arguments containing event-specific data.
            :param debug: Indicates if debug mode is enabled.
            """
            if not event_subscribers:  # pragma: no cover
                raise PyventusException("The 'event_subscribers' argument cannot be None or empty.")

            if not event:  # pragma: no cover
                raise PyventusException("The 'event' argument cannot be None or empty.")

            # Set the event emission metadata
            self.__id: str = str(uuid4())
            self.__timestamp: datetime = datetime.now()
            self.__debug: bool = debug

            # Set the event emission properties
            self.__event: str = event
            self.__event_subscribers: List[EventSubscriber] = event_subscribers
            self.__event_args: Tuple[Any, ...] = event_args
            self.__event_kwargs: Dict[str, Any] = event_kwargs

        async def __call__(self) -> None:
            """
            Execute the event subscribers concurrently.
            :return: None
            """
            # Log the event execution if debug is enabled
            if self.__debug:  # pragma: no cover
                StdOutLogger.debug(name=type(self).__name__, action="Running:", msg=str(self))

            # Execute the event subscribers concurrently
            await gather(
                *[sub.execute(*self.__event_args, **self.__event_kwargs) for sub in self.__event_subscribers],
                return_exceptions=True,
            )

        def __str__(self) -> str:
            """
            Returns a formatted string representation of the event emission.
            :return: The formatted string representation of the event emission.
            """
            return (
                f"ID: {self.id} | Timestamp: {self.timestamp.strftime('%Y-%m-%d %I:%M:%S %p')} | "
                f"Event: {self.event} | Subscribers: {len(self.__event_subscribers)}"
            )

    def __init__(self, event_linker: Type[EventLinker] = EventLinker, debug: bool | None = None) -> None:
        """
        Initialize an instance of `EventEmitter`.
        :param event_linker: Specifies the type of event linker used to manage and access
            events along with their corresponding event subscribers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is determined
            based on the execution environment.
        :raises PyventusException: If the `event_linker` argument is None or invalid.
        """
        # Validate the event linker argument
        if event_linker is None:
            raise PyventusException("The 'event_linker' argument cannot be None.")
        if not issubclass(event_linker, EventLinker):
            raise PyventusException("The 'event_linker' argument must be a subtype of the EventLinker class.")

        # Set the event_linker value
        self._event_linker: Type[EventLinker] = event_linker

        # Set up the logger
        self._logger: Logger = Logger(
            name=type(self).__name__,
            debug=debug if debug is not None else bool(gettrace() is not None),
        )

    def emit(self, /, event: EmittableEventType, *args: Any, **kwargs: Any) -> None:
        """
        Emits an event and notifies all registered event subscribers.

        **Notes:**

        -   When emitting `dataclass` objects or `Exception` objects, they are automatically
            passed to the event subscribers as the first positional argument, even if you pass
            additional `*args` or `**kwargs`.

        -   If there are event subscribers registered to the global event `...` (also known
            as `Ellipsis`), they will be notified each time an event is emitted.

        :param event: The event to be emitted. It can be `str`, a `dataclass`
            object, or an `Exception` object.
        :param args: Positional arguments containing event-specific data.
        :param kwargs: Keyword arguments containing event-specific data.
        :return: None
        """
        # Raise an exception if the event is None.
        if event is None:
            raise PyventusException("The 'event' argument cannot be None.")

        # Raise an exception if the event is a type.
        if isinstance(event, type):
            raise PyventusException("The 'event' argument cannot be a type.")

        # Determine the event name.
        event_name: str = self._event_linker.get_event_name(event=event if isinstance(event, str) else type(event))

        # Retrieve the list of event subscribers associated with the event.
        event_subscribers = self._event_linker.get_event_subscribers_by_events(event_name, Ellipsis)

        # Initialize the list of event subscribers to be executed.
        pending_event_subscribers: List[EventSubscriber] = []

        # Iterate through each event subscriber to determine which ones to process.
        for event_subscriber in event_subscribers:
            # Skip closed subscribers
            if event_subscriber.closed:
                continue

            # Check if the event subscriber is a one-time subscription.
            if event_subscriber.once:
                # Attempt to unsubscribe the one-time subscriber.
                if event_subscriber.unsubscribe():
                    # If unsubscription is successful, add it to the pending list
                    pending_event_subscribers.append(event_subscriber)
            else:
                # Add regular subscribers to the pending list for processing
                pending_event_subscribers.append(event_subscriber)

        # Check if the pending list is not empty
        if len(pending_event_subscribers) > 0:
            # Create a new EventEmission instance
            event_emission = EventEmitter.EventEmission(
                event=event_name,
                event_subscribers=pending_event_subscribers,
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
        else:
            # Log a debug message if there are no subscribers for the event
            if self._logger.debug_enabled:  # pragma: no cover
                self._logger.debug(
                    action="Emitting Event:",
                    msg=f"{event_name}{StdOutColors.PURPLE} Message:{StdOutColors.DEFAULT} No event subscribers.",
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
