from dataclasses import is_dataclass
from sys import gettrace
from threading import Lock
from types import TracebackType, EllipsisType
from typing import TypeAlias, Mapping, Tuple, Dict, List, Type, Set, Any, final

from ..handlers import EventHandler, EventCallbackType, SuccessCallbackType, FailureCallbackType
from ...core.constants import StdOutColors
from ...core.exceptions import PyventusException
from ...core.loggers import Logger
from ...core.utils import validate_callback, get_callback_name

SubscribableEventType: TypeAlias = str | Type[Exception] | Type[object] | EllipsisType
"""A type alias representing the supported event types for subscription."""


class EventLinker:
    """
    A base class that acts as a global registry for events and callbacks linkage. It provides
    a centralized mechanism for managing event subscriptions, unsubscriptions, and retrieval
    of events and their associated event handlers.

    **Notes:**

    -   The `EventLinker` class can be subclassed to create specific namespaces or contexts
        for managing events and event handlers separately. By subclassing the `EventLinker`,
        users can organize event subscriptions and handlers within different scopes, providing
        modularity and flexibility in event management. Subclassing also allows users to
        configure settings of the `EventLinker` to suit their specific use cases.

    -   The `EventLinker` has been implemented with *thread safety* in mind. All of its methods
        synchronize access to prevent race conditions when managing events and event handlers
        across multiple threads. This ensures that concurrent operations on the `EventLinker`
        are properly synchronized, avoiding data inconsistencies and race conditions.

    ---
    Read more in the
    [Pyventus docs for Event Linker](https://mdapena.github.io/pyventus/tutorials/event-linker/).
    """

    @final
    class EventLinkageWrapper:
        """
        A class that serves as a wrapper for event linking operations, providing a simplified
        interface for subscribing events with their corresponding callbacks.

        **Notes:**

        -   This class can be used as either a decorator or a context manager. When used as a
            decorator, it automatically subscribes the decorated callback to the provided events.
            When used as a context manager with the `with` statement, it allows multiple callbacks
            to be associated with the provided events within the context block.

        -   This class is not intended to be subclassed or manually created.
            The `EventLinkageWrapper` is used internally as a wrapper for event
            linking operations.
        """

        # Event linkage wrapper attributes
        __slots__ = (
            "__event_linker",
            "__events",
            "__once",
            "__force_async",
            "__event_callback",
            "__success_callback",
            "__failure_callback",
        )

        def on_event(self, callback: EventCallbackType) -> EventCallbackType:
            """
            Decorator that sets the main callback for the event.
            :param callback: The callback to be executed when the event occurs.
            :return: The decorated callback.
            """
            self.__event_callback = callback
            return callback

        def on_success(self, callback: SuccessCallbackType) -> SuccessCallbackType:
            """
            Decorator that sets the success callback.
            :param callback: The callback to be executed when
            the event execution completes successfully.
            :return: The decorated callback.
            """
            self.__success_callback = callback
            return callback

        def on_failure(self, callback: FailureCallbackType) -> FailureCallbackType:
            """
            Decorator that sets the failure callback.
            :param callback: The callback to be executed
            when the event execution fails.
            :return: The decorated callback.
            """
            self.__failure_callback = callback
            return callback

        def __init__(
            self,
            *events: SubscribableEventType,
            event_linker: Type["EventLinker"],
            force_async: bool,
            once: bool,
        ) -> None:
            """
            Initialize an instance of `EventLinkageWrapper`.
            :param events: The events to subscribe/link to.
            :param event_linker: The event linker instance used for subscription.
            :param force_async: Determines whether to force all callbacks to run asynchronously.
            :param once: Specifies if the callback is a one-time subscription.
            """
            self.__event_linker: Type[EventLinker] = event_linker
            self.__events: Tuple[SubscribableEventType, ...] = events

            self.__once: bool = once
            self.__force_async: bool = force_async
            self.__event_callback: EventCallbackType | None = None  # type: ignore[no-redef, assignment]
            self.__success_callback: SuccessCallbackType | None = None  # type: ignore[no-redef, assignment]
            self.__failure_callback: FailureCallbackType | None = None  # type: ignore[no-redef, assignment]

        def __call__(self, callback: EventCallbackType) -> EventCallbackType:
            """
            Subscribes the provided events to the decorated callback.
            :param callback: The callback to associate with the events.
            :return: The decorated callback.
            """
            self.__event_callback = callback
            self.__event_linker.subscribe(
                *self.__events,
                event_callback=self.__event_callback,
                success_callback=None,
                failure_callback=None,
                force_async=self.__force_async,
                once=self.__once,
            )
            del self
            return callback

        def __enter__(self) -> "EventLinker.EventLinkageWrapper":
            """
            Enters the linkage context block, allowing multiple
            callbacks to be associated with the events.
            :return: The context manager object
            """
            return self

        def __exit__(
            self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
        ) -> None:
            """
            Exits the linkage context block, subscribing the provided callbacks within
            the context to the specified events. Performs any necessary cleanup.
            :param exc_type: The type of the exception raised, if any.
            :param exc_val: The exception object raised, if any.
            :param exc_tb: The traceback information, if any.
            :return: None
            """
            self.__event_linker.subscribe(
                *self.__events,
                event_callback=self.__event_callback,
                success_callback=self.__success_callback,
                failure_callback=self.__failure_callback,
                force_async=self.__force_async,
                once=self.__once,
            )
            del self

    __registry: Dict[str, List[EventHandler]] = {}
    """ 
    A dictionary that serves as a container for storing events and their associated event 
    handlers. The keys represent registered event names, and the values are lists of event
    handler objects associated with each event.
    """

    __max_event_handlers: int | None = None
    """The maximum number of `EventHandlers` allowed per event, or `None` if there is no limit."""

    __default_success_callback: SuccessCallbackType | None = None
    """ 
    Represents the default success callback function that will be assigned to event handlers in 
    the absence of a specific success callback. This callback will be executed upon successful 
    completion of the event execution in each event handler.
    """

    __default_failure_callback: FailureCallbackType | None = None
    """
    Represents the default failure callback function that will be assigned to event handlers in 
    the absence of a specific failure callback. This callback will be executed when the event 
    execution fails in each event handler.
    """

    __thread_lock: Lock = Lock()
    """
    A `threading.Lock` object used for thread synchronization when accessing and modifying the 
    event registry to ensure thread safety. It prevents multiple threads from accessing and 
    modifying the registry simultaneously.
    """

    __logger: Logger = Logger(name="EventLinker", debug=bool(gettrace() is not None))
    """
    The logger used to debug and log information within the `EventLinker` class. The debug mode
    of the logger depends on the execution environment and the value returned by the `gettrace()`
    function. The debug mode can also be influenced by subclassing and overridden in subclasses.
    """

    def __init_subclass__(
        cls,
        max_event_handlers: int | None = None,
        default_success_callback: SuccessCallbackType | None = None,
        default_failure_callback: FailureCallbackType | None = None,
        debug: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a subclass of `EventLinker`.

        By default, this method sets up the main registry and thread lock object, but
        it can also be used to configure specific settings of the `EventLinker` subclass.

        :param max_event_handlers: The maximum number of event handlers allowed per event,
            or `None` if there is no limit.
        :param default_success_callback: The default callback to assign as the success
            callback in the event handlers when no specific success callback is provided.
        :param default_failure_callback: The default callback to assign as the failure
            callback in the event handlers when no specific failure callback is provided.
        :param debug: Specifies the debug mode for the subclass logger. If `None`,
            it is determined based on the execution environment.
        :param kwargs: The keyword arguments to pass to the superclass
            `__init_subclass__` method.
        :raises PyventusException: If `max_event_handlers` is less than 1 or
            if the provided callbacks are invalid.
        :return: None
        """
        # Call the parent class' __init_subclass__ method
        super().__init_subclass__(**kwargs)

        # Initialize the main registry
        cls.__registry = {}

        # Create a lock object for thread synchronization
        cls.__thread_lock = Lock()

        # Validate the max_event_handlers argument
        if max_event_handlers is not None and max_event_handlers < 1:
            raise PyventusException("The 'max_event_handlers' argument must be greater than or equal to 1.")

        # Set the maximum number of event handlers per event
        cls.__max_event_handlers = max_event_handlers

        # Validate the default success callback, if any
        if default_success_callback is not None:
            validate_callback(callback=default_success_callback)

        # Set the default success callback
        cls.__default_success_callback = default_success_callback

        # Validate the default failure callback, if any
        if default_failure_callback is not None:
            validate_callback(callback=default_failure_callback)

        # Set the default failure callback
        cls.__default_failure_callback = default_failure_callback

        # Validate the debug argument
        if debug is not None and not isinstance(debug, bool):
            raise PyventusException("The 'debug' argument must be a boolean value.")

        # Set up the logger
        cls.__logger = Logger(
            name=cls.__name__,
            debug=debug if debug is not None else bool(gettrace() is not None),
        )

    @classmethod
    def _get_logger(cls) -> Logger:
        """
        Retrieve the class-level logger instance.
        :return: The class-level logger instance used to debug and log
            information within the `EventLinker` class.
        """
        return cls.__logger

    @classmethod
    def get_event_name(cls, event: SubscribableEventType) -> str:
        """
        Determines the name of the event.
        :param event: The event to obtain the name for.
        :return: A string that represents the event name.
        :raises PyventusException: If the `event` argument is invalid
            or if the event is not supported.
        """
        # Validate the event argument
        if event is None:
            raise PyventusException("The 'event' argument cannot be None.")

        if event is Ellipsis:
            # If the event is Ellipsis, return its type name
            return type(event).__name__
        elif isinstance(event, str):
            if not event:
                raise PyventusException("String events cannot be empty.")
            # If the event is a non-empty string, return it as the event name
            return event
        elif isinstance(event, type):
            if not is_dataclass(event) and not issubclass(event, Exception):
                raise PyventusException("Type events must be either a dataclass or an exception.")
            # If the event is either a dataclass type or an exception type, return its type name
            return event.__name__
        else:
            # If the event is not supported, raise an exception
            raise PyventusException("Unsupported event")

    @classmethod
    def get_max_event_handlers(cls) -> int | None:
        """
        Retrieve the maximum number of event handlers allowed per event.
        :return: The maximum number of event handlers or `None` if there is no limit.
        """
        return cls.__max_event_handlers

    @classmethod
    def get_default_success_callback(cls) -> SuccessCallbackType | None:
        """
        Retrieve the default callback to be assigned as the success callback
        in the event handlers when no specific success callback is provided.
        :return: The default success callback or `None` if not set.
        """
        return cls.__default_success_callback

    @classmethod
    def get_default_failure_callback(cls) -> FailureCallbackType | None:
        """
        Retrieve the default callback to be assigned as the failure callback
        in the event handlers when no specific failure callback is provided.
        :return: The default failure callback or `None` if not set.
        """
        return cls.__default_failure_callback

    @classmethod
    def get_registry(cls) -> Mapping[str, List[EventHandler]]:
        """
        Retrieve the main registry mapping.
        :return: A mapping of event names to event handlers.
        """
        with cls.__thread_lock:
            return {event_name: list(event_handlers) for event_name, event_handlers in cls.__registry.items()}

    @classmethod
    def get_events(cls) -> List[str]:
        """
        Retrieve a list of all the registered events.
        :return: A list of event names.
        """
        with cls.__thread_lock:
            return list(cls.__registry.keys())

    @classmethod
    def get_event_handlers(cls) -> List[EventHandler]:
        """
        Retrieve a list of non-duplicated event handlers
        that have been registered across all events.
        :return: A list of event handlers.
        """
        with cls.__thread_lock:
            return list(
                {event_handler for event_handlers in cls.__registry.values() for event_handler in event_handlers}
            )

    @classmethod
    def get_events_by_event_handler(cls, event_handler: EventHandler) -> List[str]:
        """
        Retrieve a list of event names associated with the provided event handler.
        :param event_handler: The handler to retrieve the associated events for.
        :return: A list of event names.
        :raise PyventusException: If the `event_handler` argument is `None` or invalid.
        """
        # Validate the event_handler argument
        if event_handler is None:
            raise PyventusException("The 'event_handler' argument cannot be None.")
        if not isinstance(event_handler, EventHandler):
            raise PyventusException("The 'event_handler' argument must be an instance of the EventHandler class.")

        with cls.__thread_lock:
            return [
                event_name for event_name, event_handlers in cls.__registry.items() if event_handler in event_handlers
            ]

    @classmethod
    def get_event_handlers_by_events(cls, *events: SubscribableEventType) -> List[EventHandler]:
        """
        Retrieve a list of non-duplicated event handlers associated with the provided events.
        :param events: Events to retrieve the event handlers for.
        :return: A list of event handlers.
        :raise PyventusException: If the `events` argument is `None`, empty or unsupported.
        """
        # Validate the events argument
        if events is None or len(events) <= 0:
            raise PyventusException("The 'events' argument cannot be None or empty.")

        # Retrieve all unique event names
        event_names: Set[str] = {cls.get_event_name(event=event) for event in events}

        with cls.__thread_lock:
            return list(
                {event_handler for event_name in event_names for event_handler in cls.__registry.get(event_name, [])}
            )

    @classmethod
    def once(cls, *events: SubscribableEventType, force_async: bool = False) -> EventLinkageWrapper:
        """
        Decorator that allows you to conveniently subscribe callbacks to the provided events
        for a single invocation.

        This method can be used as either a decorator or a context manager. When used as a
        decorator, it automatically subscribes the decorated callback to the provided events.
        When used as a context manager with the `with` statement, it allows multiple callbacks
        to be associated with the provided events within the context block.

        :param events: The events to subscribe to.
        :param force_async: Determines whether to force all callbacks to run asynchronously.
            If `True`, synchronous callbacks will be converted to run asynchronously in a
            thread pool, using the `asyncio.to_thread` function. If `False`, callbacks
            will run synchronously or asynchronously as defined.
        :return: The decorator that wraps the callback.
        """
        return EventLinker.EventLinkageWrapper(*events, event_linker=cls, force_async=force_async, once=True)

    @classmethod
    def on(cls, *events: SubscribableEventType, force_async: bool = False) -> EventLinkageWrapper:
        """
        Decorator that allows you to conveniently subscribe callbacks to the provided events.

        This method can be used as either a decorator or a context manager. When used as a
        decorator, it automatically subscribes the decorated callback to the provided events.
        When used as a context manager with the `with` statement, it allows multiple callbacks
        to be associated with the provided events within the context block.

        :param events: The events to subscribe to.
        :param force_async: Determines whether to force all callbacks to run asynchronously.
            If `True`, synchronous callbacks will be converted to run asynchronously in a
            thread pool, using the `asyncio.to_thread` function. If `False`, callbacks
            will run synchronously or asynchronously as defined.
        :return: The decorator that wraps the callback.
        """
        return EventLinker.EventLinkageWrapper(*events, event_linker=cls, force_async=force_async, once=False)

    @classmethod
    def subscribe(
        cls,
        *events: SubscribableEventType,
        event_callback: EventCallbackType,
        success_callback: SuccessCallbackType | None = None,
        failure_callback: FailureCallbackType | None = None,
        force_async: bool = False,
        once: bool = False,
    ) -> EventHandler:
        """
        Subscribes callbacks to the provided events.
        :param events: The events to subscribe to.
        :param event_callback: The callback to be executed when the event occurs.
        :param success_callback: The callback to be executed when the event execution completes
            successfully.
        :param failure_callback: The callback to be executed when the event execution fails.
        :param force_async: Determines whether to force all callbacks to run asynchronously.
            If `True`, synchronous callbacks will be converted to run asynchronously in a
            thread pool, using the `asyncio.to_thread` function. If `False`, callbacks
            will run synchronously or asynchronously as defined.
        :param once: Specifies if the event handler is a one-time subscription.
        :return: The event handler object associated with the given events.
        """
        # Validate the events argument
        if events is None or len(events) <= 0:
            raise PyventusException("The 'events' argument cannot be None or empty.")

        # Retrieve all unique event names
        event_names: Set[str] = {cls.get_event_name(event=event) for event in events}

        # Acquire the lock to ensure exclusive access to the main registry
        with cls.__thread_lock:
            # Check if the maximum number of handlers property is set
            if cls.__max_event_handlers is not None:
                # For each event name, check if the maximum number of handlers for the event has been exceeded
                for event_name in event_names:
                    if len(cls.__registry.get(event_name, [])) >= cls.__max_event_handlers:
                        raise PyventusException(
                            f"The event '{event_name}' has exceeded the maximum number of handlers allowed. The "
                            f"'{get_callback_name(callback=event_callback)}'"
                            f" callback cannot be subscribed."
                        )

            # Create a new event handler
            event_handler: EventHandler = EventHandler(
                event_callback=event_callback,
                success_callback=success_callback if success_callback else cls.__default_success_callback,
                failure_callback=failure_callback if failure_callback else cls.__default_failure_callback,
                force_async=force_async,
                once=once,
            )

            # For each event name, register the event handler
            for event_name in event_names:
                # If the event name is not present in the main registry, create a new empty list for it
                if event_name not in cls.__registry:
                    cls.__registry[event_name] = []

                # Append the event handler to the list of handlers for the event
                cls.__registry[event_name].append(event_handler)

                # Log the subscription if debug is enabled
                if cls.__logger.debug_enabled:  # pragma: no cover
                    cls.__logger.debug(
                        action="Subscribed:",
                        msg=f"{event_handler} {StdOutColors.PURPLE}Event:{StdOutColors.DEFAULT} {event_name}",
                    )

        # Return the new event handler
        return event_handler

    @classmethod
    def unsubscribe(cls, *events: SubscribableEventType, event_handler: EventHandler) -> bool:
        """
        Unsubscribes an event handler from the provided events. If there are no more
        handlers for a particular event, that event is also removed from the registry.
        :param events: The events to unsubscribe from.
        :param event_handler: The event handler to unsubscribe.
        :return: `True` if the event handler associated with the events was found and
            removed, `False` otherwise.
        :raises PyventusException: If the `events` argument is `None`, empty, unsupported,
            or if the `event_handler` argument is `None`, invalid.
        """
        # Validate the events argument
        if events is None or len(events) <= 0:
            raise PyventusException("The 'events' argument cannot be None or empty.")

        # Validate the event_handler argument
        if event_handler is None:
            raise PyventusException("The 'event_handler' argument cannot be None.")
        if not isinstance(event_handler, EventHandler):
            raise PyventusException("The 'event_handler' argument must be an instance of the EventHandler class.")

        # Retrieve all unique event names
        event_names: Set[str] = {cls.get_event_name(event=event) for event in events}

        # A flag indicating whether the event handler was successfully removed
        deleted: bool = False

        # Obtain the lock to ensure exclusive access to the main registry
        with cls.__thread_lock:
            # For each event name, check and remove the event handler if found
            for event_name in event_names:
                # Get the list of event handlers for the event name, or an empty list if it doesn't exist
                event_handlers = cls.__registry.get(event_name, [])

                # Check if the event handler is present in the list of handlers for the event
                if event_handler in event_handlers:
                    # Remove the event handler from the list of handlers
                    event_handlers.remove(event_handler)
                    deleted = True

                    # If there are no more handlers for the event, remove the event name from the registry
                    if not event_handlers:
                        cls.__registry.pop(event_name)

                    # Log the unsubscription if debug is enabled
                    if cls.__logger.debug_enabled:  # pragma: no cover
                        cls.__logger.debug(
                            action="Unsubscribed:",
                            msg=f"{event_handler} {StdOutColors.PURPLE}Event:{StdOutColors.DEFAULT} {event_name}",
                        )

        # Return the flag indicating whether the event handler was deleted
        return deleted

    @classmethod
    def remove_event_handler(cls, event_handler: EventHandler) -> bool:
        """
        Removes an event handler from all subscribed events. If there are no more
        handlers for a particular event, that event is also removed from the registry.
        :param event_handler: The event handler to remove.
        :return: `True` if the event handler was found and removed, `False` otherwise.
        :raises PyventusException: If the `event_handler` argument is `None` or invalid.
        """
        # Validate the event_handler argument
        if event_handler is None:
            raise PyventusException("The 'event_handler' argument cannot be None.")
        if not isinstance(event_handler, EventHandler):
            raise PyventusException("The 'event_handler' argument must be an instance of the EventHandler class.")

        # A flag indicating if the event handler gets removed
        deleted: bool = False

        # Acquire the lock to ensure exclusive access to the main registry
        with cls.__thread_lock:
            # Iterate through each event and its associated handlers in the main registry
            for event_name in list(cls.__registry.keys()):
                # Get the list of event handlers for the event name, or an empty list if it doesn't exist
                event_handlers = cls.__registry.get(event_name, [])

                # Check if the event handler is present in the list of handlers for the event
                if event_handler in event_handlers:
                    # Remove the event handler from the list of handlers
                    event_handlers.remove(event_handler)
                    deleted = True

                    # If there are no more handlers for the event, remove the event from the registry
                    if not event_handlers:
                        cls.__registry.pop(event_name)

                    # Log the removal of the event handler if debug is enabled
                    if cls.__logger.debug_enabled:  # pragma: no cover
                        cls.__logger.debug(
                            action="Handler Removed:",
                            msg=f"{event_handler} {StdOutColors.PURPLE}Event:{StdOutColors.DEFAULT} {event_name}",
                        )

        # Return the flag indicating if the event handler was found and deleted
        return deleted

    @classmethod
    def remove_event(cls, event: SubscribableEventType) -> bool:
        """
        Removes an event from the registry, including all its event handler subscriptions.
        :param event: The event to remove.
        :return: `True` if the event was found and removed, `False` otherwise.
        """
        # Get the event name
        event_name: str = cls.get_event_name(event=event)

        # Acquire the lock to ensure exclusive access to the main registry
        with cls.__thread_lock:
            # Check if the event name is present in the main registry
            if event_name in cls.__registry:
                # Remove the event from the registry
                cls.__registry.pop(event_name)

                # Log the removal of the event if debug is enabled
                if cls.__logger.debug_enabled:  # pragma: no cover
                    cls.__logger.debug(action="Event Removed:", msg=f"{event_name}")

                # Return True to indicate successful removal
                return True

        return False

    @classmethod
    def remove_all(cls) -> bool:
        """
        Removes all events and their associated event handlers from the registry.
        :return: `True` if the events were found and removed, `False` otherwise.
        """
        # Acquire the lock to ensure exclusive access to the main registry
        with cls.__thread_lock:
            if cls.__registry:
                # Clear the main registry
                cls.__registry.clear()

                # Log a debug message if debug is enabled
                if cls.__logger.debug_enabled:  # pragma: no cover
                    cls.__logger.debug(msg="All events and handlers were successfully removed.")

                return True
            else:
                # Log a debug message if debug is enabled
                if cls.__logger.debug_enabled:  # pragma: no cover
                    cls.__logger.debug(msg="The event registry is already empty.")

                return False
