from abc import ABC, abstractmethod
from types import TracebackType
from typing import Generic, TypeVar

from typing_extensions import Self

from ..exceptions import PyventusException
from ..utils import attributes_repr, formatted_repr
from .subscription import Subscription

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

    -   Through the `unpack()` method, this class not only returns the source object and
        its subscriber but also handles the release and cleanup of associated resources.

    -   This subscription context can be `stateful`, retaining references to the `source` object
        and `subscriber`, or `stateless`, which clears the context upon exiting the subscription
        block.
    """

    # Attributes for the SubscriptionContext
    __slots__ = ("__source", "__subscriber", "__is_stateful")

    def __init__(self, source: _SourceType, is_stateful: bool) -> None:
        """
        Initialize an instance of `SubscriptionContext`.

        :param source: The source to which the subscription is performed.
        :param is_stateful: A flag indicating whether the context preserves its state (stateful) or
            not (stateless) after exiting the subscription context. If `True`, the context retains its
            state, allowing access to stored objects, including the `source` object and the `subscriber`
            object. If `False`, the context is stateless, and the stored state is cleared upon exiting
            the subscription context to prevent memory leaks.
        """
        # Validate the source and flags
        if source is None:  # pragma: no cover
            raise PyventusException("The 'source' argument cannot be None.")
        if not isinstance(is_stateful, bool):  # pragma: no cover
            raise PyventusException("The 'stateful_context' argument must be a boolean.")

        # Initialize instance variables
        self.__source: _SourceType = source
        self.__subscriber: _SubscriberType | None = None
        self.__is_stateful: bool = is_stateful

    def __repr__(self) -> str:
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return formatted_repr(
            instance=self,
            info=attributes_repr(
                source=self._source.__name__ if isinstance(self._source, type) else self._source,
                subscriber=self._subscriber,
            ),
        )

    @property
    def _source(self) -> _SourceType | None:
        """
        Retrieve the source to which the subscription is performed.

        :return: The source object, or `None` if it was not retained
            for later access after exiting the context.
        """
        return self.__source if hasattr(self, "_SubscriptionContext__source") else None

    @property
    def _subscriber(self) -> _SubscriberType | None:
        """
        Retrieve the subscriber that is returned after performing the subscription to the specified source.

        :return: The subscriber object, or `None` if it was not retained for later access after exiting the context.
        :raises PyventusException: If accessed before or during the subscription context.
        """
        if not hasattr(self, "_SubscriptionContext__subscriber"):
            return None

        if self.__subscriber is None:
            raise PyventusException("The 'subscriber' property is not accessible before or during the context block.")

        return self.__subscriber

    @property
    def _is_stateful(self) -> bool:
        """
        Determine whether the context preserves its state or not after exiting the subscription context.

        :return: `True` if the context retains its state, allowing access to stored objects,
            including the `source` object and the `subscriber` object; `False` if the context
            is stateless, meaning the stored state is cleared upon exiting the subscription
            context to prevent memory leaks.
        """
        return self.__is_stateful

    @abstractmethod
    def _exit(self) -> _SubscriberType:
        """
        Finalize the subscription process and returns the subscriber.

        This method is invoked upon exiting the context. It is responsible
        for completing the subscription of the defined object and returning
        the corresponding subscriber object. Additionally, it must handle
        the release and cleanup of any associated resources specific to
        the subclass.

        :return: The subscriber object.
        """
        pass

    def unpack(self) -> tuple[_SourceType | None, _SubscriberType | None]:
        """
        Unpack and retrieve the source object and its associated subscriber.

        This method returns a tuple containing the source object and its subscriber,
        while also handling the cleanup of associated resources to prevent memory leaks.
        After retrieving the objects, it deletes internal references to the source and
        subscriber to ensure they are no longer retained.

        :return: A tuple of the form (source, subscriber). Both may be `None` if the
            subscription context has either unpacked the state previously or is stateless.
        :raises PyventusException: If this method is called before or during the subscription
            context, indicating that the resources are not yet available for unpacking.
        """
        # Create a tuple with the source object and its subscriber
        results: tuple[_SourceType | None, _SubscriberType | None] = (self._source, self._subscriber)

        # Perform cleanup by deleting unnecessary references
        if results[0]:
            del self.__source
        if results[1]:
            del self.__subscriber

        return results

    def __enter__(self: Self) -> Self:
        """
        Enter the subscription context block.

        This method facilitates the progressive definition of an
        object that will later be subscribed to the specified source.

        :return: The subscription context manager.
        """
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """
        Exit the subscription context block.

        This method subscribes the defined object to the
        specified source, and performs any necessary cleanup.

        :param exc_type: The type of the raised exception, if any.
        :param exc_val: The raised exception object, if any.
        :param exc_tb: The traceback information, if any.
        :return: None.
        """
        # Finalize the subscription and retrieve the subscriber
        subscriber: _SubscriberType = self._exit()

        # Ensure the subscriber is valid
        if subscriber is None:  # pragma: no cover
            raise PyventusException("The 'subscriber' argument cannot be None.")

        # Check if a subscriber has already been set to avoid an override
        if self.__subscriber:  # pragma: no cover
            raise PyventusException("A 'subscriber' has already been set.")

        if self.__is_stateful:
            # Retain the subscriber if the context is stateful
            self.__subscriber = subscriber
        else:
            # Remove context-specific references if stateless
            del self.__source, self.__subscriber

        # Remove the stateful context flag
        del self.__is_stateful
