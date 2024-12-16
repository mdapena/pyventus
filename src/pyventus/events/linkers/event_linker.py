from dataclasses import is_dataclass
from sys import gettrace
from threading import Lock
from types import EllipsisType
from typing import Generic, TypeAlias, TypeVar, final

from typing_extensions import Self, override

from ...core.collections import MultiBidict
from ...core.constants import StdOutColors
from ...core.exceptions import PyventusException
from ...core.loggers import Logger
from ...core.subscriptions import SubscriptionContext
from ...core.utils import validate_callable
from ..subscribers import EventCallbackType, EventSubscriber, FailureCallbackType, SuccessCallbackType

SubscribableEventType: TypeAlias = str | type[Exception] | type[object] | EllipsisType
"""A type alias representing the supported event types for subscription."""

_SubCtxE = TypeVar("_SubCtxE", bound=type["EventLinker"])
"""A generic type representing the event linker type used in the subscription context."""


class EventLinker:
    """
    A base class that orchestrates the linkage of events and their inherent logic.

    **Notes:**

    -   This class provides a centralized mechanism for managing the connections
        between events and their corresponding logic.

    -   The `EventLinker` can be subclassed to create specific namespaces or contexts
        for managing events within different scopes. Subclassing also allows users to
        configure the settings of the `EventLinker` to suit their specific use cases.

    -   The `EventLinker` is designed with *thread safety* in mind. All methods
        synchronize access to prevent race conditions when managing mutable
        properties across multiple threads.
    """

    @final
    class EventLinkerSubCtx(Generic[_SubCtxE], SubscriptionContext[_SubCtxE, EventSubscriber]):
        """
        A context manager for event linker subscriptions.

        **Notes:**

        -   This class establishes a context block for a step-by-step definition of event responses
            prior to the actual subscription, which occurs immediately upon exiting the context block.

        -   This class can be used as either a decorator or a context manager. When used as a
            decorator, it automatically subscribes the decorated callback to the specified events.
            When used as a context manager with the `with` statement, it allows multiple callbacks
            to be associated with the specified events within the context block.

        -   This subscription context can be `stateful`, retaining references to the `event linker`
            and `subscriber`, or `stateless`, which clears the context upon exiting the subscription
            block.

        -   This class is not intended to be subclassed or manually instantiated.
        """

        # Attributes for the EventLinkerSubCtx
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
            events: tuple[SubscribableEventType, ...],
            event_linker: _SubCtxE,
            force_async: bool,
            once: bool,
            is_stateful: bool,
        ) -> None:
            """
            Initialize an instance of `EventLinkerSubCtx`.

            :param events: The events to subscribe/link to.
            :param event_linker: The type of event linker used for the actual subscription.
            :param force_async: Determines whether to force all callbacks to run asynchronously.
            :param once: Specifies if the event subscriber will be a one-time subscription.
            :param is_stateful: A flag indicating whether the context preserves its state (stateful) or
                not (stateless) after exiting the subscription context. If `True`, the context retains its
                state, allowing access to stored objects, including the `event linker` and the `subscriber`
                object. If `False`, the context is stateless, and the stored state is cleared upon exiting
                the subscription context to prevent memory leaks.
            """
            # Initialize the base SubscriptionContext class
            super().__init__(source=event_linker, is_stateful=is_stateful)

            # Initialize variables
            self.__events: tuple[SubscribableEventType, ...] = events
            self.__event_callback: EventCallbackType | None = None
            self.__success_callback: SuccessCallbackType | None = None
            self.__failure_callback: FailureCallbackType | None = None
            self.__force_async: bool = force_async
            self.__once: bool = once

        @override
        def _exit(self) -> EventSubscriber:
            # Ensure that the source is not None
            if self._source is None:  # pragma: no cover
                raise PyventusException("The subscription context is closed.")

            # Check if the event callback has been set
            if self.__event_callback is None:
                raise PyventusException("The event callback has not been set.")

            # Subscribe the defined callbacks to the
            # specified events and store the returned subscriber.
            subscriber: EventSubscriber = self._source.subscribe(
                *self.__events,
                event_callback=self.__event_callback,
                success_callback=self.__success_callback,
                failure_callback=self.__failure_callback,
                force_async=self.__force_async,
                once=self.__once,
            )

            # Remove context-specific attributes to clean up
            # and prevent memory leaks.
            del self.__events
            del self.__event_callback, self.__success_callback, self.__failure_callback
            del self.__force_async, self.__once

            # Return the subscriber
            return subscriber

        def on_event(self, callback: EventCallbackType) -> EventCallbackType:
            """
            Set the main callback for the event.

            :param callback: The callback to be executed when the event occurs.
            :return: The decorated callback.
            """
            self.__event_callback = callback
            return callback

        def on_success(self, callback: SuccessCallbackType) -> SuccessCallbackType:
            """
            Set the success callback for the event.

            :param callback: The callback to be executed when the event response completes successfully.
            :return: The decorated callback.
            """
            self.__success_callback = callback
            return callback

        def on_failure(self, callback: FailureCallbackType) -> FailureCallbackType:
            """
            Set the failure callback for the event.

            :param callback: The callback to be executed when the event response fails.
            :return: The decorated callback.
            """
            self.__failure_callback = callback
            return callback

        def __call__(
            self, callback: EventCallbackType
        ) -> tuple[EventCallbackType, "EventLinker.EventLinkerSubCtx[_SubCtxE]"] | EventCallbackType:
            """
            Subscribe the decorated callback to the specified events.

            :param callback: The callback to be executed when the event occurs.
            :return: A tuple containing the decorated callback and its subscription context
                if the context is stateful; otherwise, returns the decorated callback alone.
            """
            # Store the provided callback as the event callback
            self.__event_callback = callback

            # Set success and failure callbacks to None
            self.__success_callback = None
            self.__failure_callback = None

            # Determine if the subscription context is stateful
            is_stateful: bool = self._is_stateful

            # Call the exit method to finalize the
            # subscription process and clean up any necessary context.
            self.__exit__(None, None, None)

            # Return a tuple containing the decorated callback
            # and the current subscription context if the context
            # is stateful; otherwise, return just the callback.
            return (callback, self) if is_stateful else callback

    __registry: MultiBidict[str, EventSubscriber] = MultiBidict[str, EventSubscriber]()
    """
    A registry that serves as a container for storing events and their associated subscribers. It 
    utilizes an optimized data structure that enables quick lookups, updates, and even deletions 
    of events and their subscribers.
    """

    __max_subscribers: int | None = None
    """The maximum number of subscribers allowed per event, or `None` if there is no limit."""

    __default_success_callback: SuccessCallbackType | None = None
    """ 
    Represents the default success callback that will be assigned to subscribers in the 
    absence of a specific success callback. This callback will be executed upon successful 
    completion of the event response in each subscriber.
    """

    __default_failure_callback: FailureCallbackType | None = None
    """
    Represents the default failure callback that will be assigned to subscribers in the
    absence of a specific failure callback. This callback will be executed when the event 
    response fails in each subscriber.
    """

    __thread_lock: Lock = Lock()
    """
    A `threading.Lock` object used for thread synchronization when accessing and modifying 
    mutable attributes to ensure thread safety. It prevents multiple threads from accessing 
    and modifying mutable properties simultaneously.
    """

    __logger: Logger = Logger(source="EventLinker(ClassReference)", debug=bool(gettrace() is not None))
    """
    The logger used to debug and log information within the `EventLinker` class. The debug mode
    of the logger depends on the execution environment and the value returned by the `gettrace()`
    function. The debug mode can also be influenced by subclassing and overridden in subclasses.
    """

    def __init_subclass__(
        cls,
        max_subscribers: int | None = None,
        default_success_callback: SuccessCallbackType | None = None,
        default_failure_callback: FailureCallbackType | None = None,
        debug: bool | None = None,
    ) -> None:
        """
        Initialize a subclass of `EventLinker`.

        By default, this method sets up the main registry and the thread lock object, but
        it can also be used to configure specific settings of the `EventLinker` subclass.

        :param max_subscribers: The maximum number of subscribers allowed per event, or `None` if there is no limit.
        :param default_success_callback: The default callback to assign as the success callback in the subscribers
            when no specific success callback is provided.
        :param default_failure_callback: The default callback to assign as the failure callback in the subscribers
            when no specific failure callback is provided.
        :param debug: Specifies the debug mode for the subclass logger. If `None`, it is determined based
            on the execution environment.
        :raises PyventusException: If `max_subscribers` is less than 1 or if the provided
            callbacks are invalid.
        :return: None.
        """
        # Initialize the main registry
        cls.__registry = MultiBidict[str, EventSubscriber]()

        # Create a lock object for thread synchronization
        cls.__thread_lock = Lock()

        # Validate the max_subscribers argument
        if max_subscribers is not None and max_subscribers < 1:
            raise PyventusException("The 'max_subscribers' argument must be greater than or equal to 1.")

        # Set the maximum number of subscribers per event
        cls.__max_subscribers = max_subscribers

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
        cls.__logger = Logger(source=cls, debug=debug if debug is not None else bool(gettrace() is not None))

    @classmethod
    def _get_logger(cls) -> Logger:
        """
        Retrieve the class-level logger instance.

        :return: The class-level logger instance used to debug and log
            information within the `EventLinker` class.
        """
        return cls.__logger

    @classmethod
    def _get_valid_and_unique_event_names(cls, events: tuple[SubscribableEventType, ...]) -> set[str]:
        """
        Validate and extract unique event names from the specified tuple of event objects.

        :param events: A tuple of event objects to validate and extract unique names from.
        :return: A set of unique and valid event names derived from the provided tuple of event objects.
        :raises PyventusException: If the 'events' argument is None, empty, or contains invalid events.
        """
        if not events:
            raise PyventusException("The 'events' argument cannot be None or empty.")
        return {cls.get_valid_event_name(event) for event in events}

    @classmethod
    def _get_valid_and_unique_subscribers(cls, subscribers: tuple[EventSubscriber, ...]) -> set[EventSubscriber]:
        """
        Validate and extract unique subscribers from the specified tuple of subscribers.

        :param subscribers: A tuple of event subscribers to validate and extract unique entries from.
        :return: A set of unique and valid subscribers derived from the provided tuple of subscribers.
        :raises PyventusException: If the 'subscribers' argument is None, empty, or contains invalid subscribers.
        """
        if not subscribers:
            raise PyventusException("The 'subscribers' argument cannot be None or empty.")
        return {cls.get_valid_subscriber(subscriber) for subscriber in subscribers}

    @classmethod
    def get_valid_event_name(cls, event: SubscribableEventType) -> str:
        """
        Determine the name of the event and performs validation.

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
    def get_valid_subscriber(cls, subscriber: EventSubscriber) -> EventSubscriber:
        """
        Validate and return the specified subscriber.

        :param subscriber: The subscriber to validate.
        :return: The validated subscriber.
        :raises PyventusException: If the subscriber is not an instance of `EventSubscriber`.
        """
        # Validate that the subscriber is an instance of EventSubscriber
        if not isinstance(subscriber, EventSubscriber):
            raise PyventusException("The 'subscriber' argument must be an instance of EventSubscriber.")
        return subscriber

    @classmethod
    def get_max_subscribers(cls) -> int | None:
        """
        Retrieve the maximum number of subscribers allowed per event.

        :return: The maximum number of subscribers or `None` if there is no limit.
        """
        return cls.__max_subscribers

    @classmethod
    def get_default_success_callback(cls) -> SuccessCallbackType | None:
        """
        Retrieve the default success callback to assign to subscribers when no specific callback is provided.

        :return: The default success callback or `None` if not set.
        """
        return cls.__default_success_callback

    @classmethod
    def get_default_failure_callback(cls) -> FailureCallbackType | None:
        """
        Retrieve the default failure callback to assign to subscribers when no specific callback is provided.

        :return: The default failure callback or `None` if not set.
        """
        return cls.__default_failure_callback

    @classmethod
    def is_empty(cls) -> bool:
        """
        Determine whether the main registry is empty.

        :return: `True` if the main registry is empty, `False` otherwise.
        """
        with cls.__thread_lock:
            return cls.__registry.is_empty

    @classmethod
    def get_registry(cls) -> dict[str, set[EventSubscriber]]:
        """
        Retrieve a shallow copy of the main registry.

        :return: A shallow copy of the main registry, where each
            event is mapped to a set of its linked subscribers.
        """
        with cls.__thread_lock:
            return cls.__registry.to_dict()

    @classmethod
    def get_events(cls) -> set[str]:
        """
        Retrieve all registered events.

        :return: A set of all registered event names.
        """
        with cls.__thread_lock:
            return cls.__registry.keys

    @classmethod
    def get_subscribers(cls) -> set[EventSubscriber]:
        """
        Retrieve all registered subscribers.

        :return: A set of all registered subscribers.
        """
        with cls.__thread_lock:
            return cls.__registry.values

    @classmethod
    def get_event_count(cls) -> int:
        """
        Retrieve the number of registered events.

        :return: The total count of events in the registry.
        """
        with cls.__thread_lock:
            return cls.__registry.key_count

    @classmethod
    def get_subscriber_count(cls) -> int:
        """
        Retrieve the number of registered subscribers.

        :return: The total count of subscribers in the registry.
        """
        with cls.__thread_lock:
            return cls.__registry.value_count

    @classmethod
    def get_events_from_subscribers(cls, *subscribers: EventSubscriber) -> set[str]:
        """
        Retrieve a set of events associated with the specified subscribers.

        :param subscribers: One or more subscribers for which to retrieve associated events.
        :return: A set of events linked to the specified subscribers. Unregistered subscribers are ignored.
        """
        # Validate and retrieve all unique subscribers to avoid duplicate processing
        unique_subscribers: set[EventSubscriber] = cls._get_valid_and_unique_subscribers(subscribers)

        # Return the set of event names associated with the unique subscribers
        with cls.__thread_lock:
            return cls.__registry.get_keys_from_values(unique_subscribers)

    @classmethod
    def get_subscribers_from_events(
        cls, *events: SubscribableEventType, pop_onetime_subscribers: bool = False
    ) -> set[EventSubscriber]:
        """
        Retrieve a set of subscribers associated with the specified events.

        :param events: One or more events for which to retrieve associated subscribers.
        :param pop_onetime_subscribers: If `True`, removes one-time subscribers (those
            with the property `once` set to True) from the registry.
        :return: A set of subscribers linked to the specified events. Unregistered events are ignored.
        """
        # Validate and retrieve all unique event names to avoid duplicate processing
        unique_events: set[str] = cls._get_valid_and_unique_event_names(events)

        # Acquire lock to ensure thread safety
        with cls.__thread_lock:
            # Retrieve subscribers associated with the unique events
            subscribers: set[EventSubscriber] = cls.__registry.get_values_from_keys(unique_events)

            # Just return subscribers if pop_one_time_subscribers is False
            if not pop_onetime_subscribers:
                return subscribers

            # Remove one-time subscribers from the registry
            for subscriber in subscribers:
                if subscriber.once:
                    cls.__registry.remove_value(subscriber)

        # Return the set of subscribers
        return subscribers

    @classmethod
    def get_event_count_from_subscriber(cls, subscriber: EventSubscriber) -> int:
        """
        Retrieve the number of events associated with the given subscriber.

        :param subscriber: The subscriber for which to count the associated events.
        :return: The count of events associated with the specified subscriber,
            or 0 if the subscriber is not found.
        """
        valid_subscriber: EventSubscriber = cls.get_valid_subscriber(subscriber)
        with cls.__thread_lock:
            return cls.__registry.get_key_count_from_value(valid_subscriber)

    @classmethod
    def get_subscriber_count_from_event(cls, event: SubscribableEventType) -> int:
        """
        Retrieve the number of subscribers associated with a given event.

        :param event: The event for which to count the associated subscribers.
        :return: The count of subscribers associated with the specified event,
            or 0 if the event is not found.
        """
        valid_event: str = cls.get_valid_event_name(event)
        with cls.__thread_lock:
            return cls.__registry.get_value_count_from_key(valid_event)

    @classmethod
    def contains_event(cls, event: SubscribableEventType) -> bool:
        """
        Determine if the specified event is present in the registry.

        :param event: The event to be checked.
        :return: `True` if the event is found; `False` otherwise.
        """
        valid_event: str = cls.get_valid_event_name(event)
        with cls.__thread_lock:
            return cls.__registry.contains_key(valid_event)

    @classmethod
    def contains_subscriber(cls, subscriber: EventSubscriber) -> bool:
        """
        Determine if the specified subscriber is present in the registry.

        :param subscriber: The subscriber to be checked.
        :return: `True` if the subscriber is found; `False` otherwise.
        """
        valid_subscriber: EventSubscriber = cls.get_valid_subscriber(subscriber)
        with cls.__thread_lock:
            return cls.__registry.contains_value(valid_subscriber)

    @classmethod
    def are_linked(cls, event: SubscribableEventType, subscriber: EventSubscriber) -> bool:
        """
        Determine whether the given event is linked with the specified subscriber.

        :param event: The event for which the association is being checked.
        :param subscriber: The subscriber for which the association is being checked.
        :return: `True` if the subscriber is linked to the event; `False` otherwise.
        """
        valid_event: str = cls.get_valid_event_name(event)
        valid_subscriber: EventSubscriber = cls.get_valid_subscriber(subscriber)
        with cls.__thread_lock:
            return cls.__registry.are_associated(valid_event, valid_subscriber)

    @classmethod
    def once(
        cls, *events: SubscribableEventType, force_async: bool = False, stateful_subctx: bool = False
    ) -> EventLinkerSubCtx[type[Self]]:
        """
        Subscribe callbacks to the specified events for a single invocation.

        This method can be used as either a decorator or a context manager. When used as a
        decorator, it automatically subscribes the decorated callback to the provided events.
        When used as a context manager with the `with` statement, it allows multiple callbacks
        to be associated with the provided events within the context block.

        :param events: The events to subscribe to.
        :param force_async: Determines whether to force all callbacks to run asynchronously.
            If `True`, synchronous callbacks will be converted to run asynchronously in a
            thread pool, using the `asyncio.to_thread` function. If `False`, callbacks
            will run synchronously or asynchronously as defined.
        :param stateful_subctx: A flag indicating whether the subscription context preserves its state
            (`stateful`) or not (`stateless`) after exiting the subscription block. If `True`, the context retains
            its state, allowing access to stored objects, including the `event linker` and the `subscriber` object.
            If `False`, the context is stateless, and the stored state is cleared upon exiting the subscription
            block to prevent memory leaks. The term 'subctx' refers to 'Subscription Context'.
        :return: A `EventLinkerSubCtx` instance.
        """
        return EventLinker.EventLinkerSubCtx[type[Self]](
            events=events, event_linker=cls, force_async=force_async, once=True, is_stateful=stateful_subctx
        )

    @classmethod
    def on(
        cls, *events: SubscribableEventType, force_async: bool = False, stateful_subctx: bool = False
    ) -> EventLinkerSubCtx[type[Self]]:
        """
        Subscribe callbacks to the specified events.

        This method can be used as either a decorator or a context manager. When used as a
        decorator, it automatically subscribes the decorated callback to the provided events.
        When used as a context manager with the `with` statement, it allows multiple callbacks
        to be associated with the provided events within the context block.

        :param events: The events to subscribe to.
        :param force_async: Determines whether to force all callbacks to run asynchronously.
            If `True`, synchronous callbacks will be converted to run asynchronously in a
            thread pool, using the `asyncio.to_thread` function. If `False`, callbacks
            will run synchronously or asynchronously as defined.
        :param stateful_subctx: A flag indicating whether the subscription context preserves its state
            (`stateful`) or not (`stateless`) after exiting the subscription block. If `True`, the context retains
            its state, allowing access to stored objects, including the `event linker` and the `subscriber` object.
            If `False`, the context is stateless, and the stored state is cleared upon exiting the subscription
            block to prevent memory leaks. The term 'subctx' refers to 'Subscription Context'.
        :return: A `EventLinkerSubCtx` instance.
        """
        return EventLinker.EventLinkerSubCtx[type[Self]](
            events=events, event_linker=cls, force_async=force_async, once=False, is_stateful=stateful_subctx
        )

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
        Subscribe the specified callbacks to the given events.

        :param events: The events to subscribe to.
        :param event_callback: The callback to be executed when the event occurs.
        :param success_callback: The callback to be executed when the event response completes successfully.
        :param failure_callback: The callback to be executed when the event response fails.
        :param force_async: Determines whether to force all callbacks to run asynchronously.
            If `True`, synchronous callbacks will be converted to run asynchronously in a
            thread pool, using the `asyncio.to_thread` function. If `False`, callbacks
            will run synchronously or asynchronously as defined.
        :param once: Specifies if the subscriber will be a one-time subscriber.
        :return: The subscriber associated with the given events.
        """
        # Validate and retrieve all unique event names
        unique_events: set[str] = cls._get_valid_and_unique_event_names(events)

        # Acquire the lock to ensure exclusive access to the main registry
        with cls.__thread_lock:
            # Check if the maximum number of subscribers is set
            if cls.__max_subscribers is not None:
                # For each event name, check if the maximum number
                # of subscribers for the event has been exceeded
                for event in unique_events:
                    if cls.__registry.get_value_count_from_key(event) >= cls.__max_subscribers:
                        raise PyventusException(
                            f"The event '{event}' has exceeded the maximum number of subscribers allowed."
                        )

            # Create a new event subscriber
            subscriber: EventSubscriber = EventSubscriber(
                teardown_callback=cls.remove_subscriber,
                event_callback=event_callback,
                success_callback=success_callback if success_callback else cls.__default_success_callback,
                failure_callback=failure_callback if failure_callback else cls.__default_failure_callback,
                force_async=force_async,
                once=once,
            )

            # Register the subscriber for each unique event
            for event in unique_events:
                cls.__registry.insert(event, subscriber)

        # Log the subscription if debug is enabled
        if cls.__logger.debug_enabled:
            cls.__logger.debug(
                action="Subscribed:", msg=f"{subscriber} {StdOutColors.PURPLE_TEXT('Events:')} {unique_events}"
            )

        # Return the new event subscriber
        return subscriber

    @classmethod
    def remove(cls, event: SubscribableEventType, subscriber: EventSubscriber) -> bool:
        """
        Remove the specified subscriber from the given event.

        :param event: The event from which the subscriber will be removed.
        :param subscriber: The subscriber to be removed from the event.
        :return: `True` if the subscriber was successfully removed; `False` if
            no removal occurred due to the event or subscriber not being registered,
            or if they are not linked.
        """
        # Validate the given event and subscriber
        valid_event: str = cls.get_valid_event_name(event)
        valid_subscriber: EventSubscriber = cls.get_valid_subscriber(subscriber)

        # Acquire lock to ensure thread safety
        with cls.__thread_lock:
            # Check if the event and subscriber are registered and linked
            if not cls.__registry.are_associated(valid_event, valid_subscriber):
                return False

            # Remove the subscriber from the event
            cls.__registry.remove(valid_event, valid_subscriber)

        # Log the removal if the debug mode is enabled
        if cls.__logger.debug_enabled:
            cls.__logger.debug(
                action="Removed:", msg=f"{valid_subscriber} {StdOutColors.PURPLE_TEXT('Event:')} '{valid_event}'"
            )

        return True

    @classmethod
    def remove_event(cls, event: SubscribableEventType) -> bool:
        """
        Remove the specified event from the registry.

        :param event: The event to be removed from the registry.
        :return: `True` if the event was successfully removed; `False`
            if the event was not found in the registry.
        """
        # Get the valid event name
        valid_event: str = cls.get_valid_event_name(event)

        # Acquire lock to ensure thread safety
        with cls.__thread_lock:
            # Check if the event is registered; return False if not
            if not cls.__registry.contains_key(valid_event):
                return False

            # Remove the event from the registry
            cls.__registry.remove_key(valid_event)

        # Log the removal if the debug mode is enabled
        if cls.__logger.debug_enabled:
            cls.__logger.debug(action="Removed:", msg=f"Event: '{valid_event}'")

        return True

    @classmethod
    def remove_subscriber(cls, subscriber: EventSubscriber) -> bool:
        """
        Remove the specified subscriber from the registry.

        :param subscriber: The subscriber to be removed from the registry.
        :return: `True` if the subscriber was successfully removed; `False` if
            the subscriber was not found in the registry.
        """
        # Get the valid subscriber instance
        valid_subscriber: EventSubscriber = cls.get_valid_subscriber(subscriber)

        # Acquire lock to ensure thread safety
        with cls.__thread_lock:
            # Check if the subscriber is registered; return False if not
            if not cls.__registry.contains_value(valid_subscriber):
                return False

            # Remove the subscriber from the registry
            cls.__registry.remove_value(valid_subscriber)

        # Log the removal if the debug mode is enabled
        if cls.__logger.debug_enabled:
            cls.__logger.debug(action="Removed:", msg=f"{valid_subscriber}")

        return True

    @classmethod
    def remove_all(cls) -> bool:
        """
        Remove all events and subscribers from the registry.

        :return: `True` if the registry was successfully cleared; `False`
            if the registry was already empty.
        """
        # Acquire lock to ensure thread safety
        with cls.__thread_lock:
            # Check if the registry is already empty
            if cls.__registry.is_empty:
                return False

            # Clear the registry
            cls.__registry.clear()

        if cls.__logger.debug_enabled:
            cls.__logger.debug(action="Removed:", msg="All events and subscribers.")

        return True
