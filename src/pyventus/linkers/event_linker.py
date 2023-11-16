from abc import ABC
from itertools import chain
from sys import version_info
from threading import Lock
from typing import Dict, List, Mapping, Callable, Type, TypeAlias, Any, Set

from src.pyventus.core.exceptions import PyventusException
from src.pyventus.events import Event
from src.pyventus.listeners import EventListener

if version_info >= (3, 10):  # pragma: no cover
    from typing import ParamSpec
else:  # pragma: no cover
    from typing_extensions import ParamSpec

SubscribableEventType: TypeAlias = Type[Event] | Type[Exception] | str
""" A type alias representing the supported event types for subscription. """

P = ParamSpec("P")
""" A generic type to represent the parameter names and types of the callback function. """


class EventLinker(ABC):
    """
    A base class that acts as a global registry for linking events with their associated event listeners.

    The `EventLinker` class provides a centralized mechanism for managing event subscriptions, unsubscriptions,
    and retrieval of events and their associated event listeners. It acts as a global registry, ensuring that
    events and their listeners are organized and easily accessible.

    **Note**: The `EventLinker` class can be subclassed to create specific namespaces or contexts for managing
    events and event listeners. By subclassing `EventLinker`, users can separate and organize event subscriptions
    and listeners within different scopes, providing modularity and flexibility in event management.
    """

    __event_registry: Dict[str, List[EventListener]] = {}
    """ 
    A dictionary that serves as a container for storing events and their respective event listeners.
    The keys represent event names, and the values are lists of `EventListener` objects. 
    """

    __max_event_listeners: int | None = None
    """ The maximum number of `EventListener` allowed per event, or None if no limit. """

    __thread_lock: Lock = Lock()
    """
    A threading.Lock object used for thread synchronization when accessing and modifying the event registry
    to ensure thread safety. It prevents multiple threads from accessing or modifying the registry simultaneously.
    """

    def __init_subclass__(cls, max_event_listeners: int | None = None, **kwargs):
        """
        Custom __init_subclass__ method called when a subclass is created.

        This method initializes the subclass by setting up the event registry and thread lock.
        It also allows specifying the maximum number of event listeners per event.

        :param max_event_listeners: The maximum number of `EventListener` allowed per event, or None if no limit.
        :param kwargs: The keyword arguments to pass to the superclass __init_subclass__ method.
        :raises PyventusException: If `max_event_listeners` is less than 1.
        :return: Any
        """
        # Call the parent class' __init_subclass__ method
        super().__init_subclass__(**kwargs)

        # Initialize the event registry dictionary
        cls.__event_registry = {}

        # Create a lock object for thread synchronization
        cls.__thread_lock = Lock()

        # Validate the max_event_listeners argument
        if max_event_listeners is not None and max_event_listeners < 1:
            raise PyventusException("The 'max_event_listeners' argument must be greater than or equal to 0.")

        # Set the maximum number of event listeners per event
        cls.__max_event_listeners = max_event_listeners

    @classmethod
    @property
    def events(cls) -> List[str]:
        """
        Returns a list of all the registered event names.
        :return: A list of event names.
        """
        with cls.__thread_lock:
            return list(cls.__event_registry.keys())

    @classmethod
    @property
    def event_listeners(cls) -> List[EventListener]:
        """
        Retrieves a list of non-duplicated event listeners
        who have been registered across all events.
        :return: A list of event listeners.
        """
        with cls.__thread_lock:
            return list(set(chain(*cls.__event_registry.values())))

    @classmethod
    @property
    def event_registry(cls) -> Mapping[str, List[EventListener]]:
        """
        Retrieves the event registry mapping.
        :return: A mapping of event names to event listeners.
        """
        with cls.__thread_lock:
            return {event: list(event_listeners) for event, event_listeners in cls.__event_registry.items()}

    @classmethod
    @property
    def max_event_listeners(cls) -> None | int:
        """
        Retrieves the maximum number of listeners allowed per event.
        :return: The maximum number of listeners or None if there is no limit.
        """
        return cls.__max_event_listeners

    @classmethod
    def _get_event_key(cls, event: SubscribableEventType) -> str:
        """
        Determines the event string key based on the given event.
        :param event: The event to obtain the key for.
        :return: The event string key.
        :raise PyventusException: If the `event` argument is None
            or if the event type is not supported.
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
            raise PyventusException('Unsupported event type')

    @classmethod
    def get_events_by_listener(cls, event_listener: EventListener) -> List[str]:
        """
        Retrieves a list of event names associated with the specified event listener.
        :param event_listener: The listener to retrieve the associated events for.
        :return: A list of event names.
        :raise PyventusException: If the `event_listener` argument is None.
        """
        # Validate the event_listener argument
        if event_listener is None:
            raise PyventusException("The 'event_listener' argument cannot be None.")

        with cls.__thread_lock:
            return [
                event
                for event, event_listeners in cls.__event_registry.items()
                if event_listener in event_listeners
            ]

    @classmethod
    def get_listeners_by_events(cls, *events: SubscribableEventType) -> List[EventListener]:
        """
        Retrieves a list of non-duplicated event listeners associated with the specified events.
        :param events: Events to retrieve the listeners for.
        :return: A list of event listeners.
        :raise PyventusException: If the `events` argument is None or empty.
        """
        # Validate the events argument
        if events is None or len(events) <= 0:
            raise PyventusException("The 'events' argument cannot be None or empty.")

        # Retrieve all unique event keys
        event_keys: Set[str] = set([cls._get_event_key(event=event) for event in events])

        with cls.__thread_lock:
            return list({
                event_listener
                for event_key in event_keys
                for event_listener in cls.__event_registry.get(event_key, [])
            })

    @classmethod
    def once(cls, *events: SubscribableEventType) -> Callable[[Callable[P, Any]], Callable[P, Any]]:
        """
        Decorator that subscribes a callback function to the specified events to be invoked only once.
        This decorator is used to conveniently subscribe a callback function as a one-time listener.
        :param events: The events to subscribe to.
        :return: The decorator function that wraps the callback.
        """

        def _decorator(callback: Callable[P, Any]) -> Callable[P, Any]:
            cls.subscribe(*events, callback=callback, once=True)
            return callback

        return _decorator

    @classmethod
    def on(cls, *events: SubscribableEventType) -> Callable[[Callable[P, Any]], Callable[P, Any]]:
        """
        Decorator that subscribes a callback function to the specified events.
        :param events: The events to subscribe to.
        :return: The decorator function that wraps the callback.
        """

        def _decorator(callback: Callable[P, Any]) -> Callable[P, Any]:
            cls.subscribe(*events, callback=callback, once=False)
            return callback

        return _decorator

    @classmethod
    def subscribe(cls, *events: SubscribableEventType, callback: Callable[P, Any], once: bool = False) -> EventListener:
        """
        Subscribes a callback function to the specified events.
        :param events: The events to subscribe to.
        :param callback: The callback function to associate with the events.
        :param once: Specifies if the callback function is a one-time listener. If set to `True`,
            the listener will be invoked once when the event occurs and then automatically unsubscribed.
            If set to `False` (default), the listener can be invoked multiple times until explicitly
            unsubscribed.
        :return: The event listener object associated with the subscribed callback function.
        :raise PyventusException: If the maximum number of listeners for an event has been exceeded
            or if the `events` argument is None or empty.
        """
        # Validate the events argument
        if events is None or len(events) <= 0:
            raise PyventusException("The 'events' argument cannot be None or empty.")

        # Retrieve all unique event keys
        event_keys: Set[str] = set([cls._get_event_key(event=event) for event in events])

        # Acquire the lock to ensure exclusive access to the event registry
        with cls.__thread_lock:

            # Check if the maximum number of listeners property is set
            if cls.__max_event_listeners is not None:

                # For each event key, check if the maximum number of listeners for the event has been exceeded
                for event_key in event_keys:
                    if len(cls.__event_registry.get(event_key, [])) >= cls.__max_event_listeners:
                        raise PyventusException(
                            f"The event '{event_key}' has exceeded the maximum number of listeners allowed. "
                            f"The '{callback.__name__}' listener cannot be added."
                        )

            # Create a new event listener
            event_listener: EventListener = EventListener(callback=callback, once=once)

            # For each event key, register the event listener
            for event_key in event_keys:

                # If the event key is not present in the event registry, create a new empty list for it
                if event_key not in cls.__event_registry:
                    cls.__event_registry[event_key] = []

                # Append the event listener to the list of listeners for the event
                cls.__event_registry[event_key].append(event_listener)

        # Return the new event listener
        return event_listener

    @classmethod
    def unsubscribe(cls, *events: SubscribableEventType, event_listener: EventListener) -> bool:
        """
        Unsubscribes an event listener from the specified events. The method removes the event
        listener from the event registry and, if there are no more listeners for a particular
        event, removes that event from the registry as well.
        :param events: The events to unsubscribe from.
        :param event_listener: The event listener to unsubscribe.
        :return: `True` if the event listener associated with the events was found and removed, `False` otherwise.
        :raise PyventusException: If the `events` argument is None, empty or if the `event_listener` argument is None.
        """
        # Validate the events argument
        if events is None or len(events) <= 0:
            raise PyventusException("The 'events' argument cannot be None or empty.")

        # Validate the event_listener argument
        if event_listener is None:
            raise PyventusException("The 'event_listener' argument cannot be None.")

        # Retrieve all unique event keys
        event_keys: Set[str] = set([cls._get_event_key(event=event) for event in events])

        # Flag indicating whether the event listener was successfully removed
        deleted: bool = False

        # Obtain the lock to ensure exclusive access to the event registry
        with cls.__thread_lock:

            # For each event key, check and remove the event listener if found
            for event_key in event_keys:
                # Get the list of event listeners for the event key, or an empty list if it doesn't exist
                event_listeners = cls.__event_registry.get(event_key, [])

                # Check if the event listener is present in the list of listeners for the event
                if event_listener in event_listeners:
                    # Remove the event listener from the list of listeners
                    event_listeners.remove(event_listener)
                    deleted = True

                    # If there are no more listeners for the event, remove the event key from the registry
                    if not event_listeners:
                        cls.__event_registry.pop(event_key)

        # Return the flag indicating whether the event listener was deleted
        return deleted

    @classmethod
    def remove_event_listener(cls, event_listener: EventListener) -> bool:
        """
        Removes an event listener from all subscribed events. If there are no more
        listeners for a particular event, that event is removed from the registry.
        :param event_listener: The event listener to remove.
        :return: `True` if the event listener was found and removed, `False` otherwise.
        :raise PyventusException: If the `event_listener` argument is None.
        """
        # Validate the event_listener argument
        if event_listener is None:
            raise PyventusException("The 'event_listener' argument cannot be None.")

        # A flag indicating if the event listener gets removed
        deleted: bool = False

        # Acquire the lock to ensure exclusive access to the event registry
        with cls.__thread_lock:

            # Iterate through each event and its associated listeners in the event registry
            for event in list(cls.__event_registry.keys()):
                # Get the list of event listeners for the event key, or an empty list if it doesn't exist
                event_listeners = cls.__event_registry.get(event, [])

                # Check if the event listener is present in the list of listeners for the event
                if event_listener in event_listeners:
                    # Remove the event listener from the list of listeners
                    event_listeners.remove(event_listener)
                    deleted = True

                    # If there are no more listeners for the event, remove the event from the registry
                    if not event_listeners:
                        cls.__event_registry.pop(event)

        # Return the flag indicating if the event listener was found and deleted
        return deleted

    @classmethod
    def remove_event(cls, event: SubscribableEventType) -> bool:
        """
        Removes an event and all associated event listeners.
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
                return True

        return False

    @classmethod
    def remove_all(cls) -> bool:
        """
        Removes all events and event listeners.
        :return: `True` if the events were found and removed, `False` otherwise.
        """
        # Acquire the lock to ensure exclusive access to the event registry
        with cls.__thread_lock:
            # Clear the event registry by assigning an empty dictionary
            cls.__event_registry = {}

        return True
