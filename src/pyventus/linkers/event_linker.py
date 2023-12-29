from abc import ABC
from itertools import chain
from sys import gettrace
from threading import Lock
from types import TracebackType
from typing import TypeAlias, Callable, Mapping, Tuple, Dict, List, Type, Set, Any, final

from ..core.constants import StdOutColors
from ..core.exceptions import PyventusException
from ..core.loggers import Logger
from ..events import Event
from ..handlers import EventHandler, EventCallbackType, SuccessCallbackType, FailureCallbackType

SubscribableEventType: TypeAlias = Type[Event] | Type[Exception] | str
""" A type alias representing the supported event types for subscription. """


class EventLinker(ABC):
    """
    A base class that acts as a global registry for linking events with their associated event
    handlers.

    The `EventLinker` class provides a centralized mechanism for managing event subscriptions,
    unsubscriptions, and retrieval of events and their associated event handlers. It acts as a
    global registry, ensuring that events and their handlers are organized and easily accessible.

    The `EventLinker` class can be subclassed to create specific namespaces or contexts for
    managing events and event handlers separately. By subclassing the `EventLinker`, users can
    organize event subscriptions and handlers within different scopes, providing modularity and
    flexibility in event management. Subclassing also allows users to configure settings of the
    `EventLinker` to suit their specific use cases.

    **Thread-Safe:** The `EventLinker` has been implemented with thread safety in mind. All of its
    methods synchronize access to prevent race conditions when managing events and event handlers
    across multiple threads. This ensures that concurrent operations on the `EventLinker` are
    properly synchronized, avoiding data inconsistencies and race conditions.

    For more information and code examples, please refer to the `EventLinker` tutorials at:
    [https://mdapena.github.io/pyventus/tutorials/event-linker/](https://mdapena.github.io/pyventus/tutorials/event-linker/).
    """

    @final
    class EventLinkageWrapper:
        """
        A class that serves as a wrapper for event linking operations, providing a simplified
        interface for subscribing events and associating callbacks.

        This class can be used as either a decorator or context manager. As a decorator, it
        automatically subscribes the decorated callback to the specified events.

        When used as a context manager via the `with` statement, it allows multiple callbacks
        to be associated with events within the context block.

        Also, this class is not intended to be subclassed or created manually. It is used
        internally to serves as a wrapper for event linking operation.
        """

        @property
        def on_event(self) -> Callable[[EventCallbackType], EventCallbackType]:  # type: ignore[type-arg]
            """
            Decorator that sets the main callback for the event. This callback will be invoked
            when the associated event occurs.
            :return: The decorated callback.
            """

            def _wrapper(callback: EventCallbackType) -> EventCallbackType:  # type: ignore[type-arg]
                self._event_callback = callback
                return callback

            return _wrapper

        @property
        def on_success(self) -> Callable[[SuccessCallbackType], SuccessCallbackType]:
            """
            Decorator that sets the success callback. This callback will be invoked when the
            event execution completes successfully.
            :return: The decorated callback.
            """

            def _wrapper(callback: SuccessCallbackType) -> SuccessCallbackType:
                self._success_callback = callback
                return callback

            return _wrapper

        @property
        def on_failure(self) -> Callable[[FailureCallbackType], FailureCallbackType]:
            """
            Decorator that sets the failure callback. This callback will be invoked when the
            event execution fails.
            :return: The decorated callback.
            """

            def _wrapper(callback: FailureCallbackType) -> FailureCallbackType:
                self._failure_callback = callback
                return callback

            return _wrapper

        def __init__(self, *events: SubscribableEventType, event_linker: Type["EventLinker"], once: bool):
            """
            Initializes the wrapper instance.
            :param events: The events to link/subscribe to.
            :param event_linker: The event linker type for associating events with callbacks.
            :param once: Whether the callback is a one-time subscription.
            """
            self._events: Tuple[SubscribableEventType, ...] = events
            self._event_linker: Type[EventLinker] = event_linker
            self._once: bool = once

            self._event_callback: EventCallbackType | None = None  # type: ignore[type-arg, no-redef, assignment]
            self._success_callback: SuccessCallbackType | None = None  # type: ignore[no-redef, assignment]
            self._failure_callback: FailureCallbackType | None = None  # type: ignore[no-redef, assignment]

        def __call__(self, callback: EventCallbackType) -> EventCallbackType:  # type: ignore[type-arg]
            """
            Decorates a callback to subscribe it to the specified events.
            :param callback: The callback to associate.
            :return: The decorated callback.
            """
            self._event_callback = callback
            self._event_linker.subscribe(
                *self._events,
                event_callback=self._event_callback,
                success_callback=None,
                failure_callback=None,
                once=self._once,
            )
            del self
            return callback

        def __enter__(self) -> "EventLinker.EventLinkageWrapper":
            """
            Enters the linkage context block, allowing multiple callbacks to be associated
            with events within the block.
            :return: The context manager object
            """
            return self

        def __exit__(
            self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
        ) -> None:
            """
            Exits the linkage context manager, subscribing any callbacks associated within the
            block to the specified events. Also performs any cleanup.
            :param exc_type: The type of the exception raised, if any.
            :param exc_val: The exception object raised, if any.
            :param exc_tb: The traceback information, if any.
            :return: None
            """
            self._event_linker.subscribe(
                *self._events,
                event_callback=self._event_callback,
                success_callback=self._success_callback,
                failure_callback=self._failure_callback,
                once=self._once,
            )
            del self

    __event_registry: Dict[str, List[EventHandler]] = {}
    """ 
    A dictionary that serves as a container for storing events and their respective event handlers.
    The keys represent event names, and the values are lists of `EventHandler` objects. 
    """

    __max_event_handlers: int | None = None
    """ The maximum number of `EventHandlers` allowed per event, or None if no limit. """

    __default_success_callback: SuccessCallbackType | None = None
    """ 
    Represents the default success callback function that will be assigned to event handlers in the
    absence of a specific success callback. This callback will be executed upon successful completion
    of the event execution in each event handler.
    """

    __default_failure_callback: FailureCallbackType | None = None
    """
    Represents the default failure callback function that will be assigned to event handlers in the 
    absence of a specific failure callback. This callback will be executed when the event execution
    fails in each event handler.
    """

    __thread_lock: Lock = Lock()
    """
    A `threading.Lock` object used for thread synchronization when accessing and modifying the event
    registry to ensure thread safety. It prevents multiple threads from accessing or modifying the 
    registry simultaneously.
    """

    __logger: Logger = Logger(name="EventLinker", debug=bool(gettrace() is not None))
    """
    An instance of the logger used for logging events and debugging information. The debug mode
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
        Custom `__init_subclass__` method called when a subclass is created.

        This method initializes the subclass by setting up the event registry and thread
        lock. It also allows specifying the maximum number of event handlers per event.

        :param max_event_handlers: The maximum number of event handlers allowed per event,
            or `None` if no limit.
        :param default_success_callback: The default callback to be assigned as the success
            callback in the event handlers when no specific success callback is provided.
        :param default_failure_callback: The default callback to be assigned as the failure
            callback in the event handlers when no specific failure callback is provided.
        :param debug: Specifies the debug mode for the subclass logger. If `None`,
            it is determined based on the execution environment.
        :param kwargs: The keyword arguments to pass to the superclass
            `__init_subclass__` method.
        :raises PyventusException: If `max_event_handlers` is less than 1.
        :return: Any
        """
        # Call the parent class' __init_subclass__ method
        super().__init_subclass__(**kwargs)

        # Initialize the event registry dictionary
        cls.__event_registry = {}

        # Create a lock object for thread synchronization
        cls.__thread_lock = Lock()

        # Validate the max_event_handlers argument
        if max_event_handlers is not None and max_event_handlers < 1:
            raise PyventusException("The 'max_event_handlers' argument must be greater than or equal to 1.")

        # Set the maximum number of event handlers per event
        cls.__max_event_handlers = max_event_handlers

        # Validate the default success callback, if any
        if default_success_callback:
            EventHandler.validate_callback(callback=default_success_callback)

        # Set the default success callback
        cls.__default_success_callback = default_success_callback

        # Validate the default failure callback, if any
        if default_failure_callback:
            EventHandler.validate_callback(callback=default_failure_callback)

        # Set the default failure callback
        cls.__default_failure_callback = default_failure_callback

        # Set up the logger for the subclass
        cls.__logger = Logger(
            name=cls.__name__,
            debug=debug if debug is not None else bool(gettrace() is not None),
        )

    @classmethod
    def get_event_registry(cls) -> Mapping[str, List[EventHandler]]:
        """
        Retrieves the event registry mapping.
        :return: A mapping of event names to event handlers.
        """
        with cls.__thread_lock:
            return {event: list(event_handlers) for event, event_handlers in cls.__event_registry.items()}

    @classmethod
    def get_events(cls) -> List[str]:
        """
        Returns a list of all the registered event names.
        :return: A list of event names.
        """
        with cls.__thread_lock:
            return list(cls.__event_registry.keys())

    @classmethod
    def get_event_handlers(cls) -> List[EventHandler]:
        """
        Retrieves a list of non-duplicated event handlers
        who have been registered across all events.
        :return: A list of event handlers.
        """
        with cls.__thread_lock:
            return list(set(chain(*cls.__event_registry.values())))

    @classmethod
    def get_max_event_handlers(cls) -> None | int:
        """
        Retrieves the maximum number of handlers allowed per event.
        :return: The maximum number of handlers or None if there is no limit.
        """
        return cls.__max_event_handlers

    @classmethod
    def get_default_success_callback(cls) -> SuccessCallbackType | None:
        """
        Retrieves the default callback to be assigned as the success callback in
            the event handlers when no specific success callback is provided.
        :return: The default callback to be assigned as the success callback in
            the event handlers when no specific success callback is provided.
        """
        return cls.__default_success_callback

    @classmethod
    def get_default_failure_callback(cls) -> FailureCallbackType | None:
        """
        Retrieves the default callback to be assigned as the failure callback
            in the event handlers when no specific failure callback is provided.
        :return: The default callback to be assigned as the failure callback
            in the event handlers when no specific failure callback is provided.
        """
        return cls.__default_failure_callback

    @classmethod
    def _get_logger(cls) -> Logger:
        """
        Returns the class-level logger instance.
        :return: The class-level logger instance used for logging events and
            debugging information.
        """
        return cls.__logger

    @classmethod
    def _get_event_key(cls, event: SubscribableEventType) -> str:
        """
        Determines the event string key based on the given event.
        :param event: The event to obtain the key for.
        :return: The event string key.
        :raises PyventusException: If the `event` argument is None or if
            the event type is not supported.
        """
        # Validate the event argument
        if event is None:
            raise PyventusException("The 'event' argument cannot be None.")

        if isinstance(event, str):
            # If the event is already a string, return it as the key
            return event
        elif issubclass(event, (Event, Exception)):
            # If the event is a subclass of Event or Exception, return its name as the key
            return event.__name__
        else:
            # If the event type is not supported, raise an exception
            raise PyventusException("Unsupported event type")

    @classmethod
    def get_events_by_handler(cls, event_handler: EventHandler) -> List[str]:
        """
        Retrieves a list of event names associated with the specified event handler.
        :param event_handler: The handler to retrieve the associated events for.
        :return: A list of event names.
        :raise PyventusException: If the `event_handler` argument is None.
        """
        # Validate the event_handler argument
        if event_handler is None:
            raise PyventusException("The 'event_handler' argument cannot be None.")

        with cls.__thread_lock:
            return [
                event_key
                for event_key, event_handlers in cls.__event_registry.items()
                if event_handler in event_handlers
            ]

    @classmethod
    def get_handlers_by_events(cls, *events: SubscribableEventType) -> List[EventHandler]:
        """
        Retrieves a list of non-duplicated event handlers associated with the specified events.
        :param events: Events to retrieve the handlers for.
        :return: A list of event handlers.
        :raise PyventusException: If the `events` argument is None, empty or unsupported.
        """
        # Validate the events argument
        if events is None or len(events) <= 0:
            raise PyventusException("The 'events' argument cannot be None or empty.")

        # Retrieve all unique event keys
        event_keys: Set[str] = set([cls._get_event_key(event=event) for event in events])

        with cls.__thread_lock:
            return list(
                {event_handler for event_key in event_keys for event_handler in cls.__event_registry.get(event_key, [])}
            )

    @classmethod
    def once(cls, *events: SubscribableEventType) -> EventLinkageWrapper:
        """
        Decorator that subscribes a callback to the specified events to be invoked only once.
        This decorator is used to conveniently subscribe a callback as a one-time handler.
        :param events: The events to subscribe to.
        :return: The decorator that wraps the callback.
        """
        return EventLinker.EventLinkageWrapper(*events, event_linker=cls, once=True)

    @classmethod
    def on(cls, *events: SubscribableEventType) -> EventLinkageWrapper:
        """
        Decorator that subscribes a callback to the specified events.
        :param events: The events to subscribe to.
        :return: The decorator that wraps the callback.
        """
        return EventLinker.EventLinkageWrapper(*events, event_linker=cls, once=False)

    @classmethod
    def subscribe(
        cls,
        *events: SubscribableEventType,
        event_callback: EventCallbackType,  # type: ignore[type-arg]
        success_callback: SuccessCallbackType | None = None,
        failure_callback: FailureCallbackType | None = None,
        once: bool = False,
    ) -> EventHandler:
        """
        Subscribes callbacks to the specified events.
        :param events: The events to subscribe to.
        :param event_callback: The callback to be executed when the event occurs.
        :param success_callback: The callback to be executed when the event execution completes
            successfully.
        :param failure_callback: The callback to be executed when the event execution fails.
        :param once: Specifies if the callback is a one-time subscription. If set to `True`,
            the handler will be invoked once when the event occurs and then automatically unsubscribed.
            If set to `False` (default), the handler can be invoked multiple times until explicitly
            unsubscribed.
        :return: The event handler object associated with the events.
        :raises PyventusException: If the maximum number of handlers for an event has been exceeded
            or if the `events` argument is None, empty or unsupported.
        """
        # Validate the events argument
        if events is None or len(events) <= 0:
            raise PyventusException("The 'events' argument cannot be None or empty.")

        # Retrieve all unique event keys
        event_keys: Set[str] = set([cls._get_event_key(event=event) for event in events])

        # Acquire the lock to ensure exclusive access to the event registry
        with cls.__thread_lock:
            # Check if the maximum number of handlers property is set
            if cls.__max_event_handlers is not None:
                # For each event key, check if the maximum number of handlers for the event has been exceeded
                for event_key in event_keys:
                    if len(cls.__event_registry.get(event_key, [])) >= cls.__max_event_handlers:
                        raise PyventusException(
                            f"The event '{event_key}' has exceeded the maximum number of handlers allowed. The "
                            f"'{event_callback.__name__ if hasattr(event_callback, '__name__') else event_callback}'"
                            f" callback cannot be added."
                        )

            # Create a new event handler
            event_handler: EventHandler = EventHandler(
                event_callback=event_callback,
                success_callback=success_callback if success_callback else cls.__default_success_callback,
                failure_callback=failure_callback if failure_callback else cls.__default_failure_callback,
                once=once,
            )

            # For each event key, register the event handler
            for event_key in event_keys:
                # If the event key is not present in the event registry, create a new empty list for it
                if event_key not in cls.__event_registry:
                    cls.__event_registry[event_key] = []

                # Append the event handler to the list of handlers for the event
                cls.__event_registry[event_key].append(event_handler)

                # Log the subscription if debug is enabled
                if cls.__logger.debug_enabled:  # pragma: no cover
                    cls.__logger.debug(
                        action="Subscribed:",
                        msg=f"[{event_handler}] {StdOutColors.PURPLE}Event:{StdOutColors.DEFAULT} [{event_key}]",
                    )

        # Return the new event handler
        return event_handler

    @classmethod
    def unsubscribe(cls, *events: SubscribableEventType, event_handler: EventHandler) -> bool:
        """
        Unsubscribes an event handler from the specified events. The method removes the event
        handler from the event registry and, if there are no more handlers for a particular
        event, removes that event from the registry as well.
        :param events: The events to unsubscribe from.
        :param event_handler: The event handler to unsubscribe.
        :return: `True` if the event handler associated with the events was found and removed,
            `False` otherwise.
        :raises PyventusException: If the `events` argument is None, empty, unsupported or if
            the `event_handler` argument is None.
        """
        # Validate the events argument
        if events is None or len(events) <= 0:
            raise PyventusException("The 'events' argument cannot be None or empty.")

        # Validate the event_handler argument
        if event_handler is None:
            raise PyventusException("The 'event_handler' argument cannot be None.")

        # Retrieve all unique event keys
        event_keys: Set[str] = set([cls._get_event_key(event=event) for event in events])

        # Flag indicating whether the event handler was successfully removed
        deleted: bool = False

        # Obtain the lock to ensure exclusive access to the event registry
        with cls.__thread_lock:
            # For each event key, check and remove the event handler if found
            for event_key in event_keys:
                # Get the list of event handlers for the event key, or an empty list if it doesn't exist
                event_handlers = cls.__event_registry.get(event_key, [])

                # Check if the event handler is present in the list of handlers for the event
                if event_handler in event_handlers:
                    # Remove the event handler from the list of handlers
                    event_handlers.remove(event_handler)
                    deleted = True

                    # If there are no more handlers for the event, remove the event key from the registry
                    if not event_handlers:
                        cls.__event_registry.pop(event_key)

                    # Log the unsubscription if debug is enabled
                    if cls.__logger.debug_enabled:  # pragma: no cover
                        cls.__logger.debug(
                            action="Unsubscribed",
                            msg=f"[{event_handler}] {StdOutColors.PURPLE}Event:{StdOutColors.DEFAULT} [{event_key}]",
                        )

        # Return the flag indicating whether the event handler was deleted
        return deleted

    @classmethod
    def remove_event_handler(cls, event_handler: EventHandler) -> bool:
        """
        Removes an event handler from all subscribed events. If there are no more
        handlers for a particular event, that event is removed from the registry.
        :param event_handler: The event handler to remove.
        :return: `True` if the event handler was found and removed, `False` otherwise.
        :raises PyventusException: If the `event_handler` argument is None.
        """
        # Validate the event_handler argument
        if event_handler is None:
            raise PyventusException("The 'event_handler' argument cannot be None.")

        # A flag indicating if the event handler gets removed
        deleted: bool = False

        # Acquire the lock to ensure exclusive access to the event registry
        with cls.__thread_lock:
            # Iterate through each event and its associated handlers in the event registry
            for event_key in list(cls.__event_registry.keys()):
                # Get the list of event handlers for the event key, or an empty list if it doesn't exist
                event_handlers = cls.__event_registry.get(event_key, [])

                # Check if the event handler is present in the list of handlers for the event
                if event_handler in event_handlers:
                    # Remove the event handler from the list of handlers
                    event_handlers.remove(event_handler)
                    deleted = True

                    # If there are no more handlers for the event, remove the event from the registry
                    if not event_handlers:
                        cls.__event_registry.pop(event_key)

                    # Log the removal of the event handler if debug is enabled
                    if cls.__logger.debug_enabled:  # pragma: no cover
                        cls.__logger.debug(
                            action="Handler Removed:",
                            msg=f"[{event_handler}] {StdOutColors.PURPLE}Event:{StdOutColors.DEFAULT} [{event_key}]",
                        )

        # Return the flag indicating if the event handler was found and deleted
        return deleted

    @classmethod
    def remove_event(cls, event: SubscribableEventType) -> bool:
        """
        Removes an event and all associated event handlers.
        :param event: The event to remove.
        :return: `True` if the event was found and removed, `False` otherwise.
        """
        # Get the event key
        event_key: str = cls._get_event_key(event=event)

        # Acquire the lock to ensure exclusive access to the event registry
        with cls.__thread_lock:
            # Check if the event key is present in the event registry
            if event_key in cls.__event_registry:
                # Remove the event from the registry
                cls.__event_registry.pop(event_key)

                # Log the removal of the event if debug is enabled
                if cls.__logger.debug_enabled:  # pragma: no cover
                    cls.__logger.debug(action="Event Removed:", msg=f"[{event_key}]")

                # Return True to indicate successful removal
                return True

        return False

    @classmethod
    def remove_all(cls) -> bool:
        """
        Removes all events and event handlers.
        :return: `True` if the events were found and removed, `False` otherwise.
        """
        # Acquire the lock to ensure exclusive access to the event registry
        with cls.__thread_lock:
            # Clear the event registry by assigning an empty dictionary
            cls.__event_registry = {}

        # Log a debug message if debug is enabled
        if cls.__logger.debug_enabled:  # pragma: no cover
            cls.__logger.debug(msg="All events and handlers were successfully removed")

        return True
