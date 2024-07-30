import sys
from datetime import datetime
from threading import Lock
from typing import TypeAlias, Callable, Set, Union, List, Any, Dict

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from .unsubscribable import Unsubscribable
from ..exceptions import PyventusException
from ..utils import validate_callback

FinalizerType: TypeAlias = Union["Subscription", Callable[[], None]]
"""Type alias denoting a finalizer, which may refer to either a Subscription or a teardown callback."""


class Subscription(Unsubscribable):
    """
    A base class that represents a subscription to a source and provides a
    mechanism to release or clean up any associated resources.

    **Notes:**

    -   Finalizers, which may refer to either a Subscription instance or a
        callback function, can be attached to another subscription as a parent.

    -   When a parent subscription is unsubscribed, all its attached finalizers
        will be invoked. Subscription-based finalizers will have their `unsubscribe()`
        method called, while callback function-based finalizers will be executed.

    -   If a subscription-based finalizer is unsubscribed before its parent,
        it will be removed from the parent subscription.

    -   This class has been implemented with *thread safety* in mind. All of its
        methods synchronize access to mutable attributes to prevent race conditions
        when managing subscriptions in a multi-threaded environment.

    -   The serialization process for this class is optimized to ensure that only
        attributes relevant to the object's state are preserved. This helps maintain
        valid states across different scopes by ensuring that attributes that are out
        of context (such as the `teardown_callback`, `finalizers`, and `_thread_lock`)
        are not serialized.
    """

    # Subscription attributes
    __slots__ = ("__closed", "__timestamp", "__teardown_callback", "__finalizers", "_thread_lock")

    @property
    def closed(self) -> bool:
        """
        Determines whether the `Subscription` has already been unsubscribed.
        :return: A boolean value indicating if the subscription is closed (unsubscribed).
        """
        return self.__closed

    @property
    def timestamp(self) -> datetime:
        """
        Retrieves the timestamp when the subscription was created.
        :return: The timestamp when the subscription was created.
        """
        return self.__timestamp

    def __init__(self, teardown_callback: Callable[[Self], None]) -> None:
        """
        Initialize an instance of `Subscription`.
        :param teardown_callback: A callback function that is invoked during
            unsubscription. This callback is responsible for performing cleanup
            or teardown logic associated with the subscription.
        """
        # Validate the teardown callback
        validate_callback(callback=teardown_callback)

        # Initialize attributes
        self.__closed: bool = False
        self.__timestamp: datetime = datetime.now()
        self.__teardown_callback: Callable[[Self], None] = teardown_callback
        self.__finalizers: Set[FinalizerType] | None = None
        self._thread_lock: Lock = Lock()

    def unsubscribe(self: Self) -> None:
        # Initialize variables to store the teardown callback and finalizers
        # that will be executed when the current subscription is unsubscribed
        teardown_callback: Callable[[Self], None] | None = None
        finalizers: Set[FinalizerType] | None = None

        # Acquire the lock to ensure exclusive access to mutable properties
        with self._thread_lock:

            # Check if the current subscription is open
            if not self.__closed:
                # Mark the subscription as closed
                self.__closed = True

                # Store the teardown callback and finalizers for later execution
                teardown_callback = self.__teardown_callback
                finalizers = self.__finalizers
                self.__finalizers = None

        # Execute the teardown logic if any
        if teardown_callback is not None:
            teardown_callback(self)

        # Execute finalizers if any
        if finalizers is not None:
            # Track exceptions raised during finalizer execution
            exceptions: List[str] = []

            # Execute each finalizer
            for finalizer in finalizers:
                try:
                    # Call 'unsubscribe' for subscription-based finalizers,
                    # and execute callback function-based finalizers
                    if isinstance(finalizer, Subscription):
                        finalizer.unsubscribe()
                    else:
                        finalizer()
                except Exception as exception:
                    # Store exceptions raised during finalizer execution
                    exceptions.append(repr(exception))

            # Raise an exception if there were any
            # exceptions during finalizer execution
            if exceptions:
                raise PyventusException(exceptions)

    def contains_finalizer(self, finalizer: FinalizerType) -> bool:
        """
        Determines whether the current subscription contains the given finalizer.
        :param finalizer: The finalizer to be checked.
        :return: `True` if the current subscription contains
            the given finalizer, `False` otherwise.
        """
        if finalizer is None:
            return False  # type: ignore[unreachable]

        with self._thread_lock:
            if self.__finalizers is None:
                return False
            return finalizer in self.__finalizers

    def add_finalizers(self, *finalizers: FinalizerType) -> None:
        """
        Attach one or more finalizers to the current subscription.

        **Notes**:

        -   When the current subscription is unsubscribed, all its attached
            finalizers will be invoked. Subscription-based finalizers will have
            their `unsubscribe()` method called, while callback function-based
            finalizers will be executed.

        :param finalizers: The finalizers to be attached to the subscription.
        :return: None
        """
        # Return if no finalizers have been provided
        if not finalizers:
            return

        # Create a set to hold the new finalizers
        new_finalizers: Set[FinalizerType] = set()

        # Iterate over each finalizer
        for finalizer in finalizers:

            # Skip the finalizer if it is the current subscription
            if finalizer is self:
                continue

            # If it is a Subscription-based finalizer
            if isinstance(finalizer, Subscription):

                # Skip the finalizer if it is already closed
                if finalizer.closed:
                    continue

                # If the current subscription is already closed, call
                # the finalizer's unsubscribe method and skip it
                if self.__closed:
                    finalizer.unsubscribe()
                    continue
            else:
                # If it is a callback function-based finalizer,
                # ensure that it is a valid callback function
                validate_callback(callback=finalizer)

                # If the current subscription is already closed,
                # execute the finalizer and skip it
                if self.__closed:
                    finalizer()
                    continue

            # Add the finalizer to the new_finalizers set
            new_finalizers.add(finalizer)

        # If there are new finalizers to add, acquire the
        # lock and add them to the current subscription
        if new_finalizers:
            with self._thread_lock:
                if self.__finalizers is None:
                    # If there are no existing finalizers, set the new finalizers directly
                    self.__finalizers = new_finalizers
                else:
                    # If there are existing finalizers, add the new finalizers to the set
                    self.__finalizers.update(new_finalizers)

    def remove_finalizers(self, *finalizers: FinalizerType) -> None:
        """
        Remove one or more finalizers from the current subscription.
        :param finalizers: The finalizers to be removed from the subscription.
        :return: None
        """
        # Return if no finalizers have been provided
        if not finalizers:
            return

        # Acquire the lock to ensure exclusive access to mutable properties
        with self._thread_lock:

            # If there are no existing finalizers, return early
            if self.__finalizers is None:
                return

            # Iterate over each finalizer to remove them from the set
            for finalizer in finalizers:
                self.__finalizers.discard(finalizer)

            # If there are no more remaining finalizers,
            # set the finalizers property to None
            if not self.__finalizers:
                self.__finalizers = None

    def clear_finalizers(self) -> None:
        """
        Clear all finalizers from the current subscription.
        :return: None
        """
        with self._thread_lock:
            self.__finalizers = None

    def __getstate__(self) -> Dict[str, Any]:
        """
        Prepare the object state for serialization.

        This method is called when the object is pickled. It returns a dictionary
        containing the attributes that should be serialized. Only the attributes
        that are necessary for reconstructing the object in another process or
        context are included to improve efficiency and avoid issues with
        contextually irrelevant attributes.

        :return: A dictionary containing the serialized state of the object.
        """
        # Include only the attributes that are necessary for serialization
        # Attributes like __teardown_callback are not included as they are
        # context-specific and do not make sense in another scope/process.
        return {"__closed": self.__closed, "__timestamp": self.__timestamp}

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Restore the object from the serialized state.

        This method is called when the object is unpickled. It takes a dictionary
        containing the serialized state and restores the object's attributes.
        Additionally, it sets default values for attributes that were not serialized,
        ensuring the object remains in a valid state after deserialization.

        :param state: A dictionary containing the serialized state of the object.
        :return: None
        """
        # Restore the attributes from the serialized state
        self.__closed = state["__closed"]
        self.__timestamp = state["__timestamp"]

        # Set default values for attributes that were not serialized
        self.__teardown_callback = lambda s: print("The teardown_callback is out of scope and has no effect.")
        self.__finalizers = None
        self._thread_lock = Lock()

    def __str__(self) -> str:
        """
        Return a formatted string representation of the subscription.
        :return: A string representation of the subscription.
        """
        return "".join(
            [
                f"Closed: {self.__closed} | ",
                f"Finalizers: {0 if self.__finalizers is None else len(self.__finalizers)} | ",
                f"Timestamp: {self.__timestamp.strftime('%Y-%m-%d %I:%M:%S %p')}",
            ]
        )
