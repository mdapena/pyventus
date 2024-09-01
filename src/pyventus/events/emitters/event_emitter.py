from abc import ABC, abstractmethod
from asyncio import gather
from datetime import datetime
from sys import gettrace
from types import EllipsisType
from typing import Any, TypeAlias, final
from uuid import uuid4

from ...core.exceptions import PyventusException
from ...core.loggers import Logger, StdOutLogger
from ...core.utils import attributes_repr, formatted_repr
from ..linkers import EventLinker
from ..subscribers import EventSubscriber

EmittableEventType: TypeAlias = str | Exception | object | EllipsisType
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
        Represents an event emission that has been triggered but whose propagation is not yet complete.

        This class provides a self-contained context for executing the event emission, encapsulating both the
        event data and the associated subscribers. It acts as an isolated unit of work to asynchronously propagate
        the emission of an event. When an event occurs, the `EventEmitter` class creates an `EventEmission`
        instance, which is then processed by the `_process()` method to handle the event propagation.
        """

        # Attributes for the EventEmission
        __slots__ = ("__id", "__event", "__subscribers", "__args", "__kwargs", "__timestamp", "__debug")

        def __init__(
            self,
            event: str,
            subscribers: set[EventSubscriber],
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
            debug: bool,
        ) -> None:
            """
            Initialize an instance of `EventEmission`.

            :param event: The name of the event being emitted.
            :param subscribers: A set of subscribers associated with the event.
            :param args: Positional arguments containing event-specific data.
            :param kwargs: Keyword arguments containing event-specific data.
            :param debug: Indicates whether debug mode is enabled.
            """
            if not event:  # pragma: no cover
                raise PyventusException("The 'event' argument cannot be None or empty.")

            if not subscribers:  # pragma: no cover
                raise PyventusException("The 'subscribers' argument cannot be None or empty.")

            # Define and set the event emission attributes
            self.__id: str = str(uuid4())
            self.__event: str = event
            self.__subscribers: set[EventSubscriber] = subscribers
            self.__args: tuple[Any, ...] = args
            self.__kwargs: dict[str, Any] = kwargs
            self.__timestamp: datetime = datetime.now()
            self.__debug: bool = debug

        def __repr__(self) -> str:  # pragma: no cover
            """
            Retrieve a string representation of the instance.

            :return: A string representation of the instance.
            """
            return formatted_repr(
                instance=self,
                info=attributes_repr(
                    id=self.__id,
                    event=self.__event,
                    subscribers=self.__subscribers,
                    args=self.__args,
                    kwargs=self.__kwargs,
                    timestamp=self.__timestamp,
                    debug=self.__debug,
                ),
            )

        @property
        def id(self) -> str:  # pragma: no cover
            """
            Retrieve the unique identifier of the event emission.

            :return: The unique identifier of the event emission.
            """
            return self.__id

        @property
        def event(self) -> str:  # pragma: no cover
            """
            Retrieve the name of the emitted event.

            :return: The name of the event.
            """
            return self.__event

        @property
        def timestamp(self) -> datetime:  # pragma: no cover
            """
            Retrieve the timestamp when the event emission was created.

            :return: The timestamp when the event emission was created.
            """
            return self.__timestamp

        async def __call__(self) -> None:
            """
            Execute the subscribers concurrently.

            :return: None.
            """
            # Log the event execution if debug mode is enabled
            if self.__debug:  # pragma: no cover
                StdOutLogger.debug(name=type(self).__name__, action="Executing:", msg=f"{self}")

            # Execute the subscribers concurrently
            await gather(
                *[subscriber.execute(*self.__args, **self.__kwargs) for subscriber in self.__subscribers],
                return_exceptions=True,
            )

            # Perform cleanup by deleting unnecessary references
            del self.__id, self.__event, self.__subscribers, self.__args, self.__kwargs, self.__timestamp, self.__debug

    def __init__(self, event_linker: type[EventLinker] = EventLinker, debug: bool | None = None) -> None:
        """
        Initialize an instance of `EventEmitter`.

        :param event_linker: Specifies the type of event linker used to manage and access
            events along with their corresponding subscribers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is determined
            based on the execution environment.
        :raises PyventusException: If the `event_linker` argument is None or invalid.
        """
        # Validate the event_linker and debug arguments
        if event_linker is None:
            raise PyventusException("The 'event_linker' argument cannot be None.")
        if not issubclass(event_linker, EventLinker):
            raise PyventusException("The 'event_linker' argument must be a subtype of the EventLinker class.")
        if debug is not None and not isinstance(debug, bool):
            raise PyventusException("The 'debug' argument must be a boolean value.")

        # Set the event_linker value
        self._event_linker: type[EventLinker] = event_linker

        # Set up the logger
        self._logger: Logger = Logger(
            name=type(self).__name__,
            debug=debug if debug is not None else bool(gettrace() is not None),
        )

    def __repr__(self) -> str:  # pragma: no cover
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return attributes_repr(
            event_linker=self._event_linker.__name__,
            debug=self._logger.debug_enabled,
        )

    @abstractmethod
    def _process(self, event_emission: EventEmission) -> None:
        """
        Process the event emission execution.

        Subclasses must implement this method to define the specific processing logic.

        :param event_emission: The event emission to be processed.
        :return: None
        """
        pass

    def emit(self, /, event: EmittableEventType, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event and notifies all registered subscribers.

        **Notes:**

        -   When emitting `dataclass` objects or `Exception` objects, they are automatically
            passed to the subscribers as the first positional argument, even if you pass
            additional `*args` or `**kwargs`.

        -   If there are subscribers registered to the global event `...` (also known
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

        # Get the valid event name
        event_name: str = self._event_linker.get_valid_event_name(
            event=(event if isinstance(event, str | EllipsisType) else type(event))
        )

        # Get the set of subscribers associated with the event, removing one-time subscribers.
        subscribers: set[EventSubscriber] = self._event_linker.get_subscribers_from_events(
            event_name, Ellipsis, pop_one_time_subscribers=True
        )

        # If there are no subscribers for the event, log a
        # debug message if debug mode is enabled and exit.
        if not subscribers:
            if self._logger.debug_enabled:  # pragma: no cover
                self._logger.debug(action="Emitting:", msg=f"No subscribers registered for the event '{event_name}'.")
            return

        # Create a new EventEmission instance to handle the event propagation.
        event_emission = EventEmitter.EventEmission(
            event=event_name,
            subscribers=subscribers,
            args=(args if isinstance(event, str | EllipsisType) else (event, *args)),
            kwargs=kwargs,
            debug=self._logger.debug_enabled,
        )

        # Log the event emission if debug mode is enabled.
        if self._logger.debug_enabled:  # pragma: no cover
            self._logger.debug(action="Emitting:", msg=f"{event_emission}")

        # Delegate the event emission processing to subclasses
        self._process(event_emission)
