import sys
from datetime import datetime
from typing import Callable, TypeAlias, Union

from .unsubscribable import Unsubscribable
from ..utils import validate_callable

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

FinalizerType: TypeAlias = Union["Subscription", Callable[[], None]]
"""Type alias denoting a finalizer, which may refer to either a Subscription or a teardown callback."""


class Subscription(Unsubscribable):
    """
    A base class that represents a subscription to a source and provides a
    mechanism to release or clean up any associated resources.
    """

    # Attributes for the Subscription
    __slots__ = ("__timestamp", "__teardown_callback")

    @property
    def timestamp(self) -> datetime:
        """
        Retrieves the timestamp when the subscription was created.
        :return: The timestamp when the subscription was created.
        """
        return self.__timestamp

    def __init__(self, teardown_callback: Callable[[Self], bool]) -> None:
        """
        Initialize an instance of `Subscription`.
        :param teardown_callback: A callback function invoked during the
            unsubscription process to perform cleanup or teardown operations
            associated with the subscription. It should return `True` if the
            cleanup was successful, or `False` if the teardown has already been
            executed and the subscription is no longer active.
        """
        # Validate the teardown callback
        validate_callable(teardown_callback)

        # Initialize attributes
        self.__timestamp: datetime = datetime.now()
        self.__teardown_callback: Callable[[Self], bool] = teardown_callback

    def unsubscribe(self: Self) -> bool:
        return self.__teardown_callback(self)

    def __str__(self) -> str:
        """
        Return a formatted string representation of the subscription.
        :return: A string representation of the subscription.
        """
        return f"Timestamp: {self.__timestamp.strftime('%Y-%m-%d %I:%M:%S %p')}"
