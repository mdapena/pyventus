from typing import final, Dict, Set, Tuple

from ..subscribers import EventSubscriber


@final
class EventRegistry:
    """
    An optimized data structure for storing events and their event subscribers.

    **Notes:**

    -   This class employs a multikeyed multivalued bidirectional mapping structure
        for efficient lookups, updates, and deletions of events and their subscribers.

    -   Despite employing a bidirectional mapping structure, the memory footprint of
        this data structure remains minimal, thanks to the fact that events and their
        subscribers are immutable objects. As a result, references are used instead of
        duplication, limiting its impact solely to the additional dictionary and set
        data structures.

    -   Most of this data structure's methods operate at an average of O(1) time
        complexity, ensuring high efficiency. However, the efficiency of removal
        operations, while optimized, may vary based on the relationships between
        events and their subscribers.

    -   This data structure is not inherently designed for concurrency, so thread
        safety considerations must be taken into account.
    """

    # Attributes for the EventRegistry
    __slots__ = ("__fwd_registry", "__inv_registry")

    def __init__(self) -> None:
        """Initializes an instance of `EventRegistry`."""
        # Initialize the registry and its inverse mapping
        self.__fwd_registry: Dict[str, Set[EventSubscriber]] = {}
        self.__inv_registry: Dict[EventSubscriber, Set[str]] = {}

    def get_registry(self) -> Dict[str, Set[EventSubscriber]]:
        """
        Retrieves a copy of the main registry.
        :return: A mapping representing the main registry, where
            each event is mapped to a set of its subscribers.
        """
        return self.__fwd_registry.copy()

    def get_events(self, event_subscriber: EventSubscriber | None = None) -> Set[str] | None:
        """
        Retrieves all registered events, or those associated with the specified event subscriber.
        :param event_subscriber: An optional `EventSubscriber` instance. If provided, the method returns
            events associated with this subscriber. If `None`, all registered events are returned.
        :return: A set of all registered events if `event_subscriber` is `None`, a set of events
            associated with the given event subscriber if it exists, or `None` if the subscriber
            is not found.
        """
        if event_subscriber is None:
            return set(self.__fwd_registry.keys())
        elif event_subscriber in self.__inv_registry:
            return set(self.__inv_registry[event_subscriber])
        else:
            return None

    def get_event_subscribers(self, event: str | None = None) -> Set[EventSubscriber] | None:
        """
        Retrieves all registered event subscribers, or those associated with the specified event.
        :param event: An optional string representing the event name. If provided, the method returns
            subscribers associated with this event. If `None`, all registered event subscribers are returned.
        :return: A set of all registered `EventSubscriber` instances if `event` is `None`, a set of subscribers
            associated with the given event if it exists, or `None` if the event is not found.
        """
        if event is None:
            return set(self.__inv_registry.keys())
        elif event in self.__fwd_registry:
            return set(self.__fwd_registry[event])
        else:
            return None

    def get_event_count(self, event_subscriber: EventSubscriber | None = None) -> int | None:
        """
        Retrieves the number of events registered, or the number of events associated with a specific event subscriber.
        :param event_subscriber: An optional `EventSubscriber` instance. If provided, the method returns the count of
            events associated with this subscriber. If `None`, it returns the total count of all registered events.
        :return: The total count of events currently registered if `event_subscriber` is `None`, the count of events
            for the specified `event_subscriber` if provided, or `None` if the `event_subscriber` is not found in
            the registry.
        """
        if event_subscriber is None:
            return len(self.__fwd_registry)
        elif event_subscriber in self.__inv_registry:
            return len(self.__inv_registry[event_subscriber])
        else:
            return None

    def get_event_subscriber_count(self, event: str | None = None) -> int | None:
        """
        Retrieves the number of subscribers registered, or the number of subscribers associated with a specific event.
        :param event: An optional string representing the event name. If provided, the method returns the count of
            subscribers associated with this event. If `None`, it returns the total count of all registered subscribers.
        :return: The total count of event subscribers currently registered if `event` is `None`, the count of
            subscribers for the specified event if provided, or `None` if the event is not found in the registry.
        """
        if event is None:
            return len(self.__inv_registry)
        elif event in self.__fwd_registry:
            return len(self.__fwd_registry[event])
        else:
            return None

    def contains_event(self, event: str) -> bool:
        """
        Checks if the given event is registered.
        :param event: The event to be checked.
        :return: `True` if the event is registered, `False` otherwise.
        """
        return event in self.__fwd_registry

    def contains_event_subscriber(self, event_subscriber: EventSubscriber) -> bool:
        """
        Checks if the given event subscriber is registered.
        :param event_subscriber: The event subscriber to be checked.
        :return: `True` if the event subscriber is registered, `False` otherwise.
        """
        return event_subscriber in self.__inv_registry

    def insert(self, event: str, event_subscriber: EventSubscriber) -> None:
        """
        Inserts the given event subscriber with the specified event in the registry.
        :param event: The event to which the event subscriber will be associated.
        :param event_subscriber: The event subscriber to be inserted for the event.
        :return: None
        """
        # Add the event subscriber to the event's set in the main registry
        if event not in self.__fwd_registry:
            self.__fwd_registry[event] = set()
        self.__fwd_registry[event].add(event_subscriber)

        # Add the event to the event subscriber's set in the inverse registry
        if event_subscriber not in self.__inv_registry:
            self.__inv_registry[event_subscriber] = set()
        self.__inv_registry[event_subscriber].add(event)

    def remove_event(self, event: str) -> Set[EventSubscriber] | None:
        """
        Removes the specified event from the registry and returns a set of event subscribers
        who were completely unsubscribed as a side effect of removing the event.
        :param event: The event to be removed from the registry.
        :return: A set of event subscribers who were completely unsubscribed due to the
            removal of the event, or `None` if the event is not found in the registry.
        """
        # If the event is not within the registry, return early
        if event not in self.__fwd_registry:
            return None

        # Remove the event and retrieve its subscribers
        event_subscribers: Set[EventSubscriber] = self.__fwd_registry.pop(event)

        # Initialize a set to store the event subscribers
        # that will be completely removed from both registries
        removed_event_subscribers: Set[EventSubscriber] = set()

        # Remove the event from the event subscriber's set
        for event_subscriber in event_subscribers:
            self.__inv_registry[event_subscriber].remove(event)

            # If the event subscriber was only subscribed to this event, remove it from
            # the inverse registry and add it to the list of removed event subscribers
            if len(self.__inv_registry[event_subscriber]) == 0:
                self.__inv_registry.pop(event_subscriber)
                removed_event_subscribers.add(event_subscriber)

        # Return the removed event subscribers
        return removed_event_subscribers

    def remove_event_subscriber(self, event_subscriber: EventSubscriber) -> Set[str] | None:
        """
        Removes the specified event subscriber from the registry and returns a set of events
        that were completely removed as a side effect of removing the event subscriber.
        :param event_subscriber: The event subscriber to be removed from the registry.
        :return: A set of events that were completely removed as a side effect of removing
            the event subscriber, or `None` if the event subscriber is not found in the registry.
        """
        # If the event subscriber is not in the inverse registry, return early
        if event_subscriber not in self.__inv_registry:
            return None

        # Retrieve events associated with the event subscriber and remove it from the inverse registry
        events: Set[str] = self.__inv_registry.pop(event_subscriber)

        # Initialize a set to store the events that will
        # be completely removed from both registries
        removed_events: Set[str] = set()

        # Remove the event subscriber from the event's set
        for event in events:
            self.__fwd_registry[event].remove(event_subscriber)

            # If the event had only that subscriber, remove it from
            # the registry and add it to the list of removed events
            if len(self.__fwd_registry[event]) == 0:
                self.__fwd_registry.pop(event)
                removed_events.add(event)

        # Return the removed events
        return removed_events

    def clear(self) -> Tuple[Set[str], Set[EventSubscriber]]:
        """
        Clears the event registry by removing all events and event subscribers.
        :return: A tuple containing two sets; the first set includes the events that were removed
            from the registry, and the second set consists of the event subscribers that were removed.
        """
        # Store the current events and event subscribers before clearing the registry
        events, event_subscribers = set(self.__fwd_registry.keys()), set(self.__inv_registry.keys())

        # Clear both the main registry and the inverse registry
        self.__fwd_registry.clear()
        self.__inv_registry.clear()

        return events, event_subscribers

    def __str__(self) -> str:
        """
        Returns a string representation of the EventRegistry.
        :return: A string representation of the EventRegistry.
        """
        return (
            "Event Registry: {\n"
            + "\n".join(
                f"\t'{event}': {{{', '.join(f'EventSubscriber <{hex(id(sub))}>' for sub in event_subscribers)}}}"
                for event, event_subscribers in self.__fwd_registry.items()
            )
            + "\n}"
        )
