import sys
from abc import abstractmethod, ABC
from types import TracebackType
from typing import TypeVar, Generic, Tuple, Type

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from .subscription import Subscription
from ..exceptions import PyventusException

_T = TypeVar("_T")
"""A generic type representing the source to which the subscription is performed."""

_S = TypeVar("_S", bound=Subscription)
"""A generic type representing the subscriber returned after performing the subscription."""


class SubscriptionContext(ABC, Generic[_T, _S]):
    """
    An abstract base class for subscription context managers.

    **Notes:**

    -   This class is designed to establish a context block for a step-by-step
        definition of an object that will later be subscribed to a specified source.

    -   Upon exiting the context, the defined object will be automatically subscribed and
        its returned subscriber available.

    -   Through the `astuple()` method, this class not only returns the source object and
        its subscriber but also handles the release and cleanup of associated resources.

    -   Accessing the `subscriber` property before or during the subscription context
        will raise an exception.
    """

    # Subscription Context attributes
    __slots__ = (
        "__source",
        "__subscriber",
    )

    @property
    def source(self) -> _T:
        """
        Retrieves the source to which the subscription is performed.
        :return: The source object.
        """
        return self.__source

    @property
    def subscriber(self) -> _S:
        """
        Retrieves the subscriber that is returned after performing the subscription
        to the specified source.
        :return: The subscriber object.
        :raises PyventusException: If accessed before or during the subscription context.
        """
        if self.__subscriber is None:
            raise PyventusException("The 'subscriber' property is not accessible before or during the context block.")
        return self.__subscriber

    def __init__(self, source: _T) -> None:
        """
        Initialize an instance of `SubscriptionContext`.
        :param source: The source to which the subscription is performed.
        """
        # Ensure 'source' is not None
        if source is None:
            raise PyventusException("The 'source' argument cannot be None.")

        # Initialize source and subscriber variables
        self.__source: _T = source
        self.__subscriber: _S | None = None

    def __enter__(self: Self) -> Self:
        """
        Enters the subscription context block. Enables a progressive definition
        of the object that will later be subscribed to the specified source.
        :return: The subscription context manager.
        """
        return self

    @abstractmethod
    def __exit__(
        self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """
        Exits the subscription context block. Subscribes the defined object
        to the specified source, and performs any necessary cleanup.
        :param exc_type: The type of the raised exception, if any.
        :param exc_val: The raised exception object, if any.
        :param exc_tb: The traceback information, if any.
        :return: None
        """
        pass

    def _set_subscriber(self, subscriber: _S) -> None:
        """
        Sets the subscriber object.
        :param subscriber: The subscriber object to be assigned.
        :return: None
        :raise PyventusException: If the `subscriber` argument is `None`
        or if a `subscriber` has already been set.
        """
        # Ensure 'subscriber' is not None
        if subscriber is None:
            raise PyventusException("The 'subscriber' argument cannot be None.")

        # Check if a subscriber has already been set to avoid an override
        if self.__subscriber:
            raise PyventusException("A 'subscriber' has already been set.")

        # Assign the given subscriber
        self.__subscriber = subscriber

    def astuple(self) -> Tuple[_T, _S]:
        """
        Retrieves a tuple containing the source object and its subscriber.
        Handles the release and cleanup of associated resources.
        :return: A tuple containing the source object and its subscriber.
        :raises PyventusException: If accessed before or during the subscription context.
        """
        # Create a tuple with the source object and its subscriber
        results: Tuple[_T, _S] = (self.source, self.subscriber)

        # Perform cleanup by deleting unnecessary references
        del self.__source, self.__subscriber

        return results
