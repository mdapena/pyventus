import sys
from abc import abstractmethod, ABC
from types import TracebackType
from typing import TypeVar, Generic, Tuple, Type

from .subscription import Subscription
from ..exceptions import PyventusException

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

_SourceType = TypeVar("_SourceType")
"""A generic type representing the source to which the subscription is performed."""

_SubscriberType = TypeVar("_SubscriberType", bound=Subscription)
"""A generic type representing the subscriber returned after performing the subscription."""


class SubscriptionContext(ABC, Generic[_SourceType, _SubscriberType]):
    """
    An abstract base class for subscription context managers.

    **Notes:**

    -   This class is designed to establish a context block for a step-by-step
        definition of an object that will later be subscribed to a specified source.

    -   Upon exiting the context, the defined object will be automatically subscribed.

    -   Through the `astuple()` method, this class not only returns the source object and
        its subscriber but also handles the release and cleanup of associated resources.

    -   Accessing the `subscriber` property before or during the subscription context
        will raise an exception.
    """

    # Attributes for the SubscriptionContext
    __slots__ = ("__source", "__retain_source", "__subscriber", "__retain_subscriber")

    @property
    def source(self) -> _SourceType | None:
        """
        Retrieves the source to which the subscription is performed.
        :return: The source object, or `None` if it was not retained
            for later access after exiting the context.
        """
        return self.__source if hasattr(self, "_SubscriptionContext__source") else None

    @property
    def subscriber(self) -> _SubscriberType | None:
        """
        Retrieves the subscriber that is returned after performing the subscription
        to the specified source.
        :return: The subscriber object, or `None` if it was not retained for later
            access after exiting the context.
        :raises PyventusException: If accessed before or during the subscription context.
        """
        if not hasattr(self, "_SubscriptionContext__subscriber"):
            return None

        if self.__subscriber is None:
            raise PyventusException("The 'subscriber' property is not accessible before or during the context block.")

        return self.__subscriber

    def __init__(self, source: _SourceType, retain_source: bool, retain_subscriber: bool) -> None:
        """
        Initialize an instance of `SubscriptionContext`.
        :param source: The source to which the subscription is performed.
        :param retain_source: A flag indicating whether to store the source object within the context,
            allowing it to be retrieved after the subscription context is closed. If set to `False`,
            the reference to the source object will be removed from the context instance upon closing
            the subscription context to optimize memory usage.
        :param retain_subscriber: A flag indicating whether to store the returned subscriber object
            within the context, allowing it to be retrieved after the subscription context block is
            closed. If set to `False`, the reference to the subscriber will not be stored in the
            context instance upon closing the subscription context, thereby optimizing memory usage.
        """
        # Validate the source and return flags
        if source is None:
            raise PyventusException("The 'source' argument cannot be None.")
        if not isinstance(retain_source, bool):
            raise PyventusException("The 'return_source' argument must be a boolean.")
        if not isinstance(retain_subscriber, bool):
            raise PyventusException("The 'return_subscriber' argument must be a boolean.")

        # Initialize instance variables
        self.__source: _SourceType = source
        self.__retain_source: bool = retain_source
        self.__subscriber: _SubscriberType | None = None
        self.__retain_subscriber: bool = retain_subscriber

    def __enter__(self: Self) -> Self:
        """
        Enters the subscription context block. Enables a progressive definition
        of the object that will later be subscribed to the specified source.
        :return: The subscription context manager.
        """
        return self

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
        # Finalize the subscription and retrieve the subscriber
        subscriber: _SubscriberType = self._exit()

        # Ensure the subscriber is valid
        if subscriber is None:
            raise PyventusException("The 'subscriber' argument cannot be None.")

        # Check if a subscriber has already been set to avoid an override
        if self.__subscriber:
            raise PyventusException("A 'subscriber' has already been set.")

        # Check if the subscriber should be retained for future access
        if not self.__retain_subscriber:
            # Remove subscriber-related attributes from the context
            del self.__subscriber, self.__retain_subscriber
        else:
            # Store the subscriber for future access
            self.__subscriber = subscriber

        # Remove source-related attributes from the context if not retained
        if not self.__retain_source:
            del self.__source, self.__retain_source

    @abstractmethod
    def _exit(self) -> _SubscriberType:
        """
        Finalizes the subscription process and returns the subscriber.

        This method is invoked upon exiting the context. It is responsible
        for completing the subscription of the defined object and returning
        the corresponding subscriber object. Additionally, it must handle
        the release and cleanup of any associated resources specific to
        the subclass.

        :return: The subscriber object.
        """
        pass

    def astuple(self) -> Tuple[_SourceType | None, _SubscriberType | None]:
        """
        Retrieves a tuple containing the source object and its subscriber.
        Handles the release and cleanup of associated resources.
        :return: A tuple containing the source object and its subscriber.
        :raises PyventusException: If accessed before or during the subscription context.
        """
        # Create a tuple with the source object and its subscriber
        results: Tuple[_SourceType | None, _SubscriberType | None] = (self.source, self.subscriber)

        # Perform cleanup by deleting unnecessary references
        if results[0]:
            del self.__source, self.__retain_source
        if results[1]:
            del self.__subscriber, self.__retain_subscriber

        return results
