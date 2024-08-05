from typing import final, Dict, Set, Tuple

from ..subscribers import EventSubscriber


@final
class EventRegistry:
    """
    An optimized data structure for storing events and their subscribers.

    **Notes:**

    -   This class employs a multikeyed multivalued bidirectional mapping structure
        for efficient lookups, updates, and deletions of events and their subscribers.

    -   Despite employing a bidirectional mapping structure, the memory footprint of this data
        structure remains minimal, thanks to the fact that events and their subscribers are
        immutable objects. As a result, references are used instead of duplication, limiting
        its impact solely to the additional dictionary and set data structures.

    -   Most of this data structure's methods operate at an average of O(1) time complexity,
        ensuring high efficiency. However, the efficiency of removal operations, while optimized,
        may vary based on the relationships between events and their subscribers.

    -   This data structure is not inherently designed for concurrency, so thread safety
        considerations must be taken into account.
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

    def get_events(self) -> Set[str]:
        """
        Retrieves all registered events.
        :return: A set of all registered events.
        """
        return set(self.__fwd_registry.keys())

    def get_subscribers(self) -> Set[EventSubscriber]:
        """
        Retrieves all registered subscribers.
        :return: A set of all registered subscribers.
        """
        return set(self.__inv_registry.keys())

    def get_events_from_subscribers(self, subscribers: Set[EventSubscriber]) -> Set[str]:
        """
        Retrieves a set of events associated with the specified subscribers.
        :param subscribers: A set of subscribers for which to retrieve the associated events.
        :return: A set of events associated with the given subscribers.
        """
        return {event for subscriber in subscribers for event in self.__inv_registry.get(subscriber, [])}

    def get_subscribers_from_events(self, events: Set[str]) -> Set[EventSubscriber]:
        """
        Retrieves a set of subscribers associated with the specified events.
        :param events: A set of events for which to retrieve the associated subscribers.
        :return: A set of subscribers associated with the given events.
        """
        return {subscriber for event in events for subscriber in self.__fwd_registry.get(event, [])}

    def get_event_count(self) -> int:
        """
        Retrieves the number of events registered.
        :return: The total count of events currently registered.
        """
        return len(self.__fwd_registry)

    def get_subscriber_count(self) -> int:
        """
        Retrieves the number of subscribers registered.
        :return: The total count of subscribers registered.
        """
        return len(self.__inv_registry)

    def get_event_count_from_subscriber(self, subscriber: EventSubscriber) -> int:
        """
        Retrieves the count of events associated with the specified subscriber.
        :param subscriber: The subscriber for which to count associated events.
        :return: The number of events associated with the given subscriber.
        """
        return len(self.__inv_registry[subscriber]) if subscriber in self.__inv_registry else 0

    def get_subscriber_count_from_event(self, event: str) -> int:
        """
        Retrieves the count of subscribers associated with the specified event.
        :param event: The event for which to count associated subscribers.
        :return: The number of subscribers associated with the given event.
        """
        return len(self.__fwd_registry[event]) if event in self.__fwd_registry else 0

    def contains_event(self, event: str) -> bool:
        """
        Checks if the given event is registered.
        :param event: The event to be checked.
        :return: `True` if the event is registered, `False` otherwise.
        """
        return event in self.__fwd_registry

    def contains_subscriber(self, subscriber: EventSubscriber) -> bool:
        """
        Checks if the given subscriber is registered.
        :param subscriber: The subscriber to be checked.
        :return: `True` if the subscriber is registered, `False` otherwise.
        """
        return subscriber in self.__inv_registry

    def are_associated(self, event: str, subscriber: EventSubscriber) -> bool:
        """
        Check if a specific event is associated with a particular subscriber.
        :param event: The event for which association is being checked.
        :param subscriber: The subscriber for which association is being checked.
        :return: `True` if the subscriber is associated with the event, `False` otherwise.
        """
        # Ensure that both the event and subscriber are registered
        if event not in self.__fwd_registry or subscriber not in self.__inv_registry:
            return False

        # Check if the subscriber is associated with the event
        return subscriber in self.__fwd_registry[event]

    def insert(self, event: str, subscriber: EventSubscriber) -> None:
        """
        Inserts the given subscriber with the specified event in the registry.
        :param event: The event to which the subscriber will be associated.
        :param subscriber: The subscriber to be inserted for the event.
        :return: None
        """
        # Add the subscriber to the event's set in the main registry
        if event not in self.__fwd_registry:
            self.__fwd_registry[event] = set()
        self.__fwd_registry[event].add(subscriber)

        # Add the event to the subscriber's set in the inverse registry
        if subscriber not in self.__inv_registry:
            self.__inv_registry[subscriber] = set()
        self.__inv_registry[subscriber].add(event)

    def remove(self, event: str, subscriber: EventSubscriber) -> Tuple[str | None, EventSubscriber | None]:
        """
        Removes the given subscriber from the specified event.
        :param event: The event from which the subscriber will be removed.
        :param subscriber: The subscriber to be removed from the event.
        :return: A tuple containing the removed event and subscriber, if applicable.
        """
        removed_event: str | None = None
        removed_subscriber: EventSubscriber | None = None

        # Remove the subscriber from the event's set
        self.__fwd_registry[event].remove(subscriber)

        # If the event has no remaining
        # subscribers, remove it from the registry
        if len(self.__fwd_registry[event]) == 0:
            self.__fwd_registry.pop(event)
            removed_event = event

        # Remove the event from the subscriber's set
        self.__inv_registry[subscriber].remove(event)

        # If the subscriber is no longer subscribed to
        # any event, remove it from the inverse registry
        if len(self.__inv_registry[subscriber]) == 0:
            self.__inv_registry.pop(subscriber)
            removed_subscriber = subscriber

        return removed_event, removed_subscriber

    def remove_event(self, event: str) -> Set[EventSubscriber]:
        """
        Removes the specified event from the registry and returns a set of subscribers
        that were completely removed as a side effect of removing the event.
        :param event: The event to be removed from the registry.
        :return: A set of subscribers that were completely
            removed due to the removal of the event.
        """
        # Remove the event and retrieve its subscribers
        subscribers: Set[EventSubscriber] = self.__fwd_registry.pop(event)

        # Initialize a set to store the subscribers
        # that will be completely removed from both registries
        removed_subscribers: Set[EventSubscriber] = set()

        # Remove the event from the subscriber's set
        for subscriber in subscribers:
            self.__inv_registry[subscriber].remove(event)

            # If the subscriber was only subscribed to this event, remove it from
            # the inverse registry and add it to the set of removed subscribers
            if len(self.__inv_registry[subscriber]) == 0:
                self.__inv_registry.pop(subscriber)
                removed_subscribers.add(subscriber)

        # Return the removed subscribers
        return removed_subscribers

    def remove_subscriber(self, subscriber: EventSubscriber) -> Set[str]:
        """
        Removes the specified subscriber from the registry and returns a set of events
        that were completely removed as a side effect of removing the subscriber.
        :param subscriber: The subscriber to be removed from the registry.
        :return: A set of events that were completely removed as a side
            effect of removing the subscriber.
        """
        # Retrieve events associated with the subscriber and remove it from the inverse registry
        events: Set[str] = self.__inv_registry.pop(subscriber)

        # Initialize a set to store the events that will
        # be completely removed from both registries
        removed_events: Set[str] = set()

        # Remove the subscriber from the event's set
        for event in events:
            self.__fwd_registry[event].remove(subscriber)

            # If the event had only that subscriber, remove it from
            # the registry and add it to the list of removed events
            if len(self.__fwd_registry[event]) == 0:
                self.__fwd_registry.pop(event)
                removed_events.add(event)

        # Return the removed events
        return removed_events

    def clear(self) -> Tuple[Set[str], Set[EventSubscriber]]:
        """
        Clears the event registry by removing all events and subscribers.
        :return: A tuple containing two sets; the first set includes the events that were removed
            from the registry, and the second set consists of the subscribers that were removed.
        """
        # Store the current events and subscribers before clearing the registry
        events, subscribers = self.get_events(), self.get_subscribers()

        # Clear both the main registry and the inverse registry
        self.__fwd_registry.clear()
        self.__inv_registry.clear()

        return events, subscribers

    def is_empty(self) -> bool:
        """
        Checks if the registry is empty.
        :return: `True` if the forward registry is empty, `False` otherwise.
        """
        return not self.__fwd_registry

    def __str__(self) -> str:
        """
        Returns a string representation of the EventRegistry.
        :return: A string representation of the EventRegistry.
        """
        return (
            "Event Registry: {\n"
            + "\n".join(
                f"\t'{event}': {{{', '.join(f'EventSubscriber <{hex(id(sub))}>' for sub in subscribers)}}}"
                for event, subscribers in self.__fwd_registry.items()
            )
            + "\n}"
        )
