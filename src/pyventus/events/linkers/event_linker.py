from dataclasses import is_dataclass
from sys import gettrace
from threading import Lock
from types import TracebackType, EllipsisType
from typing import TypeAlias, Mapping, Tuple, Dict, List, Type, Set, final

from ..subscribers import EventSubscriber, EventCallbackType, SuccessCallbackType, FailureCallbackType
from ...core.constants import StdOutColors
from ...core.exceptions import PyventusException
from ...core.loggers import Logger
from ...core.subscriptions import SubscriptionContext
from ...core.utils import validate_callable, get_callable_name

SubscribableEventType: TypeAlias = str | Type[Exception] | Type[object] | EllipsisType
"""A type alias representing the supported event types for subscription."""


class EventLinker:
    """
    A base class that serves as a global registry for linking events and their responses. It
    provides a centralized mechanism for managing event subscriptions, unsubscriptions, and
    retrieval of events along with their associated event subscribers.

    **Notes:**

    -   The `EventLinker` can be subclassed to create specific namespaces or contexts for managing
        event subscriptions within different scopes. This design offers modularity and flexibility
        in event management. Subclassing also allows users to configure settings of the `EventLinker`
        to suit their specific use cases.

    -   The `EventLinker` is designed with *thread safety* in mind. All methods synchronize access
        to prevent race conditions when managing events and event subscribers across multiple threads. This
        ensures that concurrent operations on the `EventLinker` are properly synchronized, avoiding
        data inconsistencies.

    ---
    Read more in the
    [Pyventus docs for Event Linker](https://mdapena.github.io/pyventus/tutorials/events/event-linker/).
    """

    @final
    class EventSubscriptionContext(SubscriptionContext[Type["EventLinker"], EventSubscriber]):
        """
        A context manager for event subscriptions. This class establishes a context block for
        the step-by-step definition of event responses prior to the actual subscription, which
        occurs immediately upon exiting the context block.

        **Notes:**

        -   This class can be used as either a decorator or a context manager. When used as a
            decorator, it automatically subscribes the decorated callback to the specified events.
            When used as a context manager with the `with` statement, it allows multiple callbacks
            to be associated with the specified events within the context block.

        -   This class is not intended to be subclassed or manually instantiated.
        """

        # Attributes for the EventSubscriptionContext
        __slots__ = (
            "__events",
            "__event_callback",
            "__success_callback",
            "__failure_callback",
            "__force_async",
            "__once",
        )

        def __init__(
            self,
            *events: SubscribableEventType,
            event_linker: Type["EventLinker"],
            force_async: bool,
            once: bool,
        ) -> None:
            """
            Initialize an instance of `EventSubscriptionContext`.
            :param events: The events to subscribe/link to.
            :param event_linker: The type of event linker used for the actual subscription.
            :param force_async: Determines whether to force all callbacks to run asynchronously.
            :param once: Specifies if the event subscriber will be a one-time subscription.
            """
            # Initialize the base SubscriptionContext class with the given source
            super().__init__(source=event_linker)

            # Initialize variables
            self.__events: Tuple[SubscribableEventType, ...] = events
            self.__event_callback: EventCallbackType | None = None
            self.__success_callback: SuccessCallbackType | None = None
            self.__failure_callback: FailureCallbackType | None = None
            self.__force_async: bool = force_async
            self.__once: bool = once

        def __call__(self, callback: EventCallbackType) -> EventCallbackType:
            """
            Subscribes the decorated callback to the specified events.
            :param callback: The callback to be executed when the event occurs.
            :return: The decorated callback.
            """
            # Subscribe the decorated callback to the specified events
            # and store the returned subscriber for future reference.
            self._set_subscriber(
                subscriber=self.source.subscribe(
                    *self.__events,
                    event_callback=callback,
                    success_callback=None,
                    failure_callback=None,
                    force_async=self.__force_async,
                    once=self.__once,
                )
            )

            # Remove context-specific attributes.
            del self.__events
            del self.__event_callback, self.__success_callback, self.__failure_callback
            del self.__force_async, self.__once

            return callback

        def __exit__(
            self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
        ) -> None:
            # Check if the event callback has been set
            if self.__event_callback is None:
                raise PyventusException("The event callback has not been set.")

            # Subscribe the defined callbacks to the specified events
            # and store the returned subscriber for future reference.
            self.source.subscribe(
                *self.__events,
                event_callback=self.__event_callback,
                success_callback=self.__success_callback,
                failure_callback=self.__failure_callback,
                force_async=self.__force_async,
                once=self.__once,
            )

            # Remove context-specific attributes.
            del self.__events
            del self.__event_callback, self.__success_callback, self.__failure_callback
            del self.__force_async, self.__once

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
            :param callback: The callback to be executed when the event response completes successfully.
            :return: The decorated callback.
            """
            self.__success_callback = callback
            return callback

        def on_failure(self, callback: FailureCallbackType) -> FailureCallbackType:
            """
            Decorator that sets the failure callback.
            :param callback: The callback to be executed when the event response fails.
            :return: The decorated callback.
            """
            self.__failure_callback = callback
            return callback

    __registry: Dict[str, List[EventSubscriber]] = {}
    """ 
    A dictionary that serves as a container for storing events and their associated event 
    subscribers. The keys represent registered event names, and the values are lists of event
    subscribers associated with each event.
    """

    __max_event_subscribers: int | None = None
    """The maximum number of event subscribers allowed per event, or `None` if there is no limit."""

    __default_success_callback: SuccessCallbackType | None = None
    """ 
    Represents the default success callback that will be assigned to event subscribers in the 
    absence of a specific success callback. This callback will be executed upon successful 
    completion of the event response in each event subscriber.
    """

    __default_failure_callback: FailureCallbackType | None = None
    """
    Represents the default failure callback that will be assigned to event subscribers in the
    absence of a specific failure callback. This callback will be executed when the event 
    response fails in each event subscriber.
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
        max_event_subscribers: int | None = None,
        default_success_callback: SuccessCallbackType | None = None,
        default_failure_callback: FailureCallbackType | None = None,
        debug: bool | None = None,
    ) -> None:
        """
        Initialize a subclass of `EventLinker`.

        By default, this method sets up the main registry and the thread lock object, but
        it can also be used to configure specific settings of the `EventLinker` subclass.

        :param max_event_subscribers: The maximum number of event subscribers allowed per
            event, or `None` if there is no limit.
        :param default_success_callback: The default callback to assign as the success
            callback in the event subscribers when no specific success callback is provided.
        :param default_failure_callback: The default callback to assign as the failure
            callback in the event subscribers when no specific failure callback is provided.
        :param debug: Specifies the debug mode for the subclass logger. If `None`,
            it is determined based on the execution environment.
        :raises PyventusException: If `max_event_subscribers` is less than 1 or
            if the provided callbacks are invalid.
        :return: None
        """
        # Initialize the main registry
        cls.__registry = {}

        # Create a lock object for thread synchronization
        cls.__thread_lock = Lock()

        # Validate the max_event_subscribers argument
        if max_event_subscribers is not None and max_event_subscribers < 1:
            raise PyventusException("The 'max_event_subscribers' argument must be greater than or equal to 1.")

        # Set the maximum number of event subscribers per event
        cls.__max_event_subscribers = max_event_subscribers

        # Validate the default success callback, if any
        if default_success_callback is not None:
            validate_callable(default_success_callback)

        # Set the default success callback
        cls.__default_success_callback = default_success_callback

        # Validate the default failure callback, if any
        if default_failure_callback is not None:
            validate_callable(default_failure_callback)

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
    def __remove_event_subscriber_from_events(
        cls, *events: SubscribableEventType, event_subscriber: EventSubscriber
    ) -> None:
        """
        Remove the specified event subscriber from the given events. If there are no more
        subscribers for a particular event, that event is also removed from the registry.
        :param events: The events from which to remove the subscriber.
        :param event_subscriber: The event subscriber to remove.
        :return: None
        :raises PyventusException: If the `events` argument is `None`, empty, unsupported,
            or if the `event_subscriber` argument is `None`, invalid.
        """
        # Validate the events argument
        if events is None or len(events) <= 0:
            raise PyventusException("The 'events' argument cannot be None or empty.")

        # Validate the event_subscriber argument
        if event_subscriber is None:
            raise PyventusException("The 'event_subscriber' argument cannot be None.")
        if not isinstance(event_subscriber, EventSubscriber):
            raise PyventusException("The 'event_subscriber' argument must be an instance of the EventSubscriber class.")

        # Retrieve all unique event names
        event_names: Set[str] = {cls.get_event_name(event=event) for event in events}

        # Obtain the lock to ensure exclusive access to the main registry
        with cls.__thread_lock:
            # For each event name, check and remove the event subscriber if found
            for event_name in event_names:
                # Skip if the event name is not found in the registry
                if event_name not in cls.__registry:
                    continue

                # Get the list of event subscribers for the current event name
                event_subscribers = cls.__registry[event_name]

                # Check if the event subscriber is present
                if event_subscriber in event_subscribers:
                    # Remove the event subscriber
                    event_subscribers.remove(event_subscriber)

                    # If there are no more subscribers for the event, remove the event
                    if not event_subscribers:
                        cls.__registry.pop(event_name)

                    # Log the removal of the subscriber from the event if debug is enabled.
                    if cls.__logger.debug_enabled:  # pragma: no cover
                        cls.__logger.debug(
                            action="Event Subscriber Removed:",
                            msg=f"{event_subscriber} {StdOutColors.PURPLE}Event:{StdOutColors.DEFAULT} {event_name}",
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
    def get_max_event_subscribers(cls) -> int | None:
        """
        Retrieve the maximum number of event subscribers allowed per event.
        :return: The maximum number of event subscribers or `None` if there is no limit.
        """
        return cls.__max_event_subscribers

    @classmethod
    def get_default_success_callback(cls) -> SuccessCallbackType | None:
        """
        Retrieve the default callback to be assigned as the success callback
        in the event subscribers when no specific success callback is provided.
        :return: The default success callback or `None` if not set.
        """
        return cls.__default_success_callback

    @classmethod
    def get_default_failure_callback(cls) -> FailureCallbackType | None:
        """
        Retrieve the default callback to be assigned as the failure callback
        in the event subscribers when no specific failure callback is provided.
        :return: The default failure callback or `None` if not set.
        """
        return cls.__default_failure_callback

    @classmethod
    def get_registry(cls) -> Mapping[str, List[EventSubscriber]]:
        """
        Retrieve the main registry mapping.
        :return: A mapping of event names to event subscribers.
        """
        with cls.__thread_lock:
            return {event_name: event_subscribers.copy() for event_name, event_subscribers in cls.__registry.items()}

    @classmethod
    def get_events(cls) -> List[str]:
        """
        Retrieve a list of all the registered events.
        :return: A list of event names.
        """
        with cls.__thread_lock:
            return list(cls.__registry.keys())

    @classmethod
    def get_event_subscribers(cls) -> List[EventSubscriber]:
        """
        Retrieve a list of non-duplicated event subscribers
        that have been registered across all events.
        :return: A list of event subscribers.
        """
        with cls.__thread_lock:
            return list(
                {
                    event_subscriber
                    for event_subscribers in cls.__registry.values()
                    for event_subscriber in event_subscribers
                }
            )

    @classmethod
    def get_events_by_event_subscriber(cls, event_subscriber: EventSubscriber) -> List[str]:
        """
        Retrieve a list of event names associated with the given event subscriber.
        :param event_subscriber: The event subscriber to retrieve the associated events for.
        :return: A list of event names.
        :raise PyventusException: If the `event_subscriber` argument is `None` or invalid.
        """
        # Validate the event_subscriber argument
        if event_subscriber is None:
            raise PyventusException("The 'event_subscriber' argument cannot be None.")
        if not isinstance(event_subscriber, EventSubscriber):
            raise PyventusException("The 'event_subscriber' argument must be an instance of the EventSubscriber class.")

        with cls.__thread_lock:
            return [
                event_name
                for event_name, event_subscribers in cls.__registry.items()
                if event_subscriber in event_subscribers
            ]

    @classmethod
    def get_event_subscribers_by_events(cls, *events: SubscribableEventType) -> List[EventSubscriber]:
        """
        Retrieve a list of non-duplicated event subscribers associated with the specified events.
        :param events: Events to retrieve the event subscribers for.
        :return: A list of event subscribers.
        :raise PyventusException: If the `events` argument is `None`, empty or unsupported.
        """
        # Validate the events argument
        if events is None or len(events) <= 0:
            raise PyventusException("The 'events' argument cannot be None or empty.")

        # Retrieve all unique event names
        event_names: Set[str] = {cls.get_event_name(event=event) for event in events}

        with cls.__thread_lock:
            return list(
                {
                    event_subscriber
                    for event_name in event_names
                    for event_subscriber in cls.__registry.get(event_name, [])
                }
            )

    @classmethod
    def once(cls, *events: SubscribableEventType, force_async: bool = False) -> EventSubscriptionContext:
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
        :return: A `EventSubscriptionContext` instance.
        """
        return EventLinker.EventSubscriptionContext(*events, event_linker=cls, force_async=force_async, once=True)

    @classmethod
    def on(cls, *events: SubscribableEventType, force_async: bool = False) -> EventSubscriptionContext:
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
        :return: A `EventSubscriptionContext` instance.
        """
        return EventLinker.EventSubscriptionContext(*events, event_linker=cls, force_async=force_async, once=False)

    @classmethod
    def subscribe(
        cls,
        *events: SubscribableEventType,
        event_callback: EventCallbackType,
        success_callback: SuccessCallbackType | None = None,
        failure_callback: FailureCallbackType | None = None,
        force_async: bool = False,
        once: bool = False,
    ) -> EventSubscriber:
        """
        Subscribes the specified callbacks to the given events.
        :param events: The events to subscribe to.
        :param event_callback: The callback to be executed when the event occurs.
        :param success_callback: The callback to be executed when the event response completes successfully.
        :param failure_callback: The callback to be executed when the event response fails.
        :param force_async: Determines whether to force all callbacks to run asynchronously.
            If `True`, synchronous callbacks will be converted to run asynchronously in a
            thread pool, using the `asyncio.to_thread` function. If `False`, callbacks
            will run synchronously or asynchronously as defined.
        :param once: Specifies if the event subscriber will be a one-time subscription.
        :return: The event subscriber associated with the given events.
        """
        # Validate the events argument
        if events is None or len(events) <= 0:
            raise PyventusException("The 'events' argument cannot be None or empty.")

        # Retrieve all unique event names
        event_names: Set[str] = {cls.get_event_name(event=event) for event in events}

        # Acquire the lock to ensure exclusive access to the main registry
        with cls.__thread_lock:
            # Check if the maximum number of event subscribers is set
            if cls.__max_event_subscribers is not None:
                # For each event name, check if the maximum number of event subscribers for the event has been exceeded
                for event_name in event_names:
                    if len(cls.__registry.get(event_name, [])) >= cls.__max_event_subscribers:
                        raise PyventusException(
                            f"The event '{event_name}' has exceeded the maximum number of event subscribers allowed. "
                            f"The '{get_callable_name(event_callback)}' callback cannot be subscribed."
                        )

            # Create a new event subscriber
            event_subscriber: EventSubscriber = EventSubscriber(
                teardown_callback=(
                    lambda self: cls.__remove_event_subscriber_from_events(*events, event_subscriber=self)
                ),
                event_callback=event_callback,
                success_callback=success_callback if success_callback else cls.__default_success_callback,
                failure_callback=failure_callback if failure_callback else cls.__default_failure_callback,
                force_async=force_async,
                once=once,
            )

            # For each event name, register the event subscriber
            for event_name in event_names:
                # If the event name is not present in the main registry, create a new empty list for it
                if event_name not in cls.__registry:
                    cls.__registry[event_name] = []

                # Append the event subscriber to the list
                cls.__registry[event_name].append(event_subscriber)

                # Log the subscription if debug is enabled
                if cls.__logger.debug_enabled:  # pragma: no cover
                    cls.__logger.debug(
                        action="Subscribed:",
                        msg=f"{event_subscriber} {StdOutColors.PURPLE}Event:{StdOutColors.DEFAULT} {event_name}",
                    )

        # Return the new event subscriber
        return event_subscriber

    @classmethod
    def remove_all(cls) -> None:
        """
        Removes all events and their associated subscribers from the registry.
        :return: None
        """
        # Retrieve the list of event subscribers from the registry
        event_subscribers: List[EventSubscriber] = cls.get_event_subscribers()

        # Check if there are no event subscribers
        if not event_subscribers:
            # Log a debug message indicating that the registry is empty
            if cls.__logger.debug_enabled:  # pragma: no cover
                cls.__logger.debug(msg="The event registry is already empty.")

        # Iterate over each event subscriber to unsubscribe them
        for event_subscriber in event_subscribers:
            event_subscriber.unsubscribe()

        # Log a debug message indicating that all events and their subscribers have been removed
        if cls.__logger.debug_enabled:  # pragma: no cover
            cls.__logger.debug(
                msg="All events and their associated subscribers have been successfully removed from the registry."
            )
